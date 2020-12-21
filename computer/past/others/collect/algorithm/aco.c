#include <time.h>
#include <stdlib.h>
#include <stdio.h>

#define EPSILON 1e-6f
#define ZERO(x) ((x) < 0 ?(-(x) < EPSILON):((x) < EPSILON))

typedef struct {
  int   n;
  int * matrix;
} graph;

typedef struct {
  graph * g;
  int k, from, to;
  float * pheromone;
  int   * stay;
} ants;

void
lib_memclear(char * list, int n) {
  while (n > 0) {
    *list = 0;
    list ++;
    n --;
  }
}

int
graph_search_decode(ants * s, int printout) {
  int i, j, k, v, max, n;
  int * visited, * path;
  int sum = 0;
  n = s->g->n;
  visited = (int*)malloc(sizeof(int)*n);
  path = (int*)malloc(sizeof(int)*n);
  lib_memclear((char*)visited, sizeof(int)*n);
  lib_memclear((char*)path, sizeof(int)*n);
  j = max = s->from;
  v = 0;
  visited[j] = 1;
  path[v++] = j;
  for (i=n-1; i>0; i--) {
    for (k=n-1; k>=0; k--) {
      if (k == j) continue;
      if (!visited[k] && s->g->matrix[j * n + k] > 0 && (s->g->matrix[j * n + max] <= 0 || s->pheromone[k] > s->pheromone[max])) {
        max = k;
      }
    }
    sum += s->g->matrix[j * n + max];
    j = max;
    visited[j] = 1;
    path[v++] = j;
    if (j == s->to) break;
  }
  if (j == s->to) {
    if (sum < printout) {
      printf("%d", path[0]);
      for (i=1; i<v; i++) {
        printf("->%d", path[i]);
      }
      printf(", path=%d\n", sum);
      printout = sum;
    }
  } else {
    sum = 999999;
  }
  free(visited);
  free(path);
  sum = printout;
  return sum;
}

void
graph_search_dump(ants * s) {
  printf("k=%d, from=%d, to=%d ( ", s->k, s->from, s->to);
  int i;
  for (i=0; i<s->g->n; i++) {
    printf("[%d, %.4f] ", s->stay[i], s->pheromone[i]);
  }
  printf(")\n");
}

void
graph_init(graph * self, int n) {
  int i;
  self->n = n;
  self->matrix = (int*)malloc(sizeof(int)*n*n);
  for (i=n*n-1; i>=0; i--) {
    self->matrix[i] = 0;
  }
}

void graph_set_dist(graph * self, int from, int to, int dist) {
  self->matrix[from * self->n + to] = dist;
  self->matrix[to * self->n + from] = dist;
}

int graph_get_dist(graph * self, int from, int to) {
  return self->matrix[from * self->n + to];
}

void
graph_search_init(graph * self, ants * search, int k, int from, int to) {
  int i;
  int n = self->n;
  search->g = self;
  search->k = k;
  search->from = from;
  search->to = to;
  search->pheromone = (float*)malloc(sizeof(float)*n);
  search->stay = (int*)malloc(sizeof(int)*n);
  lib_memclear((char*)(search->pheromone), sizeof(float)*n);
  lib_memclear((char*)(search->stay), sizeof(int)*n);
  for (i=0; i<n; i++) {
    search->stay[from] = k;
  }
  search->pheromone[from] = 1.0f;
  search->pheromone[to]   = 1.0f;
}

