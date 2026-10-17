import numpy as np


def center(X):
    mean = X.mean(axis=1, keepdims=True)
    return X - mean, mean


def whiten(X):
    cov = np.cov(X)
    vals, vecs = np.linalg.eigh(cov)
    order = np.argsort(vals)[::-1]
    vals, vecs = vals[order], vecs[:, order]
    V = np.diag(vals ** -0.5) @ vecs.T
    return V @ X, V


def decorrelate(W):
    vals, vecs = np.linalg.eigh(W @ W.T)
    return vecs @ np.diag(vals ** -0.5) @ vecs.T @ W


def fastica(Z, n_iter=500, tol=1e-8, seed=0):
    n, m = Z.shape
    rng = np.random.default_rng(seed)
    W = decorrelate(rng.standard_normal((n, n)))
    for _ in range(n_iter):
        Y = W @ Z
        g = np.tanh(Y)
        g_prime = 1 - g ** 2
        W_new = (g @ Z.T) / m - np.diag(g_prime.mean(axis=1)) @ W
        W_new = decorrelate(W_new)
        change = np.max(np.abs(np.abs(np.diag(W_new @ W.T)) - 1))
        W = W_new
        if change < tol:
            break
    return W
