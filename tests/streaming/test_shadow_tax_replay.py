from pathlib import Path

def test_stream_declares_watermark_dedup_and_tenant_scope():
    text=(Path(__file__).resolve().parents[2]/'data/databricks/src/gold_shadow_tax.py').read_text()
    assert 'withWatermark' in text and 'dropDuplicatesWithinWatermark' in text
    assert 'tenant_id' in text and 'company_tax_id' in text

def test_stream_never_silently_claims_transport_exactly_once():
    text=(Path(__file__).resolve().parents[2]/'data/databricks/src/gold_shadow_tax.py').read_text().lower()
    assert 'exactly-once' not in text
