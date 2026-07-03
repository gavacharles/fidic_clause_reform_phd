# Hypothetical 4-Year Pipeline Run: FIDIC vs Dynamic Lag-Adjusted Model

- Timeline: **2019-01-31 to 2022-12-31**
- Effective months (after lag initialization): **48**

## Tracking Accuracy (Factor-Level)

- FIDIC MAE: **0.1374**
- Dynamic MAE: **0.0705**
- FIDIC RMSE: **0.1975**
- Dynamic RMSE: **0.0886**
- FIDIC MAPE: **20.76%**
- Dynamic MAPE: **11.49%**

## Tracking Accuracy (Certificate UGX)

- FIDIC MAE: **300604.63 UGX**
- Dynamic MAE: **166987.90 UGX**
- FIDIC RMSE: **593161.95 UGX**
- Dynamic RMSE: **255315.00 UGX**

## Cumulative Gap vs Realized Proxy

- FIDIC cumulative gap: **-11277016.05 UGX**
- Dynamic cumulative gap: **-7594338.73 UGX**

## Figures

- [analysis_output/fidic_clause_reform_phd/results/figures/conceptual_macro_shock_transmission_framework.png](analysis_output/fidic_clause_reform_phd/results/figures/conceptual_macro_shock_transmission_framework.png)
- [analysis_output/fidic_clause_reform_phd/results/figures/fidic_vs_dynamic_factor_tracking.png](analysis_output/fidic_clause_reform_phd/results/figures/fidic_vs_dynamic_factor_tracking.png)
- [analysis_output/fidic_clause_reform_phd/results/figures/fidic_vs_dynamic_cumulative_gap.png](analysis_output/fidic_clause_reform_phd/results/figures/fidic_vs_dynamic_cumulative_gap.png)
- [analysis_output/fidic_clause_reform_phd/results/figures/phase_regime_heatmap.png](analysis_output/fidic_clause_reform_phd/results/figures/phase_regime_heatmap.png)

## Notes

This is a policy simulation pipeline for methodological comparison. The realized proxy is synthetic and designed to emulate lagged friction for side-by-side performance testing under a controlled hypothetical project timeline.