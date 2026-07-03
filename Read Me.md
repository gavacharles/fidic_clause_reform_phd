# Comprehensive Report: Reassessing FIDIC Clause 13.8 (1999) / Clause 13.7 (2017) for Uganda’s Construction Price Adjustment

## 1. Report Purpose
This report develops a standalone PhD workstream that critiques the standard FIDIC escalation mechanism and proposes a Uganda-specific, data-driven alternative based on measured lag transmission, regime changes, and exchange-rate exposure.

## 2. Baseline Contract Mechanism Under Review
The standard multiplier form is represented as:

$$
P_n = a + b\left(\frac{L_n}{L_0}\right) + c\left(\frac{M_n}{M_0}\right) + d\left(\frac{E_n}{E_0}\right) + \cdots
$$

Where `a` is a fixed non-adjustable share, `b,c,d` are fixed category weights, and current/base index ratios drive monthly adjustment.

## 3. Core Critique in Uganda’s Macroeconomic Context
### 3.1 Instantaneous pass-through assumption is empirically weak
Uganda’s reconstructed 2015–2025 panel indicates lagged transmission rather than same-month equivalence. Peak responses differ materially across segments and channels.

### 3.2 Fixed coefficients are misaligned with project phase reality
Cost exposure is phase-dependent. Earthworks, structure, finishing, and electromechanical stages do not share identical labor/material/equipment composition.

### 3.3 Fixed non-adjustable share can become distortionary
In volatility windows, a rigid `a` can transfer disproportionate risk and increase certificate stress, renegotiation pressure, and dispute exposure.

## 4. Proposed Dynamic, Lag-Adjusted Escalation Model
A generalized Uganda-specific form:

$$
P_n^* = a_n + \sum_{k=0}^{K} \beta_k\left(\frac{M_{n-k}}{M_0}\right) + \sum_{j=0}^{J} \gamma_j\left(\frac{E_{n-j}}{E_0}\right) + \delta_n\left(\frac{EXR_n}{EXR_0}\right)
$$

Optional extensions:

$$
+\sum_{h=0}^{H}\lambda_h\left(\frac{L_{n-h}}{L_0}\right) + \sum_{q=0}^{Q}\phi_q\,\Delta CBR_{n-q}
$$

## 5. Calibration Logic
- Lag structure (`K,J,H,Q`) derived from IRF timing and decay.
- Coefficients (`a_n,\beta_k,\gamma_j,\delta_n`) allowed to vary by regime and project phase.
- Regimes identified from clustering outputs and break windows.

## 6. Side-by-Side Simulation Framework
### 6.1 Objective
Evaluate whether `P_n^*` tracks observed market friction better than baseline FIDIC form.

### 6.2 Steps
1. Define project timeline and monthly certificate sequence.
2. Compute baseline FIDIC adjustment using fixed weights and contemporaneous indices.
3. Compute dynamic adjustment using lag-distributed terms and exchange-rate elasticity.
4. Compare both to realized friction proxy.

### 6.3 Evaluation Metrics
- MAE and RMSE.
- Peak-timing error (months).
- Cumulative under/over-adjustment.
- Stress-window performance (2018–2019; 2020–2021).

### 6.4 Implemented Pipeline and 4-Year Hypothetical Run
The simulation pipeline has been implemented and executed for a hypothetical 4-year project timeline.

- Pipeline script: [analysis_output/fidic_clause_reform_phd/run_hypothetical_4y_pipeline.py](analysis_output/fidic_clause_reform_phd/run_hypothetical_4y_pipeline.py)
- Monthly simulation output: [analysis_output/fidic_clause_reform_phd/results/hypothetical_4y_monthly_simulation.csv](analysis_output/fidic_clause_reform_phd/results/hypothetical_4y_monthly_simulation.csv)
- Metrics JSON: [analysis_output/fidic_clause_reform_phd/results/hypothetical_4y_metrics.json](analysis_output/fidic_clause_reform_phd/results/hypothetical_4y_metrics.json)
- Run report: [analysis_output/fidic_clause_reform_phd/results/hypothetical_4y_run_report.md](analysis_output/fidic_clause_reform_phd/results/hypothetical_4y_run_report.md)

Run specification:
- Project horizon: **48 months** (2019-01-31 to 2022-12-31).
- Four execution phases: Earthworks, Structural, Finishes, MEP/Commissioning.
- Baseline arm: static FIDIC-style coefficients with same-month indices.
- Dynamic arm: lag-distributed terms + regime/phase-sensitive coefficients + exchange-rate elasticity.

Observed comparison results from the executed run:
- **Factor MAE**: FIDIC = **0.1374**, Dynamic = **0.0705**.
- **Factor RMSE**: FIDIC = **0.1975**, Dynamic = **0.0886**.
- **Factor MAPE**: FIDIC = **20.76%**, Dynamic = **11.49%**.
- **Certificate MAE**: FIDIC = **300,604.63 UGX**, Dynamic = **166,987.90 UGX**.
- **Certificate RMSE**: FIDIC = **593,161.95 UGX**, Dynamic = **255,314.99 UGX**.
- **Cumulative gap vs proxy**: FIDIC = **-11,277,016.05 UGX**, Dynamic = **-7,594,338.73 UGX**.

