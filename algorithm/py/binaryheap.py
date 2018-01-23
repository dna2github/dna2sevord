class BinaryHeap(object):
   heap = []
   cmpfn = lambda self,x,y: x < y
   def __init__(self, array=None, cmpfn=None):
      if cmpfn:
         self.cmpfn = cmpfn
      if array:
         self.build(array)

   def build(self, array):
      self.heap = array[:]
      n = len(self.heap)
      for i in range(n/2, -1, -1):
         self.down(i)

   def push(self, val):
      n = len(self.heap)
      self.heap.append(val)
      self.up(n)

   def pop(self):
      n = len(self.heap)
      if n == 0: return
      n -= 1
      t = self.heap[0]
      self.heap[0] = self.heap[n]
      self.heap[n] = t
      self.heap.pop()
      self.down(0)

   def update(self, index, val):
      n = len(self.heap)
      if index < 0 or index >= n: return
      self.heap[index] = val
      index = self.down(index)
      self.up(index)

   def top(self):
      return self.get(0)

   def get(self, index):
      n = len(self.heap)
      if index < 0 or index >= n: return None
      return self.heap[index]

   def down(self, index):
      i = index
      n = len(self.heap)
      while i < n:
         c1 = i*2+1
         if c1 >= n: break
         c2 = c1+1
         if c2 < n and self.cmpfn(self.heap[c2], self.heap[c1]):
            c1 = c2
         if self.cmpfn(self.heap[c1], self.heap[i]):
            t = self.heap[i]
            self.heap[i] = self.heap[c1]
            self.heap[c1] = t
         else:
            break
         i = c1
      return i

   def up(self, index):
      i = index
      while i > 0:
         p = (i-1)/2
         if self.cmpfn(self.heap[i], self.heap[p]):
            t = self.heap[i]
            self.heap[i] = self.heap[p]
            self.heap[p] = t
         else:
            break
         i = p
      return i


if __name__ == '__main__':
   b = BinaryHeap([9,8,7,6,5,4,3,2,1])
   print(b.heap) # 1 2 3 6 5 4 7 8 9
   b.pop()
   print(b.heap) # 2 5 3 6 9 4 7 8
   b.pop()
   print(b.heap) # 3 5 4 6 9 8 7
   b.push(1)
   b.push(2)
   b.update(1, 10)
   print(b.heap) # 13 4 5 9 8 7 6 10
