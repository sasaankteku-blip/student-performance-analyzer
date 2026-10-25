"""Data visualization module for student performance analysis."""

from pathlib import Path
import matplotlib
matplotlib.use("Agg")  # Non-interactive headless backend
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from .analyzer import CourseAnalysis


def plot_grade_distributions(
    math_df: pd.DataFrame,
    por_df: pd.DataFrame,
    math_threshold: float,
    output_path: Path
) -> Path:
    """Plot side-by-side G3 score distributions with the pass threshold benchmark."""
    plt.figure(figsize=(12, 5))

    # Math subplot
    plt.subplot(1, 2, 1)
    sns.histplot(math_df["G3"], bins=range(0, 22), kde=True, color="#1f77b4", edgecolor="black")
    plt.axvline(
        math_threshold,
        color="#d62728",
        linestyle="--",
        linewidth=2,
        label=f"Pass Threshold ({math_threshold:.1f}/20)",
    )
    plt.title("Mathematics: Final Grade (G3) Distribution", fontsize=12)
    plt.xlabel("Final Grade (0–20 Scale)", fontsize=10)
    plt.ylabel("Number of Students", fontsize=10)
    plt.xlim(-0.5, 20.5)
    plt.grid(axis="y", linestyle=":", alpha=0.6)
    plt.legend(loc="upper right")

    # Por subplot
    plt.subplot(1, 2, 2)
    sns.histplot(por_df["G3"], bins=range(0, 22), kde=True, color="#2ca02c", edgecolor="black")
    plt.axvline(
        math_threshold,
        color="#d62728",
        linestyle="--",
        linewidth=2,
        label=f"Pass Threshold ({math_threshold:.1f}/20)",
    )
    plt.title("Portuguese: Final Grade (G3) Distribution", fontsize=12)
    plt.xlabel("Final Grade (0–20 Scale)", fontsize=10)
    plt.ylabel("Number of Students", fontsize=10)
    plt.xlim(-0.5, 20.5)
    plt.grid(axis="y", linestyle=":", alpha=0.6)
    plt.legend(loc="upper right")

    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()
    return output_path


def plot_pass_rates(
    math_analysis: CourseAnalysis,
    por_analysis: CourseAnalysis,
    output_path: Path
) -> Path:
    """Plot bar chart comparing pass rates between courses."""
    plt.figure(figsize=(7, 5))

    courses = ["Mathematics", "Portuguese"]
    pass_rates = [math_analysis.pass_rate, por_analysis.pass_rate]
    colors = ["#1f77b4", "#2ca02c"]

    bars = plt.bar(courses, pass_rates, color=colors, width=0.45, edgecolor="black")
    plt.ylabel("Pass Rate (%)", fontsize=11)
    plt.ylim(0, 105)
    plt.title(
        f"Course Pass Rate Comparison (Threshold G3 >= {math_analysis.pass_threshold:.1f}/20)",
        fontsize=12,
    )
    plt.grid(axis="y", linestyle=":", alpha=0.6)

    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2.0,
            height + 2,
            f"{height:.1f}%",
            ha="center",
            va="bottom",
            fontweight="bold",
            fontsize=11,
        )

    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()
    return output_path


def plot_studytime_performance(
    math_analysis: CourseAnalysis,
    por_analysis: CourseAnalysis,
    output_path: Path
) -> Path:
    """Plot comparison of average G3 by ordinal studytime categories."""
    plt.figure(figsize=(9, 5))

    labels = [s.label for s in math_analysis.studytime_stats]
    math_means = [s.g3_mean for s in math_analysis.studytime_stats]
    por_means = [s.g3_mean for s in por_analysis.studytime_stats]

    x = np.arange(len(labels))
    width = 0.35

    plt.bar(
        x - width / 2,
        math_means,
        width,
        label="Mathematics (Mean G3)",
        color="#1f77b4",
        edgecolor="black",
    )
    plt.bar(
        x + width / 2,
        por_means,
        width,
        label="Portuguese (Mean G3)",
        color="#2ca02c",
        edgecolor="black",
    )

    plt.axhline(
        math_analysis.pass_threshold,
        color="#d62728",
        linestyle="--",
        label=f"Pass Threshold ({math_analysis.pass_threshold:.1f}/20)",
    )
    plt.xlabel("Weekly Study Time Category (Ordinal)", fontsize=11)
    plt.ylabel("Mean Final Grade (G3)", fontsize=11)
    plt.title("Academic Performance by Weekly Study Time Category", fontsize=12)
    plt.xticks(x, labels, fontsize=10)
    plt.ylim(0, 20)
    plt.grid(axis="y", linestyle=":", alpha=0.6)
    plt.legend(loc="lower right")

    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()
    return output_path


