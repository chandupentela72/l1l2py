r"""Miscellaneous useful tools.

The :mod:`tools` module contains four type of functions:

* Range generators
    - :func:`linear_range`
    - :func:`geometric_range`
* Data Normalization
    - :func:`center`
    - :func:`standardize`
* Error calculation
    - :func:`classification_error`
    - :func:`balanced_classification_error`
    - :func:`regression_error`
* Cross Validation utilities
    - :func:`kfold_splits`
    - :func:`stratified_kfold_splits`

"""

__all__ = ['linear_range', 'geometric_range', 'standardize', 'center',
           'classification_error', 'balanced_classification_error',
           'regression_error', 'kfold_splits', 'stratified_kfold_splits']

import math
import random
import numpy as np

# Ranges functions ------------------------------------------------------------
def linear_range(min_value, max_value, number):
    r"""Returns a linear range of values.

    Returns a sequence of ``number`` evenly spaced values from ``min_value``
    to ``max_value``.

    Parameters
    ----------
    min_value : float
    max_value : float
    number : int

    Returns
    -------
    range : ndarray

    Examples
    --------    
    >>> l1l2py.tools.linear_range(0.0, 10.0, 4)
    array([  0.        ,   3.33333333,   6.66666667,  10.        ])
    >>> l1l2py.tools.linear_range(0.0, 10.0, 2)
    array([  0.,  10.])
    >>> l1l2py.tools.linear_range(0.0, 10.0, 1)
    array([ 0.])
    >>> l1l2py.tools.linear_range(0.0, 10.0, 0)
    array([], dtype=float64)

    """
    return np.linspace(min_value, max_value, number)

def geometric_range(min_value, max_value, number):
    r"""Returns a geometric range of values.

    Returns ``number`` values from ``min_value``
    to ``max_value`` generated by a geometric sequence.

    Parameters
    ----------
    min_value : float
    max_value : float
    number : int

    Returns
    -------
    range : ndarray

    Raises
    ------
    ZeroDivisionError
        If ``min_value`` is ``0.0`` or ``number`` is ``1``

    Examples
    --------
    >>> l1l2py.tools.geometric_range(0.0, 10.0, 4)
    Traceback (most recent call last):
        ...
    ZeroDivisionError: float division
    >>> l1l2py.tools.geometric_range(0.1, 10.0, 4)
    array([ 0.1       ,  0.46415888,  2.15443469, 10.        ])
    >>> l1l2py.tools.geometric_range(0.1, 10.0, 2)
    array([  0.1,  10. ])
    >>> l1l2py.tools.geometric_range(0.1, 10.0, 1)
    Traceback (most recent call last):
        ...
    ZeroDivisionError: float division
    >>> l1l2py.tools.geometric_range(0.1, 10.0, 0)
    array([], dtype=float64)

    """
    ratio = (max_value/float(min_value))**(1.0/(number-1))
    return min_value * (ratio ** np.arange(number))

