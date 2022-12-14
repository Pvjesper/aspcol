import numpy as np
import scipy.linalg as splin

import aspcol.matrices as mat


def mse(var1, var2):
    """
    The normalized mean square error

    Normalized by the second variable
    """
    return np.sum(np.abs(var1 - var2)**2) / np.sum(np.abs(var2)**2)



#============== FOR VECTORS ======================
def angular_distance(vec1, vec2):
    """
    A distance metric based on the cosine similary, that retains the
        scale invariant property, but is also a proper distance metric

    Note that it is scale invariant, but not sign invariant 
        (same shape but opposite signs is maximum distance)
    """
    return np.arccos(cos_similary(vec1, vec2)) / np.pi

def cos_similary(vec1, vec2):
    """Computes <vec1, vec2> / (||vec1|| ||vec2||)
        which is cosine of the angle between the two vectors. 
        1 is paralell vectors, 0 is orthogonal, and -1 is opposite directions

        If the arrays have more than 1 axis, it will be flattened.
    """
    assert vec1.shape == vec2.shape
    vec1 = np.ravel(vec1)
    vec2 = np.ravel(vec2)
    norms = np.linalg.norm(vec1) *np.linalg.norm(vec2)
    if norms == 0:
        return np.nan
    ip = vec1.T @ vec2
    return ip / norms


#=============== FOR COVARIANCE MATRICES =============

def corr_matrix_distance(mat1, mat2):
    """Computes the correlation matrix distance, as defined in:
    Correlation matrix distaince, a meaningful measure for evaluation of 
    non-stationary MIMO channels - Herdin, Czink, Ozcelik, Bonek
    
    0 means that the matrices are equal up to a scaling
    1 means that they are maximally different (orthogonal in NxN dimensional space)
    """
    assert mat1.shape == mat2.shape
    norm1 = np.linalg.norm(mat1, ord="fro", axis=(-2,-1))
    norm2 = np.linalg.norm(mat2, ord="fro", axis=(-2,-1))
    if norm1 * norm2 == 0:
        return np.nan
    return 1 - np.trace(mat1 @ mat2) / (norm1 * norm2)


def covariance_distance_riemannian(mat1, mat2):
    """
    Computes the covariance matrix distance as proposed in 
        A Metric for Covariance Matrices - Wolfgang F??rstner, Boudewijn Moonen
        http://www.ipb.uni-bonn.de/pdfs/Forstner1999Metric.pdf

    It is the distance of a canonical invariant Riemannian metric on the space 
        Sym+(n, R) of real symmetric positive definite matrices. 

    When the metric of the space is the fisher information metric, this is the 
        distance of the space. See COVARIANCE CLUSTERING ON RIEMANNIAN MANIFOLDS
        FOR ACOUSTIC MODEL COMPRESSION - Shinohara, Masukp, Akamine

    Invariant to affine transformations and inversions. 
    It is a distance measure, so 0 means equal and then it goes to infinity
        and the matrices become more unequal.

    """
    eigvals = splin.eigh(mat1, mat2, eigvals_only=True)
    return np.sqrt(np.sum(np.log(eigvals)**2))


def covariance_distance_kl_divergence(mat1, mat2):
    """
    It is the Kullback Leibler divergence between two Gaussian
        distributions that has mat1 and mat2 as their covariance matrices. 
        Assumes both of these distributions has zero mean

    It is a distance measure, so 0 means equal and then it goes to infinity
        and the matrices become more unequal.
    
    """
    assert mat1.shape == mat2.shape
    assert mat1.shape[0] == mat1.shape[1]
    assert mat.ndim == 2
    N = mat1.shape[0]
    eigvals = splin.eigh(mat1, mat2, eigvals_only=True)

    det1 = splin.det(mat1)
    det2 = splin.det(mat2)
    common_trace = np.sum(eigvals)
    return np.sqrt((np.log(det2 / det1) + common_trace - N) / 2)

