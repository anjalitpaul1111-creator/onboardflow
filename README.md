# 🚀 OnboardFlow — Automated Onboarding Checklist Generator

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-lightgrey.svg)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/Database-SQLite3-green.svg)](https://www.sqlite.org/)
[![Status](https://img.shields.io/badge/Audit%20Status-100%25%20Verified-emerald.svg)]()

> **Transform manual, chaotic employee onboarding into a structured, role-tailored 90-day interactive roadmap with real-time tracking and database persistence.**

---

## 🌟 The Problem & The Solution

* **The Problem:** 33% of new hires quit within their first 90 days. Most companies hand incoming employees a generic, disorganized PDF checklist. A Software Engineer receives the exact same onboarding list as an HR Specialist or Sales Rep.
* **The Solution:** **OnboardFlow** dynamically creates an interactive, personalized 4-phase onboarding roadmap (Day 1, Week 1, 30 Days, 90 Days) tailored to the employee's department, role, seniority, location, and employment type.

---

## ✨ Key Features

1. **⚡ One-Click Generation:** Enter simple parameters (or click *⚡ Quick Demo Auto-Fill*) to instantly build an onboarding plan in under 200ms.
2. **🎯 Deep Department Personalization:**
   * **Engineering:** Git repos, IDE setup, CI/CD pipelines, architectural walkthroughs.
   * **Design:** Figma Enterprise workspaces, brand design systems, design sprint reviews.
   * **Marketing:** CMS access, social analytics, content calendars, campaign briefs.
   * **Sales:** CRM setup (Salesforce/HubSpot), pitch collateral, call shadowing.
   * **HR & People:** HRIS access, payroll compliance, benefits administration.
   * **Finance:** ERP systems, audit guidelines, ledger workflows.
3. **💡 "Why This Task?" Context Modals:** Educates new hires on the exact business impact behind each task.
4. **🔄 Real-time Database Persistence:** Checkbox state syncs instantly to an embedded SQLite database (`onboardflow.db`). Progress is never lost on page refresh (`F5`).
5. **📊 HR Executive Dashboard:** Aggregates company-wide onboarding statistics (total hires, active onboardings, completed count, average organization progress, and recent hires table).
6. **🎉 Gamified Celebration:** Milestone phase filtering (`Day 1`, `Week 1`, etc.), quick bulk-actions (`⚡ Complete Phase`), and a completion celebration banner upon reaching 100%.

---

## 🛠️ Technology Stack

* **Frontend:** Semantic HTML5, Modern CSS3 with Design Tokens (Indigo palette, glassmorphism), Vanilla JavaScript (ES6+ async `fetch` API, no heavy build frameworks).
* **Backend:** Python Flask REST API with defensive input validation and custom personalization rules engine.
* **Database:** Embedded SQLite3 with ACID compliance, relational foreign keys (`employees` and `tasks` tables), and parameterized query security.

---

## 🚀 Quickstart Guide

### 1. Clone the Repository
```bash
git clone https://github.com/anjalitpaul1111-creator/onboardflow.git
cd onboardflow
```

### 2. Install Dependencies
```bash
pip install flask
```

### 3. Start the Server
```bash
python app.py
```

### 4. Open in Your Browser
Navigate to:
```
http://127.0.0.1:5000
```

---

## 🧪 Automated End-to-End Testing

Run our 5-pillar automated audit to verify server health, form validation, all 6 department rules, real-time math, and SQLite data isolation:

```bash
python test_suite_e2e.py
```

All 5 pillars verified:
* `[PASS]` Web Server & Static Assets Integrity (HTTP 200)
* `[PASS]` Input Validation & Error Handling (HTTP 400)
* `[PASS]` Deep Personalization Matrix Across All 6 Departments
* `[PASS]` Task Completion, Math & Multi-Employee Isolation
* `[PASS]` HR Dashboard Metrics & SQLite Database Health

---

## 📁 Project Structure

```
hack@123/
├── app.py                   # Python Flask server & REST API
├── onboardflow.db           # SQLite database storing employees & tasks
├── templates/
│   └── index.html           # Single-page web application frontend
├── static/
│   ├── css/
│   │   └── style.css        # Responsive styling & modern design system
│   └── js/
│       └── main.js          # Interactive UI logic & async API communication
├── DEMO_SCRIPT.md           # 3-Minute word-for-word hackathon pitch guide
├── ARCHITECTURE_AND_QA.md   # System architecture & Judge Q&A defense sheet
├── test_suite_e2e.py        # Automated 5-pillar test suite
└── README.md                # Project documentation
```

---

## 📄 Documentation Links
* [3-Minute Hackathon Demo Script](DEMO_SCRIPT.md)
* [System Architecture & Judge Q&A Guide](ARCHITECTURE_AND_QA.md)

---
*Built with ❤️ for hackathons.*
