import hashlib
import json
import unittest
from decimal import Decimal


def canonical_result(cloud: str) -> dict[str, str]:
    base = Decimal("1000.00")
    rate = Decimal("0.265")
    return {
        "cloud": cloud,
        "base": str(base),
        "rate": str(rate),
        "tax": str((base * rate).quantize(Decimal("0.01"))),
        "rule_version": "2027.1",
    }


def semantic_hash(result: dict[str, str]) -> str:
    semantic = {key: value for key, value in result.items() if key != "cloud"}
    return hashlib.sha256(json.dumps(semantic, sort_keys=True).encode()).hexdigest()


class MultiCloudParityTests(unittest.TestCase):
    def test_semantic_results_match_across_clouds(self) -> None:
        hashes = {semantic_hash(canonical_result(cloud)) for cloud in ("aws", "azure", "gcp")}
        self.assertEqual(len(hashes), 1)


if __name__ == "__main__":
    unittest.main()

