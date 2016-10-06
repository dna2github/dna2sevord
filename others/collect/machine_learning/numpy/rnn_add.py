import numpy as np
import random

POS_L1 = 0
POS_L2 = 1
POS_dL1 = 2

def sigmoid(x): return 1/(1+np.exp(-x))

def sigmoidD(s): return s*(1-s)

def xround(x):
   if x > 0.5: return 1
   else: return 0

def decode(x):
   out = 0
   for index, v in enumerate(reversed(map(xround, x[0]))):
      out += v * pow(2, index)
   return out

def add_trainer(m, x1, x2, y, rate):
   predict = add_predict(m, x1, x2)
   dS0 = np.zeros_like(m.S0)
   dSH = np.zeros_like(m.SH)
   dS1 = np.zeros_like(m.S1)
   for i in range(7, -1, -1):
      m.switch(i)
      L0 = np.array([ [x1[0][7-i], x2[0][7-i] ] ])
      L1 = m.context[i][POS_L1]
      L1_prev = m.prev()[POS_L1]
      L2 = m.context[i][POS_L2]
      e2 = np.array([[ y[0][7-i] - predict[0][7-i] ]])
      dL2 = e2*sigmoidD(L2)
      e1 = np.dot(dL2, m.S1.T)
      dL1 = (e1 + np.dot(m.next()[POS_dL1], m.SH.T))*sigmoidD(L1)
      m.context[i][POS_dL1] = dL1
      dS1 += np.dot(L1.T, dL2)
      dSH += np.dot(L1_prev.T, dL1)
      dS0 += np.dot(L0.T, dL1)

   m.S1 += dS1 * rate
   m.SH += dSH * rate
   m.S0 += dS0 * rate

def add_predict(m, x1, x2):
   out = np.zeros(shape=(1, 8))
   for i in range(8):
      m.switch(i)
      L0 = np.array([ [x1[0][7-i], x2[0][7-i] ] ])
      L1 = sigmoid(np.dot(L0, m.S0) + np.dot(m.prev()[POS_L1], m.SH))
      L2 = sigmoid(np.dot(L1, m.S1))
      out[0][7-i] = L2[0][0]
      m.context[i] = [L1, L2, None]
   return out

class M(object):
   def __init__(self):
      self.cursor = 0
      self.context = [None] * 8
      self.h = 12
      self.S0 = np.random.normal(size=(2, self.h), scale=0.5)
      self.SH = np.random.normal(size=(self.h, self.h), scale=0.5)
      self.S1 = np.random.normal(size=(self.h, 1), scale=0.5)

   def switch(self, i):
      self.cursor = i

   def next(self):
      # return (L1, L2, dL1)
      if self.cursor >= len(self.context) - 1:
         return [np.zeros(shape=(1, self.h)), np.zeros(shape=(1, 1)), np.zeros(shape=(1, self.h))]
      return self.context[self.cursor+1]

   def prev(self):
      # return (L1, L2, dL1)
      if self.cursor <= 0:
         return [np.zeros(shape=(1, self.h)), np.zeros(shape=(1, 1)), np.zeros(shape=(1, self.h))]
      return self.context[self.cursor-1]

def main():
   binary = np.array(np.unpackbits(np.array([range(256)],dtype=np.uint8).T,axis=1), dtype=np.double)
   m = M()
   for i in range(20000):
      a1 = np.random.randint(128)
      a2 = np.random.randint(128)
      x1 = np.atleast_2d(binary[a1])
      x2 = np.atleast_2d(binary[a2])
      y =  np.atleast_2d(binary[a1 + a2])
      add_trainer(m, x1, x2, y, 0.1)

   error = 0
   for i in range(10000):
      a1 = np.random.randint(128)
      a2 = np.random.randint(128)
      x1 = np.atleast_2d(binary[a1])
      x2 = np.atleast_2d(binary[a2])
      y =  np.atleast_2d(binary[a1 + a2])
      p = add_predict(m, x1, x2)
      if decode(p) != decode(y):
         error += 1
   print "test error:", error / 20000.0 * 100.0

if __name__ == "__main__":
   main()

