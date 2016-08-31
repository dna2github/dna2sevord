package main

import (
   "fmt"
   "os"
   "flag"
   "langparser/core"
)

func usage() {
   fmt.Printf("Usage: %s\n", os.Args[0])
   flag.PrintDefaults()
}

func main () {
   stops := flag.String("stops", "\n\t ~!@#$%^&*()-+=_{}[]|\\:;'\"<>,./?", "Language Word Stopper")
   stops_rune := []rune(*stops)
   text := flag.String("text", "This is a test.", "Raw Text")
   flag.Usage = usage
   flag.Parse()

   flag.Args()
   fmt.Println(*stops)

   fmt.Println("Hello World")

   walker := core.Walker{&stops_rune, []rune(""), "", '\x00', 0, 0}
   walker.SetText(*text)
   for walker.Next() {
      fmt.Println(walker.Token)
      if walker.Stop == '"' {
         walker.ParseString(true)
         fmt.Println(walker.Token)
      } else if walker.Stop == '/' {
         if walker.ParseLongString("//", "\n", false) {
            fmt.Println(walker.Token)
         } else if walker.ParseLongString("/*", "*/", false) {
            fmt.Println(walker.Token)
         }
      }
   }
}