# Normalization ---------------------------------------------------------------
def standardize(matrix, optional_matrix=None, return_factors=False):
    r"""Standardize columns of a matrix.

    Returns the standardized ``matrix`` given as input.
    Optionally standardizes an ``optional_matrix`` with respect to
    mean and standard deviation calculated for ``matrix``.

    Parameters
    ----------
    matrix : (N,) or (N, D) ndarray
        Input matrix whose columns are to be standardized
        to mean `0` and standard deviation `1`.
    optional_matrix : (N,) or (N, D) ndarray, optional (default is `None`)
        Optional matrix whose columns are to be standardized
        using mean and standard deviation of ``matrix``.
        It must have same number of columns as ``matrix``.
    return_factors : bool, optional (default is `False`)
        If `True`, returns mean and standard deviation of ``matrix``.

    Returns
    -------
    matrix_standardized : (N,) or (N, D) ndarray
        Standardized ``matrix``.
    optional_matrix_standardized : (N,) or (N, D) ndarray, optional
        Standardized ``optional_matrix`` with respect to ``matrix``
    mean : float or (D,) ndarray, optional
        Mean of ``matrix`` columns.
    std : float or (D,) ndarray, optional
        Standard deviation of ``matrix`` columns.

    Examples
    --------
    >>> X = numpy.array([[1, 2, 3], [4, 5, 6]])
    >>> l1l2py.tools.standardize(X)
    array([[-0.70710678, -0.70710678, -0.70710678],
           [ 0.70710678,  0.70710678,  0.70710678]])
    >>> l1l2py.tools.standardize(X, return_factors=True)
    (array([[-0.70710678, -0.70710678, -0.70710678],
           [ 0.70710678,  0.70710678,  0.70710678]]), array([ 2.5,  3.5,  4.5]), array([ 2.12132034,  2.12132034,  2.12132034]))
    >>> x = numpy.array([1, 2, 3])
    >>> l1l2py.tools.standardize(x)
    array([-1.,  0.,  1.])

    """
    mean = matrix.mean(axis=0)
    std = matrix.std(axis=0, ddof=1)

    # Simple case
    if optional_matrix is None and return_factors is False:
        return (matrix - mean)/std

    if optional_matrix is None: # than return_factors is True
        return (matrix - mean)/std, mean, std

    if return_factors is False: # ... with p not None
        return (matrix - mean)/std, (optional_matrix - mean)/std

    # Full case
    return (matrix - mean)/std, (optional_matrix - mean)/std, mean, std

def center(matrix, optional_matrix=None, return_mean=False):
    r"""Center columns of a matrix.

    Returns the centered ``matrix`` given as input.
    Optionally centers an ``optional_matrix`` with respect to mean calculated
    for ``matrix``.

    Parameters
    ----------
    matrix : (N,) or (N, D) ndarray
        Input matrix whose columns are to be centered.
    optional_matrix : (N,) or (N, D) ndarray, optional (default is `None`)
        Optional matrix whose columns are to be centered
        using mean of ``matrix``.
        It must have same number of columns as ``matrix``.
    return_mean : bool, optional (default is `False`)
        If `True` returns mean of ``matrix``.

    Returns
    -------
    matrix_centered : (N,) or (N, D) ndarray
        Centered ``matrix``.
    optional_matrix_centered : (N,) or (N, D) ndarray, optional
        Centered ``optional_matrix`` with respect to ``matrix``
    mean : float or (D,) ndarray, optional
        Mean of ``matrix`` columns.

    Examples
    --------
    >>> X = numpy.array([[1, 2, 3], [4, 5, 6]])
    >>> l1l2py.tools.center(X)
    array([[-1.5, -1.5, -1.5],
           [ 1.5,  1.5,  1.5]])
    >>> l1l2py.tools.center(X, return_mean=True)
    (array([[-1.5, -1.5, -1.5],
           [ 1.5,  1.5,  1.5]]), array([ 2.5,  3.5,  4.5]))
    >>> x = numpy.array([1, 2, 3])
    >>> l1l2py.tools.center(x)
    array([-1.,  0.,  1.])

    """
    mean = matrix.mean(axis=0)

    # Simple case
    if optional_matrix is None and return_mean is False:
        return matrix - mean

    if optional_matrix is None: # than return_mean is True
        return (matrix - mean, mean)

    if return_mean is False: # ...with p not None
        return (matrix - mean, optional_matrix - mean)

    # Full case
    return (matrix - mean, optional_matrix - mean, mean)

