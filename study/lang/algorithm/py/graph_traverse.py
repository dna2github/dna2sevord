# graph = [ [x, { out: val }], ... ]

def bfs(G, start):
    r = []
    st = [start]
    n = len(G)
    v = [False] * n
    while len(st) > 0:
        curN = len(st)
        for i in range(curN):
            k = st[i]
            node = G[k]
            v[k] = True
            r.append(node[0])
            for j in node[1].keys():
                if v[j]: continue
                v[j] = True
                st.append(j)
        st = st[curN:]
    return r

def dfs(G, start):
    r = []
    st = [start]
    n = len(G)
    v = [False] * n
    while len(st) > 0:
        k = st.pop()
        node = G[k]
        v[k] = True
        r.append(node[0])
        for j in node[1].keys():
            if v[j]: continue
            v[j] = True
            st.append(j)
    return r

def build_udg(G):
    for i, node in enumerate(G):
        for j in node[1].keys():
            another = G[j]
            if i not in another[1]:
                another[1][i] = node[1][j]
    return G

test = [
    [1, {1: 8, 2: 9}],
    [2, {3: 5, 4: 8}],
    [3, {5: 5}],
    [4, {6: 5, 7: 8}],
    [5, {7: 6, 8: 9}],
    [6, {4: 3}],
    [7, {9: 6}],
    [8, {9: 7}],
    [9, {9: 6}],
    [10, {}],
] # DG definition
test = build_udg(test)

print("BFS", bfs(test, 0))
print("DFS", dfs(test, 0))
