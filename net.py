#!/usr/bin/env python
'''
from https://github.com/pfnet/chainer/blob/master/examples/vae/net.py
'''

import six

import chainer
import chainer.functions as F
from chainer.functions.loss.vae import gaussian_kl_divergence
import chainer.links as L


class VAE(chainer.Chain):
    """Variational AutoEncoder"""

    def __init__(self, n_in, n_latent, n_h, C=15.0, k=1):
        """
        Args:
            args below are for loss function
            C (int): Usually this is 1.0. Can be changed to control the
                second term of ELBO bound, which works as regularization.
            k (int): Number of Monte Carlo samples used in encoded vector.
            train (bool): If true loss_function is used for training.
        """

        super(VAE, self).__init__(
            # encoder
            le1=L.Linear(n_in, n_h),
            le2_mu=L.Linear(n_h, n_latent),
            le2_ln_var=L.Linear(n_h, n_latent),
            # decoder
            ld1=L.Linear(n_latent, n_h),
            ld2=L.Linear(n_h, n_in),
        )
        self.C = C
        self.k = k

    def __call__(self, x, sigmoid=True):
        """AutoEncoder"""
        mu, ln_var = self.encode(x)
        batchsize = len(mu.data)
        # reconstruction loss
        rec_loss = 0
        for l in six.moves.range(self.k):
            z = F.gaussian(mu, ln_var)
            rec_loss += F.bernoulli_nll(x, self.decode(z, sigmoid=False)) \
                / (self.k * batchsize)
	#print('1  c: {}'.format(self.C))
	loss = rec_loss + \
            self.C * gaussian_kl_divergence(mu, ln_var) / batchsize
        chainer.report({'loss': loss}, self)
        return loss

    def encode(self, x):
        h1 = F.tanh(self.le1(x))
        mu = self.le2_mu(h1)
        ln_var = self.le2_ln_var(h1)  # log(sigma**2)
        return mu, ln_var

    def decode(self, z, sigmoid=True):
        h1 = F.tanh(self.ld1(z))
        h2 = self.ld2(h1)
        if sigmoid:
            return F.sigmoid(h2)
        else:
            return h2

    def get_loss_func(self, C=1.0, k=1, train=True):
        """Get loss function of VAE.
        The loss value is equal to ELBO (Evidence Lower Bound)
        multiplied by -1.
        Args:
            C (int): Usually this is 1.0. Can be changed to control the
                second term of ELBO bound, which works as regularization.
            k (int): Number of Monte Carlo samples used in encoded vector.
            train (bool): If true loss_function is used for training.
        """
    def lf(self, x):
        mu, ln_var = self.encode(x)
        batchsize = len(mu.data)
        # reconstruction loss
        rec_loss = 0
        for l in six.moves.range(self.k):
            z = F.gaussian(mu, ln_var)
            rec_loss += F.bernoulli_nll(x, self.decode(z, sigmoid=False)) \
                / (self.k * batchsize)
        self.rec_loss = rec_loss
        print('2  c: {}'.format(self.C))
	self.loss = self.rec_loss + \
            self.C * gaussian_kl_divergence(mu, ln_var) / batchsize
        return self.loss
