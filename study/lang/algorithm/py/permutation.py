def next(arr):
    n = len(arr)
    if n <= 1: return False, arr
    j = n-2
    for _ in range(n-2, -1, -1):
        if arr[j] < arr[j+1]: break
        j -= 1
    if j == -1:
        arr = list(reversed(arr))
        return False, arr
    l = n-1
    for _ in range(n-1, j, -1):
        if arr[l] > arr[j]: break
        l -= 1
    arr[j], arr[l] = arr[l], arr[j]
    arr = arr[:j+1] + list(reversed(arr[j+1:]))
    return True, arr

# common swap
def permutateA(arr):
    while True:
        yield arr
        ok, arr = next(arr)
        if not ok: break

def permutateB(arr):
    copy = arr[:]
    n = len(arr)
    c = [0] * n
    o = [1] * n
    j = n-1
    s = 0
    yield copy
    while True:
        q = c[j] + o[j]
        if q >= 0 and q != j + 1:
            i1 = j - c[j] + s
            i2 = j - q + s
            copy[i1], copy[i2] = copy[i2], copy[i1]
            yield copy
            c[j] = q
            j = n-1
            s = 0
            continue
        if q == j + 1:
            if j == 0: break
            s += 1
        o[j] = -o[j]
        j -= 1

# O(n^2) instead of O(n) for each permutation
def permutateC(arr):
    n = len(arr)
    constFac = [i for i in range(n+1)]
    constFac[0] = 1
    for i in range(2, n+1):
        constFac[i] *= constFac[i-1]

    fac = constFac[n]
    for offset in range(fac):
        r = arr[:]
        used = [False] * n
        for i in range(n):
            k = offset // constFac[n - i - 1]
            for j in range(n):
                if not used[j]:
                    if k == 0: break
                    k -= 1
            r[i] = arr[j]
            used[j] = True
            offset %= constFac[n - i - 1]
        yield r


print("Swap")
for one in permutateA([1, 2, 3]):
    print(one)

print("Steinhaus-Johnson-Trotter")
for one in permutateB([1, 2, 3]):
    print(one)

print("A[i]")
for one in permutateC([1, 2, 3]):
    print(one)