# Error functions -------------------------------------------------------------
def classification_error(labels, predicted):
    r"""Returns classification error.

    The classification error is based on the sign of the ``predicted`` values,
    with respect to the sign of the data ``labels``.

    The function assumes that ``labels`` contain positive number for first
    class and negative numbers for the second one (see `Notes`).

    .. warning::

        The values contained in ``labels`` are not checked by the function for
        efficiency.

    Parameters
    ----------
    labels : array_like, shape (N,)
        Classification labels (usually contains only 1s and -1s).
    predicted : array_like, shape (N,)
        Classification labels predicted.

    Returns
    -------
    error : float
        Classification error calculated.
   
    Examples
    --------    
    >>> l1l2py.tools.classification_error([1, 1, 1], [1, 1, 1])
    0.0
    >>> l1l2py.tools.classification_error([1, 1, 1], [1, 1, -1])
    0.33333333333333331
    >>> l1l2py.tools.classification_error([1, 1, 1], [1, -1, -1])
    0.66666666666666663
    >>> l1l2py.tools.classification_error([1, 1, 1], [-1, -1, -1])
    1.0
    >>> l1l2py.tools.classification_error([1, 1, 1], [10, -2, -3])
    0.66666666666666663

    """
    difference = (np.sign(labels) != np.sign(predicted))
    return difference[difference].size / float(len(labels))

def balanced_classification_error(labels, predicted):
    r"""Returns classification error balanced across the size of classes.

    Using similar algorithm as in :func:`classification_error`,
    this function returns a biased classification error,
    assigning greater weight to the errors belonging to the smaller class.

    Parameters
    ----------
    labels : array_like, shape (N,)
        Classification labels (usually contains only 1s and -1s).
    predicted : array_like, shape (N,)
        Classification labels predicted.

    Returns
    -------
    error : float
        Classification error calculated.

    Examples
    --------    
    >>> l1l2py.tools.balanced_classification_error([1, 1, 1], [-1, -1, -1])
    0.0
    >>> l1l2py.tools.balanced_classification_error([-1, 1, 1], [-1, 1, 1])
    0.0
    >>> l1l2py.tools.balanced_classification_error([-1, 1, 1], [1, -1, -1])
    0.88888888888888895
    >>> l1l2py.tools.balanced_classification_error([-1, 1, 1], [1, 1, 1])
    0.44444444444444442
    >>> l1l2py.tools.balanced_classification_error([-1, 1, 1], [-1, 1, -1])
    0.22222222222222224

    """
    balance_factors = np.abs(center(np.asarray(labels)))

    errors = (np.sign(labels) != np.sign(predicted)) * balance_factors
    return errors.sum() / float(len(labels))

def regression_error(labels, predicted):
    r"""Returns regression error.

    The regression error is the sum of the quadratic difference between the
    ``labels`` value and the ``predicted`` values, over the number of
    samples (see `Notes`).

    Parameters
    ----------
    labels : array_like, shape (N,)
        Regression labels.
    predicted : array_like, shape (N,)
        Regression labels predicted.

    Returns
    -------
    error : float
        Regression error calculated.

    """
    difference = np.asarray(labels) - np.asarray(predicted)
    return np.dot(difference.T, difference) / float(len(labels))

# KCV tools -------------------------------------------------------------------
def kfold_splits(labels, k, rseed=0):
    r"""Returns k-fold cross validation splits.

    Given the list of labels, the function produces a list of ``k`` splits.
    Each split is a pair of tuples containing the indexes of the training set
    and the indexes of the testing set.

    Parameters
    
    labels : array_like, shape (N,)
        Data labels (for this function is important only its length).
    k : int, greater than `0`
        Number of splits.
    rseed : int, optional (default is `0`)
        Random seed.

    Returns
    
    splits : list of ``k`` tuples
        Each tuple contains two lists with the training set and testing set
        indexes.

    Raises
    
    ValueError
        If ``k`` is negative or greater than number of `labels`.

    See Also
    
    stratified_kfold_splits

    Examples
    
    >>> labels = range(10)
    >>> l1l2py.tools.kfold_splits(labels, 2)
    [([7, 1, 3, 6, 8], [9, 4, 0, 5, 2]), ([9, 4, 0, 5, 2], [7, 1, 3, 6, 8])]
    >>> l1l2py.tools.kfold_splits(labels, 1)
    [([], [9, 4, 0, 5, 2, 7, 1, 3, 6, 8])]
    >>> l1l2py.tools.kfold_splits(labels, 0)
    Traceback (most recent call last):
        ...
    ValueError: 'k' must be greater than zero and smaller or equal than number of samples

    """

    if not (0 < k <= len(labels)):
        raise ValueError("'k' must be greater than zero and smaller or equal "
                         "than number of samples")

    random.seed(rseed)
    indexes = range(len(labels))
    random.shuffle(indexes)

    return _splits(indexes, k)

