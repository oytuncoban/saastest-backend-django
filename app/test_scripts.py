import numpy as np
import pandas as pd
from scipy.special import binom
from scipy.stats import chi2_contingency, mannwhitneyu, norm, t, ttest_ind, shapiro, fisher_exact

def hypergeom(k, K, n, N):
    """Probability mass funciton of the hypergeometric distribution."""
    return binom(K, k) * binom(N - K, n - k) / binom(N, n)


def fisher_prob(m):
    """Probability of a given observed contingency table according to Fisher's exact test."""
    ((a, b), (c, d)) = m
    k = a
    K = a + b
    n = a + c
    N = a + b + c + d
    return hypergeom(k, K, n, N)


def fisher_probs_histogram(m):
    """Computes prob mass function histogram accroding to Fisher's exact test."""
    neg_val = -min(m[0, 0], m[1, 1])
    pos_val = min(m[0, 1], m[1, 0])
    probs = []
    for k in range(neg_val, pos_val + 1):
        m1 = m + np.array([[1, -1], [-1, 1]]) * k
        probs.append(fisher_prob(m1))
    return probs


def fisher_pval(m):
    _, p_val = fisher_exact(m)
    return p_val


def chi_square_test(m):
    (chi2, p) = chi2_contingency(m, correction=False)[:2]
    return p


def perform_t_test(df):
    # Perform the t-test
    t_score, p_value = ttest_ind(
        df["A"], df["B"], nan_policy="omit"
    )  # 'omit' to exclude any NaN values

    return p_value


def perform_welch_t_test(df):
    # Perform the Welch's t-test
    t_score, p_value = ttest_ind(
        df["A"], df["B"], equal_var=False, nan_policy="omit"
    )  # 'omit' to exclude any NaN values

    return p_value


def perform_mann_whitney_u_test(df):
    # Perform the Mann-Whitney U test
    u_score, p_value = mannwhitneyu(
        df["A"], df["B"], alternative="two-sided"
    )  # 'two-sided' for a two-sided test

    return p_value


def is_normal(df, column, alpha=0.05):
    """
    Perform Shapiro-Wilk test for normality.

    H0: the sample is drawn from a normal distribution

    If the p-value is greater than alpha, we cannot reject the hypothesis that the data is normal.
    """

    stat, p_value = shapiro(df[column])

    return p_value > alpha