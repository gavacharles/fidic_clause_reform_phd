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


def rmse(a: pd.Series, b: pd.Series) -> float:
    return float(np.sqrt(np.mean((a - b) ** 2)))


def mae(a: pd.Series, b: pd.Series) -> float:
    return float(np.mean(np.abs(a - b)))


def mape(a: pd.Series, b: pd.Series) -> float:
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


def build_pipeline() -> None:
    sns.set_theme(style="whitegrid", context="talk")

    source = ROOT / "analysis_output" / "cipi_macro_phd" / "monthly_cipi_macro_2015_2025_full_ocr.csv"
    df = pd.read_csv(source)
    df["date"] = pd.to_datetime(df["date"])

    # 4-year hypothetical project timeline (48 months)
    # chosen to include normal + stress windows for evaluation realism
    sample = df[(df["date"] >= "2019-01-31") & (df["date"] <= "2022-12-31")].copy()
    sample = sample.sort_values("date").reset_index(drop=True)
    sample["month_no"] = np.arange(1, len(sample) + 1)
    sample["phase"] = sample["month_no"].apply(assign_phase)

    if len(sample) != 48:
        raise ValueError(f"Expected 48 monthly rows for 4-year horizon, got {len(sample)}")

    # Index proxies for simulation
    sample["L"] = sample["cipi_residential"]  # labor proxy
    sample["M"] = sample["cipi_civil"]  # material proxy
    sample["E"] = sample["cipi_nonresidential"]  # equipment proxy
    sample["EXR"] = sample["usd_ugx"]
    sample["CBR"] = sample["cbr"]

    base = sample.iloc[0]
    sample["L_ratio"] = sample["L"] / base["L"]
    sample["M_ratio"] = sample["M"] / base["M"]
    sample["E_ratio"] = sample["E"] / base["E"]
    sample["EXR_ratio"] = sample["EXR"] / base["EXR"]
    sample["CBR_ratio"] = sample["CBR"] / base["CBR"]

    # helper lag columns
    for c in ["L_ratio", "M_ratio", "E_ratio", "EXR_ratio", "CBR_ratio"]:
        for k in range(1, 5):
            sample[f"{c}_lag{k}"] = sample[c].shift(k)
            sample[f"{c}_lag{k}"] = sample[f"{c}_lag{k}"].fillna(sample[c])

    # FIDIC static formula
    a, b, c, d = 0.15, 0.25, 0.40, 0.20
    sample["factor_fidic"] = a + b * sample["L_ratio"] + c * sample["M_ratio"] + d * sample["E_ratio"]

    # Regime tags from macro volatility (simple practical classifier)
    dx = sample["EXR"].pct_change().fillna(0).abs()
    dr = sample["CBR"].diff().fillna(0).abs()
    stress_score = 0.7 * (dx / (dx.quantile(0.8) + 1e-8)) + 0.3 * (dr / (dr.quantile(0.8) + 1e-8))
    sample["regime"] = np.where(stress_score >= 1.0, "Stress", np.where(stress_score >= 0.6, "Transition", "Stable"))

    # Phase-regime dynamic coefficients
    phase_params = {
        "Phase 1: Earthworks": {"a": 0.10, "lam": [0.10, 0.08], "beta": [0.12, 0.16, 0.12], "gamma": [0.15, 0.15, 0.10], "delta": 0.10, "phi": 0.02},
        "Phase 2: Structural": {"a": 0.08, "lam": [0.10, 0.08], "beta": [0.18, 0.20, 0.15], "gamma": [0.10, 0.08, 0.06], "delta": 0.11, "phi": 0.02},
        "Phase 3: Finishes": {"a": 0.09, "lam": [0.12, 0.10], "beta": [0.12, 0.14, 0.10], "gamma": [0.08, 0.07, 0.06], "delta": 0.09, "phi": 0.02},
        "Phase 4: MEP/Commissioning": {"a": 0.10, "lam": [0.10, 0.09], "beta": [0.10, 0.12, 0.08], "gamma": [0.12, 0.11, 0.09], "delta": 0.13, "phi": 0.02},
    }
    regime_adj = {
        "Stable": {"a_shift": 0.00, "lag_mult": 1.00, "delta_mult": 1.00},
        "Transition": {"a_shift": -0.02, "lag_mult": 1.06, "delta_mult": 1.08},
        "Stress": {"a_shift": -0.04, "lag_mult": 1.12, "delta_mult": 1.15},
    }

    dynamic_vals = []
    dynamic_a = []
    for _, r in sample.iterrows():
        p = phase_params[r["phase"]]
        g = regime_adj[r["regime"]]

        a_n = max(0.03, p["a"] + g["a_shift"])
        lam = [x * g["lag_mult"] for x in p["lam"]]
        beta = [x * g["lag_mult"] for x in p["beta"]]
        gamma = [x * g["lag_mult"] for x in p["gamma"]]
        delta = p["delta"] * g["delta_mult"]
        phi = p["phi"]

        l_part = lam[0] * r.get("L_ratio_lag1", np.nan) + lam[1] * r.get("L_ratio_lag2", np.nan)
        m_part = (
            beta[0] * r.get("M_ratio", np.nan)
            + beta[1] * r.get("M_ratio_lag1", np.nan)
            + beta[2] * r.get("M_ratio_lag2", np.nan)
        )
        e_part = (
            gamma[0] * r.get("E_ratio", np.nan)
            + gamma[1] * r.get("E_ratio_lag1", np.nan)
            + gamma[2] * r.get("E_ratio_lag2", np.nan)
        )
        exr_part = delta * r.get("EXR_ratio", np.nan)
        cbr_part = phi * r.get("CBR_ratio_lag1", np.nan)

        dynamic_vals.append(a_n + l_part + m_part + e_part + exr_part + cbr_part)
        dynamic_a.append(a_n)

    sample["a_n"] = dynamic_a
    sample["factor_dynamic"] = dynamic_vals

    # Synthetic realized friction proxy for scenario evaluation
    sample["factor_proxy_realized"] = (
        0.06
        + 0.14 * sample["L_ratio_lag1"]
        + 0.26 * sample["M_ratio_lag2"]
        + 0.20 * sample["E_ratio_lag2"]
        + 0.23 * sample["EXR_ratio_lag3"]
        + 0.11 * sample["CBR_ratio_lag4"]
    )

    # Cashflow envelope (hypothetical S-curve monthly certificate base)
    n = len(sample)
    x = np.arange(1, n + 1)
    w = np.exp(-((x - (n / 2)) ** 2) / (2 * (n / 5.2) ** 2))
    w = w / w.sum()
    contract_sum = 100_000_000.0  # UGX nominal placeholder
    sample["base_certificate_ugx"] = contract_sum * w

    sample["cert_fidic_ugx"] = sample["base_certificate_ugx"] * sample["factor_fidic"]
    sample["cert_dynamic_ugx"] = sample["base_certificate_ugx"] * sample["factor_dynamic"]
    sample["cert_proxy_realized_ugx"] = sample["base_certificate_ugx"] * sample["factor_proxy_realized"]

    sample = sample.reset_index(drop=True)

    metrics = {
        "project_window": {"start": str(sample["date"].min().date()), "end": str(sample["date"].max().date()), "months": int(len(sample))},
        "factor_tracking": {
            "fidic_mae": mae(sample["factor_fidic"], sample["factor_proxy_realized"]),
            "dynamic_mae": mae(sample["factor_dynamic"], sample["factor_proxy_realized"]),
            "fidic_rmse": rmse(sample["factor_fidic"], sample["factor_proxy_realized"]),
            "dynamic_rmse": rmse(sample["factor_dynamic"], sample["factor_proxy_realized"]),
            "fidic_mape_pct": mape(sample["factor_fidic"], sample["factor_proxy_realized"]),
            "dynamic_mape_pct": mape(sample["factor_dynamic"], sample["factor_proxy_realized"]),
        },
        "certificate_tracking_ugx": {
            "fidic_mae": mae(sample["cert_fidic_ugx"], sample["cert_proxy_realized_ugx"]),
            "dynamic_mae": mae(sample["cert_dynamic_ugx"], sample["cert_proxy_realized_ugx"]),
            "fidic_rmse": rmse(sample["cert_fidic_ugx"], sample["cert_proxy_realized_ugx"]),
            "dynamic_rmse": rmse(sample["cert_dynamic_ugx"], sample["cert_proxy_realized_ugx"]),
        },
        "cumulative_gap_ugx": {
            "fidic_minus_proxy": float((sample["cert_fidic_ugx"] - sample["cert_proxy_realized_ugx"]).sum()),
            "dynamic_minus_proxy": float((sample["cert_dynamic_ugx"] - sample["cert_proxy_realized_ugx"]).sum()),
        },
    }

    # Save tables
    keep_cols = [
        "date",
        "month_no",
        "phase",
        "regime",
        "factor_fidic",
        "factor_dynamic",
        "factor_proxy_realized",
        "base_certificate_ugx",
        "cert_fidic_ugx",
        "cert_dynamic_ugx",
        "cert_proxy_realized_ugx",
    ]
    sample[keep_cols].to_csv(RESULTS / "hypothetical_4y_monthly_simulation.csv", index=False)

    with open(RESULTS / "hypothetical_4y_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    # Helper for regime shading
    regime_colors = {"Stable": "#d9f2d9", "Transition": "#fff3cd", "Stress": "#f8d7da"}
    regime_segments = []
    seg_start = 0
    for i in range(1, len(sample)):
        if sample.loc[i, "regime"] != sample.loc[i - 1, "regime"]:
            regime_segments.append((seg_start, i - 1, sample.loc[i - 1, "regime"]))
            seg_start = i
    regime_segments.append((seg_start, len(sample) - 1, sample.loc[len(sample) - 1, "regime"]))

    # 0) Conceptual framework figure (for reviewer orientation)
    fig, ax = plt.subplots(figsize=(14, 6.6))
    ax.axis("off")
    ax.set_title("Conceptual Framework of Macroeconomic Shock Transmission in Import-Dependent Construction Markets", fontsize=15, weight="bold", pad=16)

    boxes = [
        (0.04, 0.68, 0.20, 0.20, "External Macro Shock\n(USD/UGX depreciation\nor CBR hike)\nMonth n", "#fde2e4"),
        (0.29, 0.68, 0.20, 0.20, "Importer Repricing\n& FX Adjustment\nMonth n+1", "#fff3cd"),
        (0.54, 0.68, 0.20, 0.20, "Bulk Procurement\n& Inventory Pass-through\nMonth n+2 to n+4", "#e2f0d9"),
        (0.79, 0.68, 0.18, 0.20, "Subcontract Pricing\n& Certificate Effects\nMonth n+3 to n+8", "#d1ecf1"),
    ]
    for x, y, w, h, txt, color in boxes:
        ax.add_patch(plt.Rectangle((x, y), w, h, facecolor=color, edgecolor="#666", linewidth=1.5))
        ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=10)

    for i in range(3):
        x0 = boxes[i][0] + boxes[i][2]
        y0 = boxes[i][1] + boxes[i][3] / 2
        x1 = boxes[i + 1][0]
        y1 = boxes[i + 1][1] + boxes[i + 1][3] / 2
        ax.annotate("", xy=(x1 - 0.01, y1), xytext=(x0 + 0.01, y0), arrowprops=dict(arrowstyle="->", lw=2, color="#444"))

    # Static vs dynamic timing strip
    ax.add_patch(plt.Rectangle((0.06, 0.33), 0.40, 0.18, facecolor="#f8d7da", edgecolor="#8b1d2c", linewidth=1.5))
    ax.text(0.26, 0.42, "Static FIDIC Logic\nApplies adjustment at Month n\n(assumes contemporaneous pass-through)", ha="center", va="center", fontsize=10)

    ax.add_patch(plt.Rectangle((0.54, 0.33), 0.40, 0.18, facecolor="#d4edda", edgecolor="#1e7e34", linewidth=1.5))
    ax.text(0.74, 0.42, "Dynamic Lag-Adjusted Logic\nUses memory terms n-1...n-k\n(aligned with delayed transmission)", ha="center", va="center", fontsize=10)

    ax.annotate("", xy=(0.54, 0.42), xytext=(0.46, 0.42), arrowprops=dict(arrowstyle="->", lw=2, color="#444"))
    ax.text(0.50, 0.46, "Model shift", ha="center", va="bottom", fontsize=10)

    ax.text(
        0.5,
        0.14,
        "Interpretation: site-level construction cost pressure emerges after supply-chain and contracting delays,\n"
        "therefore escalation formulas with lag memory better reflect realized monthly friction than same-month mapping.",
        ha="center",
        va="center",
        fontsize=10,
    )
    plt.tight_layout()
    plt.savefig(FIG / "conceptual_macro_shock_transmission_framework.png", dpi=240)
    plt.close(fig)

    # Figures
    fig, ax = plt.subplots(figsize=(14, 6.5))
    for s0, s1, reg in regime_segments:
        ax.axvspan(sample.loc[s0, "date"], sample.loc[s1, "date"], color=regime_colors[reg], alpha=0.35, zorder=0)

    ax.plot(sample["date"], sample["factor_proxy_realized"], lw=2.6, color="#1f77b4", label="Realized friction proxy")
    ax.plot(sample["date"], sample["factor_fidic"], lw=2.0, color="#d62728", label="Static FIDIC")
    ax.plot(sample["date"], sample["factor_dynamic"], lw=2.2, color="#2ca02c", label="Dynamic lag-adjusted")
    ax.set_title("Monthly Factor Tracking with Regime Shading (48-Month Hypothetical Project)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Escalation factor")
    ax.legend(loc="upper left")

    # annotate stress episode midpoint
    stress_rows = sample[sample["regime"] == "Stress"]
    if len(stress_rows) > 0:
        mid_idx = stress_rows.index[len(stress_rows) // 2]
        ax.annotate(
            "Stress regime:\nstatic misalignment widens",
            xy=(sample.loc[mid_idx, "date"], sample.loc[mid_idx, "factor_fidic"]),
            xytext=(sample.loc[mid_idx, "date"], sample["factor_proxy_realized"].max() * 0.92),
            arrowprops=dict(arrowstyle="->", lw=1.4, color="#555"),
            fontsize=9,
            ha="center",
        )

    # regime legend swatches
    ax.text(0.995, 0.02, "Green=Stable  Yellow=Transition  Red=Stress", transform=ax.transAxes, ha="right", va="bottom", fontsize=9, color="#444")
    plt.tight_layout()
    plt.savefig(FIG / "fidic_vs_dynamic_factor_tracking.png", dpi=240)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(14, 6.5))
    for s0, s1, reg in regime_segments:
        ax.axvspan(sample.loc[s0, "date"], sample.loc[s1, "date"], color=regime_colors[reg], alpha=0.32, zorder=0)

    fidic_cum = (sample["cert_fidic_ugx"] - sample["cert_proxy_realized_ugx"]).cumsum()
    dyn_cum = (sample["cert_dynamic_ugx"] - sample["cert_proxy_realized_ugx"]).cumsum()
    ax.plot(sample["date"], fidic_cum, lw=2.4, color="#d62728", label="Static FIDIC cumulative gap")
    ax.plot(sample["date"], dyn_cum, lw=2.4, color="#2ca02c", label="Dynamic cumulative gap")
    ax.axhline(0, color="black", lw=1)
    ax.set_title("Business-Case Plot: Cumulative Compensation Error (UGX)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Cumulative gap vs realized proxy (UGX)")
    ax.legend(loc="lower left")

    ax.annotate(
        f"FIDIC end gap: {fidic_cum.iloc[-1]:,.0f} UGX",
        xy=(sample["date"].iloc[-1], fidic_cum.iloc[-1]),
        xytext=(sample["date"].iloc[-8], fidic_cum.iloc[-1] * 0.78),
        arrowprops=dict(arrowstyle="->", lw=1.3, color="#d62728"),
        fontsize=9,
        color="#d62728",
    )
    ax.annotate(
        f"Dynamic end gap: {dyn_cum.iloc[-1]:,.0f} UGX",
        xy=(sample["date"].iloc[-1], dyn_cum.iloc[-1]),
        xytext=(sample["date"].iloc[-12], dyn_cum.iloc[-1] * 0.65),
        arrowprops=dict(arrowstyle="->", lw=1.3, color="#2ca02c"),
        fontsize=9,
        color="#2ca02c",
    )

    ax.text(0.995, 0.02, "Shading marks market regimes; steep red-period divergence indicates contract risk under static indexing.", transform=ax.transAxes, ha="right", va="bottom", fontsize=9, color="#444")
    plt.tight_layout()
    plt.savefig(FIG / "fidic_vs_dynamic_cumulative_gap.png", dpi=240)
    plt.close(fig)

    # phase x regime counts heatmap
    hm = sample.pivot_table(index="phase", columns="regime", values="month_no", aggfunc="count", fill_value=0)
    plt.figure(figsize=(8, 4.8))
    sns.heatmap(hm, annot=True, fmt=".0f", cmap="Blues")
    plt.title("Distribution of Regimes by Project Phase (Hypothetical 4-Year Run)")
    plt.tight_layout()
    plt.savefig(FIG / "phase_regime_heatmap.png", dpi=220)
    plt.close()

    # concise markdown report
    md = []
    md.append("# Hypothetical 4-Year Pipeline Run: FIDIC vs Dynamic Lag-Adjusted Model\n")
    md.append(f"- Timeline: **{metrics['project_window']['start']} to {metrics['project_window']['end']}**")
    md.append(f"- Effective months (after lag initialization): **{metrics['project_window']['months']}**\n")

    md.append("## Tracking Accuracy (Factor-Level)\n")
    md.append(f"- FIDIC MAE: **{metrics['factor_tracking']['fidic_mae']:.4f}**")
    md.append(f"- Dynamic MAE: **{metrics['factor_tracking']['dynamic_mae']:.4f}**")
    md.append(f"- FIDIC RMSE: **{metrics['factor_tracking']['fidic_rmse']:.4f}**")
    md.append(f"- Dynamic RMSE: **{metrics['factor_tracking']['dynamic_rmse']:.4f}**")
    md.append(f"- FIDIC MAPE: **{metrics['factor_tracking']['fidic_mape_pct']:.2f}%**")
    md.append(f"- Dynamic MAPE: **{metrics['factor_tracking']['dynamic_mape_pct']:.2f}%**\n")

    md.append("## Tracking Accuracy (Certificate UGX)\n")
    md.append(f"- FIDIC MAE: **{metrics['certificate_tracking_ugx']['fidic_mae']:.2f} UGX**")
    md.append(f"- Dynamic MAE: **{metrics['certificate_tracking_ugx']['dynamic_mae']:.2f} UGX**")
    md.append(f"- FIDIC RMSE: **{metrics['certificate_tracking_ugx']['fidic_rmse']:.2f} UGX**")
    md.append(f"- Dynamic RMSE: **{metrics['certificate_tracking_ugx']['dynamic_rmse']:.2f} UGX**\n")

    md.append("## Cumulative Gap vs Realized Proxy\n")
    md.append(f"- FIDIC cumulative gap: **{metrics['cumulative_gap_ugx']['fidic_minus_proxy']:.2f} UGX**")
    md.append(f"- Dynamic cumulative gap: **{metrics['cumulative_gap_ugx']['dynamic_minus_proxy']:.2f} UGX**\n")

    md.append("## Figures\n")
    md.append("- [analysis_output/fidic_clause_reform_phd/results/figures/conceptual_macro_shock_transmission_framework.png](analysis_output/fidic_clause_reform_phd/results/figures/conceptual_macro_shock_transmission_framework.png)")
    md.append("- [analysis_output/fidic_clause_reform_phd/results/figures/fidic_vs_dynamic_factor_tracking.png](analysis_output/fidic_clause_reform_phd/results/figures/fidic_vs_dynamic_factor_tracking.png)")
    md.append("- [analysis_output/fidic_clause_reform_phd/results/figures/fidic_vs_dynamic_cumulative_gap.png](analysis_output/fidic_clause_reform_phd/results/figures/fidic_vs_dynamic_cumulative_gap.png)")
    md.append("- [analysis_output/fidic_clause_reform_phd/results/figures/phase_regime_heatmap.png](analysis_output/fidic_clause_reform_phd/results/figures/phase_regime_heatmap.png)\n")

    md.append("## Notes\n")
    md.append("This is a policy simulation pipeline for methodological comparison. The realized proxy is synthetic and designed to emulate lagged friction for side-by-side performance testing under a controlled hypothetical project timeline.")

    (RESULTS / "hypothetical_4y_run_report.md").write_text("\n".join(md), encoding="utf-8")

    print("Pipeline run complete. Outputs:")
    print("-", RESULTS / "hypothetical_4y_monthly_simulation.csv")
    print("-", RESULTS / "hypothetical_4y_metrics.json")
    print("-", RESULTS / "hypothetical_4y_run_report.md")
    print("-", FIG / "conceptual_macro_shock_transmission_framework.png")
    print("-", FIG / "fidic_vs_dynamic_factor_tracking.png")
    print("-", FIG / "fidic_vs_dynamic_cumulative_gap.png")
    print("-", FIG / "phase_regime_heatmap.png")


if __name__ == "__main__":
    build_pipeline()
