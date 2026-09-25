import urllib.request
import json

BASE = "http://127.0.0.1:5000"

def post(endpoint, data):
    req = urllib.request.Request(
        f"{BASE}{endpoint}",
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

print("=== STARTING STEP 8 DEEP PERSONALIZATION TESTS ===")

# TEST 1: Intern in Design Department
print("\n--- TEST 1: Intern in Design (Priya, UI/UX Design Intern) ---")
res_intern = post("/api/generate-checklist", {
    "name": "Priya Patel",
    "department": "Design",
    "role": "UI/UX Designer",
    "joining_date": "2026-10-01",
    "location": "Remote",
    "experience": "Fresher",
    "employment_type": "Intern"
})
day1_titles = [t["title"] for t in res_intern["phases"]["day_1"]["tasks"]]
week1_titles = [t["title"] for t in res_intern["phases"]["week_1"]["tasks"]]
day90_titles = [t["title"] for t in res_intern["phases"]["day_90"]["tasks"]]

print(f"[PASS] Intern Created ID: {res_intern['employee_id']}, Total Tasks: {res_intern['total_tasks']}")
assert any("Intern Mentor" in t for t in day1_titles), "Missing intern mentor in Day 1"
assert any("Capstone Project" in t for t in week1_titles), "Missing capstone in Week 1"
assert any("Figma" in t for t in day1_titles), "Missing Figma in Design Day 1"
assert any("Intern Capstone Presentation" in t for t in day90_titles), "Missing final intern evaluation in Day 90"
print("[PASS] Intern & Design-specific tasks verified!")

# TEST 2: Contractor in Sales Department
print("\n--- TEST 2: Contractor in Sales (David, Sales Specialist) ---")
res_contract = post("/api/generate-checklist", {
    "name": "David Miller",
    "department": "Sales",
    "role": "Account Executive",
    "joining_date": "2026-10-15",
    "location": "Hybrid",
    "experience": "3-5 years",
    "employment_type": "Contract"
})
c_day1 = [t["title"] for t in res_contract["phases"]["day_1"]["tasks"]]
c_week1 = [t["title"] for t in res_contract["phases"]["week_1"]["tasks"]]
c_day30 = [t["title"] for t in res_contract["phases"]["day_30"]["tasks"]]

print(f"[PASS] Contractor Created ID: {res_contract['employee_id']}, Total Tasks: {res_contract['total_tasks']}")
assert any("Statement of Work (SOW)" in t for t in c_day1), "Missing SOW in Contract Day 1"
assert any("vendor time-tracking" in t for t in c_week1), "Missing invoicing setup in Contract Week 1"
assert any("CRM (Salesforce/HubSpot)" in t for t in c_day1), "Missing CRM in Sales Day 1"
assert any("Contract Milestone 1" in t for t in c_day30), "Missing Milestone review in Contract 30 Days"
print("[PASS] Contractor & Sales-specific tasks verified!")

# TEST 3: Full-time Senior in Finance
print("\n--- TEST 3: Full-time Senior in Finance (Meera, Finance Lead) ---")
res_finance = post("/api/generate-checklist", {
    "name": "Meera Joshi",
    "department": "Finance",
    "role": "Financial Analyst",
    "joining_date": "2026-11-01",
    "location": "On-site",
    "experience": "5+ years",
    "employment_type": "Full-time"
})
f_day1 = [t["title"] for t in res_finance["phases"]["day_1"]["tasks"]]
f_week1 = [t["title"] for t in res_finance["phases"]["week_1"]["tasks"]]

print(f"[PASS] Finance Senior Created ID: {res_finance['employee_id']}, Total Tasks: {res_finance['total_tasks']}")
assert any("ERP & secure financial accounting" in t for t in f_day1), "Missing ERP in Finance Day 1"
assert any("benefits, health insurance" in t for t in f_day1), "Missing benefits in Full-time Day 1"
assert any("cross-functional alignment chats" in t for t in f_week1), "Missing senior alignment in 5+ yrs"
print("[PASS] Full-time & Senior Finance tasks verified!")

print("\n*** ALL STEP 8 PERSONALIZATION TESTS PASSED WITH 100% SUCCESS! ***")