These outputs indicate that the dynamic lag-adjusted architecture tracks the simulated friction process materially better than the static contemporaneous benchmark.

### 6.5 Visual Outputs from the Run
- Conceptual framework of delayed transmission: [analysis_output/fidic_clause_reform_phd/results/figures/conceptual_macro_shock_transmission_framework.png](analysis_output/fidic_clause_reform_phd/results/figures/conceptual_macro_shock_transmission_framework.png)
- Factor tracking: [analysis_output/fidic_clause_reform_phd/results/figures/fidic_vs_dynamic_factor_tracking.png](analysis_output/fidic_clause_reform_phd/results/figures/fidic_vs_dynamic_factor_tracking.png)
- Cumulative gap tracking: [analysis_output/fidic_clause_reform_phd/results/figures/fidic_vs_dynamic_cumulative_gap.png](analysis_output/fidic_clause_reform_phd/results/figures/fidic_vs_dynamic_cumulative_gap.png)
- Regime-by-phase heatmap: [analysis_output/fidic_clause_reform_phd/results/figures/phase_regime_heatmap.png](analysis_output/fidic_clause_reform_phd/results/figures/phase_regime_heatmap.png)

### 6.5A Submission-Ready Figure Ordering and Action Captions
To improve reviewer comprehension and align with top-tier presentation expectations, figures should be inserted in the following narrative order with action-style captions:

1. **Figure 1 (Conceptual Mechanism):**
	[analysis_output/fidic_clause_reform_phd/results/figures/conceptual_macro_shock_transmission_framework.png](analysis_output/fidic_clause_reform_phd/results/figures/conceptual_macro_shock_transmission_framework.png)

	**Action caption:** “Figure 1: Conceptual Framework of Macroeconomic Shock Transmission. External monetary and exchange-rate shocks enter at Month $n$ but transmit through procurement, inventory, and subcontract layers before site-level cost realization at approximately Month $n+3$ to $n+8$, motivating lag-memory escalation design.”

2. **Figure 2 (Core Empirical Tracking):**
	[analysis_output/fidic_clause_reform_phd/results/figures/fidic_vs_dynamic_factor_tracking.png](analysis_output/fidic_clause_reform_phd/results/figures/fidic_vs_dynamic_factor_tracking.png)

	**Action caption:** “Figure 2: Monthly Factor Tracking under Regime Shading. Note the severe temporal misalignment of the static formula during stress periods (red shading), contrasted with tighter proxy tracking under the dynamic lag-adjusted architecture.”

3. **Figure 3 (Business-Case Consequence):**
	[analysis_output/fidic_clause_reform_phd/results/figures/fidic_vs_dynamic_cumulative_gap.png](analysis_output/fidic_clause_reform_phd/results/figures/fidic_vs_dynamic_cumulative_gap.png)

	**Action caption:** “Figure 3: Cumulative Compensation Error in UGX. The static formulation accumulates a deeper negative gap during macro-stress windows, while the dynamic model maintains a materially shallower cumulative under-compensation trajectory.”

4. **Figure 4 (Regime-Phase Exposure Context):**
	[analysis_output/fidic_clause_reform_phd/results/figures/phase_regime_heatmap.png](analysis_output/fidic_clause_reform_phd/results/figures/phase_regime_heatmap.png)

	**Action caption:** “Figure 4: Regime Occurrence by Execution Phase. The exposure profile is not temporally uniform; stress and transition states cluster differently across project phases, supporting phase-sensitive coefficient updates.”

### 6.6 Monte Carlo Extension (Project-Risk Uncertainty)
To stress-test robustness, a Monte Carlo module was implemented and executed over the same 4-year project horizon, with stochastic perturbations on macro channels and coefficient uncertainty.

- Monte Carlo pipeline: [analysis_output/fidic_clause_reform_phd/run_monte_carlo_4y.py](analysis_output/fidic_clause_reform_phd/run_monte_carlo_4y.py)
- Simulation metrics table (5,000 runs): [analysis_output/fidic_clause_reform_phd/results/monte_carlo_4y_simulation_metrics.csv](analysis_output/fidic_clause_reform_phd/results/monte_carlo_4y_simulation_metrics.csv)
- Summary metrics JSON: [analysis_output/fidic_clause_reform_phd/results/monte_carlo_4y_summary.json](analysis_output/fidic_clause_reform_phd/results/monte_carlo_4y_summary.json)
- Narrative run report: [analysis_output/fidic_clause_reform_phd/results/monte_carlo_4y_report.md](analysis_output/fidic_clause_reform_phd/results/monte_carlo_4y_report.md)

Key Monte Carlo findings:
- $P(\text{Dynamic MAE} < \text{FIDIC MAE}) = 1.000$
- $P(\text{Dynamic RMSE} < \text{FIDIC RMSE}) = 1.000$
- $P(\text{Dynamic certificate RMSE} < \text{FIDIC certificate RMSE}) = 1.000$
- MAE improvement (FIDIC - Dynamic), quantiles: P50 = **0.0602**, P80 = **0.0648**, P95 = **0.0693**
- RMSE improvement (FIDIC - Dynamic), quantiles: P50 = **0.1022**, P80 = **0.1074**, P95 = **0.1120**

