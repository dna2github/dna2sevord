import random

class Node(object):
   val = None
   pri = 0
   parent = None
   left = None
   right = None
   size = 0

   def __init__(self, val):
      self.val = val
      self.size = 1
      self.pri = random.random()

   def rotate(self):
      if not self.parent: return
      p = self.parent
      gp = self.parent.parent
      if p.left == self:
         if self.right:
            p.left = self.right
            self.right.parent = p
         else:
            p.left = None
         self.right = p
      else:
         if self.left:
            p.right = self.left
            self.left.parent = p
         else:
            p.right = None
         self.left = p
      p.parent = self
      if gp:
         self.parent = gp
         if gp.left == p:
            gp.left = self
         else:
            gp.right = self
      else:
         self.parent = None
      p.size = 1
      if p.left: p.size += p.left.size
      if p.right: p.size += p.right.size
      self.size = 1
      if self.left: self.size += self.left.size
      if self.right: self.size += self.right.size


class Treap(object):
   root = None
   cmpfn = lambda self,x,y: x < y

   def __init__(self):
      pass

   def _rotate(self, node):
      node.rotate()
      if not node.parent: self.root = node

   def _search(self, val):
      cur = self.root
      if not cur: return None
      last = None
      while cur and cur.val != val:
         last = cur
         if self.cmpfn(val, cur.val):
            cur = cur.left
         else:
            cur = cur.right
      if cur:
         return cur
      return last

   def find(self, val):
      return self._search(val)

   def insert(self, val):
      newnode = Node(val)
      node = self._search(val)
      if node:
         if self.cmpfn(val, node.val):
            node.left = newnode
         else:
            node.right = newnode
         newnode.parent = node
         cur = newnode.parent
         while cur:
            cur.size += 1
            cur = cur.parent
         cur = newnode
         while cur.parent:
            if cur.pri > cur.parent.pri: break
            self._rotate(cur)
      else:
         self.root = newnode

   def remove(self, val):
      node = self._search(val)
      if not node: return
      while node.left or node.right:
         if not node.left or node.right and node.left.pri > node.right.pri:
            self._rotate(node.right)
         else:
            self._rotate(node.left)
      par = None
      if node.parent:
         if node.parent.left == node:
            par = node.parent.left
            node.parent.left = None
         else:
            par = node.parent.right
            node.parent.right = None
      if par:
         cur = node.parent
         while cur:
            cur.size -= 1
            cur = cur.parent
      else:
         self.root = None

   def rank(self, k):
      cur = self.root
      if not cur: return None
      if k < 1 or k > cur.size: return None
      while True:
         left_size = 0
         if cur.left: left_size = cur.left.size
         if left_size + 1 == k: break
         if cur.left and cur.left.size >= k:
            cur = cur.left
         else:
            k -= cur.left.size+1 if cur.left else 1
            cur = cur.right
         if not cur: break
      return cur


if __name__ == '__main__':
    t = Treap()
    t.insert(1)
    t.insert(2)
    t.insert(3)
    t.insert(5)
    t.insert(4)
    t.insert(6)
    t.insert(7)
    t.insert(8)
    t.insert(9)
    t.remove(3)
    print t.rank(3).val, t.root.size
