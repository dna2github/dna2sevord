def step(G, shortestStat, out, candidate):
    node = G[candidate]
    for k in reaches:
        base = shortestStat[candidate]
        baseL = base[0]
        thisL = node[1][k]

        if k not in out:
            out[k] = baseL + thisL
        elif out[k] > baseL + thisL:
            out[k] = baseL + thisL

        if k not in shortestStat:
            shortestStat[k] = [baseL + thisL, [one + [candidate] for one in base[1]]]
        else:
            stat = shortestStat[k]
            statL = stat[0]
            if statL > baseL + thisL:
                shortestStat[k] = [baseL + thisL, [one + [candidate] for one in base[1]]]
            elif statL == baseL + thisL:
                stat[1] += [one + [candidate] for one in base[1]]
        #print(candidate, k, shortestStat)

def dp_shortestpath(G, start, end):
    if start == end: return r
    n = len(G)
    v = [False] * n
    candidates = []
    # i: [shortestValue, [path, ...]]
    shortestStat = { start: [0, [ [] ]] }
    # i: edgeValue
    out = {}
    candidate = 0
    while candidate != -1:
        v[candidate] = True
        step(G, shortestStat, out, candidate)
        candidate = -1
        candidateV = -1
        for j in out.keys():
            if v[j]: continue
            if candidateV == -1 or candidateV > out[j]:
                candidate = j
                candidateV = out[j]
    if end not in shortestStat:
        return None
    stat = shortestStat[end]

    for i, one in enumerate(stat[1]):
        stat[1][i] = [G[x][0] for x in one]
        stat[1][i].append(G[end][0])
    return stat


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
    [5, {7: 6, 8: 7}],
    [6, {4: 3}],
    [7, {9: 6}],
    [8, {9: 7}],
    [9, {9: 1}],
    [10, {}],
] # DG definition
test = build_udg(test)
# 24; [1 2 4 7 10] [1 2 5 9 10]
print(dp_shortestpath(test, 0, 9))
