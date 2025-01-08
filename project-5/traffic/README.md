1. Initially started with same layers as given in handwriting.py sample code
* small dataset: 11/11 - 0s - 8ms/step - accuracy: 0.8304 - loss: 0.3653
* large dataset: 333/333 - 1s - 2ms/step - accuracy: 0.0566 - loss: 3.5051

2. Removed Dropout layer.  This improved accuracy.  Traffic signs are designed to be easily distinguished from one another so low risk of overfitting?
* small dataset: 11/11 - 0s - 9ms/step - accuracy: 0.9970 - loss: 0.0089
* large dataset: 333/333 - 1s - 3ms/step - accuracy: 0.9237 - loss: 0.6994

3. Reduce dropout to 0.25 - Improved small dataset but large dataset is worse
* small dataset: 11/11 - 0s - 9ms/step - accuracy: 1.0000 - loss: 0.0000e+00
* large dataset: 333/333 - 1s - 3ms/step - accuracy: 0.7331 - loss: 0.9789

Adding more convolution layers didn't improve accuracy.  Because images are simple with few features?

Doubling neurons in hidden layer didn't offer significant improvement but slows model
Halving neurons in hidden layer resulted in significant deterioration in accuracy but faster training as expected