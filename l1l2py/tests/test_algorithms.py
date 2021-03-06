# This code is written by Salvatore Masecchia <salvatore.masecchia@unige.it>
# and Annalisa Barla <annalisa.barla@unige.it>
# Copyright (C) 2010 SlipGURU -
# Statistical Learning and Image Processing Genoa University Research Group
# Via Dodecaneso, 35 - 16146 Genova, ITALY.
#
# This file is part of L1L2Py.
#
# L1L2Py is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# L1L2Py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with L1L2Py. If not, see <http://www.gnu.org/licenses/>.

import numpy as np
from nose.tools import assert_equals, assert_equal, assert_true
from six.moves import xrange

from l1l2py.algorithms import (
    ridge_regression, l1l2_regularization, l1_bound, l1l2_path)
from l1l2py.tests import _TEST_DATA_PATH


class TestAlgorithms(object):

    def setup(self):
        data = np.loadtxt(_TEST_DATA_PATH)
        self.X = data[:, :-1]
        self.Y = data[:, -1]

    def test_data(self):
        assert_equals((30, 40), self.X.shape)
        assert_equals((30, ), self.Y.shape)

    def test_rls(self):
        # case n >= d
        for penalty in np.linspace(0.0, 1.0, 5):
            value = ridge_regression(self.X, self.Y, penalty)
            assert_equal(value.shape, (self.X.shape[1], 1))

        expected = ridge_regression(self.X, self.Y, 0.0)
        value = ridge_regression(self.X, self.Y)
        assert_true(np.allclose(expected, value))

        # case d > n
        X = self.X.T
        Y = self.X[0:1, :].T
        for penalty in np.linspace(0.0, 1.0, 5):
            value = ridge_regression(X, Y, penalty)
            assert_equal(value.shape, (X.shape[1], 1))

        expected = ridge_regression(X, Y, 0.0)
        value = ridge_regression(X, Y)
        assert_true(np.allclose(expected, value))

    def test_l1l2_bigd(self):
        self.l1l2_regtest(self.X, self.Y)

    def test_l1l2_bign(self):
        Y = np.r_[self.Y, self.Y[:10]]
        Y = Y.reshape((-1, 1))
        self.l1l2_regtest(self.X.T, Y)

    def l1l2_regtest(self, X, Y):
        from itertools import product

        values = np.linspace(0.1, 1.0, 5)
        for mu, tau in product(values, values):
            beta, k1 = l1l2_regularization(X, Y, mu, tau,
                                           return_iterations=True)
            assert_equal(beta.shape, (X.shape[1], 1))

            beta, k2 = l1l2_regularization(X, Y, mu, tau,
                                           tolerance=1e-3,
                                           return_iterations=True)
            assert_true(k2 <= k1)

            beta, k3 = l1l2_regularization(X, Y, mu, tau,
                                           tolerance=1e-3, kmax=10,
                                           return_iterations=True)
            assert_true(k3 <= k2)
            assert_true(k3 == 10)

            beta1, k1 = l1l2_regularization(X, Y, mu, tau,
                                            return_iterations=True)
            beta2, k2 = l1l2_regularization(X, Y, mu, tau,
                                            beta=beta1.squeeze(),
                                            return_iterations=True)
            assert_true(k2 <= k1)

            beta1, k1 = l1l2_regularization(X, Y, mu, tau,
                                            return_iterations=True)
            beta2, k2 = l1l2_regularization(X, Y.squeeze(), mu, tau,
                                            return_iterations=True)
            assert_equal(k1, k2)
            assert_true(beta1.shape, beta2.shape)
            assert_true(np.allclose(beta1, beta2))

    def test_l1l2_path(self):
        values = np.linspace(0.1, 1.0, 5)
        beta_path = l1l2_path(self.X, self.Y, 0.1, values)

        assert_true(len(beta_path) <= len(values))
        for i in xrange(1, len(beta_path)):

            b = beta_path[i]
            b_prev = beta_path[i-1]

            selected_prev = len(b_prev[b_prev != 0.0])
            selected = len(b[b != 0.0])
            assert_true(selected <= selected_prev)

    def test_l1l2_path_saturation(self):
        values = [0.1, 1e1, 1e3, 1e4]
        beta_path = l1l2_path(self.X, self.Y, 0.1, values)
        assert_equals(len(beta_path), 2)

        for i in xrange(2):
            b = beta_path[i]
            selected = len(b[b != 0.0])

            assert_true(selected <= len(b))

    def test_l1_bound(self):
        tau_max = l1_bound(self.X, self.Y)

        beta = l1l2_regularization(self.X, self.Y, 0.0, tau_max, adaptive=True)
        assert_equals(0, len(beta.nonzero()[0]))

        beta = l1l2_regularization(self.X, self.Y, 0.0, tau_max - 1e-3)
        assert_equals(1, len(beta.nonzero()[0]))
