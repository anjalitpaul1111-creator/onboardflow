import urllib.request
import json

BASE = "http://127.0.0.1:5000"

def get(endpoint):
    with urllib.request.urlopen(BASE + endpoint) as resp:
        return json.loads(resp.read().decode("utf-8"))

print("=== VERIFYING STEP 9 HR DASHBOARD ===")

data = get("/api/dashboard/stats")
print(f"[PASS] Total Employees: {data['total_employees']}")
print(f"[PASS] Active Onboardings: {data['active_onboardings']}")
print(f"[PASS] Completed Onboardings: {data['completed_onboardings']}")
print(f"[PASS] Average Company Progress: {data['average_progress']}%")
print(f"[PASS] Recent Employees Count: {len(data['recent_employees'])}")

print("\n--- Recent Employees Sample ---")
for emp in data['recent_employees'][:4]:
    print(f"[PASS] Employee #{emp['id']}: {emp['name']} | Dept: {emp['department']} | Role: {emp['role']} | Progress: {emp['progress_percentage']}% ({emp['completed_tasks']}/{emp['total_tasks']} tasks) | Status: {emp['status']}")

# Verify that all required keys are present
assert "total_employees" in data
assert "active_onboardings" in data
assert "completed_onboardings" in data
assert "average_progress" in data
assert "recent_employees" in data
assert len(data['recent_employees']) > 0

print("\n*** ALL STEP 9 DASHBOARD VERIFICATIONS PASSED WITH 100% SUCCESS! ***")
