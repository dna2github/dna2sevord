class Trie(object):
   trie = {}
   def __init__(self):
      self.build()

   def build(self):
      self.trie = {}

   def add(self, word):
      cur = self.trie
      for ch in word:
         if ch not in cur:
            cur[ch] = {}
         cur = cur[ch]
      cur['_t'] = True

   def lookup(self, word):
      cur = self.trie
      for ch in word:
         if ch not in cur:
            return False
         cur = cur[ch]
      return cur.get('_t', False)

if __name__ == '__main__':
   t = Trie()
   for word in ['hello', 'world', 'word', 'wow']:
      t.add(word)
   print(t.lookup('wo'), t.lookup('word'), t.trie)
