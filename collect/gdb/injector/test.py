import time

test = True
while test:
    print ("Hello World")
    time.sleep(1)
print("Bye-bye")

"""
GDB Inject:
   python test.py
   ps -ef | grep python
   gdb -p <pid>
   > call PyGILState_Ensure()
   > call PyRun_SimpleString("global test; test = False")
   > call PyGILState_Release($1)
   > c
"""
