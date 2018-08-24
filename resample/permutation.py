import numpy as np


def ttest(a1, a2, b=1000, dropna=True):
    """
    Perform permutation two sample t-test.

    Parameters
    ----------
    a1 : array-like
        First sample
    a2 : array-like
        Second sample
    b : int
        Number of permutations
    dropna : boolean
        Whether or not to drop np.nan

    Returns
    -------
    {'stat', 'prop'} : {float, float}
        t statistic as well as proportion of permutation
        distribution less than or equal to that statistic
    """
    def g(x, y):
        return ((np.mean(x) - np.mean(y)) /
                np.sqrt(np.var(x) / len(x) + np.var(y) / len(y)))

    if dropna:
        a1 = a1[~np.isnan(a1)]
        a2 = a2[~np.isnan(a2)]

    t = g(a1, a2)

    n1 = len(a1)
    n2 = len(a2)

    X = np.apply_along_axis(func1d=np.random.permutation,
                            arr=np.reshape(np.tile(np.append(a1, a2), b),
                                           newshape=(b, n1 + n2)),
                            axis=1)
    permute_t = np.apply_along_axis(func1d=lambda s: g(s[:n1], s[n1:]),
                                    arr=X,
                                    axis=1)

    return {"stat": t, "prop": np.mean(permute_t <= t)}


def anova(*args, b=1000, dropna=True):
    """
    Permutation one way analysis of variance.

    Parameters
    ----------
    args : sequence of array-like
        Samples
    b : int
        Number of permutations
    dropna : boolean
        Whether or not to drop np.nan

    Returns
    -------
    {'stat', 'prop'} : {float, float}
        F statistic as well as proportion of permutation
        distribution less than or equal to that statistic
    """
    args = [np.asarray(a) for a in args]

    if dropna:
        args = [a[~np.isnan(a)] for a in args]

    t = len(args)
    ns = [len(a) for a in args]
    n = np.sum(ns)
    pos = np.append(0, np.cumsum(ns))
    arr = np.concatenate(args)
    gmean = np.mean(arr)

    def g(a):
        sse = np.sum([ns[i] * np.var(a[pos[i]:pos[i+1]]) for i in range(t)])
        ssb = (np.sum([ns[i] * (np.mean(a[pos[i]:pos[i+1]]) - gmean)**2
                       for i in range(t)]))
        return (ssb / (t - 1)) / (sse / (n - t))

    X = np.reshape(np.tile(arr, b), newshape=(b, n))

    f = g(arr)
    permute_f = np.apply_along_axis(func1d=(lambda x:
                                            g(np.random.permutation(x))),
                                    arr=X,
                                    axis=1)

    return {"stat": f, "prop": np.mean(permute_f <= f)}
