# fidic_clause_reform_phd

Python simulations, source data, results and an article draft comparing FIDIC's standard price-adjustment formula (Sub-Clause 13.8 of the 1999 forms, 13.7 of the 2017 forms) with a lag-adjusted, regime-sensitive alternative calibrated to Ugandan price and macro data.

## Contents

| Path | What it is |
|---|---|
| `run_hypothetical_4y_pipeline.py` | Side-by-side simulation of the two adjustment formulas on a hypothetical 48-month project |
| `run_monte_carlo_4y.py` | Monte Carlo extension over project-risk uncertainty |
| `run_sensitivity_4y.py` | Sensitivity to coefficient scale, lag order and regime thresholds |
| `results/` | Simulation outputs (CSV, JSON), run reports (Markdown) and `figures/` |
| `UBOS Indices/ubos_cipi_2015_2025/` | Source material: UBOS CIPI press releases (PDF), extracted index tables, Bank of Uganda exchange-rate, interest-rate and monetary-policy files, and a manifest |

## Running

```
python run_hypothetical_4y_pipeline.py
python run_monte_carlo_4y.py
python run_sensitivity_4y.py
```

Each script writes to `results/`. They need pandas, numpy and matplotlib.
