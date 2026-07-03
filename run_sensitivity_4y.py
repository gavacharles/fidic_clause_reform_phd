from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


ROOT = Path("/Users/charlesgava/Library/CloudStorage/OneDrive-Personal/PhD/UJ/Research/Papers/Building Safety")
BASE = ROOT / "analysis_output" / "fidic_clause_reform_phd"
RESULTS = BASE / "results"
FIG = RESULTS / "figures"
RESULTS.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)


def mae(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.mean(np.abs(a - b)))


def rmse(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.sqrt(np.mean((a - b) ** 2)))


def mape(a: np.ndarray, b: np.ndarray) -> float:
    eps = 1e-8
    return float(np.mean(np.abs((a - b) / np.maximum(np.abs(b), eps))) * 100)


def assign_phase(m: int) -> str:
    if m <= 12:
        return "Phase 1: Earthworks"
    if m <= 24:
        return "Phase 2: Structural"
    if m <= 36:
        return "Phase 3: Finishes"
    return "Phase 4: MEP/Commissioning"


def get_panel() -> pd.DataFrame:
    src = ROOT / "analysis_output" / "cipi_macro_phd" / "monthly_cipi_macro_2015_2025_full_ocr.csv"
    d = pd.read_csv(src)
    d["date"] = pd.to_datetime(d["date"])
    d = d[(d["date"] >= "2019-01-31") & (d["date"] <= "2022-12-31")].copy()
    d = d.sort_values("date").reset_index(drop=True)
    d["month_no"] = np.arange(1, len(d) + 1)
    d["phase"] = d["month_no"].apply(assign_phase)

    d["L"] = d["cipi_residential"]
    d["M"] = d["cipi_civil"]
    d["E"] = d["cipi_nonresidential"]
    d["EXR"] = d["usd_ugx"]
    d["CBR"] = d["cbr"]

    b = d.iloc[0]
    d["Lr"] = d["L"] / b["L"]
    d["Mr"] = d["M"] / b["M"]
    d["Er"] = d["E"] / b["E"]
    d["XR"] = d["EXR"] / b["EXR"]
    d["CR"] = d["CBR"] / b["CBR"]

    for c in ["Lr", "Mr", "Er", "XR", "CR"]:
        for k in range(1, 7):
            d[f"{c}_lag{k}"] = d[c].shift(k).fillna(d[c])

    # Static FIDIC baseline
    d["fidic"] = 0.15 + 0.25 * d["Lr"] + 0.40 * d["Mr"] + 0.20 * d["Er"]

    # Friction proxy used for comparative diagnostics
    d["proxy"] = (
        0.06
        + 0.14 * d["Lr_lag1"]
        + 0.26 * d["Mr_lag2"]
        + 0.20 * d["Er_lag2"]
        + 0.23 * d["XR_lag3"]
        + 0.11 * d["CR_lag4"]
    )

    # Regime score
    dx = d["EXR"].pct_change().fillna(0).abs()
    dr = d["CBR"].diff().fillna(0).abs()
    d["score"] = 0.7 * (dx / (dx.quantile(0.8) + 1e-8)) + 0.3 * (dr / (dr.quantile(0.8) + 1e-8))

    return d


def extend_weights(base: list[float], n: int, decay: float = 0.6) -> list[float]:
    if n <= len(base):
        return base[:n]
    out = list(base)
    last = base[-1]
    for i in range(n - len(base)):
        out.append(last * (decay ** (i + 1)))
    return out


