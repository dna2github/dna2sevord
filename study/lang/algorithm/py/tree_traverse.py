# array as tree [0 1 2 None 4 5]
"""
0
|-- 1
|   |-- None
|   |--4
|-- 2
|   |--5
"""

def isNull(tree, index):
    if index < 0: return True
    n = len(tree)
    if index >= n: return True
    if tree[index] is None: return True
    return False

def traverse_pre(tree):
    r = []
    st = [0]
    i = 0
    while len(st) > 0:
        i = st.pop()
        if isNull(tree, i): continue
        r.append(tree[i])
        st.append(i*2+2)
        st.append(i*2+1)
    return r

def traverse_mid(tree):
    r = []
    st = []
    i = 0
    while len(st) > 0 or not isNull(tree, i):
        if isNull(tree, i):
            i = st.pop()
            r.append(tree[i])
            i = i*2+2
        else:
            st.append(i)
            i = i*2+1
    return r

def traverse_post(tree):
    r = []
    st = []
    i = 0
    pre = -1
    while len(st) > 0 or not isNull(tree, i):
        while not isNull(tree, i):
            st.append(i)
            i = i*2+1
        i = st.pop()
        if isNull(tree, i*2+2) or pre == i*2+2:
            r.append(tree[i])
            pre = i
            i = -1
        else:
            st.append(i)
            i = i*2+2
    return r

test = [1,2,3,4,5,6,7,8,9,10,11,12]
print(test)
print("--- pre", traverse_pre(test)) # 1 2 4 8 9 5 10 11 3 6 12 7
print("--- mid", traverse_mid(test)) # 8 4 9 2 10 5 11 1 12 6 3 7
print("-- post", traverse_post(test)) # 8 9 4 10 11 5 2 12 6 7 3 1
