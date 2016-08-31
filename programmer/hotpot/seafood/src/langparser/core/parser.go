package core

type Walker struct {
   Stops     *[]rune
   Text      []rune
   Token     string
   Stop      rune
   Cursor, N int
}

func (w *Walker) SetText(text string) {
   w.Text = []rune(text)
   w.N = len(w.Text)
   w.Cursor = 0
}

func (w *Walker) IsStopper (stop rune) bool {
   for _, v := range *w.Stops {
      if v == stop {
         return true
      }
   }
   return false
}

func (w *Walker) Next () bool {
   if w.Cursor >= w.N {
      return false
   }
   i := w.Cursor
   for {
      if i >= w.N {
         w.Stop = 0
         break
      }
      w.Stop = w.Text[i]
      if w.IsStopper(w.Stop) {
        break
      }
      i += 1
   }
   w.Token = string(w.Text[w.Cursor:i])
   w.Cursor = i + 1
   return true
}

func (w *Walker) ParseString (escape bool) bool {
   origin_stops := w.Stops
   pair := w.Stop
   update_stops := []rune{}
   if escape {
     update_stops = []rune{pair, '\\'}
   } else {
     update_stops = []rune{pair}
   }
   w.Stops = &update_stops
   start := w.Cursor
   for {
      if !w.Next() {
         break
      }
      if w.Stop == pair ||  w.Cursor >= w.N || w.Cursor <= 0 {
         break
      }
      // if stop == makrEscape {
      w.Cursor += 2
      // }
   }
   w.Token = string(w.Text[start:w.Cursor - 1])
   w.Stops = origin_stops
   return true
}

func (w *Walker) ParseLongString (start, end string, escape bool) bool {
   origin_stops := w.Stops
   update_stops := []rune{}
   start_rune   := []rune(start)
   start_n      := len(start_rune)
   end_rune     := []rune(end)
   end_n        := len(end_rune)
   end1st       := end_rune[0]
   markEscape   := '\\'

   // start or end is empty
   if start_n == 0 || end_n == 0 {
      return false
   }
   // eof
   if w.Cursor + start_n >= w.N {
      return false
   }
   // not match start
   if string(w.Text[w.Cursor-1:w.Cursor+start_n-1]) != start {
      return false
   }

   if escape {
     update_stops = []rune{end1st, markEscape}
   } else {
     update_stops = []rune{end1st}
   }
   w.Stops = &update_stops
   w.Cursor += start_n - 1
   start_index := w.Cursor
   end_index   := 0
   for {
      w.Next()
      if w.Stop == end1st && w.Cursor + end_n - 1 <= w.N {
         if string(w.Text[w.Cursor-1:w.Cursor+end_n-1]) == end {
            end_index = w.Cursor - 1
            w.Stop = end_rune[end_n - 1]
            w.Cursor += end_n
            break
         }
      } else if escape && markEscape == w.Stop {
         w.Cursor += 1
      }
      if '\x00' == w.Stop || w.Cursor >= w.N || w.Cursor <= 0 {
         end_index = w.Cursor
         break
      }
   }
   w.Token = string(w.Text[start_index:end_index])
   w.Stops = origin_stops
   return true
}

func (w *Walker) SeeForward(n int) string {
   n += w.Cursor
   if n > w.N {
      n = w.N
   }
   return string(w.Text[w.Cursor:n])
}

func (w *Walker) SeeBackward(n int) string {
   n = w.Cursor - n
   if n < 0 {
      n = 0
   }
   return string(w.Text[n:w.Cursor])
}

func (w *Walker) SeeCharForward(ch rune, stop rune) string {
   i := w.Cursor
   v := '\x00'
   for i < w.N {
      v = w.Text[i]
      if v == ch {
         return string(w.Text[w.Cursor:i+1])
      }
      if v == stop {
         break
      }
      i += 1
   }
   return ""
}

func (w *Walker) SeeCharBackward(ch rune, stop rune) string {
   i := w.Cursor - 1
   v := '\x00'
   for i >= 0 {
      v = w.Text[i]
      if v == ch {
         return string(w.Text[i:w.Cursor])
      }
      if v == stop {
         break
      }
      i -= 1
   }
   return ""
}
