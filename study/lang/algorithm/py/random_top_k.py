import random

def select(arr, n, k):
    v = random.randint(0, n-1)
    x = arr[v]
    a1 = []
    a2 = []
    a3 = []
    for one in arr:
        if one < x:
            a1.append(one)
        elif one > x:
            a3.append(one)
        else:
            a2.append(one)
    a1n = len(a1)
    a2n = len(a2)
    a3n = len(a3)
    if a1n >= k: return select(a1, a1n, k)
    if a1n + a2n >= k: return x
    return select(a3, a3n, k - a1n - a2n)

def top_k(arr, k):
    return select(arr, len(arr), k)

print(top_k([1,2,3,4,5,6,7,8,9,10,12,13], 7))
