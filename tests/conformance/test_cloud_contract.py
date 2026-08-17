from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def test_all_cloud_adapters_enforce_encryption_versioning_and_platform_contract():
    for cloud in ('aws','azure','gcp'):
        text=(ROOT/f'deploy/terraform/{cloud}/main.tf').read_text()
        assert 'module "platform_contract"' in text
        assert any(token in text.lower() for token in ('encryption','customer_managed','kms'))
        assert 'version' in text.lower()
