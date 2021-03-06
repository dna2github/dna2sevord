package main

import (
   "math"
   "math/rand"
   "fmt"
)

type SimpleMatrix struct {
   M, N int
   Data [][]float64
}


func NewSimpleMatrix (m, n int) *SimpleMatrix {
   mat := new(SimpleMatrix)
   mat.M = m
   mat.N = n
   mat.Data = make([][]float64, m)
   for i := m - 1; i >= 0; i-- {
      mat.Data[i] = make([]float64, n)
   }
   return mat
}

func (X *SimpleMatrix) T() *SimpleMatrix {
   R := NewSimpleMatrix(X.N, X.M)
   for i := X.M - 1; i >= 0; i-- {
      for j := X.N - 1; j >= 0; j-- {
         R.Data[j][i] = X.Data[i][j]
      }
   }
   return R
}

func (X *SimpleMatrix) FillRandom (a, b float64) *SimpleMatrix {
   for i := X.M - 1; i >= 0; i-- {
      for j := X.N - 1; j >= 0; j-- {
         X.Data[i][j] = rand.Float64() * (b - a) + a
      }
   }
   return X
}

func (X *SimpleMatrix) Clone () *SimpleMatrix {
   R := NewSimpleMatrix(X.M, X.N)
   for i := X.M - 1; i >= 0; i-- {
      for j := X.N - 1; j >= 0; j-- {
         R.Data[i][j] = X.Data[i][j]
      }
   }
   return R
}

func (X *SimpleMatrix) Map (f func (float64) float64) *SimpleMatrix {
   R := NewSimpleMatrix(X.M, X.N)
   for i := X.M - 1; i >= 0; i-- {
      for j := X.N - 1; j >= 0; j-- {
         R.Data[i][j] = f(X.Data[i][j])
      }
   }
   return R
}

func (X *SimpleMatrix) Reduce (f func(float64, float64) float64, init float64) float64 {
   r := init
   for i := X.M - 1; i >= 0; i-- {
      for j := X.N - 1; j >= 0; j-- {
         r = f(r, X.Data[i][j])
      }
   }
   return r
}

func (X *SimpleMatrix) Row (x int) *SimpleMatrix {
   R := NewSimpleMatrix(1, X.N)
   for i := X.N - 1; i >= 0; i-- {
      R.Data[0][i] = X.Data[x][i]
   }
   return R
}

func (X *SimpleMatrix) Col (x int) *SimpleMatrix {
   R := NewSimpleMatrix(X.M, 1)
   for i := X.M - 1; i >= 0; i-- {
      R.Data[i][0] = X.Data[i][x]
   }
   return R
}

func (X *SimpleMatrix) MirrorM () *SimpleMatrix {
   n := X.N - 1
   R := NewSimpleMatrix(X.M, X.N)
   for i := X.M - 1; i >= 0; i-- {
      for j := X.N - 1; j >= 0; j-- {
         R.Data[i][j] = X.Data[i][n - j]
      }
   }
   return R
}

func (X *SimpleMatrix) MirrorN () *SimpleMatrix {
   m := X.M - 1
   R := NewSimpleMatrix(X.M, X.N)
   for i := X.M - 1; i >= 0; i-- {
      for j := X.N - 1; j >= 0; j-- {
         R.Data[i][j] = X.Data[m - i][j]
      }
   }
   return R
}

func (X *SimpleMatrix) EltMul(Y *SimpleMatrix) *SimpleMatrix {
   if X.M != Y.M && X.N != Y.N {
      return nil
   }
   R := NewSimpleMatrix(X.M, X.N)
   for i := X.M - 1; i >= 0; i-- {
      for j := X.N - 1; j >= 0; j-- {
         R.Data[i][j] = X.Data[i][j] * Y.Data[i][j]
      }
   }
   return R
}

func (X *SimpleMatrix) Dot(Y *SimpleMatrix) *SimpleMatrix {
   if X.N != Y.M {
      return nil
   }
   R := NewSimpleMatrix(X.M, Y.N)
   for i := X.M - 1; i >= 0; i-- {
      for j := Y.N - 1; j >= 0; j-- {
         sum := 0.0
         for k := X.N - 1; k >= 0; k-- {
            sum += X.Data[i][k] * Y.Data[k][j]
         }
         R.Data[i][j] = sum
      }
   }
   return R
}