void
graph_search_next(ants * search) {
  int i, j, k, x;
  int n = search->g->n;
  float sum;
  float * p = (float*)malloc(sizeof(float)*n);
  int   * next_stay = (int*)malloc(sizeof(int)*n);
  lib_memclear((char*)next_stay, sizeof(int)*n);
  for (i=n-1; i>=0; i--) {
    if (search->stay[i] == 0) continue;
    lib_memclear((char*)p, sizeof(float)*n);
    sum = 0.0f;
    // calculate move prob
    for (j=n-1; j>=0; j--) {
      if (i == j) continue;
      p[j] = graph_get_dist(search->g, i, j);
      if (ZERO(p[j])) continue;
      p[j] = 1000 - p[j] * (1 - search->pheromone[j]);
      sum += p[j];
    }
    if (ZERO(sum)) { // dead node
      next_stay[search->from] += search->stay[i];
      if (i != search->to) {
        search->pheromone[i] = 0.0f;
      }
      continue;
    }
    for (j=n-1; j>=0; j--) {
      p[j] /= sum;
      p[j] *= 1000.0f;
    }
    // move ants
    for (k=search->stay[i]-1; k>=0; k--) {
      x = rand() % 1000;
      sum = 1.0f * x;
      j = n;
      do {
        j --;
        sum -= p[j];
      } while (sum > 0);
      next_stay[j] ++;
    }
  }
  // update pheromone
  // learn speed = 0.2
  float alpha = 0.2f;
  for (i=n-1; i>=0; i--) {
    search->stay[i] = next_stay[i];
    search->pheromone[i] = next_stay[i] * 1.0f / search->k * alpha + (1 - alpha) * search->pheromone[i];
  }
  search->pheromone[search->from] = 1.0f;
  search->pheromone[search->to] = 1.0f;
  free(next_stay);
  free(p);
}

void
graph_search_free(ants * search) {
}

void
graph_free(graph * self) {
}

int main() {
  srand(time(NULL));
  graph g;
  ants  a;
  graph_init(&g, 20);
  graph_set_dist(&g, 0, 1, 50);
  graph_set_dist(&g, 0, 2, 65);
  graph_set_dist(&g, 0, 3, 45);
  graph_set_dist(&g, 0, 4, 30);
  graph_set_dist(&g, 1, 2, 60);
  graph_set_dist(&g, 1, 5, 62);
  graph_set_dist(&g, 1, 6, 27);
  graph_set_dist(&g, 2, 3, 43);
  graph_set_dist(&g, 2, 6, 250);
  graph_set_dist(&g, 2, 7, 35);
  graph_set_dist(&g, 2, 8, 29);
  graph_set_dist(&g, 3, 4, 90);
  graph_set_dist(&g, 3, 8, 17);
  graph_set_dist(&g, 3, 9, 40);
  graph_set_dist(&g, 3, 10, 15);
  graph_set_dist(&g, 4, 10, 230);
  graph_set_dist(&g, 5, 6, 25);
  graph_set_dist(&g, 5, 11, 136);
  graph_set_dist(&g, 6, 7, 32);
  graph_set_dist(&g, 6, 8, 30);
  graph_set_dist(&g, 6, 11, 58);
  graph_set_dist(&g, 6, 12, 220);
  graph_set_dist(&g, 7, 8, 120);
  graph_set_dist(&g, 7, 11, 61);
  graph_set_dist(&g, 7, 12, 88);
  graph_set_dist(&g, 7, 13, 20);
  graph_set_dist(&g, 8, 9, 61);
  graph_set_dist(&g, 8, 13, 150);
  graph_set_dist(&g, 8, 14, 60);
  graph_set_dist(&g, 9, 10, 32);
  graph_set_dist(&g, 9, 14, 194);
  graph_set_dist(&g, 9, 15, 142);
  graph_set_dist(&g, 9, 18, 110);
  graph_set_dist(&g, 10, 15, 130);
  graph_set_dist(&g, 11, 12, 144);
  graph_set_dist(&g, 11, 16, 161);
  graph_set_dist(&g, 12, 13, 24);
  graph_set_dist(&g, 12, 16, 71);
  graph_set_dist(&g, 12, 17, 54);
  graph_set_dist(&g, 13, 14, 40);
  graph_set_dist(&g, 13, 17, 72);
  graph_set_dist(&g, 13, 19, 22);
  graph_set_dist(&g, 14, 15, 77);
  graph_set_dist(&g, 14, 18, 14);
  graph_set_dist(&g, 14, 19, 220);
  graph_set_dist(&g, 15, 18, 89);
  graph_set_dist(&g, 16, 17, 26);
  graph_set_dist(&g, 17, 19, 26);
  graph_set_dist(&g, 18, 19, 72);
  graph_search_init(&g, &a, 1000, 0, 19);
  int i, k, j = a.from, min = 999999;
  for (i = 0; i < 20000; i++) {
    graph_search_next(&a);
    //graph_search_dump(&a);
    min = graph_search_decode(&a, min);
  }
  graph_search_dump(&a);
  return 0;
}
