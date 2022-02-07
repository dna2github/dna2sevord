# stdout buffer

How to disable stdout buffer for immediate output:

### Python

```
python -u xxx.py
```

### C

```
ref: https://stackoverflow.com/questions/1716296/why-does-printf-not-flush-after-the-call-unless-a-newline-is-in-the-format-strin
fprintf(stderr, "I will be printed immediately");

printf("Buffered, will be flushed");
fflush(stdout);

setbuf(stdout, NULL);
setvbuf(stdout, NULL, _IONBF, 0);
```