def stratified_kfold_splits(labels, k, rseed=0):
    r"""Returns k-fold cross validation stratified splits.

    This function is a variation of :func:`kfold_splits`, which
    returns stratified splits. The divisions are made by holding
    the percentage of samples for each class, assuming that two-class problem
    is given.

    Parameters
    
    labels : array_like, shape (N,)
        Data labels (usually contains only 1s and -1s).
    k : int, greater than `0`
        Number of splits.
    rseed : int, optional (default is `0`)
        Random seed.

    Returns
    
    splits : list of ``k`` tuples
        Each tuple contains two lists with the training set and testing set
        indexes.

    Raises
    
    ValueError
        If `labels` contains more than two classes labels.
    ValueError
        If ``k`` is negative or greater than number of positive or negative
        samples in `labels`.

    See Also
    
    kfold_splits

    Examples
    
    >>> labels = range(10)
    >>> l1l2py.tools.stratified_kfold_splits(labels, 2)
    Traceback (most recent call last):
        ...
    ValueError: 'labels' must contains only two class labels
    >>> labels = [1, 1, 1, 1, 1, 1, -1, -1, -1, -1]
    >>> l1l2py.tools.stratified_kfold_splits(labels, 2)
    [([8, 9, 5, 2, 1], [7, 6, 3, 0, 4]), ([7, 6, 3, 0, 4], [8, 9, 5, 2, 1])]
    >>> l1l2py.tools.stratified_kfold_splits(labels, 1)
    [([], [7, 6, 8, 9, 3, 0, 4, 5, 2, 1])]
    >>> l1l2py.tools.stratified_kfold_splits(labels, 0)
    Traceback (most recent call last):
        ...
    ValueError: 'k' must be greater than zero and smaller or equal than number of positive and negative samples

    """
    classes = np.unique(labels)
    if classes.size != 2:
        raise ValueError("'labels' must contains only two class labels")

    random.seed(rseed)
    n_indexes = (np.where(labels == classes[0])[0]).tolist()
    p_indexes = (np.where(labels == classes[1])[0]).tolist()

    if not (0 < k <= min(len(n_indexes), len(p_indexes))):
        raise ValueError("'k' must be greater than zero and smaller or equal "
                         "than number of positive and negative samples")

    random.shuffle(n_indexes)
    n_splits = _splits(n_indexes, k)

    random.shuffle(p_indexes)
    p_splits = _splits(p_indexes, k)

    splits = list()
    for ns, ps in zip(n_splits, p_splits):
        train = ns[0] + ps[0]
        test = ns[1] + ps[1]
        splits.append( (train, test) )

    return splits

def _splits(indexes, k):
    """Splits the 'indexes' list in input in k disjoint chunks."""
    return [(indexes[:start] + indexes[end:], indexes[start:end])
                for start, end in _split_dimensions(len(indexes), k)]

def _split_dimensions(num_items, num_splits):
    """Generator wich gives the pairs of indexes to split 'num_items' data
       in 'num_splits' chunks. """
    start = 0
    remaining_items = float(num_items)

    for remaining_splits in xrange(num_splits, 0, -1):
        split_size = int(round(remaining_items / remaining_splits))
        end = start + split_size

        yield start, end

        start = end
        remaining_items -= split_size