Monte Carlo figures:
- [analysis_output/fidic_clause_reform_phd/results/figures/mc_mae_improvement_distribution.png](analysis_output/fidic_clause_reform_phd/results/figures/mc_mae_improvement_distribution.png)
- [analysis_output/fidic_clause_reform_phd/results/figures/mc_factor_mae_boxplot.png](analysis_output/fidic_clause_reform_phd/results/figures/mc_factor_mae_boxplot.png)
- [analysis_output/fidic_clause_reform_phd/results/figures/mc_mae_exceedance_curve.png](analysis_output/fidic_clause_reform_phd/results/figures/mc_mae_exceedance_curve.png)

Recommended policy-risk action caption for manuscript insertion:
“Figure 5: Monte Carlo MAE Distribution by Model (5,000 runs). The dynamic model’s distribution is structurally lower than the static benchmark, indicating stochastic dominance in tracking performance under uncertainty.”

### 6.7 Sensitivity Analysis (Reliability and Validity Checks)
To test parameter reliability, three sensitivity blocks were implemented and executed: lag-order sensitivity, coefficient-scale sensitivity, and regime-threshold sensitivity.

- Sensitivity script: [analysis_output/fidic_clause_reform_phd/run_sensitivity_4y.py](analysis_output/fidic_clause_reform_phd/run_sensitivity_4y.py)
- Lag-order results: [analysis_output/fidic_clause_reform_phd/results/sensitivity_lag_order.csv](analysis_output/fidic_clause_reform_phd/results/sensitivity_lag_order.csv)
- Coefficient-scale results: [analysis_output/fidic_clause_reform_phd/results/sensitivity_coefficient_scale.csv](analysis_output/fidic_clause_reform_phd/results/sensitivity_coefficient_scale.csv)
- Regime-threshold results: [analysis_output/fidic_clause_reform_phd/results/sensitivity_regime_thresholds.csv](analysis_output/fidic_clause_reform_phd/results/sensitivity_regime_thresholds.csv)
- Summary file: [analysis_output/fidic_clause_reform_phd/results/sensitivity_summary.json](analysis_output/fidic_clause_reform_phd/results/sensitivity_summary.json)
- Narrative sensitivity report: [analysis_output/fidic_clause_reform_phd/results/sensitivity_analysis_report.md](analysis_output/fidic_clause_reform_phd/results/sensitivity_analysis_report.md)

Key sensitivity findings:
- **Lag order:** best dynamic MAE occurs at lag order **2** (dynamic MAE **0.0643**).
- **Coefficient scale:** best dynamic MAE occurs at coefficient scale **1.00** (dynamic MAE **0.0643**).
- **Regime thresholds:** best tested threshold pair is **(0.50, 0.90)** with dynamic MAE **0.0641**.
- **Stability ranges:**
	- Lag-order MAE improvement range (FIDIC - Dynamic): **-0.0364 to +0.0731**.
	- Coefficient-scale MAE improvement range: **-0.0241 to +0.0731**.
	- Regime-threshold MAE improvement range: **+0.0718 to +0.0733**.

Sensitivity visuals:
- [analysis_output/fidic_clause_reform_phd/results/figures/sensitivity_lag_order_mae.png](analysis_output/fidic_clause_reform_phd/results/figures/sensitivity_lag_order_mae.png)
- [analysis_output/fidic_clause_reform_phd/results/figures/sensitivity_coefficient_scale_mae.png](analysis_output/fidic_clause_reform_phd/results/figures/sensitivity_coefficient_scale_mae.png)
- [analysis_output/fidic_clause_reform_phd/results/figures/sensitivity_regime_threshold_mae_improvement.png](analysis_output/fidic_clause_reform_phd/results/figures/sensitivity_regime_threshold_mae_improvement.png)

Interpretation: the dynamic model remains robustly superior across tested regime-threshold perturbations and around baseline calibration settings; however, very short lag memory and broad coefficient mis-scaling can weaken performance, which justifies data-anchored calibration and explicit sensitivity reporting in submission appendices.

## 7. Practical Contract Drafting Implications
- Replace single same-month escalation trigger with lag-window triggers by segment.
- Define coefficient update protocol by phase/regime.
- Include explicit exchange-rate sensitivity term for import-dependent inputs.
- Require transparent monthly computation sheet publication.

## 8. Governance and Implementation Path
1. Pilot on one completed project and one live project.
2. Validate timing performance against historical certificates.
3. Embed formula under Particular Conditions with review protocol.
4. Recalibrate after validated structural breaks.

## 9. Conclusion
For Uganda’s macro-construction environment, the static FIDIC architecture is operationally simple but structurally incomplete. A lag-aware and regime-aware escalation design is more consistent with observed transmission mechanics and can improve fairness, predictability, and dispute prevention.
