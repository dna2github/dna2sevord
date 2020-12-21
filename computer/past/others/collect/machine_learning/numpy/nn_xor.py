import numpy as np

def sigmoid(x): return 1/(1+np.exp(-x))

def sigmoidD(s): return s*(1-s)

def xround(x):
   if x > 0.5: return 1
   else: return 0

def xor_trainer(m, x, y, rate):
   L0 = x
   L1 = sigmoid(np.dot(L0, m.S0))
   L2 = sigmoid(np.dot(L1, m.S1))
   e2 = y - L2
   dL2 = e2*sigmoidD(L2)
   e1 = np.dot(dL2, m.S1.T)
   dL1 = e1*sigmoidD(L1)
   m.S1 += np.dot(L1.T, dL2)*rate
   m.S0 += np.dot(L0.T, dL1)*rate

def xor_predict(m, x):
   L0 = x
   L1 = sigmoid(np.dot(L0, m.S0))
   L2 = sigmoid(np.dot(L1, m.S1))
   return L2

class M(object):
   def __init__(self):
      self.S0 = np.random.normal(size=(2, 12), scale=0.5)
      self.S1 = np.random.normal(size=(12, 1), scale=0.5)

def main():
   m = M()
   data = [ [0, 0, 0], [0, 1, 1], [1, 0, 1], [1, 1, 0] ]
   for i in range(20000):
      X = np.array([data[i % 4][0:2]])
      y = np.array([data[i % 4][2:3]])
      xor_trainer(m, X, y, 0.1)

   error = 0
   for i in range(20000):
      X = np.array([data[i % 4][0:2]])
      y = np.array([data[i % 4][2:3]])
      if xround(xor_predict(m, X)[0][0]) != xround(y[0][0]):
         error += 1
   print "text error:", error / 20000.0 * 100.0

if __name__ == "__main__":
   main()