func (X *SimpleMatrix) Add(Y *SimpleMatrix, a1, a2 float64) *SimpleMatrix {
   if X.M != Y.M && X.N != Y.N {
      return nil
   }
   R := NewSimpleMatrix(X.M, X.N)
   for i := X.M - 1; i >= 0; i-- {
      for j := X.N - 1; j >= 0; j-- {
         R.Data[i][j] = a1 * X.Data[i][j] + a2 * Y.Data[i][j]
      }
   }
   return R
}

func (X *SimpleMatrix) Scale(a float64) *SimpleMatrix {
   R := NewSimpleMatrix(X.M, X.N)
   for i := X.M - 1; i >= 0; i-- {
      for j := X.N - 1; j >= 0; j-- {
         R.Data[i][j] = X.Data[i][j] * a
      }
   }
   return R
}

type RecurrentNerualNetwork struct {
   Alpha float64
   InputDim, HiddenDim, OutputDim int
   Synapse0, Synapse1, SynapseH, Tmp *SimpleMatrix
}

func sigmoid(x float64) float64 {
   return 1.0/(1.0 + math.Exp(x))
}

func sigmoid_backward(x float64) float64 {
   return x*(1 - x)
}

func add(r float64, x float64) float64 {
   return r + x
}

func NewRecurrentNerualNetwork (alpha float64, indim, hiddendim, outdim int) *RecurrentNerualNetwork {
   rnn := new(RecurrentNerualNetwork)
   rnn.Alpha = alpha
   rnn.InputDim = indim
   rnn.HiddenDim = hiddendim
   rnn.OutputDim = outdim
   rnn.Synapse0 = NewSimpleMatrix(rnn.InputDim, rnn.HiddenDim)
   rnn.Synapse1 = NewSimpleMatrix(rnn.HiddenDim, rnn.OutputDim)
   rnn.SynapseH = NewSimpleMatrix(rnn.HiddenDim, rnn.HiddenDim)
   return rnn
}

func (rnn *RecurrentNerualNetwork) Train(in *SimpleMatrix, out *SimpleMatrix) float64 {
   // in = M*N, out = 1*N
   n   := out.N
   err := 0.0
   layer_2_deltas := make([]*SimpleMatrix, 0)
   layer_1_values := make([]*SimpleMatrix, 0)
   layer_1_values = append(layer_1_values, NewSimpleMatrix(1, rnn.HiddenDim))
   current := NewSimpleMatrix(out.M, out.N)
   for i := 0; i < n; i++ {
      X := in.Col(in.N - i - 1).T()
      y := out.Col(out.N - i - 1).T()
      layer_1 := X.Dot(rnn.Synapse0).Add(layer_1_values[len(layer_1_values) - 1].Dot(rnn.SynapseH), 1, 1).Map(sigmoid)
      layer_2 := layer_1.Dot(rnn.Synapse1).Map(sigmoid)
      layer_2_error := y.Add(layer_2, 1, -1)
      layer_2_delta := layer_2_error.EltMul(layer_2.Map(sigmoid_backward))
      layer_2_deltas = append(layer_2_deltas, layer_2_delta)
      layer_1_values = append(layer_1_values, layer_1)

      err += layer_2_error.Map(math.Abs).Reduce(add, 0)
      for j := out.M - 1; j >= 0; j-- {
         current.Data[j][i] = layer_2.Data[0][j]
      }
   }
   rnn.Tmp = current

   future_layer_1_delta := NewSimpleMatrix(1, rnn.HiddenDim)
   s0update := NewSimpleMatrix(rnn.Synapse0.M, rnn.Synapse0.N)
   s1update := NewSimpleMatrix(rnn.Synapse1.M, rnn.Synapse1.N)
   shupdate := NewSimpleMatrix(rnn.SynapseH.M, rnn.SynapseH.N)
   for i := 0; i < n; i++ {
      X := in.Col(i).T()
      layer_1 := layer_1_values[len(layer_1_values) - i - 1]
      prev_layer_1 := layer_1_values[len(layer_1_values) - i - 2]
      layer_2_delta := layer_2_deltas[len(layer_2_deltas) - i - 1]
      future_layer_1_delta = future_layer_1_delta.Dot(rnn.SynapseH.T())
      layer_2_delta = layer_2_delta.Dot(rnn.Synapse1.T())
      layer_1_delta := future_layer_1_delta.Add(layer_2_delta, 1, 1).EltMul(layer_1.Map(sigmoid_backward))
      s0update = s0update.Add(X.T().Dot(layer_1_delta), 1, 1)
      s1update = s1update.Add(layer_1.T().Dot(layer_2_delta), 1, 1)
      shupdate = shupdate.Add(prev_layer_1.T().Dot(layer_1_delta), 1, 1)
   }
   rnn.Synapse0 = rnn.Synapse0.Add(s0update, 1, rnn.Alpha)
   rnn.Synapse1 = rnn.Synapse1.Add(s1update, 1, rnn.Alpha)
   rnn.SynapseH = rnn.SynapseH.Add(shupdate, 1, rnn.Alpha)
   return err
}

