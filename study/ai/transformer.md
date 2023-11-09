```
transformer
= -> [embedding, position_encoding] -> multi-head_attention -> (norm1) -> feedforward -> (norm2) ->

scaled_dot-product_attention
= Q K V -> softmax(Q.K(T) / sqrt(d(k)) + MASK).V

multi-head_attention
= -> scaled_dot-product_attention ->
= -> Q = X.Wq, K = X.Wk, V = X.Wv
  split(N/n -> e.g. 64/8 => 8 8 8 8 8 8 8 8)
  concat( ...scaled_dot-product_attention(Q[i], K[i], V[i]) ).Wo ->

norm(.)
= mean(.), std(.), (x - mean) / (std + epsilon) ->

(norm1)
= norm(X + multi-head_attention)

feedforward
= ReLu(X.W1 + b1).W2 + b2

(norm2)
= norm(norm1 + feedforward(norm1))

```