def build_dynamic(
    d: pd.DataFrame,
    lag_order: int = 2,
    coef_scale: float = 1.0,
    threshold_low: float = 0.6,
    threshold_high: float = 1.0,
) -> np.ndarray:
    phase_params = {
        "Phase 1: Earthworks": {"a": 0.10, "lam": [0.10, 0.08], "beta": [0.12, 0.16, 0.12], "gamma": [0.15, 0.15, 0.10], "delta": 0.10, "phi": [0.02]},
        "Phase 2: Structural": {"a": 0.08, "lam": [0.10, 0.08], "beta": [0.18, 0.20, 0.15], "gamma": [0.10, 0.08, 0.06], "delta": 0.11, "phi": [0.02]},
        "Phase 3: Finishes": {"a": 0.09, "lam": [0.12, 0.10], "beta": [0.12, 0.14, 0.10], "gamma": [0.08, 0.07, 0.06], "delta": 0.09, "phi": [0.02]},
        "Phase 4: MEP/Commissioning": {"a": 0.10, "lam": [0.10, 0.09], "beta": [0.10, 0.12, 0.08], "gamma": [0.12, 0.11, 0.09], "delta": 0.13, "phi": [0.02]},
    }
    regime_adj = {
        "Stable": {"a_shift": 0.00, "lag_mult": 1.00, "delta_mult": 1.00},
        "Transition": {"a_shift": -0.02, "lag_mult": 1.06, "delta_mult": 1.08},
        "Stress": {"a_shift": -0.04, "lag_mult": 1.12, "delta_mult": 1.15},
    }

    regime = np.where(d["score"] >= threshold_high, "Stress", np.where(d["score"] >= threshold_low, "Transition", "Stable"))

    out = []
    for i, r in d.iterrows():
        p = phase_params[r["phase"]]
        g = regime_adj[str(regime[i])]

        a_n = max(0.03, (p["a"] + g["a_shift"]) * coef_scale)
        lam = [x * g["lag_mult"] * coef_scale for x in extend_weights(p["lam"], lag_order)]
        beta = [x * g["lag_mult"] * coef_scale for x in extend_weights(p["beta"], lag_order + 1)]  # includes contemporaneous
        gamma = [x * g["lag_mult"] * coef_scale for x in extend_weights(p["gamma"], lag_order + 1)]
        phi = [x * coef_scale for x in extend_weights(p["phi"], lag_order)]
        delta = p["delta"] * g["delta_mult"] * coef_scale

        l_part = sum(lam[k] * r[f"Lr_lag{k+1}"] for k in range(lag_order))
        m_part = beta[0] * r["Mr"] + sum(beta[k + 1] * r[f"Mr_lag{k+1}"] for k in range(lag_order))
        e_part = gamma[0] * r["Er"] + sum(gamma[k + 1] * r[f"Er_lag{k+1}"] for k in range(lag_order))
        c_part = sum(phi[k] * r[f"CR_lag{k+1}"] for k in range(lag_order))

        out.append(a_n + l_part + m_part + e_part + delta * r["XR"] + c_part)

    return np.array(out)


def evaluate(dynamic: np.ndarray, d: pd.DataFrame) -> dict:
    f = d["fidic"].to_numpy()
    y = d["proxy"].to_numpy()
    return {
        "fidic_mae": mae(f, y),
        "dynamic_mae": mae(dynamic, y),
        "fidic_rmse": rmse(f, y),
        "dynamic_rmse": rmse(dynamic, y),
        "fidic_mape": mape(f, y),
        "dynamic_mape": mape(dynamic, y),
        "mae_improvement": mae(f, y) - mae(dynamic, y),
        "rmse_improvement": rmse(f, y) - rmse(dynamic, y),
    }