func (rnn *RecurrentNerualNetwork) Predict (in *SimpleMatrix) *SimpleMatrix {
   n   := in.N
   layer_1_values := make([]*SimpleMatrix, 0)
   layer_1_values = append(layer_1_values, NewSimpleMatrix(1, rnn.HiddenDim))
   current := NewSimpleMatrix(1, in.N)
   for i := 0; i < n; i++ {
      X := in.Col(in.N - i - 1).T()
      layer_1 := X.Dot(rnn.Synapse0).Add(layer_1_values[len(layer_1_values) - 1].Dot(rnn.SynapseH), 1, 1).Map(sigmoid)
      layer_1_values = append(layer_1_values, layer_1)
      layer_2 := layer_1.Dot(rnn.Synapse1).Map(sigmoid)
      current.Data[0][i] = layer_2.Data[0][0]
   }
   return current

}

func (rnn *RecurrentNerualNetwork) Dump () {
   fmt.Println(rnn)
}

func prepareBits(x int) []int {
   v := make([]int, 8)
   t := x
   for i := 0; i < 8; i++ {
      v[7 - i] = t % 2
      t /= 2
   }
   return v
}

func prepareBinaryMap() map[int][]int {
   m := make(map[int][]int)
   for i := 0; i < 256; i++ {
      m[i] = prepareBits(i)
   }
   return m
}

func convertBits (bits *SimpleMatrix) []int {
   r := make([]int, 8)
   for i := 0; i < 8; i++ {
      r[i] = int(bits.Data[0][i] + 0.5)
   }
   return r
}

func decodeNum (bits []int) int {
   r := 0.0
   for i := 0; i < 8; i++ {
      r += math.Pow(2.0, float64(i)) * float64(bits[7 - i])
   }
   return int(r)
}

func main () {
   rnn := NewRecurrentNerualNetwork(0.2, 2, 16, 1)
   rnn.Synapse0.FillRandom(-1, 1)
   rnn.Synapse1.FillRandom(-1, 1)
   rnn.SynapseH.FillRandom(-1, 1)
   binary := prepareBinaryMap()
   for i := 1; i <= 50000; i++ {
      a_int := rand.Intn(128)
      b_int := rand.Intn(128)
      c_int := a_int + b_int
      a := binary[a_int]
      b := binary[b_int]
      c := binary[c_int]
      in := NewSimpleMatrix(2, 8)
      out := NewSimpleMatrix(1, 8)
      for j := 0; j < 8; j++ {
         in.Data[0][j] = float64(a[j])
         in.Data[1][j] = float64(b[j])
         out.Data[0][j] = float64(c[j])
      }
      err := rnn.Train(in, out)
      if (i % 1000 == 0) {
         fmt.Println("Error: [", err, "]")
         fmt.Println("Pred:", convertBits(rnn.Tmp.MirrorM()))
         fmt.Println("True:", c)
         fmt.Println(decodeNum(a), "+", decodeNum(b), "=", decodeNum(convertBits(rnn.Tmp.MirrorM())) )
         fmt.Println("------------")
      }
   }

   error := 0
   times := 50000
   for i := 1; i <= times; i++ {
      a_int := rand.Intn(128)
      b_int := rand.Intn(128)
      c_int := a_int + b_int
      a := binary[a_int]
      b := binary[b_int]
      in := NewSimpleMatrix(2, 8)
      for j := 0; j < 8; j++ {
         in.Data[0][j] = float64(a[j])
         in.Data[1][j] = float64(b[j])
      }
      out := rnn.Predict(in)
      if (decodeNum(convertBits(out.MirrorM())) != c_int) {
         error ++
      }
   }
   fmt.Println("Test Error:", (float64(error)/float64(times)) * 100.0, "%");
}
