package main

import "time"
import "fmt"

func main() {
  test := true
  for test {
    fmt.Println("hello world!")
    time.Sleep(1000 * time.Millisecond)
  }
  fmt.Println("Bye-bye")
}

/*
GDB Inject:
   go build -gcflags "-N" test.go
   ./test
   ps -ef | grep test
   gdb -p <pid>
   > b test.go:9
   > c
   > info locals
   > set test = false
   > c
*/