def main() -> None:
    sns.set_theme(style="whitegrid", context="talk")
    d = get_panel()

    # Sensitivity 1: lag-order
    lag_rows = []
    for L in [1, 2, 3, 4]:
        dyn = build_dynamic(d, lag_order=L, coef_scale=1.0, threshold_low=0.6, threshold_high=1.0)
        m = evaluate(dyn, d)
        m["scenario"] = f"lag_order_{L}"
        m["lag_order"] = L
        lag_rows.append(m)
    lag_df = pd.DataFrame(lag_rows)
    lag_df.to_csv(RESULTS / "sensitivity_lag_order.csv", index=False)

    # Sensitivity 2: coefficient priors/scales
    coef_rows = []
    for s in [0.80, 0.90, 1.00, 1.10, 1.20]:
        dyn = build_dynamic(d, lag_order=2, coef_scale=s, threshold_low=0.6, threshold_high=1.0)
        m = evaluate(dyn, d)
        m["scenario"] = f"coef_scale_{s:.2f}"
        m["coef_scale"] = s
        coef_rows.append(m)
    coef_df = pd.DataFrame(coef_rows)
    coef_df.to_csv(RESULTS / "sensitivity_coefficient_scale.csv", index=False)

    # Sensitivity 3: regime thresholds
    thr_rows = []
    for low, high in [(0.50, 0.90), (0.60, 1.00), (0.70, 1.10), (0.80, 1.20)]:
        dyn = build_dynamic(d, lag_order=2, coef_scale=1.0, threshold_low=low, threshold_high=high)
        m = evaluate(dyn, d)
        m["scenario"] = f"threshold_{low:.2f}_{high:.2f}"
        m["threshold_low"] = low
        m["threshold_high"] = high
        thr_rows.append(m)
    thr_df = pd.DataFrame(thr_rows)
    thr_df.to_csv(RESULTS / "sensitivity_regime_thresholds.csv", index=False)

    # Summary
    summary = {
        "lag_order": {
            "best_dynamic_mae": float(lag_df["dynamic_mae"].min()),
            "best_lag_order": int(lag_df.loc[lag_df["dynamic_mae"].idxmin(), "lag_order"]),
            "mae_improvement_range": [float(lag_df["mae_improvement"].min()), float(lag_df["mae_improvement"].max())],
        },
        "coefficient_scale": {
            "best_dynamic_mae": float(coef_df["dynamic_mae"].min()),
            "best_coef_scale": float(coef_df.loc[coef_df["dynamic_mae"].idxmin(), "coef_scale"]),
            "mae_improvement_range": [float(coef_df["mae_improvement"].min()), float(coef_df["mae_improvement"].max())],
        },
        "regime_thresholds": {
            "best_dynamic_mae": float(thr_df["dynamic_mae"].min()),
            "best_threshold_pair": [
                float(thr_df.loc[thr_df["dynamic_mae"].idxmin(), "threshold_low"]),
                float(thr_df.loc[thr_df["dynamic_mae"].idxmin(), "threshold_high"]),
            ],
            "mae_improvement_range": [float(thr_df["mae_improvement"].min()), float(thr_df["mae_improvement"].max())],
        },
    }
    with open(RESULTS / "sensitivity_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    # Figures
    plt.figure(figsize=(10, 5.8))
    plt.plot(lag_df["lag_order"], lag_df["dynamic_mae"], marker="o", lw=2, label="Dynamic MAE")
    plt.axhline(lag_df["fidic_mae"].iloc[0], linestyle="--", color="black", label="FIDIC MAE")
    plt.title("Sensitivity 1: Lag-Order vs Factor MAE")
    plt.xlabel("Lag order")
    plt.ylabel("MAE")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG / "sensitivity_lag_order_mae.png", dpi=220)
    plt.close()

    plt.figure(figsize=(10, 5.8))
    plt.plot(coef_df["coef_scale"], coef_df["dynamic_mae"], marker="o", lw=2, label="Dynamic MAE")
    plt.axhline(coef_df["fidic_mae"].iloc[0], linestyle="--", color="black", label="FIDIC MAE")
    plt.title("Sensitivity 2: Coefficient Scale vs Factor MAE")
    plt.xlabel("Coefficient scale")
    plt.ylabel("MAE")
    plt.legend()
    plt.tight_layout()
    plt.savefig(FIG / "sensitivity_coefficient_scale_mae.png", dpi=220)
    plt.close()

    plt.figure(figsize=(11, 6.0))
    labels = [f"({r.threshold_low:.1f},{r.threshold_high:.1f})" for r in thr_df.itertuples(index=False)]
    sns.barplot(x=labels, y=thr_df["mae_improvement"], color="#2ca02c")
    plt.axhline(0, color="black", lw=1)
    plt.title("Sensitivity 3: Regime Thresholds and MAE Improvement")
    plt.xlabel("Regime threshold pair (low, high)")
    plt.ylabel("MAE improvement (FIDIC - Dynamic)")
    plt.tight_layout()
    plt.savefig(FIG / "sensitivity_regime_threshold_mae_improvement.png", dpi=220)
    plt.close()

    # Markdown report
    md = []
    md.append("# Sensitivity Analysis Report (Standalone FIDIC Reform Paper)\n")
    md.append("Implemented tests: lag-order sensitivity, coefficient-scale sensitivity, and regime-threshold sensitivity.\n")

    md.append("## Lag-order sensitivity\n")
    for r in lag_df.itertuples(index=False):
        md.append(f"- lag={int(r.lag_order)}: dynamic MAE={r.dynamic_mae:.4f}, improvement={r.mae_improvement:.4f}")

    md.append("\n## Coefficient-scale sensitivity\n")
    for r in coef_df.itertuples(index=False):
        md.append(f"- scale={r.coef_scale:.2f}: dynamic MAE={r.dynamic_mae:.4f}, improvement={r.mae_improvement:.4f}")

    md.append("\n## Regime-threshold sensitivity\n")
    for r in thr_df.itertuples(index=False):
        md.append(
            f"- thresholds=({r.threshold_low:.2f},{r.threshold_high:.2f}): dynamic MAE={r.dynamic_mae:.4f}, improvement={r.mae_improvement:.4f}"
        )

    md.append("\n## Files\n")
    md.append("- [analysis_output/fidic_clause_reform_phd/results/sensitivity_lag_order.csv](analysis_output/fidic_clause_reform_phd/results/sensitivity_lag_order.csv)")
    md.append("- [analysis_output/fidic_clause_reform_phd/results/sensitivity_coefficient_scale.csv](analysis_output/fidic_clause_reform_phd/results/sensitivity_coefficient_scale.csv)")
    md.append("- [analysis_output/fidic_clause_reform_phd/results/sensitivity_regime_thresholds.csv](analysis_output/fidic_clause_reform_phd/results/sensitivity_regime_thresholds.csv)")
    md.append("- [analysis_output/fidic_clause_reform_phd/results/sensitivity_summary.json](analysis_output/fidic_clause_reform_phd/results/sensitivity_summary.json)")
    md.append("- [analysis_output/fidic_clause_reform_phd/results/figures/sensitivity_lag_order_mae.png](analysis_output/fidic_clause_reform_phd/results/figures/sensitivity_lag_order_mae.png)")
    md.append("- [analysis_output/fidic_clause_reform_phd/results/figures/sensitivity_coefficient_scale_mae.png](analysis_output/fidic_clause_reform_phd/results/figures/sensitivity_coefficient_scale_mae.png)")
    md.append("- [analysis_output/fidic_clause_reform_phd/results/figures/sensitivity_regime_threshold_mae_improvement.png](analysis_output/fidic_clause_reform_phd/results/figures/sensitivity_regime_threshold_mae_improvement.png)")

    (RESULTS / "sensitivity_analysis_report.md").write_text("\n".join(md), encoding="utf-8")

    print("Sensitivity analysis complete:")
    print("-", RESULTS / "sensitivity_lag_order.csv")
    print("-", RESULTS / "sensitivity_coefficient_scale.csv")
    print("-", RESULTS / "sensitivity_regime_thresholds.csv")
    print("-", RESULTS / "sensitivity_summary.json")
    print("-", RESULTS / "sensitivity_analysis_report.md")
    print("-", FIG / "sensitivity_lag_order_mae.png")
    print("-", FIG / "sensitivity_coefficient_scale_mae.png")
    print("-", FIG / "sensitivity_regime_threshold_mae_improvement.png")


if __name__ == "__main__":
    main()
