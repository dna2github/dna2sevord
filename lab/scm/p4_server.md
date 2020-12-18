how to get file list and file content:

```
p4 dirs -e <path>*[#<revision>]
p4 files -e <path>*[#<revision>]

p4 print -q <path>[#<revision>]
```

how to get blame info:

```
p4 filelog -s -i <path>
p4 annotate -q <path>[#<revision>] (rev)
p4 annotate -c -I -q <path>#<client> (cln)
```

how to search:

```
p4 grep -n -e <regexp> <path>...
e.g. p4 grep -n -e test //depot/main/... //depot/b1/....java
```

p4 server:
- a file is stored as "<path>,v" e.g. `//depot/main/README.md` -> `/p4root/depot/main/README.md,v`

```
head     1.1;
access   ;
symbols  ;
locks    ;comment  @@;


1.1
date     2020.11.15.23.14.03;  author p4;  state Exp;
branches ;
next     ;


desc
@@


1.1
log
@@
text
@........hello@@world.com........@
```
