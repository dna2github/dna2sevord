def lookfor_substring(text, pattern):
   n = len(pattern)
   next_tbl = [0]*(n+1)
   for i in range(n):
      j = i
      while j > 0:
         j = next_tbl[j]
         if pattern[i] == pattern[j]:
            next_tbl[i+1] = j + 1
            break
   # optimize original kmp
   for i in range(n):
      if next_tbl[i] > 0:
         if pattern[i] == pattern[next_tbl[i]]:
            next_tbl[i] = 0
   #######################
   print(next_tbl)
   p = []
   j = 0
   for i in range(len(text)):
      if j < n and text[i] == pattern[j]:
         j += 1
      else:
         while j > 0:
            j = next_tbl[j]
            if text[i] == pattern[j]:
               j += 1
               break
      if j == n:
         p.append(i - n + 1)
   return p

if __name__ == '__main__':
   print (lookfor_substring('this is a test and test', 'test'))
   print (lookfor_substring('abcabcabcaabcdaabcabaabcbaabcab', 'abcdaabcab'))
