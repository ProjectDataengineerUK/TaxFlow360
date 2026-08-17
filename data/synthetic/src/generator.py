import argparse
import random
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from uuid import UUID, uuid5

PROFILES = {"small": 100_000, "medium": 10_000_000, "enterprise": 100_000_000}
NAMESPACE = UUID("1bb2e506-8298-4bce-9ef2-cb18df892bbb")


@dataclass(frozen=True, slots=True)
class SyntheticTransaction:
    event_id: str
    tax_transaction_id: str
    tenant_id: str
    company_tax_id: str
    source_system: str
    source_event_id: str
    occurred_at: str
    operation_amount: str
    correlation_id: str
    ingested_at: str
    document_type: str = "NFE"
    document_key: str | None = None
    currency: str = "BRL"
    schema_version: str = "1.0.0"


def transactions(count: int, *, seed: int = 360, tenants: int = 10) -> Iterator[SyntheticTransaction]:
    if count < 0 or tenants < 1:
        raise ValueError("count must be non-negative and tenants must be positive")
    randomizer = random.Random(seed)
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    tenant_ids = tuple(str(uuid5(NAMESPACE, f"tenant:{number}")) for number in range(tenants))
    deterministic_prefix = (seed & ((1 << 32) - 1)) << 96
    for index in range(count):
        source_event_id = f"synthetic-{seed}-{index}"
        occurred_at = start + timedelta(seconds=index % 31_536_000)
        yield SyntheticTransaction(
            event_id=str(UUID(int=deterministic_prefix | index)),
            tax_transaction_id=f"TX-{index:012d}", tenant_id=tenant_ids[index % tenants],
            company_tax_id=f"{10_000_000_000_000 + index % 90_000_000_000_000:014d}",
            source_system="synthetic-generator", source_event_id=source_event_id,
            occurred_at=occurred_at.isoformat(),
            operation_amount=str(Decimal(randomizer.randrange(100, 10_000_000)) / Decimal(100)),
            correlation_id=str(UUID(int=deterministic_prefix | (1 << 95) | index)),
            ingested_at=(occurred_at + timedelta(seconds=1)).isoformat(),
            document_key=f"{index:044d}",
        )


def write_csv(destination: Path, count: int, *, seed: int, tenants: int) -> None:
    if count < 0 or tenants < 1:
        raise ValueError("count must be non-negative and tenants must be positive")
    destination.parent.mkdir(parents=True, exist_ok=True)
    fields = list(SyntheticTransaction.__dataclass_fields__)
    randomizer = random.Random(seed)
    tenant_ids = tuple(str(uuid5(NAMESPACE, f"tenant:{number}")) for number in range(tenants))
    prefix = seed & ((1 << 32) - 1)
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    timestamps = tuple((start + timedelta(seconds=second)).isoformat() for second in range(min(count, 86_400)))
    with destination.open("w", encoding="utf-8", newline="", buffering=1024 * 1024) as output:
        output.write(",".join(fields) + "\n")
        batch: list[str] = []
        for index in range(count):
            event = f"{prefix:08x}-0000-0000-0000-{index:012x}"
            correlation = f"{prefix:08x}-8000-0000-0000-{index:012x}"
            cents = randomizer.randrange(100, 10_000_000)
            occurred = timestamps[index % len(timestamps)]
            row = (event, f"TX-{index:012d}", tenant_ids[index % tenants],
                   f"{10_000_000_000_000 + index % 90_000_000_000_000:014d}", "synthetic-generator",
                   f"synthetic-{seed}-{index}", occurred, f"{cents // 100}.{cents % 100:02d}",
                   correlation, occurred, "NFE", f"{index:044d}", "BRL", "1.0.0")
            batch.append(",".join(row) + "\n")
            if len(batch) == 10_000:
                output.writelines(batch)
                batch.clear()
        output.writelines(batch)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic canonical TaxFlow CSV data")
    parser.add_argument("--profile", choices=PROFILES, default="small")
    parser.add_argument("--count", type=int, help="Override the selected profile for local verification")
    parser.add_argument("--seed", type=int, default=360)
    parser.add_argument("--tenants", type=int, default=10)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    count = args.count if args.count is not None else PROFILES[args.profile]
    write_csv(args.output, count, seed=args.seed, tenants=args.tenants)


if __name__ == "__main__":
    main()
