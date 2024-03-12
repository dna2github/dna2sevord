class Node(object):
    def __init__(self, x, left=None, right=None, h=1):
        self.x = x
        self.h = h
        self.L = left
        self.R = right

    def __str__(self):
        return f"{self.x} [{self.L.x if self.L else None} {self.R.x if self.R else None}]"

class AVL(object):
    def __init__(self):
        self.tree = None

    def lookup(self, x):
        cur = self.tree
        while cur is not None:
            if cur.x == x:
                return cur
            if cur.x < x:
                cur = cur.R
            else:
                cur = cur.L
        return cur

    def insert(self, x):
        self.tree = self._insert(self.tree, x)

    def _insert(self, node, x):
        if node is None:
            return Node(x)

        if x < node.x:
            node.L = self._insert(node.L, x)
        elif x > node.x:
            node.R = self._insert(node.R, x)
        else:
            return node

        node.h = max(self._h(node.L), self._h(node.R)) + 1
        b = self._is_balance(node)

        if b > 1:
            if x < node.L.x:
                return self._R(node)
            elif x > node.L.x:
                node.L = self._L(node.L)
                return self._R(node)
        if b < -1:
            if x > node.R.x:
                return self._L(node)
            elif x < node.R.x:
                node.R = self._R(node.R)
                return self._L(node)
        return node

    def remove(self, x):
        self.tree = self._remove(self.tree, x)
    def _min(self, node):
        cur = node
        while cur and cur.L:
            cur = cur.L
        return cur
    def _remove(self, node, x):
        if node is None:
            return None

        if x < node.x:
            node.L = self._remove(node.L, x)
        elif x > node.x:
            node.R = self._remove(node.R, x)
        elif not node.L or not node.R:
            if node.L:
                node = node.L
            elif node.R:
                node = node.R
            else:
                return None
        else:
            minR = self._min(node.R)
            node.x = minR.x
            node.R = self._remove(node.R, minR.x)

        if node is None:
            return None

        node.h = max(self._h(node.L), self._h(node.R)) + 1
        b = self._is_balance(node)
        if b > 1:
            if self._is_balance(node.L) >= 0:
                return self._R(node)
            else:
                node.L = self._L(node.L)
                return self._R(node)
        elif b < -1:
            if self._is_balance(node.R) <= 0:
                return self._L(node)
            else:
                node.R = self._R(node.R)
                return self._L(node)
        return node

    def traverse_mid(self):
        self._traverse_mid(self.tree)
    def _traverse_mid(self, node):
        if node is None: return
        self._traverse_mid(node.L)
        print(node)
        self._traverse_mid(node.R)

    def _is_balance(self, node):
        if node is None: return 0
        return self._h(node.L) - self._h(node.R)

    def _h(self, node):
        if node is None: return 0
        return node.h

    def _L(self, node):
        newp = node.R
        move = newp.L
        newp.L = node
        node.R = move

        node.h = max(self._h(node.L), self._h(node.R))+1
        newp.h = max(self._h(newp.L), self._h(newp.R))+1
        return newp

    def _R(self):
        newp = node.L
        move = newp.R
        newp.R = node
        node.L = move

        node.h = max(self._h(node.L), self._h(node.R))+1
        newp.h = max(self._h(newp.L), self._h(newp.R))+1
        return newp


a = AVL()
a.insert(10)
a.insert(20)
a.insert(30)
a.insert(40)
a.insert(50)
a.insert(60)
a.insert(70)
a.remove(40)
a.traverse_mid()
