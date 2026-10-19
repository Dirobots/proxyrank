"""Plot of experiments/results/g1_study.md (Spearman section) for the README.

    uv run --with matplotlib python docs/figures/g1_plot.py
"""

from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).parents[2]


def table(section):
    lines = (ROOT / "experiments/results/g1_study.md").read_text().split("\n")
    start = lines.index(f"## {section}")
    rows = []
    for line in lines[start + 4:]:
        if not line.startswith("| "):
            break
        rows.append([c.strip() for c in line.strip("|").split("|")])
    return rows


rows = table("spearman")
n = [int(r[0]) for r in rows]
pct = lambda c: [float(r[c].rstrip("%")) for r in rows]
fig, ax = plt.subplots(1, 2, figsize=(9, 3.2), dpi=160)
ax[0].plot(n, [100 * float(r[1]) for r in rows], "o-", color="#444")
ax[0].set(xlabel="real trials per policy", ylabel="%", title="naive Spearman picks the best simulator",
          ylim=(0, 100), xscale="log", xticks=n, xticklabels=n)
ax[1].plot(n, pct(2), "o-", color="#c44", label="naive (sign of observed difference)")
ax[1].plot(n, pct(4), "o-", color="#26a", label="proxyrank compare, P ≥ 0.95")
ax[1].set(xlabel="real trials per policy", ylabel="% of claims wrong", title="which simulator agrees better?",
          ylim=(0, 25), xscale="log", xticks=n, xticklabels=n)
ax[1].legend(frameon=False, fontsize=8)
for a in ax:
    a.spines[["top", "right"]].set_visible(False)
    a.xaxis.set_minor_locator(plt.NullLocator())
fig.tight_layout()
fig.savefig(ROOT / "docs/figures/g1_claims.png")
