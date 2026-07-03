# Sensitivity Analysis Report (Standalone FIDIC Reform Paper)

Implemented tests: lag-order sensitivity, coefficient-scale sensitivity, and regime-threshold sensitivity.

## Lag-order sensitivity

- lag=1: dynamic MAE=0.1738, improvement=-0.0364
- lag=2: dynamic MAE=0.0643, improvement=0.0731
- lag=3: dynamic MAE=0.0732, improvement=0.0642
- lag=4: dynamic MAE=0.1008, improvement=0.0366

## Coefficient-scale sensitivity

- scale=0.80: dynamic MAE=0.1615, improvement=-0.0241
- scale=0.90: dynamic MAE=0.1075, improvement=0.0299
- scale=1.00: dynamic MAE=0.0643, improvement=0.0731
- scale=1.10: dynamic MAE=0.0680, improvement=0.0694
- scale=1.20: dynamic MAE=0.0992, improvement=0.0382

## Regime-threshold sensitivity

- thresholds=(0.50,0.90): dynamic MAE=0.0641, improvement=0.0733
- thresholds=(0.60,1.00): dynamic MAE=0.0643, improvement=0.0731
- thresholds=(0.70,1.10): dynamic MAE=0.0648, improvement=0.0726
- thresholds=(0.80,1.20): dynamic MAE=0.0656, improvement=0.0718

## Files

- [analysis_output/fidic_clause_reform_phd/results/sensitivity_lag_order.csv](analysis_output/fidic_clause_reform_phd/results/sensitivity_lag_order.csv)
- [analysis_output/fidic_clause_reform_phd/results/sensitivity_coefficient_scale.csv](analysis_output/fidic_clause_reform_phd/results/sensitivity_coefficient_scale.csv)
- [analysis_output/fidic_clause_reform_phd/results/sensitivity_regime_thresholds.csv](analysis_output/fidic_clause_reform_phd/results/sensitivity_regime_thresholds.csv)
- [analysis_output/fidic_clause_reform_phd/results/sensitivity_summary.json](analysis_output/fidic_clause_reform_phd/results/sensitivity_summary.json)
- [analysis_output/fidic_clause_reform_phd/results/figures/sensitivity_lag_order_mae.png](analysis_output/fidic_clause_reform_phd/results/figures/sensitivity_lag_order_mae.png)
- [analysis_output/fidic_clause_reform_phd/results/figures/sensitivity_coefficient_scale_mae.png](analysis_output/fidic_clause_reform_phd/results/figures/sensitivity_coefficient_scale_mae.png)
- [analysis_output/fidic_clause_reform_phd/results/figures/sensitivity_regime_threshold_mae_improvement.png](analysis_output/fidic_clause_reform_phd/results/figures/sensitivity_regime_threshold_mae_improvement.png)