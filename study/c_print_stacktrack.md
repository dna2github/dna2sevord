```
#include <execinfo.h>
#include <stdio.h>

void print_trace (void) {
   void *array[10];
   char **strings;
   int size, i;
   size = backtrace(array, 10);
   strings = backtrace_symbols(array, size);
   if (strings) {
      printf ("Obtained %d stack frames.\n", size);
      for (i = 0; i < size; i++) printf ("%s\n", strings[i]);
   } else {
      printf("<trace> nothing.\n");
   }
   free (strings);
}

// use print_trace() when needed
```
