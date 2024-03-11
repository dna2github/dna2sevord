def dup(G, emptyEdge=False):
    if emptyEdge:
        return [[one[0], {}] for one in G]
    else:
        return [[one[0], {k: v for k, v in one[1].items()}] for one in G]

def build_layer(G, st, ed):
    L = dup(G)
    que = [st]
    lv = { st: 0 }
    lvcur = 1
    while len(que) > 0:
        n = len(que)
        for _ in range(n):
            cur = que.pop(0)
            tos = list(L[cur][1].keys())
            for to in tos:
                if to in lv:
                    if to != ed and lv[to] < lvcur:
                        L[cur][1].pop(to)
                    continue
                que.append(to)
                lv[to] = lvcur
        lvcur += 1
    if ed not in lv:
        return None
    return L

def step(Gstream, Gremain, st, ed):
    L = build_layer(Gremain, st, ed)
    if L is None:
        return False
    cur = st
    p = []
    c = -1
    while len(L[st][1].keys()) > 0:
        Lu = dup(L, True)
        while cur != ed:
            if len(L[cur][1].keys()) > 0:
                p.append(cur)
                v = list(L[cur][1].keys())[0]
                cv = L[cur][1][v]
                if c == -1 or c > cv:
                    c = cv
                cur = v
            else:
                L[cur][1] = {}
                for one in L:
                    if cur in one[1]:
                        one[1].pop(cur)
                if cur == st: break
                cur = p.pop()
        if cur == ed:
            p.append(ed)
            u = p.pop(0)
            for v in p:
                Lu[u][1][v] = c
                if v not in Gstream[u][1]:
                    Gstream[u][1][v] = c
                else:
                    Gstream[u][1][v] += c
                remain = L[u][1][v] - c
                if remain == 0:
                    L[u][1].pop(v)
                else:
                    L[u][1][v] = remain
                u = v
        for i, one in enumerate(Lu):
            for to in Lu[i][1].keys():
                remain = Gremain[i][1][to] - Lu[i][1][to]
                if remain == 0:
                    Gremain[i][1].pop(to)
                else:
                    Gremain[i][1][to] = remain
        p = []
        cur = st
    return True

def dinic(G, st, ed):
    Gstream = dup(G, True)
    Gremain = dup(G)
    while step(Gstream, Gremain, st, ed):
        pass
    return Gstream

def build_udg(G):
    for i, node in enumerate(G):
        for j in node[1].keys():
            another = G[j]
            if i not in another[1]:
                another[1][i] = node[1][j]
    return G

test = [
    ['s', {1: 13, 2: 4}],
    ['a', {2: 2, 3: 9}],
    ['b', {1: 10, 4: 8}],
    ['c', {2: 9, 4: 1, 5: 7}],
    ['d', {5: 9}],
    ['t', {}],
]

print(dinic(test, 0, 5))
