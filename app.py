from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import sqlite3
import os
import shutil
import tempfile

# Resolve base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Initialize Flask application with explicit template and static paths
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static'),
    static_url_path='/static'
)

# On Vercel (and other serverless platforms), the deployment filesystem is read-only.
# SQLite requires write access for WAL/journal and INSERTs, so we use tempfile directory when on Vercel.
if os.environ.get("VERCEL"):
    DB_PATH = os.path.join(tempfile.gettempdir(), 'onboardflow.db')
    seed_db = os.path.join(BASE_DIR, 'onboardflow.db')
    if not os.path.exists(DB_PATH) and os.path.exists(seed_db):
        try:
            shutil.copy2(seed_db, DB_PATH)
        except Exception as e:
            print(f"Notice: Could not copy seed DB: {e}")
else:
    DB_PATH = os.path.join(BASE_DIR, 'onboardflow.db')

def get_db_connection():
    """Returns a connection to the SQLite database with Row support."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Creates the SQLite database tables if they do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table 1: Employees
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            role TEXT NOT NULL,
            joining_date TEXT NOT NULL,
            location TEXT NOT NULL,
            experience TEXT NOT NULL,
            employment_type TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Table 2: Tasks (persists completion state for each employee)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            task_key TEXT NOT NULL,
            title TEXT NOT NULL,
            priority TEXT NOT NULL,
            owner TEXT NOT NULL,
            due_date TEXT NOT NULL,
            stage TEXT NOT NULL,
            reason TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            FOREIGN KEY (employee_id) REFERENCES employees (id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

def generate_checklist_rules(employee):
    """
    Step 8: Deep Personalization Rule Engine.
    Generates intelligent onboarding tasks based on:
    1. Department (Engineering, Marketing, HR, Finance, Sales, Design)
    2. Specific Job Role
    3. Employment Type (Full-time, Intern, Contract, Part-time)
    4. Work Location (Remote, Hybrid, On-site)
    5. Experience Level (Fresher, 1-3 years, 3-5 years, 5+ years)
    """
    name = employee.get("name", "New Employee")
    dept = employee.get("department", "General")
    role = employee.get("role", "Team Member")
    location = employee.get("location", "On-site")
    experience = employee.get("experience", "Fresher")
    emp_type = employee.get("employment_type", "Full-time")
    joining_date_str = employee.get("joining_date", "")

    # Calculate target milestone dates from joining date
    try:
        joining_date = datetime.strptime(joining_date_str, "%Y-%m-%d")
    except Exception:
        joining_date = datetime.now()

    day_1_date = joining_date.strftime("%b %d, %Y")
    week_1_date = (joining_date + timedelta(days=7)).strftime("%b %d, %Y")
    day_30_date = (joining_date + timedelta(days=30)).strftime("%b %d, %Y")
    day_90_date = (joining_date + timedelta(days=90)).strftime("%b %d, %Y")

    tasks = {
        "day_1": [],
        "week_1": [],
        "day_30": [],
        "day_90": []
    }

    task_counter = 1

    def make_task(title, priority, owner, due_date, stage, reason):
        nonlocal task_counter
        t = {
            "task_key": f"task_{task_counter}",
            "title": title,
            "priority": priority,
            "owner": owner,
            "due_date": due_date,
            "stage": stage,
            "reason": reason,
            "completed": 0
        }
        task_counter += 1
        return t

    # =========================================================================
    # PHASE 1: DAY 1 TASKS (Essential Formalities & Initial Provisioning)
    # =========================================================================
    
    # 1. Universal Day 1 Tasks
    tasks["day_1"].append(make_task(
        "Complete HR documentation and identity verification",
        "High",
        "HR Operations",
        day_1_date,
        "Day 1",
        f"Universal regulatory compliance for all new employees including {name}."
    ))
    tasks["day_1"].append(make_task(
        "Create corporate email & single sign-on (SSO) credentials",
        "High",
        "IT Helpdesk",
        day_1_date,
        "Day 1",
        "Required for accessing company communication channels, Slack/Teams, and tools."
    ))
    tasks["day_1"].append(make_task(
        "Team welcome huddle & introductions",
        "Medium",
        "Reporting Manager",
        day_1_date,
        "Day 1",
        f"Introduces {name} to their direct colleagues and assigned team."
    ))

    # 2. Employment Type Day 1 Rules
    if emp_type == "Intern":
        tasks["day_1"].append(make_task(
            "Pair with dedicated Intern Mentor & review intern handbook",
            "High",
            "Assigned Mentor",
            day_1_date,
            "Day 1",
            "Employment type is Intern; immediate pairing with a mentor provides clear guidance."
        ))
    elif emp_type == "Contract":
        tasks["day_1"].append(make_task(
            "Contractor Statement of Work (SOW) & NDA confirmation",
            "High",
            "Legal & HR",
            day_1_date,
            "Day 1",
            "Employment type is Contract; formalizing project scope and IP protection is required."
        ))
    elif emp_type == "Full-time":
        tasks["day_1"].append(make_task(
            "Company benefits, health insurance & 401(k)/PF enrollment",
            "Medium",
            "Benefits Team",
            day_1_date,
            "Day 1",
            "Employment type is Full-time; standard corporate benefits orientation."
        ))

    # 3. Location Day 1 Rules
    if location == "Remote":
        tasks["day_1"].append(make_task(
            "Verify home workstation delivery & configure secure VPN",
            "High",
            "IT Logistics",
            day_1_date,
            "Day 1",
            "Work location is Remote; hardware shipment and secure network tunnel access are required."
        ))
        tasks["day_1"].append(make_task(
            "Submit Remote Workspace & Ergonomics Stipend form",
            "Low",
            "People Ops",
            day_1_date,
            "Day 1",
            "Remote employees receive a one-time home-office setup allowance."
        ))
    elif location == "Hybrid":
        tasks["day_1"].append(make_task(
            "Issue smart office badge & configure hot-desk booking app",
            "Medium",
            "Facilities",
            day_1_date,
            "Day 1",
            "Work location is Hybrid; employee requires building access and flexible desk booking."
        ))
    else:  # On-site
        tasks["day_1"].append(make_task(
            "Issue physical RFID security badge & parking pass",
            "High",
            "Facilities",
            day_1_date,
            "Day 1",
            "Work location is On-site; physical access and campus parking permits required."
        ))
        tasks["day_1"].append(make_task(
            "Office ergonomics check & safety emergency exit tour",
            "Medium",
            "Facilities",
            day_1_date,
            "Day 1",
            "On-site requirement: occupational health inspection and safety briefing."
        ))

    # 4. Department Day 1 Rules
    if dept == "Engineering":
        tasks["day_1"].append(make_task(
            f"Provision developer workstation & toolchain for {role}",
            "High",
            "Engineering IT",
            day_1_date,
            "Day 1",
            f"Department is Engineering; {role} requires pre-configured dev hardware, terminals & compilers."
        ))
    elif dept == "Marketing":
        tasks["day_1"].append(make_task(
            f"Grant access to Marketing suite (CMS, Socials & Analytics) for {role}",
            "High",
            "Marketing Ops",
            day_1_date,
            "Day 1",
            f"Department is Marketing; {role} needs immediate access to content platforms."
        ))
    elif dept == "HR":
        tasks["day_1"].append(make_task(
            f"Configure HRIS (Workday/BambooHR) administrative account for {role}",
            "High",
            "HR Tech Lead",
            day_1_date,
            "Day 1",
            f"Department is HR; {role} requires administrative access to employee databases."
        ))
    elif dept == "Finance":
        tasks["day_1"].append(make_task(
            f"Provision ERP & secure financial accounting portal access for {role}",
            "High",
            "Finance Systems",
            day_1_date,
            "Day 1",
            f"Department is Finance; {role} requires access to ledger and payment software."
        ))
    elif dept == "Sales":
        tasks["day_1"].append(make_task(
            f"Set up CRM (Salesforce/HubSpot) account & cloud phone dialer for {role}",
            "High",
            "Sales Operations",
            day_1_date,
            "Day 1",
            f"Department is Sales; {role} requires client contact pipelines and tracking."
        ))
    elif dept == "Design":
        tasks["day_1"].append(make_task(
            f"Assign Figma Enterprise & Adobe Creative Cloud license for {role}",
            "High",
            "Design Ops",
            day_1_date,
            "Day 1",
            f"Department is Design; {role} requires design collaboration platforms."
        ))

    # =========================================================================
    # PHASE 2: WEEK 1 TASKS (Orientation & Department Integration)
    # =========================================================================
    
    # 1. Universal Week 1 Tasks
    tasks["week_1"].append(make_task(
        "Company mission, values, and handbook review",
        "Medium",
        "People Team",
        week_1_date,
        "Week 1",
        "Standard company-wide cultural onboarding for all team members."
    ))
    tasks["week_1"].append(make_task(
        "Complete mandatory data security & compliance certification",
        "High",
        "InfoSec Team",
        week_1_date,
        "Week 1",
        "Ensures adherence to company privacy and data security standards."
    ))
    tasks["week_1"].append(make_task(
        "Manager 1-on-1: Set 30-day goals and expectations",
        "High",
        "Reporting Manager",
        week_1_date,
        "Week 1",
        "Aligns the new hire with immediate team priorities and deliverables."
    ))

    # 2. Employment Type Week 1 Rules
    if emp_type == "Intern":
        tasks["week_1"].append(make_task(
            "Define 90-day Intern Capstone Project scope & learning objectives",
            "High",
            "Mentor & Manager",
            week_1_date,
            "Week 1",
            "Interns work towards a structured capstone project to demonstrate applied skills."
        ))
    elif emp_type == "Contract":
        tasks["week_1"].append(make_task(
            "Configure vendor time-tracking & monthly invoicing account",
            "Medium",
            "Finance Ops",
            week_1_date,
            "Week 1",
            "Contractors require established billing channels for payment processing."
        ))

    # 3. Experience Week 1 Rules
    if experience == "Fresher":
        tasks["week_1"].append(make_task(
            "Schedule weekly 1-on-1 buddy mentorship check-ins",
            "High",
            "Assigned Mentor",
            week_1_date,
            "Week 1",
            "Experience level is Fresher; peer mentoring ensures continuous learning and support."
        ))
        tasks["week_1"].append(make_task(
            "Complete company workplace communication & etiquette workshop",
            "Low",
            "Learning & Dev",
            week_1_date,
            "Week 1",
            "Foundational professional development for entry-level hires."
        ))
    elif experience == "5+ years":
        tasks["week_1"].append(make_task(
            "Schedule cross-functional alignment chats with department heads",
            "Medium",
            "Executive Leads",
            week_1_date,
            "Week 1",
            "Experience is 5+ years (Senior); senior hires require strategic leadership context."
        ))

    # 4. Department Week 1 Rules
    if dept == "Engineering":
        tasks["week_1"].append(make_task(
            "Clone Git repositories & complete local build setup",
            "High",
            "Tech Lead",
            week_1_date,
            "Week 1",
            "Engineering requirement: verify ability to build and run test suites locally."
        ))
        tasks["week_1"].append(make_task(
            "Architecture overview & codebase walkthrough with Senior Engineer",
            "Medium",
            "Tech Lead",
            week_1_date,
            "Week 1",
            "Ensures deep comprehension of system architecture before writing code."
        ))
    elif dept == "Marketing":
        tasks["week_1"].append(make_task(
            "Review company brand voice guidelines & target audience personas",
            "High",
            "Content Lead",
            week_1_date,
            "Week 1",
            "Marketing requirement: align on brand positioning and messaging standards."
        ))
        tasks["week_1"].append(make_task(
            "Inspect active quarterly marketing campaign calendar & KPI goals",
            "Medium",
            "Marketing Manager",
            week_1_date,
            "Week 1",
            "Provides visibility into upcoming campaign launches and deliverables."
        ))
    elif dept == "HR":
        tasks["week_1"].append(make_task(
            "Deep-dive into employee policies, benefits structure, and leave rules",
            "High",
            "HR Manager",
            week_1_date,
            "Week 1",
            "HR requirement: enables new specialist to accurately answer staff inquiries."
        ))
        tasks["week_1"].append(make_task(
            "Review Applicant Tracking System (ATS) active candidate pipelines",
            "Medium",
            "Talent Lead",
            week_1_date,
            "Week 1",
            "Aligns HR team on open hiring requisitions and candidate stages."
        ))
    elif dept == "Finance":
        tasks["week_1"].append(make_task(
            "Complete internal financial controls and audit compliance briefing",
            "High",
            "Finance Controller",
            week_1_date,
            "Week 1",
            "Finance requirement: safeguards financial reporting and regulatory integrity."
        ))
        tasks["week_1"].append(make_task(
            "Review corporate travel & expense reimbursement guidelines",
            "Medium",
            "Finance Ops",
            week_1_date,
            "Week 1",
            "Familiarizes finance hire with employee expense approval thresholds."
        ))
    elif dept == "Sales":
        tasks["week_1"].append(make_task(
            "Review product pitch decks, pricing matrices, and competitive battlecards",
            "High",
            "Sales Enablement",
            week_1_date,
            "Week 1",
            "Sales requirement: equips salesperson with objection handling and product knowledge."
        ))
        tasks["week_1"].append(make_task(
            "Shadow 3 live sales discovery calls with Senior Account Executive",
            "High",
            "Sales Mentor",
            week_1_date,
            "Week 1",
            "Hands-on demonstration of buyer interactions and sales pitch delivery."
        ))
    elif dept == "Design":
        tasks["week_1"].append(make_task(
            "Explore design token system, UI library, and user research repository",
            "Medium",
            "Design Lead",
            week_1_date,
            "Week 1",
            "Design requirement: ensures consistency across existing UI design systems."
        ))
        tasks["week_1"].append(make_task(
            "Participate in weekly design critique and work-in-progress review",
            "Medium",
            "Design Team",
            week_1_date,
            "Week 1",
            "Integrates designer into collaborative peer feedback cycles."
        ))

    # =========================================================================
    # PHASE 3: FIRST 30 DAYS (Core Competency & Early Contribution)
    # =========================================================================
    
    # 1. Universal 30 Days Tasks
    tasks["day_30"].append(make_task(
        "30-day onboarding feedback & milestone check-in",
        "Medium",
        "Reporting Manager",
        day_30_date,
        "First 30 Days",
        "Formal check-in to assess progress, address blockers, and celebrate early wins."
    ))

    # 2. Employment Type 30 Days Rules
    if emp_type == "Intern":
        tasks["day_30"].append(make_task(
            "Mid-Internship capstone progress check & mentor feedback session",
            "High",
            "Assigned Mentor",
            day_30_date,
            "First 30 Days",
            "Ensures intern project is on track and provides constructive mid-point guidance."
        ))
    elif emp_type == "Contract":
        tasks["day_30"].append(make_task(
            "Contract Milestone 1 deliverable review against SOW scope",
            "High",
            "Project Lead",
            day_30_date,
            "First 30 Days",
            "Formal checkpoint to verify contract deliverables meet acceptance criteria."
        ))

    # 3. Department 30 Days Rules
    if dept == "Engineering":
        tasks["day_30"].append(make_task(
            f"Submit first pull request / bug fix to development branch for {role}",
            "High",
            "Tech Lead",
            day_30_date,
            "First 30 Days",
            f"Validates that {name} has mastered the git workflow and CI/CD deployment pipeline."
        ))
    elif dept == "Marketing":
        tasks["day_30"].append(make_task(
            f"Publish first campaign creative or drafted blog article for {role}",
            "High",
            "Marketing Lead",
            day_30_date,
            "First 30 Days",
            f"Demonstrates practical campaign delivery in {role} role."
        ))
    elif dept == "HR":
        tasks["day_30"].append(make_task(
            f"Facilitate an onboarding session for another new joiner ({role})",
            "Medium",
            "HR Director",
            day_30_date,
            "First 30 Days",
            "Practical test of HR domain knowledge and process mastery."
        ))
    elif dept == "Finance":
        tasks["day_30"].append(make_task(
            f"Participate in monthly accounting reconciliation cycle ({role})",
            "High",
            "Finance Lead",
            day_30_date,
            "First 30 Days",
            "Validates operational comfort with company ledger procedures."
        ))
    elif dept == "Sales":
        tasks["day_30"].append(make_task(
            f"Conduct first live customer discovery call with mentor shadowing ({role})",
            "High",
            "Sales Lead",
            day_30_date,
            "First 30 Days",
            "Milestone test of sales pitch presentation skills with actual prospects."
        ))
    elif dept == "Design":
        tasks["day_30"].append(make_task(
            f"Deliver interactive prototype for upcoming product feature ({role})",
            "High",
            "Design Lead",
            day_30_date,
            "First 30 Days",
            "Demonstrates UX workflow from wireframes to high-fidelity designs."
        ))

    # =========================================================================
    # PHASE 4: FIRST 90 DAYS (Autonomy, Ownership & Long-term Goals)
    # =========================================================================
    
    # 1. Universal 90 Days Tasks
    tasks["day_90"].append(make_task(
        "Formal 90-day probationary review & full onboarding completion",
        "High",
        "HR Operations",
        day_90_date,
        "First 90 Days",
        "Official confirmation of successful onboarding and transition to core status."
    ))
    tasks["day_90"].append(make_task(
        "Establish annual performance OKRs and development roadmap",
        "Medium",
        "Reporting Manager",
        day_90_date,
        "First 90 Days",
        "Transitions the employee from onboarding to long-term career growth objectives."
    ))

    # 2. Employment Type 90 Days Rules
    if emp_type == "Intern":
        tasks["day_90"].append(make_task(
            "Deliver final Intern Capstone Presentation & full-time conversion evaluation",
            "High",
            "Department Head",
            day_90_date,
            "First 90 Days",
            "Intern showcases deliverables to leadership for full-time offer consideration."
        ))
    elif emp_type == "Contract":
        tasks["day_90"].append(make_task(
            "Final contract deliverable sign-off & contract extension/closure review",
            "High",
            "Engagement Lead",
            day_90_date,
            "First 90 Days",
            "Concludes contract terms or evaluates renewal based on project milestones."
        ))

    # 3. Department 90 Days Rules
    if dept == "Engineering":
        tasks["day_90"].append(make_task(
            f"Own and deploy an end-to-end production feature independently ({role})",
            "High",
            "Engineering Manager",
            day_90_date,
            "First 90 Days",
            f"Confirms full engineering autonomy for {role}."
        ))
    elif dept == "Marketing":
        tasks["day_90"].append(make_task(
            f"Lead a quarterly campaign review with performance analytics ({role})",
            "Medium",
            "Head of Marketing",
            day_90_date,
            "First 90 Days",
            "Measures ability to drive ROI and present marketing insights."
        ))
    elif dept == "Sales":
        tasks["day_90"].append(make_task(
            f"Achieve full independent quota run-rate ({role})",
            "High",
            "VP of Sales",
            day_90_date,
            "First 90 Days",
            "Validates independent revenue generation capability."
        ))
    elif dept == "Design":
        tasks["day_90"].append(make_task(
            f"Contribute a new reusable component pattern to company Design System ({role})",
            "Medium",
            "Design Director",
            day_90_date,
            "First 90 Days",
            "Demonstrates systemic design thinking and long-term UI contributions."
        ))

    return tasks

# =====================================================================
# ROUTES & APIS
# =====================================================================

@app.route('/')
def home():
    """Serves the main single-page application."""
    return render_template('index.html')

@app.route('/api/generate-checklist', methods=['POST'])
def api_generate_checklist():
    """
    Receives JSON with employee details, generates tasks, saves employee and tasks
    into the SQLite database, and returns the persisted record.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided in request"}), 400

        # Validate required fields
        required_fields = ["name", "department", "role", "joining_date"]
        missing = [f for f in required_fields if not data.get(f)]
        if missing:
            return jsonify({"error": f"Missing required fields: {', '.join(missing)}"}), 400

        name = data.get("name").strip()
        dept = data.get("department")
        role = data.get("role").strip()
        joining_date = data.get("joining_date")
        location = data.get("location", "On-site")
        experience = data.get("experience", "Fresher")
        employment_type = data.get("employment_type", "Full-time")

        # 1. Save employee to SQLite
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO employees (name, department, role, joining_date, location, experience, employment_type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, dept, role, joining_date, location, experience, employment_type))
        employee_id = cursor.lastrowid

        # 2. Generate rule-based tasks with deep personalization
        tasks_by_stage = generate_checklist_rules(data)

        # 3. Save all tasks into SQLite associated with this employee_id
        db_tasks = []
        for stage_key, task_list in tasks_by_stage.items():
            for t in task_list:
                cursor.execute('''
                    INSERT INTO tasks (employee_id, task_key, title, priority, owner, due_date, stage, reason, completed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
                ''', (employee_id, t["task_key"], t["title"], t["priority"], t["owner"], t["due_date"], t["stage"], t["reason"]))
                
                # Attach the auto-generated database primary key ID
                task_db_id = cursor.lastrowid
                t["id"] = task_db_id
                t["completed"] = False
                db_tasks.append(t)

        conn.commit()
        conn.close()

        # Build response with phase separation
        return jsonify({
            "employee_id": employee_id,
            "employee": {
                "id": employee_id,
                "name": name,
                "department": dept,
                "role": role,
                "joining_date": joining_date,
                "location": location,
                "experience": experience,
                "employment_type": employment_type
            },
            "phases": {
                "day_1": {
                    "label": "DAY 1: Welcome & Setup",
                    "description": "First-day essentials, accounts, and immediate team introductions.",
                    "tasks": [t for t in db_tasks if t["stage"] == "Day 1"]
                },
                "week_1": {
                    "label": "WEEK 1: Orientation & Integration",
                    "description": "Tools setup, compliance training, and mentor pairing.",
                    "tasks": [t for t in db_tasks if t["stage"] == "Week 1"]
                },
                "day_30": {
                    "label": "FIRST 30 DAYS: Ramp-up & First Deliverable",
                    "description": "First meaningful contributions and operational milestones.",
                    "tasks": [t for t in db_tasks if t["stage"] == "First 30 Days"]
                },
                "day_90": {
                    "label": "FIRST 90 DAYS: Autonomy & Ownership",
                    "description": "Transition to full independence, performance review, and goal setting.",
                    "tasks": [t for t in db_tasks if t["stage"] == "First 90 Days"]
                }
            },
            "total_tasks": len(db_tasks),
            "completed_tasks": 0,
            "progress_percentage": 0
        }), 201

    except Exception as e:
        print(f"Error generating and saving checklist: {e}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/api/tasks/toggle', methods=['POST'])
def api_toggle_task():
    """
    Toggles the completion status (0 or 1) of a task in SQLite,
    and returns the recalculated progress directly from database data.
    """
    try:
        data = request.get_json()
        if not data or 'task_id' not in data or 'completed' not in data:
            return jsonify({"error": "task_id and completed status are required"}), 400

        task_id = int(data['task_id'])
        completed_val = 1 if data['completed'] else 0

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if task exists and find its employee_id
        task_row = cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
        if not task_row:
            conn.close()
            return jsonify({"error": "Task not found"}), 404

        employee_id = task_row['employee_id']

        # Update task status in database
        cursor.execute('UPDATE tasks SET completed = ? WHERE id = ?', (completed_val, task_id))
        conn.commit()

        # Recalculate progress for this employee directly from DB
        stats = cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) as completed_count
            FROM tasks
            WHERE employee_id = ?
        ''', (employee_id,)).fetchone()

        total = stats['total'] if stats else 0
        completed_count = stats['completed_count'] if (stats and stats['completed_count']) else 0
        percentage = round((completed_count / total) * 100) if total > 0 else 0

        conn.close()

        return jsonify({
            "success": True,
            "task_id": task_id,
            "employee_id": employee_id,
            "completed": bool(completed_val),
            "completed_count": completed_count,
            "total_tasks": total,
            "progress_percentage": percentage
        }), 200

    except Exception as e:
        print(f"Error toggling task: {e}")
        return jsonify({"error": f"Error updating task: {str(e)}"}), 500

@app.route('/api/employee/<int:employee_id>/checklist', methods=['GET'])
def api_get_employee_checklist(employee_id):
    """
    Fetches an employee's checklist and persisted completion states from SQLite.
    Allows restoring the checklist upon page refresh!
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch employee
        emp = cursor.execute('SELECT * FROM employees WHERE id = ?', (employee_id,)).fetchone()
        if not emp:
            conn.close()
            return jsonify({"error": "Employee not found"}), 404

        # Fetch all tasks for this employee
        tasks_rows = cursor.execute('SELECT * FROM tasks WHERE employee_id = ? ORDER BY id ASC', (employee_id,)).fetchall()
        conn.close()

        tasks_list = []
        completed_count = 0
        for r in tasks_rows:
            is_done = bool(r['completed'])
            if is_done:
                completed_count += 1
            tasks_list.append({
                "id": r["id"],
                "task_key": r["task_key"],
                "title": r["title"],
                "priority": r["priority"],
                "owner": r["owner"],
                "due_date": r["due_date"],
                "stage": r["stage"],
                "reason": r["reason"],
                "completed": is_done
            })

        total = len(tasks_list)
        percentage = round((completed_count / total) * 100) if total > 0 else 0

        return jsonify({
            "employee_id": emp["id"],
            "employee": {
                "id": emp["id"],
                "name": emp["name"],
                "department": emp["department"],
                "role": emp["role"],
                "joining_date": emp["joining_date"],
                "location": emp["location"],
                "experience": emp["experience"],
                "employment_type": emp["employment_type"]
            },
            "phases": {
                "day_1": {
                    "label": "DAY 1: Welcome & Setup",
                    "description": "First-day essentials, accounts, and immediate team introductions.",
                    "tasks": [t for t in tasks_list if t["stage"] == "Day 1"]
                },
                "week_1": {
                    "label": "WEEK 1: Orientation & Integration",
                    "description": "Tools setup, compliance training, and mentor pairing.",
                    "tasks": [t for t in tasks_list if t["stage"] == "Week 1"]
                },
                "day_30": {
                    "label": "FIRST 30 DAYS: Ramp-up & First Deliverable",
                    "description": "First meaningful contributions and operational milestones.",
                    "tasks": [t for t in tasks_list if t["stage"] == "First 30 Days"]
                },
                "day_90": {
                    "label": "FIRST 90 DAYS: Autonomy & Ownership",
                    "description": "Transition to full independence, performance review, and goal setting.",
                    "tasks": [t for t in tasks_list if t["stage"] == "First 90 Days"]
                }
            },
            "total_tasks": total,
            "completed_tasks": completed_count,
            "progress_percentage": percentage
        }), 200

    except Exception as e:
        print(f"Error fetching checklist: {e}")
        return jsonify({"error": f"Error fetching checklist: {str(e)}"}), 500

@app.route('/api/dashboard/stats', methods=['GET'])
def api_dashboard_stats():
    """
    Returns high-level onboarding metrics across the organization:
    - Total employees onboarded
    - Active onboardings (progress < 100%)
    - Completed onboardings (progress == 100%)
    - Average onboarding progress percentage
    - List of recent employees with individual task stats
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Count total employees
        total_employees = cursor.execute('SELECT COUNT(*) FROM employees').fetchone()[0]

        if total_employees == 0:
            conn.close()
            return jsonify({
                "total_employees": 0,
                "active_onboardings": 0,
                "completed_onboardings": 0,
                "average_progress": 0,
                "recent_employees": []
            }), 200

        # Query all employees and their aggregate task stats
        query = '''
            SELECT 
                e.id, e.name, e.department, e.role, e.joining_date, e.location, e.experience, e.employment_type, e.created_at,
                COUNT(t.id) as total_tasks,
                SUM(CASE WHEN t.completed = 1 THEN 1 ELSE 0 END) as completed_tasks
            FROM employees e
            LEFT JOIN tasks t ON e.id = t.employee_id
            GROUP BY e.id
            ORDER BY e.id DESC
        '''
        rows = cursor.execute(query).fetchall()
        conn.close()

        employees_list = []
        completed_onboardings = 0
        total_progress_sum = 0

        for r in rows:
            total = r['total_tasks'] or 0
            done = r['completed_tasks'] or 0
            pct = round((done / total) * 100) if total > 0 else 0
            total_progress_sum += pct
            is_complete = (pct == 100 and total > 0)
            if is_complete:
                completed_onboardings += 1

            employees_list.append({
                "id": r["id"],
                "name": r["name"],
                "department": r["department"],
                "role": r["role"],
                "joining_date": r["joining_date"],
                "location": r["location"],
                "experience": r["experience"],
                "employment_type": r["employment_type"],
                "total_tasks": total,
                "completed_tasks": done,
                "progress_percentage": pct,
                "status": "Completed" if is_complete else "Active"
            })

        active_onboardings = total_employees - completed_onboardings
        avg_progress = round(total_progress_sum / total_employees) if total_employees > 0 else 0

        return jsonify({
            "total_employees": total_employees,
            "active_onboardings": active_onboardings,
            "completed_onboardings": completed_onboardings,
            "average_progress": avg_progress,
            "recent_employees": employees_list
        }), 200

    except Exception as e:
        print(f"Error fetching dashboard stats: {e}")
        return jsonify({"error": f"Error fetching dashboard stats: {str(e)}"}), 500

if __name__ == '__main__':
    print("Starting OnboardFlow server on http://127.0.0.1:5000 ...")
    app.run(debug=True, port=5000)
