class Knapsack(object):
   def package(self, bag, items):
      n = len(items)
      v0 = [0]*(bag+1)
      for item in items:
         v = [0]*(bag+1)
         for j in range(1, bag+1):
            v[j] = v0[j]
            w = item['w']
            z = item['v']
            if w <= j:
               i = j - w
               # v[j] = max([v[j], v0[i]+z])
               if v[j] > v0[i] + z:
                  pass
               elif v[j] < v0[i] + z:
                  v[j] = v0[i] + z
               else: # v[j] = v0[i] + z
                  pass
         v0 = v
      return v[-1]

if __name__ == '__main__':
   print(Knapsack().package(100, [
      {'w': 51, 'v': 51},
      {'w': 50, 'v': 50},
      {'w': 20, 'v': 22},
      {'w': 41, 'v': 21},
      {'w': 30, 'v': 25},
      {'w': 14, 'v': 10},
      {'w': 50, 'v': 50},
      {'w': 28, 'v': 27},
      {'w': 24, 'v': 27},
      {'w': 30, 'v': 26},
   ]))
