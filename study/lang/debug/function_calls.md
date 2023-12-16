# Debug program to Get Function Call Relationships

### Python

Write a python file, for example, named as `pytrace.py`; then import
it to any python application entry. It will print function calls during
the application running.

```python
import sys
import os


ME_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "")
ME_DIR_N = len(ME_DIR)

import subprocess
PYTHON_DIR = os.path.dirname(subprocess.check_output("which python", shell=True))
PYTHON_DIR_N = len(PYTHON_DIR)

def _frame_deep(f_back):
    n = 0
    while f_back:
        f_back = f_back.f_back
        n += 1
    return n


def _trace_calls_and_returns(frame, event, arg):
    co = frame.f_code
    func_name = co.co_name
    if func_name == "write":
        # Ignore write() calls from print statements
        return
    line_no = frame.f_lineno
    filename = co.co_filename
    if ME_DIR in filename:
        cur_dir_n = ME_DIR_N
    # uncoment below lines to track function calls in python libraries
    #elif PYTHON_DIR in filename:
    #    cur_dir_n = PYTHON_DIR_N
    else:
        return

    filename = filename[cur_dir_n:]
    frame_deep = _frame_deep(frame.f_back) * 3
    if event == "call":
        print "%s<F:%s :: %s(%s)>" % (" " * frame_deep, func_name, filename, line_no)
        return _trace_calls_and_returns
    elif event == "return":
        print "%s<F:%s :: return>" % (" " * frame_deep, func_name) # %s -> arg => return_val
    return


sys.settrace(_trace_calls_and_returns)
```

### NodeJS

`node --trace <app.js>` will print verbose function calls. Thus we can do tricky to filter in
what we need like adding `grep`.
