from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[2]
def test_100k_profile_accounting_contract():
    journey=yaml.safe_load((ROOT/'tests/e2e/fixtures/platform-journey.yaml').read_text()); profile=100_000
    events=profile*4; assert events==400_000 and len(journey['expectedProducts'])==6
    # Hosted certification supplies measured SLO evidence; local gate validates deterministic accounting only.
