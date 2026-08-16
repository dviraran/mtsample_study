#!/usr/bin/env python3
"""
Agreement statistics.

Agreement is quantified with Lin's concordance correlation coefficient rather
than Pearson's r, and displayed with Bland-Altman plots rather than two-way
scatterplots. Pearson's r measures linear association; Lin's coefficient
measures agreement with the line of identity, and a Bland-Altman summary
expresses the magnitude of agreement as 95% intervals for paired differences.

Lin's CCC (Lin, Biometrics 1989):
    rho_c = 2 * s_xy / (s_x^2 + s_y^2 + (xbar - ybar)^2)
with population (1/n) moments. It equals Pearson's r multiplied by a bias
correction factor Cb <= 1, so CCC <= |r| always.
"""

import numpy as np

BOOT_SEED = 20260728
RNG = np.random.default_rng(BOOT_SEED)


def lins_ccc(x, y, n_boot=2000, ci=True):
    """Lin's concordance correlation coefficient with a bootstrap 95% CI.

    Returns a dict with the CCC, Pearson r, the bias-correction factor Cb
    (= CCC / r, the penalty for departure from the 45-degree line), the
    location and scale shifts, and the CI.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    n = len(x)
    if n < 3:
        return {"ccc": float("nan"), "n": n}

    def _ccc(a, b):
        ma, mb = a.mean(), b.mean()
        va = ((a - ma) ** 2).mean()
        vb = ((b - mb) ** 2).mean()
        cov = ((a - ma) * (b - mb)).mean()
        denom = va + vb + (ma - mb) ** 2
        return 2 * cov / denom if denom else float("nan")

    ccc = _ccc(x, y)
    sx, sy = x.std(ddof=1), y.std(ddof=1)
    r = float(np.corrcoef(x, y)[0, 1]) if sx > 0 and sy > 0 else float("nan")
    out = {
        "n": n,
        "ccc": float(ccc),
        "pearson_r": r,
        # Cb: bias-correction factor; how much agreement is lost to systematic
        # location/scale shift relative to pure correlation.
        "cb": float(ccc / r) if r and np.isfinite(r) and r != 0 else float("nan"),
        # location shift (u) and scale shift (v), Lin's diagnostics
        "location_shift": float((x.mean() - y.mean()) / np.sqrt(sx * sy)) if sx > 0 and sy > 0 else float("nan"),
        "scale_shift": float(sx / sy) if sy > 0 else float("nan"),
    }
    if ci and n >= 10:
        idx = np.random.default_rng(BOOT_SEED).integers(0, n, size=(n_boot, n))
        boots = np.array([_ccc(x[i], y[i]) for i in idx])
        boots = boots[np.isfinite(boots)]
        if len(boots):
            out["ccc_ci"] = [float(np.percentile(boots, 2.5)),
                             float(np.percentile(boots, 97.5))]
    return out


def bland_altman(x, y):
    """Bland-Altman summary for paired measurements.

    Returns bias (mean difference y - x), the 95% limits of agreement
    (bias +/- 1.96 SD of the differences) with their own 95% CIs, and a
    proportional-bias slope (regression of difference on mean), which tests
    whether disagreement grows with the magnitude of the measurement.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    n = len(x)
    if n < 3:
        return {"n": n}

    diff = y - x
    mean = (x + y) / 2
    bias = float(diff.mean())
    sd = float(diff.std(ddof=1))
    loa_lo, loa_hi = bias - 1.96 * sd, bias + 1.96 * sd
    # SE of a limit of agreement ~ sqrt(3) * SE of the mean difference
    se_loa = float(np.sqrt(3) * sd / np.sqrt(n))
    se_bias = float(sd / np.sqrt(n))
    slope = float(np.polyfit(mean, diff, 1)[0]) if np.ptp(mean) > 0 else float("nan")

    return {
        "n": n,
        "bias": bias,
        "bias_ci": [bias - 1.96 * se_bias, bias + 1.96 * se_bias],
        "sd_diff": sd,
        "loa_lower": float(loa_lo),
        "loa_upper": float(loa_hi),
        "loa_lower_ci": [loa_lo - 1.96 * se_loa, loa_lo + 1.96 * se_loa],
        "loa_upper_ci": [loa_hi - 1.96 * se_loa, loa_hi + 1.96 * se_loa],
        "proportional_bias_slope": slope,
        "mean": mean,
        "diff": diff,
    }


def format_ccc(d):
    """Compact 'CCC 0.83 (0.71-0.90)' string for figure annotation."""
    if not np.isfinite(d.get("ccc", float("nan"))):
        return "CCC n/a"
    s = f"CCC {d['ccc']:.2f}"
    if "ccc_ci" in d:
        s += f" ({d['ccc_ci'][0]:.2f}–{d['ccc_ci'][1]:.2f})"
    return s
