"""Strict, offline loader for immutable TaxFlow tax-rule snapshots."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, ROUND_HALF_EVEN
from hashlib import sha256
from pathlib import Path
import re
from urllib.parse import urlsplit

import yaml

_SHA256 = re.compile(r"^[a-f0-9]{64}$")


@dataclass(frozen=True)
class LegalSource:
    source_id: str
    source_url: str
    authority: str
    document_id: str
    provision: str
    content_sha256: str


@dataclass(frozen=True)
class TaxRule:
    rule_id: str
    component: str
    scenario: str
    rate: Decimal
    priority: int
    valid_from: datetime
    valid_until: datetime | None
    sources: tuple[LegalSource, ...]


@dataclass(frozen=True)
class RuleCatalog:
    version: str
    checksum: str
    scale: int
    rules: tuple[TaxRule, ...]

    def select(self, scenario: str, effective_at: datetime) -> tuple[TaxRule, ...]:
        selected = tuple(rule for rule in self.rules if rule.scenario == scenario and rule.valid_from <= effective_at
                         and (rule.valid_until is None or effective_at < rule.valid_until))
        components = {rule.component for rule in selected}
        if len(components) != len(selected) or not selected:
            raise ValueError("exactly one effective approved rule per component is required")
        return selected

    def calculate(self, amount: Decimal, scenario: str, effective_at: datetime) -> dict[str, Decimal]:
        quantum = Decimal(1).scaleb(-self.scale)
        return {rule.component: (amount * rule.rate).quantize(quantum, rounding=ROUND_HALF_EVEN)
                for rule in self.select(scenario, effective_at)}


def _instant(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value.replace("Z", "+00:00")) if value else None


def load_catalog(catalog_path: str, authorities_path: str) -> RuleCatalog:
    catalog_payload = Path(catalog_path).read_bytes()
    root = yaml.safe_load(catalog_payload.decode("utf-8"))["catalog"]
    policy = yaml.safe_load(Path(authorities_path).read_text(encoding="utf-8"))["source_policy"]
    if root.get("status") != "synthetic-approved" or not root.get("governance", {}).get("immutable"):
        raise ValueError("only immutable synthetic-approved snapshots are accepted in this wave")
    if root.get("rounding") != {"scale": 2, "mode": "HALF_EVEN"}:
        raise ValueError("catalog must declare scale 2 and HALF_EVEN")
    allowed_hosts = {host for authority in policy["authorities"] for host in authority["allowed_hosts"]}
    rules: list[TaxRule] = []
    for item in root.get("rules", []):
        if item.get("status") != "approved" or item.get("author_id") == item.get("approver_id"):
            raise ValueError(f"rule {item.get('id')} is not four-eyes approved")
        sources: list[LegalSource] = []
        for source in item.get("sources", []):
            parsed = urlsplit(source["source_url"])
            if parsed.scheme != "https" or parsed.hostname not in allowed_hosts or parsed.username or parsed.password or parsed.fragment:
                raise ValueError(f"rule {item['id']} contains a non-official source URL")
            if source.get("status") != "validated" or not _SHA256.fullmatch(source.get("content_sha256", "")):
                raise ValueError(f"rule {item['id']} contains an unvalidated source")
            sources.append(LegalSource(source["source_id"], source["source_url"], source["authority"],
                                       source["document_id"], source["provision"], source["content_sha256"]))
        if not sources:
            raise ValueError(f"rule {item['id']} must have an official source")
        rules.append(TaxRule(item["id"], item["component"], item["scenario"], Decimal(item["rate"]),
                             int(item["priority"]), _instant(item["valid_from"]), _instant(item.get("valid_until")), tuple(sources)))
    return RuleCatalog(root["version"], sha256(catalog_payload).hexdigest(), 2, tuple(rules))
