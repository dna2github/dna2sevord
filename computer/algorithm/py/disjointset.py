class DisjointSet(object):
   array = None
   parent = {}
   rank = {}
   def __init__(self, array=None):
      if array:
         self.build(array)

   def build(self, array):
      self.array = array[:]
      for i, v in enumerate(array):
         self.parent[v] = i
         self.rank[v] = 0

   def find(self, val):
      t = val
      p = self.parent[val]
      v = self.array[p]
      while (t != v):
         p = self.parent[v]
         t = v
         v = self.array[p]
      # path compress
      rp = p
      rv = self.array[rp]
      p = self.parent[val]
      self.parent[val] = rp
      while (rp != p):
         v = self.array[p]
         p = self.parent[v]
         self.parent[v] = rp
      return p, v

   def union(self, val1, val2):
      p1, v1 = self.find(val1)
      p2, v2 = self.find(val2)
      if self.rank[v1] < self.rank[v2]:
         self.parent[v2] = p1
      else:
         self.parent[v1] = p2
         if self.rank[v1] == self.rank[v2]: self.rank[v2] += 1


if __name__ == '__main__':
   s = DisjointSet([1,2,3,4,5,6,7,8,9])
   s.union(1, 2)
   s.union(3, 4)
   s.union(5, 6)
   s.union(7, 8)
   s.union(2, 4)
   s.union(8, 9)
   s.union(6, 8)
   s.find(5)
   s.union(4, 8)
   s.find(1)
   print(s.rank, s.parent, s.array)
