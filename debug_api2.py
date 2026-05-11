import panorama_client as api
import json

institutions = api.get_institutions()
inst = institutions[0]
inst_uid = inst["uid"]

# Queries of interest for the success criteria
targets = {
    "Distribuicao de Desempenho": "e21e22ab-6da4-4808-ad51-ca6b470703c9",
    "Participacao Media": "592d91e2-843b-444a-ab0b-f8b56690ed53",
    "Performance media por simulado": "e0fa07e2-c614-4b59-880d-aaf132b664fb",
    "Media Geral": "100e49fc-8041-4cdc-ae03-7d47acff9470",
    "Alunos Matriculados": "fbe59dab-e999-4d63-885d-d0bb6031bdcd",
    "Adesao a plataforma": "b3ca3fd1-be26-4207-81ef-3adaf381a564",
}

for name, uid in targets.items():
    print(f"\n=== {name} ===")
    try:
        results = api.get_report_results(uid, institution=inst_uid, period_days=30)
        print(json.dumps(results, indent=2, ensure_ascii=False)[:800])
    except Exception as e:
        print(f"ERROR: {e}")
