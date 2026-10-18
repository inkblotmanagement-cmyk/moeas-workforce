"""Money calculators with real math. Replaces the originals' fixed "$100 a month" payoff and
"7% annual return, mercy-aligned" text. Projections are arithmetic, not financial advice."""
from __future__ import annotations

import math


def debt_payoff(balance: float, apr_percent: float, monthly_payment: float, max_months: int = 1200) -> dict:
    """Months to pay off a balance with monthly compounding, and total interest paid."""
    if balance <= 0 or monthly_payment <= 0 or apr_percent < 0:
        raise ValueError("balance and payment must be positive; APR cannot be negative")
    r = apr_percent / 100 / 12
    if r and monthly_payment <= balance * r:
        return {"payoff_possible": False,
                "reason": f"payment must exceed the monthly interest of ${balance * r:.2f}"}
    months, interest, b = 0, 0.0, float(balance)
    while b > 0.005 and months < max_months:
        i = b * r
        interest += i
        b = b + i - min(monthly_payment, b + i)
        months += 1
    return {"payoff_possible": True, "months": months, "years": round(months / 12, 1),
            "total_interest": round(interest, 2), "total_paid": round(balance + interest, 2)}


def savings_projection(monthly_deposit: float, years: float, annual_return_percent: float,
                       start_balance: float = 0.0) -> dict:
    """Future value with monthly deposits and monthly compounding at a rate YOU choose."""
    if monthly_deposit < 0 or years <= 0 or start_balance < 0:
        raise ValueError("deposits/balance cannot be negative; years must be positive")
    n, r = int(round(years * 12)), annual_return_percent / 100 / 12
    fv = start_balance * (1 + r) ** n + (monthly_deposit * (((1 + r) ** n - 1) / r) if r else monthly_deposit * n)
    deposited = start_balance + monthly_deposit * n
    return {"future_value": round(fv, 2), "deposited": round(deposited, 2),
            "growth": round(fv - deposited, 2), "assumed_annual_return_percent": annual_return_percent,
            "note": "Illustration only. Returns are not guaranteed."} if math.isfinite(fv) else {"error": "overflow"}
