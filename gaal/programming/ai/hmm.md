# POS-TAGGING with Hidden Markov Model

Install NLTK package by `pip install nltk`.

```python
raw = [('data', 'tag'), ]
data = [raw]
symbols = list(set([one[0] for one in raw]) + set([one[1] for one in raw]))
states = range(100)
trainer = nltk.tag.hmm.HiddenMarkovModelTrainer(states=states,symbols=symbols)
model = trainer.train_unsupervised(data)
model.tag(['data'])
```
