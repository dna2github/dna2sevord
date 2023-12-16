package main

import (
   "fmt"
   "flag"
   "os"
   "io"
   "bufio"
   "langparser/core"
)

const BUF_SIZE = 4 * 1204

func usage() {
   fmt.Printf("Usage: %s\n", os.Args[0])
   flag.PrintDefaults()
}

func paused (stop rune) bool {
   return stop == '\x00'
}

func java_c_javascript_block (walker *core.Walker) (state rune, last string) {
   for walker.Next() {
      if paused(walker.Stop) {
         last = walker.Token
         break
      }
      fmt.Println(string(walker.Stop), walker.Token)
      state = walker.Stop
      last = ""
      if state == '"' || state == '\'' {
         walker.ParseString(true)
         fmt.Println("char/string>", walker.Token)
      } else if state == '/' {
         if walker.ParseLongString("//", "\n", false) {
            fmt.Println("line comment>", walker.Token)
         } else if walker.ParseLongString("/*", "*/", false) {
            state = '*'
            fmt.Println("multiline comment>", walker.Token)
         }
      }
      if paused(walker.Stop) {
         last = walker.Token
         break
      }
   }
   if len(last) > 0 {
      fmt.Println("tail>", state, last)
   }
   return state, last
}

func main () {
   stops := flag.String("stops", "\n\t `~!@#$%^&*()-+=_{}[]|\\:;'\"<>,./?", "Language Word Stopper")
   //text := flag.String("text", "This is a test.", "Raw Text")
   flag.Usage = usage
   flag.Parse()
   flag.Args()

   stops_rune := []rune(*stops)
   walker     := core.Walker{&stops_rune, []rune(""), "", '\x00', 0, 0}
   reader     := bufio.NewReader(os.Stdin)
   buffer     := make([]byte, 0)
   tmpbuf     := make([]byte, BUF_SIZE)
   for {
      size, err := reader.Read(tmpbuf)
      if size == 0 {
         break
      }
      if size < BUF_SIZE {
         tmpbuf = tmpbuf[:size]
      }
      buffer = append(buffer, tmpbuf...)
      if err == io.EOF {
         break
      }
   }
   walker.SetText(string(buffer))
   java_c_javascript_block(&walker)
}
