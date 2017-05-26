from __future__ import print_function

import numpy as np
import matplotlib.pyplot as plt
from past.builtins import xrange

class TwoLayerNet(object):
  """
  A two-layer fully-connected neural network. The net has an input dimension of
  N, a hidden layer dimension of H, and performs classification over C classes.
  We train the network with a softmax loss function and L2 regularization on the
  weight matrices. The network uses a ReLU nonlinearity after the first fully
  connected layer.

  In other words, the network has the following architecture:

  input - fully connected layer - ReLU - fully connected layer - softmax

  The outputs of the second fully-connected layer are the scores for each class.
  """

  def __init__(self, input_size, hidden_size, output_size, std=1e-4):
    """
    Initialize the model. Weights are initialized to small random values and
    biases are initialized to zero. Weights and biases are stored in the
    variable self.params, which is a dictionary with the following keys:

    W1: First layer weights; has shape (D, H)
    b1: First layer biases; has shape (H,)
    W2: Second layer weights; has shape (H, C)
    b2: Second layer biases; has shape (C,)

    Inputs:
    - input_size: The dimension D of the input data.
    - hidden_size: The number of neurons H in the hidden layer.
    - output_size: The number of classes C.
    """
    self.params = {}
    self.params['W1'] = std * np.random.randn(input_size, hidden_size)
    self.params['b1'] = np.zeros(hidden_size)
    self.params['W2'] = std * np.random.randn(hidden_size, output_size)
    self.params['b2'] = np.zeros(output_size)

  def loss(self, X, y=None, reg=0.0):
    """
    Compute the loss and gradients for a two layer fully connected neural
    network.

    Inputs:
    - X: Input data of shape (N, D). Each X[i] is a training sample.
    - y: Vector of training labels. y[i] is the label for X[i], and each y[i] is
      an integer in the range 0 <= y[i] < C. This parameter is optional; if it
      is not passed then we only return scores, and if it is passed then we
      instead return the loss and gradients.
    - reg: Regularization strength.

    Returns:
    If y is None, return a matrix scores of shape (N, C) where scores[i, c] is
    the score for class c on input X[i].

    If y is not None, instead return a tuple of:
    - loss: Loss (data loss and regularization loss) for this batch of training
      samples.
    - grads: Dictionary mapping parameter names to gradients of those parameters
      with respect to the loss function; has the same keys as self.params.
    """
    # Unpack variables from the params dictionary
    W1, b1 = self.params['W1'], self.params['b1']
    W2, b2 = self.params['W2'], self.params['b2']
    N, D = X.shape

    # Compute the forward pass

    #############################################################################
    # TODO: Perform the forward pass, computing the class scores for the input. #
    # Store the result in the scores variable, which should be an array of      #
    # shape (N, C).                                                             #
    #############################################################################

    h1 = np.maximum(0, X.dot(W1) + b1) # f(X, W1, b1). should be of shape (N,H) = (N,D) * (D,H) so: X.dot(W1) + b1. use ReLU, take the max

    scores = h1.dot(W2) + b2 #f(h1, W2, B2). should be of shape (N,C) = (N,H) * (H,C) = h1 * W2

    # If the targets are not given then jump out, we're done
    # we're just using the weights and input data to calculate the loss

    if y is None:
      return scores

    # Compute the loss

    #compute class probabilities
    exp_scores = np.exp(scores) # cleanly takes care of the e^ step in softmax formula
    probabilities = exp_scores / np.sum(exp_scores, axis=1, keepdims=True) # N x K, gives a score for each class for each observation

    #compute avg cross-entropy loss (data loss)& regularization
    neg_logprobs = -np.log(probabilities[range(N),y]) # gets log probabilities of all the correct classes by pulling probs in rows 0-N & column y for each row (column of correct class)
    data_loss = np.sum(neg_logprobs) / N # average negative log probability of each correct class, to minimize

    reg_loss = 0.5 * reg * np.sum(W1 ** 2) + .5 * reg * np.sum(W2 ** 2) # dividing the reg loss between the weight sets
    loss = data_loss + reg_loss

    # Softmax: L_i = -log(e^score of correct class / sum of all scores)
    # we want to minimize the loss, i.e. minimize the negative log likelihood of the correct class
    # include L2 regularization


    #############################################################################
    # TODO: Finish the forward pass, and compute the loss. This should include  #
    # both the data loss and L2 regularization for W1 and W2. Store the result  #
    # in the variable loss, which should be a scalar. Use the Softmax           #
    # classifier loss.                                                          #
    #############################################################################

    # Backward pass: compute gradients
    grads = {}

    # df/df = 1
    # dW2/df = derivative of Softmax w.r.t. W2 . do this numerically or analytically

    # compute the gradient on scores

    dscores = probs
    dscores[range(N),y]  -= 1
    dscores /= N # subtracting 1 from each correct score, and taking the average. increasing scores increases loss by a little bit, except if the score is of the correct class (so subtract 1 --> it'll get zeroed out?)

    # gradient on W2 and b2

    grads['W2'] = np.dot(h1.T, dscores) # partial derivative (gradient) w.r.t. W2 (dW2/dscores), i.e. how does a change in W2 affect scores. should have same shape as W2, i.e. (H,C)
    # h1 = (N,H), b1 = (H,), W2 = (H,C) --> (N,C)
    # dh1 / df * df / df = dh1 / df
    # so dh1/dscores * dscores/dscores = dh1/dscores
    # h1.T = (H,N), dscores = (N,C)
    # --> h1.T * dscores = (H,C)
    # do the transpose bc you're doing the operation backwards from forward propagation, solving for a W2-shaped matrix to multiply h1 by to get a shift in scores

    grads['b2'] = np.sum(dscores, axis=0) # partial derivative w.r.t. bias term, db2/dscores. sums columns of dscores, multiplied by a column vector (many rows) of constants (b2)

    # backprop into hidden layer, get partial derivative: dhidden / dscores
    # dhidden = (N,H). W2 = (H,C), dscores = (N,C)
    # --> do dscores * W2.T
    dhidden = np.dot(dscores,W2.T)

    # backprop the ReLU non-linearity by zeroing dhidden elements at indices where h1 <= 0
    dhidden[h1 <= 0] = 0

    # now, backprop into W1,b1

    # W1 = (D,H) <-- not going to use this
    # X = (N,D)
    # dhidden = (N,H)
    # dW1 / dhidden = X.T * dhidden

    grads['W1'] = np.dot(X.T, dhidden)

    # db1/dhidden = impact of each value in b1 magnified by sum of corresponding row
    grads['b1'] = np.sum(dhidden,axis=0)

    # add regularization gradient contrib
    grads['W2'] += reg *  W2
    grads['W1'] += reg * W1


    #############################################################################
    # TODO: Compute the backward pass, computing the derivatives of the weights #
    # and biases. Store the results in the grads dictionary. For example,       #
    # grads['W1'] should store the gradient on W1, and be a matrix of same size #
    #############################################################################


    return loss, grads

  def train(self, X, y, X_val, y_val,
            learning_rate=1e-3, learning_rate_decay=0.95,
            reg=5e-6, num_iters=100,
            batch_size=200, verbose=False):
    """
    Train this neural network using stochastic gradient descent.

    Inputs:
    - X: A numpy array of shape (N, D) giving training data.
    - y: A numpy array f shape (N,) giving training labels; y[i] = c means that
      X[i] has label c, where 0 <= c < C.
    - X_val: A numpy array of shape (N_val, D) giving validation data.
    - y_val: A numpy array of shape (N_val,) giving validation labels.
    - learning_rate: Scalar giving learning rate for optimization.
    - learning_rate_decay: Scalar giving factor used to decay the learning rate
      after each epoch.
    - reg: Scalar giving regularization strength.
    - num_iters: Number of steps to take when optimizing.
    - batch_size: Number of training examples to use per step.
    - verbose: boolean; if true print progress during optimization.
    """
    num_train = X.shape[0]
    iterations_per_epoch = max(num_train / batch_size, 1)

    # Use SGD to optimize the parameters in self.model
    loss_history = []
    train_acc_history = []
    val_acc_history = []

    for it in xrange(num_iters):
      X_batch = None
      y_batch = None

      #########################################################################
      # TODO: Create a random minibatch of training data and labels, storing  #
      # them in X_batch and y_batch respectively.                             #
      #########################################################################
      sample_indices = np.random.choice(np.arange(num_train),batch_size)
      X_batch = X[sample_indices]
      y_batch = y[sample_indices]

      #########################################################################
      #                             END OF YOUR CODE                          #
      #########################################################################

      # Compute loss and gradients using the current minibatch
      loss, grads = self.loss(X_batch, y=y_batch, reg=reg)
      loss_history.append(loss)

      #########################################################################
      # TODO: Use the gradients in the grads dictionary to update the         #
      # parameters of the network (stored in the dictionary self.params)      #
      # using stochastic gradient descent. You'll need to use the gradients   #
      # stored in the grads dictionary defined above.                         #
      #########################################################################
      self.params['W1'] += -learning_rate * grads['W1']
      self.params['b1'] += -learning_rate * grads['b1']
      self.params['W2'] += -learning_rate * grads['W2']
      self.params['b2'] += -learning_rate * grads['b2']

      #########################################################################
      #                             END OF YOUR CODE                          #
      #########################################################################

      if verbose and it % 100 == 0:
        print('iteration %d / %d: loss %f' % (it, num_iters, loss))

      # Every epoch, check train and val accuracy and decay learning rate.
      if it % iterations_per_epoch == 0:
        # Check accuracy
        train_acc = (self.predict(X_batch) == y_batch).mean()
        val_acc = (self.predict(X_val) == y_val).mean()
        train_acc_history.append(train_acc)
        val_acc_history.append(val_acc)

        # Decay learning rate
        learning_rate *= learning_rate_decay

    return {
      'loss_history': loss_history,
      'train_acc_history': train_acc_history,
      'val_acc_history': val_acc_history,
    }

  def predict(self, X):
    """
    Use the trained weights of this two-layer network to predict labels for
    data points. For each data point we predict scores for each of the C
    classes, and assign each data point to the class with the highest score.

    Inputs:
    - X: A numpy array of shape (N, D) giving N D-dimensional data points to
      classify.

    Returns:
    - y_pred: A numpy array of shape (N,) giving predicted labels for each of
      the elements of X. For all i, y_pred[i] = c means that X[i] is predicted
      to have class c, where 0 <= c < C.
    """
    y_pred = None

    h1 = np.maximum(X.dot(self.params['X1']) + self.params['b1'],0) # hidden layer passed through ReLU
    scores = h1.dot(self.params['W2']) + self.params['b2']
    y_pred = np.argmax(scores,axis=1) # returns the index with the highest score for each test row

    return y_pred