def plot_evaluation_period_progression(
    math_analysis: CourseAnalysis,
    por_analysis: CourseAnalysis,
    output_path: Path
) -> Path:
    """Plot grade progression across evaluation periods G1, G2, G3.

    Labels are explicitly separated above and below the respective series markers
    with high-contrast badges to guarantee zero visual overlap across all periods.
    """
    fig, ax = plt.subplots(figsize=(8, 5))

    periods = ["G1 (Period 1)", "G2 (Period 2)", "G3 (Final)"]
    math_scores = [
        math_analysis.g1_stats.mean,
        math_analysis.g2_stats.mean,
        math_analysis.g3_stats.mean,
    ]
    por_scores = [
        por_analysis.g1_stats.mean,
        por_analysis.g2_stats.mean,
        por_analysis.g3_stats.mean,
    ]

    ax.plot(
        periods,
        math_scores,
        marker="o",
        linewidth=2.5,
        color="#1f77b4",
        label="Mathematics Mean Grade",
    )
    ax.plot(
        periods,
        por_scores,
        marker="s",
        linewidth=2.5,
        color="#2ca02c",
        label="Portuguese Mean Grade",
    )
    ax.axhline(
        math_analysis.pass_threshold,
        color="#d62728",
        linestyle="--",
        label=f"Pass Threshold ({math_analysis.pass_threshold:.1f}/20)",
    )

    for i, (m, po) in enumerate(zip(math_scores, por_scores)):
        if po >= m:
            # Portuguese series is higher: place label above Portuguese marker
            ax.annotate(
                f"Por: {po:.2f}",
                (i, po),
                textcoords="offset points",
                xytext=(0, 9),
                ha="center",
                va="bottom",
                color="#2ca02c",
                fontweight="bold",
                fontsize=9,
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#2ca02c", alpha=0.9, lw=0.8),
            )
            # Mathematics series is lower: place label below Mathematics marker
            ax.annotate(
                f"Math: {m:.2f}",
                (i, m),
                textcoords="offset points",
                xytext=(0, -14),
                ha="center",
                va="top",
                color="#1f77b4",
                fontweight="bold",
                fontsize=9,
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#1f77b4", alpha=0.9, lw=0.8),
            )
        else:
            # Mathematics series is higher: place label above Mathematics marker
            ax.annotate(
                f"Math: {m:.2f}",
                (i, m),
                textcoords="offset points",
                xytext=(0, 9),
                ha="center",
                va="bottom",
                color="#1f77b4",
                fontweight="bold",
                fontsize=9,
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#1f77b4", alpha=0.9, lw=0.8),
            )
            # Portuguese series is lower: place label below Portuguese marker
            ax.annotate(
                f"Por: {po:.2f}",
                (i, po),
                textcoords="offset points",
                xytext=(0, -14),
                ha="center",
                va="top",
                color="#2ca02c",
                fontweight="bold",
                fontsize=9,
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#2ca02c", alpha=0.9, lw=0.8),
            )

    ax.set_ylabel("Mean Grade (0–20 Scale)", fontsize=11)
    ax.set_ylim(0, 20)
    ax.set_title("Grade Progression Across Evaluation Periods", fontsize=12)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="lower right")

    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()
    return output_path
