import copy
import re
import unittest
from pathlib import Path
from urllib.parse import urlsplit

import yaml


ROOT = Path(__file__).resolve().parents[2]
AUTHORITIES = yaml.safe_load((ROOT / "config" / "official-source-authorities.yaml").read_text(encoding="utf-8"))["source_policy"]
CATALOG = yaml.safe_load((ROOT / "config" / "tax-rule-catalog.yaml").read_text(encoding="utf-8"))["catalog"]


def validate_source(source: dict) -> None:
    required = {"source_id", "source_url", "authority", "document_id", "provision", "publication_date", "captured_at", "content_sha256", "status"}
    if not required.issubset(source) or any(source[key] in (None, "") for key in required):
        raise ValueError("missing official source metadata")
    parsed = urlsplit(source["source_url"])
    if parsed.scheme != "https" or parsed.username or parsed.password or parsed.fragment:
        raise ValueError("unsafe official source URL")
    authority = next((item for item in AUTHORITIES["authorities"] if item["name"] == source["authority"]), None)
    if authority is None or parsed.hostname not in authority["allowed_hosts"]:
        raise ValueError("source is outside official authority allowlist")
    prefixes = authority.get("required_path_prefixes", [])
    if prefixes and not any(parsed.path.startswith(prefix) for prefix in prefixes):
        raise ValueError("source path is outside authority scope")
    if not re.fullmatch(AUTHORITIES["validation"]["content_hash_pattern"], source["content_sha256"]):
        raise ValueError("invalid source content hash")
    if source["status"] != "validated":
        raise ValueError("source is not validated")


def authorize_result(request_tenant: str, resource_tenant: str) -> None:
    if request_tenant != resource_tenant:
        raise LookupError("not found")


class OfficialSourceSecurityTests(unittest.TestCase):
    def test_catalog_sources_are_official_and_complete(self) -> None:
        for rule in CATALOG["rules"]:
            self.assertTrue(rule["sources"])
            for source in rule["sources"]:
                validate_source(source)

    def test_missing_source_is_rejected(self) -> None:
        source = copy.deepcopy(CATALOG["rules"][0]["sources"][0])
        source.pop("provision")
        with self.assertRaisesRegex(ValueError, "missing"):
            validate_source(source)

    def test_non_https_and_host_confusion_are_rejected(self) -> None:
        source = copy.deepcopy(CATALOG["rules"][0]["sources"][0])
        for malicious_url in (
            "http://www.planalto.gov.br/document",
            "https://www.planalto.gov.br.attacker.invalid/document",
            "https://www.planalto.gov.br@attacker.invalid/document",
        ):
            source["source_url"] = malicious_url
            with self.assertRaises(ValueError):
                validate_source(source)

    def test_invalid_hash_and_unvalidated_source_are_rejected(self) -> None:
        source = copy.deepcopy(CATALOG["rules"][0]["sources"][0])
        source["content_sha256"] = "not-a-sha256"
        with self.assertRaisesRegex(ValueError, "hash"):
            validate_source(source)
        source = copy.deepcopy(CATALOG["rules"][0]["sources"][0])
        source["status"] = "proposed"
        with self.assertRaisesRegex(ValueError, "not validated"):
            validate_source(source)

    def test_cross_tenant_lookup_is_non_disclosing(self) -> None:
        with self.assertRaisesRegex(LookupError, "not found"):
            authorize_result("tenant-a", "tenant-b")
        authorize_result("tenant-a", "tenant-a")

    def test_policy_forbids_live_fetch(self) -> None:
        self.assertFalse(AUTHORITIES["live_fetch_allowed"])
        self.assertTrue(AUTHORITIES["reject_user_supplied_urls"])
        self.assertFalse(AUTHORITIES["validation"]["redirects_followed"])


if __name__ == "__main__":
    unittest.main()
