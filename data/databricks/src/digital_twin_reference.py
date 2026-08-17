from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_EVEN

MONEY = Decimal("0.01")


def money(value: Decimal) -> Decimal:
    return value.quantize(MONEY, rounding=ROUND_HALF_EVEN)


@dataclass(frozen=True, slots=True)
class CashMovement:
    projection_date: date
    inflow: Decimal
    outflow: Decimal
    tax_split_outflow: Decimal

    def __post_init__(self) -> None:
        if min(self.inflow, self.outflow, self.tax_split_outflow) < Decimal():
            raise ValueError("cash movements must be non-negative")


@dataclass(frozen=True, slots=True)
class DailyCash:
    projection_date: date
    opening_cash: Decimal
    inflow: Decimal
    outflow: Decimal
    tax_split_outflow: Decimal
    closing_cash: Decimal


@dataclass(frozen=True, slots=True)
class LiquidityIndicators:
    minimum_balance: Decimal
    maximum_working_capital_gap: Decimal
    days_below_minimum: int
    tax_float_delta: Decimal


@dataclass(frozen=True, slots=True)
class StressScenario:
    scenario_id: str
    revenue_factor: Decimal = Decimal("1")
    expense_factor: Decimal = Decimal("1")
    tax_split_factor: Decimal = Decimal("1")
    collection_delay_days: int = 0
    payable_acceleration_days: int = 0
    interest_rate_addition: Decimal = Decimal()

    def __post_init__(self) -> None:
        if not self.scenario_id or min(self.revenue_factor, self.expense_factor, self.tax_split_factor) < Decimal():
            raise ValueError("invalid stress scenario")
        if self.collection_delay_days < 0 or self.payable_acceleration_days < 0 or self.interest_rate_addition < Decimal():
            raise ValueError("stress timing and rates must be non-negative")


def project_day(day: date, opening: Decimal, inflow: Decimal,
                outflow: Decimal, tax_split: Decimal) -> DailyCash:
    values = tuple(map(money, (opening, inflow, outflow, tax_split)))
    if min(values[1:]) < Decimal():
        raise ValueError("cash movements must be non-negative")
    closing = money(values[0] + values[1] - values[2] - values[3])
    return DailyCash(day, *values, closing)


def project_ledger(opening_cash: Decimal, movements: tuple[CashMovement, ...]) -> tuple[DailyCash, ...]:
    ordered = tuple(sorted(movements, key=lambda item: item.projection_date))
    if len({item.projection_date for item in ordered}) != len(ordered):
        raise ValueError("one movement per projection date is required")
    ledger: list[DailyCash] = []
    opening = money(opening_cash)
    for movement in ordered:
        day = project_day(movement.projection_date, opening, movement.inflow,
                          movement.outflow, movement.tax_split_outflow)
        ledger.append(day)
        opening = day.closing_cash
    return tuple(ledger)


def liquidity_indicators(ledger: tuple[DailyCash, ...], minimum_cash: Decimal,
                         baseline_tax_split: Decimal = Decimal()) -> LiquidityIndicators:
    if not ledger:
        raise ValueError("ledger must not be empty")
    floor = money(minimum_cash)
    balances = tuple(item.closing_cash for item in ledger)
    gaps = tuple(max(Decimal(), floor - value) for value in balances)
    split_total = sum((item.tax_split_outflow for item in ledger), Decimal())
    return LiquidityIndicators(min(balances), max(gaps), sum(value < floor for value in balances),
                               money(split_total - baseline_tax_split))


def apply_stress(movements: tuple[CashMovement, ...], scenario: StressScenario) -> tuple[CashMovement, ...]:
    inflows = {item.projection_date: item.inflow for item in movements}
    outflows = {item.projection_date: item.outflow for item in movements}
    if scenario.collection_delay_days:
        inflows = {item.projection_date: Decimal() for item in movements}
        for index, movement in enumerate(movements):
            target = index + scenario.collection_delay_days
            if target < len(movements):
                inflows[movements[target].projection_date] += movement.inflow
    if scenario.payable_acceleration_days:
        outflows = {item.projection_date: Decimal() for item in movements}
        for index, movement in enumerate(movements):
            target = max(0, index - scenario.payable_acceleration_days)
            outflows[movements[target].projection_date] += movement.outflow
    return tuple(CashMovement(item.projection_date,
        money(inflows[item.projection_date] * scenario.revenue_factor),
        money(outflows[item.projection_date] * scenario.expense_factor * (Decimal("1") + scenario.interest_rate_addition)),
        money(item.tax_split_outflow * scenario.tax_split_factor)) for item in movements)


def run_stresses(opening_cash: Decimal, movements: tuple[CashMovement, ...],
                 scenarios: tuple[StressScenario, ...]) -> dict[str, tuple[DailyCash, ...]]:
    if len({scenario.scenario_id for scenario in scenarios}) != len(scenarios):
        raise ValueError("stress scenario IDs must be unique")
    return {scenario.scenario_id: project_ledger(opening_cash, apply_stress(movements, scenario))
            for scenario in scenarios}
