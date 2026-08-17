from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[2]
def test_every_tax_rule_has_resolvable_official_source_metadata():
    catalog=yaml.safe_load((ROOT/'config/tax-rule-catalog.yaml').read_text())['catalog']
    for rule in catalog['rules']:
        assert rule['sources']
        for source in rule['sources']:
            assert source['source_url'].startswith('https://') and len(source['content_sha256'])==64 and source['provision']
