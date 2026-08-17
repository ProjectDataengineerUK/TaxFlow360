from pathlib import Path
import json,yaml
ROOT=Path(__file__).resolve().parents[2]
def test_all_contracts_and_openapi_references_resolve():
    for path in (ROOT/'contracts').rglob('*.yaml'):yaml.safe_load(path.read_text(encoding='utf-8'))
    for path in (ROOT/'contracts').rglob('*.avsc'):json.loads(path.read_text(encoding='utf-8'))
    api=yaml.safe_load((ROOT/'contracts/api/openapi.yaml').read_text(encoding='utf-8')); refs=[]
    def walk(value):
        if isinstance(value,dict):
            for key,item in value.items():
                if key=='$ref' and item.startswith('#/components/'):refs.append(item)
                walk(item)
        elif isinstance(value,list):
            for item in value:walk(item)
    walk(api)
    for ref in refs:
        node=api
        for part in ref[2:].split('/'):node=node[part]
    assert refs
