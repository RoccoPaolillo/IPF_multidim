import pandas as pd
import numpy as np
import random
import itertools

np.random.seed(37)
random.seed(37)

height = [
    np.random.normal(5.5, 1.0, 100),
    np.random.normal(5.3, 1.0, 200),
    np.random.normal(5.9, 1.0, 300),
    np.random.normal(5.7, 1.0, 200),
    np.random.normal(5.3, 1.0, 400),
    np.random.normal(5.2, 1.0, 500),
    np.random.normal(5.8, 1.0, 300),
    np.random.normal(5.5, 1.0, 200)
]

demographic = [
    ['white', 'minor', 'male'],
    ['white', 'minor', 'female'],
    ['white', 'adult', 'male'],
    ['white', 'adult', 'female'],
    ['other', 'minor', 'male'],
    ['other', 'minor', 'female'],
    ['other', 'adult', 'male'],
    ['other', 'adult', 'female']
]

data = [[{'race': d[0], 'age': d[1], 'gender': d[2], 'height': h} for h in s]
        for d, s in zip(demographic, height)]
data = list(itertools.chain(*data))

df = pd.DataFrame(data)
df.head()

df.race.value_counts().sort_index() / df.shape[0]

###

def get_target_marginals(d):
    factors = list(d.keys())
    targets = [sorted([(k2, v2) for k2, v2 in v.items()]) for k, v in d.items()]
    targets = np.array([[v for _, v in item] for item in targets])
    return factors, targets

def get_table(df, targets):
    factors, target_marginals = get_target_marginals(targets)

    cross_tab = pd.crosstab(df[factors[0]], [df[c] for c in factors[1:]])
    shape = tuple([df[c].unique().shape[0] for c in factors])
    table = cross_tab.values.reshape(shape)

    return factors, target_marginals, table

f, u, X = get_table(df, {
    'race': {'white': 5800, 'other': 4200},
    'age': {'minor': 2800, 'adult': 7200},
    'gender': {'male': 4900, 'female': 5100}
})

### mipf

def get_coordinates(M):
    return list(itertools.product(*[list(range(n)) for n in M.shape]))

def get_marginals(M, i):
    coordinates = get_coordinates(M)

    key = lambda tup: tup[0]
    counts = [(c[i], M[c]) for c in coordinates]
    counts = sorted(counts, key=key)
    counts = itertools.groupby(counts, key=key)
    counts = {k: sum([v[1] for v in g]) for k, g in counts}

    return counts

def get_all_marginals(M):
    return np.array([[v for _, v in get_marginals(M, i).items()]
                     for i in range(len(M.shape))])

def get_counts(M, i):
    coordinates = get_coordinates(M)

    key = lambda tup: tup[0]
    counts = [(c[i], M[c], c) for c in coordinates]
    counts = sorted(counts, key=key)
    counts = itertools.groupby(counts, key=key)
    counts = {k: [(tup[1], tup[2]) for tup in g] for k, g in counts}

    return counts

# really ipf weight
def update_values(M, i, u):
    marg = get_marginals(M, i)
    vals = get_counts(M, i)

    d = [[(c, n * u[k] / marg[k]) for n, c in v] for k, v in vals.items()]
    d = itertools.chain(*d)
    d = list(d)

    return d

# iterative proportional fitting, updating the values at each time step
def ipf_update(M, u):
    for i in range(len(M.shape)):
        values = update_values(M, i, u[i])
        for idx, v in values:
            M[idx] = v

    o = get_all_marginals(M)
    d = get_deltas(o, u)

    return M, d

# 
def get_deltas(o, t):
    return np.array([np.linalg.norm(o[r] - t[r], 2) for r in range(o.shape[0])])

def get_weights(X, max_iters=50, zero_threshold=0.0001, convergence_threshold=3, debug=True):
    M = X.copy()

    d_prev = np.zeros(len(M.shape))
    count_zero = 0

    for _ in range(max_iters):
        M, d_next = ipf_update(M, u)
        d = np.linalg.norm(d_prev - d_next, 2)

        if d < zero_threshold:
            count_zero += 1

        if debug:
            print(','.join([f'{v:.5f}' for v in d_next]), d)
        d_prev = d_next

        if count_zero >= convergence_threshold:
            break

    w = M / M.sum()
    return w

## sampling

import functools

w = get_weights(X, max_iters=50, zero_threshold=0.0001, convergence_threshold=3, debug=True)

def get_sampling_weights(df, f, w):
    get_filters = lambda df, fields, values: [df[f] == v for f, v in zip(fields, values)]
    get_total = lambda df, fields, values: df[functools.reduce(lambda a, b: a & b, get_filters(df, fields, values))].shape[0]

    return {k: v / get_total(df, f, k) for k, v in zip(list(itertools.product(*[sorted(df[c].unique()) for c in f])), np.ravel(w))}

def get_samples(df, f, w, n=10_000):
    weights = get_sampling_weights(df, f, w)
    s = df.apply(lambda r: weights[tuple([r[c] for c in f])], axis=1)
    return df.sample(n=n, replace=True, weights=s)

sample_df = get_samples(df, f, w)
sample_df

ct = pd.crosstab(sample_df.race, [sample_df.age, sample_df.gender])
ct

sample_df2 = get_samples(df, f, w, n=10)

ct2 = pd.crosstab(sample_df2.race, [sample_df2.age, sample_df2.gender])

data = pd.read_csv('C:/Users/rocpa/OneDrive/Documenti/GitHub/IPF_multidim/GIS/data/lazio_ASL_istat/df_range.csv')


