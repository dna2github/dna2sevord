import random

def trie(tr, path):
   cur = tr
   for x in path:
      if x not in cur:
         cur[x] = {}
      cur = cur[x]
   if len(path) > 0:
      cur['_'] = True

def trie_find(tr, path):
   cur = tr
   for x in path:
      if x not in cur: return False
      cur = cur[x]
   if len(path) == 0: return True
   return '_' in cur

def px(arr, p):
   n = len(arr)
   for i in range(n):
      if p < arr[i]: return i
      p -= arr[i]
   return n-1

def norm(arr):
   n = len(arr)
   s = reduce(lambda x,y: x+y, arr)
   if s == 0: return False
   s *= 1.0
   for i in range(n):
      arr[i] /= s
   return True

def dist(pathmap, path):
   n = len(path)-1
   d = pathmap.distance
   s = 0
   for i in range(n):
      s += d[path[i]][path[i+1]]
   return s

class Ant(object):
   memory = None
   def __init__(self):
      self.reset()

   def reset(self):
      self.memory = {
         'path': [],
         'cold': {},
      }

class PathMap(object):
   # [ [1,-1], [-1, 1] ]
   distance = None
   ph = None

class AntColonyOptimizer(object):
   ants = None
   pathmap = None

   def build(self, n, pathmap):
      self.pathmap = pathmap
      self.ants = []
      for i in range(n):
         self.ants.append(Ant())
      m1 = len(self.pathmap.distance)
      m2 = len(self.pathmap.distance[0])
      ph0 = [1.0]*m2
      norm(ph0)
      self.pathmap.ph = []
      for i in range(m1):
         self.pathmap.ph.append(ph0[:])

   def ant_step(self, ant, source, target):
      path = ant.memory['path']
      cold = ant.memory['cold']
      n = len(path)
      if n == 0:
         path.append(source)
         cold[source] = True
      else:
         cur = path[-1]
         if self.pathmap.distance[cur][target] >= 0:
            path.append(target)
            for i in range(n):
               a = path[i]
               b = path[i+1]
               self.pathmap.ph[a][b] *= 2
               norm(self.pathmap.ph[a])
            ant.reset()
            return path
         to = px(self.pathmap.ph[cur], random.random())
         if to in cold:
            return None
         if cur == to:
            self.pathmap.ph[cur][to] = 0
            norm(self.pathmap.ph[cur])
            return None
         if self.pathmap.distance[cur][to] < 0:
            self.pathmap.ph[cur][to] = 0
            if not norm(self.pathmap.ph[cur]):
               path.pop()
               if len(path) == 0:
                  # source isolate
                  return None
            return None
         cold[to] = True
         path.append(to)
      return None

   def optimize(self, source, target):
      t = {}
      r = []
      m = -1
      for _ in range(500):
         for ant in self.ants:
            x = self.ant_step(ant, source, target)
            if x is not None:
               if trie_find(t, x):
                  continue
               d = dist(self.pathmap, x)
               if m < 0:
                  r = [x]
                  m = d
                  trie(t, x)
               elif d < m:
                  r = [x]
                  m = d
                  trie(t, x)
               elif d == m:
                  r.append(x)
                  trie(t, x)
      return r, m


if __name__ == '__main__':
   pathmap = PathMap()
   pathmap.distance = [
      [ 0,  1,  2,  3,  4,  5,  6,  7,  8, -1],
      [ 1,  0,  1, -1, -1, -1, -1, -1, -1, -1],
      [ 2,  1,  0,  1, -1, -1, -1, -1, -1, -1],
      [ 3, -1,  1,  0,  1, -1, -1, -1, -1, -1],
      [ 4, -1, -1,  1,  0,  0.5, -1, -1, -1, -1],
      [ 5, -1, -1, -1,  1,  0,  1, -1, -1, -1],
      [ 6, -1, -1, -1, -1,  1,  0,  1, -1, -1],
      [ 7, -1, -1, -1, -1, -1,  1,  0,  1, -1],
      [ 8, -1, -1, -1, -1, -1, -1,  1,  0,  1],
      [-1, -1, -1, -1, -1, -1, -1, -1,  1,  0],
   ]
   aco = AntColonyOptimizer()
   aco.build(10, pathmap)
   print(aco.optimize(0, 9))
