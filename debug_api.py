import panorama_client as api
import json

# List report queries
rq = api.get_report_queries()
print("=== REPORT QUERIES ===")
for q in rq:
    print(f"  {q['uid']} - {q['name']}")

# Pick the first query and get results for the first institution
print()
print("=== INSTITUTIONS ===")
institutions = api.get_institutions()
inst = institutions[0]
print(f"Using institution: {inst['name']} ({inst['uid']})")

print()
print("=== SAMPLE REPORT RESULTS (first query, last 30 days) ===")
first_uid = rq[0]["uid"]
print(f"Query: {rq[0]['name']}")
try:
    results = api.get_report_results(first_uid, institution=inst["uid"], period_days=30)
    print(type(results))
    print(json.dumps(results, indent=2, ensure_ascii=False)[:1000])
except Exception as e:
    print(f"ERROR: {e}")

print()
print("=== STUDENT QUERIES ===")
sq = api.get_student_queries()
for q in sq:
    print(f"  {q['uid']} - {q['name']}")

print()
print("=== SAMPLE STUDENT RESULTS (first student query) ===")
if sq:
    print(f"Query: {sq[0]['name']}")
    try:
        results = api.get_student_results(sq[0]["uid"], institution=inst["uid"], period_days=30)
        print(type(results))
        print(json.dumps(results, indent=2, ensure_ascii=False)[:1000])
    except Exception as e:
        print(f"ERROR: {e}")
