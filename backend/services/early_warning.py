"""Module 10 — Early Warning System.

Detects persistently worsening trends in a quarterly indicator series using
linear regression on the available history, and — only when the trend is
statistically consistent (R^2 above a minimum threshold) — projects how many
periods remain before a high-risk threshold is crossed.

Never invents a projection from insufficient or noisy history.
"""
from dataclasses import dataclass
import numpy as np

MIN_QUARTERS_FOR_TREND = 3
MIN_R2_FOR_PROJECTION = 0.5


@dataclass
class EarlyWarning:
    direction: str  # worsening / improving / stable / insufficient_data
    slope_per_quarter: float
    r_squared: float
    message: str
    periods_to_threshold: int | None = None


def _linreg(y: list[float]):
    x = np.arange(len(y), dtype=float)
    if len(y) < 2 or np.allclose(y, y[0]):
        return 0.0, 0.0
    slope, intercept = np.polyfit(x, y, 1)
    pred = slope * x + intercept
    ss_res = np.sum((np.array(y) - pred) ** 2)
    ss_tot = np.sum((np.array(y) - np.mean(y)) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return float(slope), float(max(r2, 0.0))


def analyze_trend(
    values: list[float],
    indicator_label: str,
    higher_is_worse: bool = True,
    threshold: float = 70.0,
) -> EarlyWarning:
    if len(values) < MIN_QUARTERS_FOR_TREND:
        return EarlyWarning(
            direction="insufficient_data", slope_per_quarter=0.0, r_squared=0.0,
            message="Insufficient historical data for reliable trend detection.",
        )

    slope, r2 = _linreg(values)
    effective_slope = slope if higher_is_worse else -slope

    if r2 < MIN_R2_FOR_PROJECTION or abs(effective_slope) < 0.5:
        direction = "stable"
        message = f"{indicator_label} has not shown a statistically consistent trend over the available history."
        return EarlyWarning(direction=direction, slope_per_quarter=round(slope, 2), r_squared=round(r2, 2), message=message)

    if effective_slope > 0:
        direction = "worsening"
        message = f"{indicator_label} is showing a persistent worsening trend over the last {len(values)} quarters."
        periods = None
        last_value = values[-1]
        if effective_slope > 0:
            remaining = threshold - (last_value if higher_is_worse else -last_value)
            if effective_slope > 0 and remaining > 0:
                periods = int(np.ceil(remaining / effective_slope))
                if periods <= 12:
                    message += f" Projected to cross the high-risk threshold in approximately {periods} quarter(s) if the trend continues."
                else:
                    periods = None
        return EarlyWarning(direction=direction, slope_per_quarter=round(slope, 2), r_squared=round(r2, 2),
                             message=message, periods_to_threshold=periods)
    else:
        direction = "improving"
        message = f"{indicator_label} is showing a persistent improving trend over the last {len(values)} quarters."
        return EarlyWarning(direction=direction, slope_per_quarter=round(slope, 2), r_squared=round(r2, 2), message=message)
