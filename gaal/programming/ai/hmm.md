# POS-TAGGING with Hidden Markov Model

Install NLTK package by `pip install nltk`.

```python
raw = [('word1', 0), ('word2', 1), ('word3', 2) ]
data = [raw]
symbols = list(set([one[0] for one in raw]))
states = range(3)
trainer = nltk.tag.hmm.HiddenMarkovModelTrainer(states=states,symbols=symbols)
model = trainer.train_unsupervised(data)
model.tag(['data'])
```
