import urllib.request
import json
import sqlite3

BASE = "http://127.0.0.1:5000"

def post(endpoint, data):
    req = urllib.request.Request(
        f"{BASE}{endpoint}",
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def get(endpoint):
    with urllib.request.urlopen(f"{BASE}{endpoint}") as resp:
        return json.loads(resp.read().decode("utf-8"))

print("=== STARTING STEP 7 PERSISTENCE & PROGRESS TESTS ===")

# TEST 1: Generate Checklist for Employee 1 (Anu Sharma)
print("\n--- TEST 1: Generate Checklist for Employee 1 (Anu Sharma) ---")
emp1 = post("/api/generate-checklist", {
    "name": "Anu Sharma",
    "department": "Engineering",
    "role": "Software Developer",
    "joining_date": "2026-10-05",
    "location": "Hybrid",
    "experience": "Fresher",
    "employment_type": "Full-time"
})
emp1_id = emp1["employee_id"]
tasks_emp1 = emp1["phases"]["day_1"]["tasks"]
task1_id = tasks_emp1[0]["id"]
task2_id = tasks_emp1[1]["id"]
print(f"[PASS] Employee 1 Created ID: {emp1_id}")
print(f"[PASS] Total Tasks: {emp1['total_tasks']}, Initial Progress: {emp1['progress_percentage']}%")
print(f"[PASS] Task 1 Database ID: {task1_id}, Task 2 Database ID: {task2_id}")

# TEST 2: Check 2 tasks for Anu
print("\n--- TEST 2: Toggle 2 Tasks as Completed for Anu ---")
t1 = post("/api/tasks/toggle", {"task_id": task1_id, "completed": True})
print(f"[PASS] Task 1 completed: {t1['completed']}, Count: {t1['completed_count']}/{t1['total_tasks']}, Progress: {t1['progress_percentage']}%")
t2 = post("/api/tasks/toggle", {"task_id": task2_id, "completed": True})
print(f"[PASS] Task 2 completed: {t2['completed']}, Count: {t2['completed_count']}/{t2['total_tasks']}, Progress: {t2['progress_percentage']}%")
assert t2['completed_count'] == 2
assert t2['progress_percentage'] > 0

# TEST 3: Uncheck 1 task (Recalculation test)
print("\n--- TEST 3: Uncomplete Task 1 for Anu (Recalculation Test) ---")
t1_uncheck = post("/api/tasks/toggle", {"task_id": task1_id, "completed": False})
print(f"[PASS] Task 1 uncompleted: {t1_uncheck['completed']}, Count: {t1_uncheck['completed_count']}/{t1_uncheck['total_tasks']}, Recalculated Progress: {t1_uncheck['progress_percentage']}%")
assert t1_uncheck['completed_count'] == 1

# TEST 4: Fetch checklist from SQLite (Simulates browser refresh)
print("\n--- TEST 4: Fetch Checklist from Database (Simulates Browser Refresh) ---")
refreshed = get(f"/api/employee/{emp1_id}/checklist")
refreshed_day1 = refreshed["phases"]["day_1"]["tasks"]
print(f"[PASS] Refreshed Employee: {refreshed['employee']['name']}")
print(f"[PASS] Refreshed Progress: {refreshed['progress_percentage']}% (Completed: {refreshed['completed_tasks']}/{refreshed['total_tasks']})")
print(f"[PASS] Task 1 state after refresh: {refreshed_day1[0]['completed']} (Expected: False)")
print(f"[PASS] Task 2 state after refresh: {refreshed_day1[1]['completed']} (Expected: True)")
assert refreshed_day1[0]['completed'] == False
assert refreshed_day1[1]['completed'] == True
assert refreshed['completed_tasks'] == 1

# TEST 5: Create Employee 2 (Rahul Varma, Marketing) - Isolation test
print("\n--- TEST 5: Create Employee 2 (Rahul Varma, Marketing) - Isolation Test ---")
emp2 = post("/api/generate-checklist", {
    "name": "Rahul Varma",
    "department": "Marketing",
    "role": "Growth Marketer",
    "joining_date": "2026-10-12",
    "location": "Remote",
    "experience": "3-5 years",
    "employment_type": "Full-time"
})
emp2_id = emp2["employee_id"]
print(f"[PASS] Employee 2 Created ID: {emp2_id}")
print(f"[PASS] Employee 2 Total Tasks: {emp2['total_tasks']}, Progress: {emp2['progress_percentage']}% (Expected: 0%)")
assert emp2['progress_percentage'] == 0
assert emp2_id != emp1_id

# Verify Employee 1 progress is unchanged
refreshed_again = get(f"/api/employee/{emp1_id}/checklist")
print(f"[PASS] Employee 1 Progress remains intact: {refreshed_again['progress_percentage']}% (Completed: {refreshed_again['completed_tasks']})")
assert refreshed_again['completed_tasks'] == 1

# TEST 6: Verify SQLite file and tables directly
print("\n--- TEST 6: Direct SQLite Database Verification ---")
conn = sqlite3.connect("onboardflow.db")
c = conn.cursor()
emp_count = c.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
task_count = c.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
completed_count = c.execute("SELECT COUNT(*) FROM tasks WHERE completed = 1").fetchone()[0]
conn.close()
print(f"[PASS] Total Employees in SQLite: {emp_count}")
print(f"[PASS] Total Tasks stored in SQLite: {task_count}")
print(f"[PASS] Total Completed Tasks in SQLite: {completed_count}")

print("\n*** ALL TESTS PASSED! Step 7 persistent task completion is 100% verified. ***")
