
### autoencoder

```
class AnomalyDetector(tf.keras.Model):
  def __init__(self):
    super(AnomalyDetector, self).__init__()
    self.encoder = tf.keras.Sequential([
      tf.keras.layers.Dense(32, activation="relu"),
      tf.keras.layers.Dense(16, activation="relu"),
      tf.keras.layers.Dense(16, activation="relu")])

    self.decoder = tf.keras.Sequential([
      tf.keras.layers.Dense(16, activation="relu"),
      tf.keras.layers.Dense(32, activation="relu"),
      tf.keras.layers.Dense(42, activation="sigmoid")])

  def call(self, x):
    encoded = self.encoder(x)
    decoded = self.decoder(encoded)
    return decoded

def buildModel():
   autoencoder = AnomalyDetector()
   autoencoder.compile(optimizer='adam', loss='mae')

   model = tf.keras.Sequential([
      autoencoder.encoder,
      tf.keras.layers.Dense(16, activation="relu"),
      tf.keras.layers.Dropout(0.2),
      tf.keras.layers.Dense(23, activation="softmax"),
   ])
   model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
   return model, autoencoder
```
