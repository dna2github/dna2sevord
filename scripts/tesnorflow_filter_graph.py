g = [n for n in tf.get_default_graph().as_graph_def().node]
m = {}
for n in g:
   if n.name not in m: m[n.name] = [n, 0]
   for x in n.input:
      if x not in m: m[x] = [n, 0]
      m[x][1] += 1
for n in g:
   print(str(m[n.name]), '\t', str(n.op), '\t', str(n.name), '\t', str(n.input))
for k, v in m.iteritems():
   if v[1] > 0: continue
   op = v[0].op
   if op in [
       'Const', 'Identity', 'NoOp', 'ExpandDims',
       'Assign', 'Shape', 'Reshape',
       'ApplyGradientDescent', 'ZerosLike'
   ]:
       continue
   print(op, k, v[0].input, v)
