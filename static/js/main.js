// ==========================================================================
// OnboardFlow Client-Side Logic (Step 11: UI/UX Enhancements)
// ==========================================================================

document.addEventListener("DOMContentLoaded", () => {
    console.log("🚀 OnboardFlow: Application initialized successfully!");

    // State
    let currentEmployeeId = null;
    let currentEmployeeData = null;

    // DOM Elements - Forms & Controls
    const employeeForm = document.getElementById("employee-form");
    const btnQuickDemo = document.getElementById("btn-view-demo");
    const btnFillSample = document.getElementById("btn-fill-sample");
    const btnGenerate = document.getElementById("btn-generate-checklist");
    const btnText = document.getElementById("btn-text");
    const btnNewChecklist = document.getElementById("btn-new-checklist");
    const formFeedback = document.getElementById("form-feedback");

    // DOM Elements - Checklist Section
    const checklistSection = document.getElementById("checklist-section");
    const checklistName = document.getElementById("checklist-employee-name");
    const checklistMeta = document.getElementById("checklist-employee-meta");
    const checklistTags = document.getElementById("checklist-tags");
    const phasesContainer = document.getElementById("phases-container");
    const progressBarFill = document.getElementById("progress-bar-fill");
    const progressPercent = document.getElementById("progress-percent");
    const progressCount = document.getElementById("progress-count");
    const saveStatusText = document.getElementById("save-status-text");

    // DOM Elements - Dashboard Section
    const statTotalHires = document.getElementById("stat-total-hires");
    const statActiveHires = document.getElementById("stat-active-hires");
    const statCompletedHires = document.getElementById("stat-completed-hires");
    const statAvgProgress = document.getElementById("stat-avg-progress");
    const tableHiresCount = document.getElementById("table-hires-count");
    const employeesTableBody = document.getElementById("employees-table-body");

    // DOM Elements - Why Task Modal (Step 10)
    const whyModal = document.getElementById("why-task-modal");
    const modalTaskTitle = document.getElementById("modal-task-title");
    const modalTaskReason = document.getElementById("modal-task-reason");
    const modalContextTags = document.getElementById("modal-context-tags");
    const modalCloseBtn = document.getElementById("modal-close-btn");
    const modalGotItBtn = document.getElementById("modal-got-it-btn");

    // Toast Notification System (Step 11)
    function showToast(message, type = "success") {
        const container = document.getElementById("toast-container");
        if (!container) return;

        const toast = document.createElement("div");
        toast.className = `toast toast-${type}`;
        const icon = type === "success" ? "✓" : "ℹ️";
        toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;

        container.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = "0";
            toast.style.transform = "translateX(40px)";
            setTimeout(() => toast.remove(), 350);
        }, 3200);
    }

    function openWhyTaskModal(title, reason) {
        if (!whyModal) return;
        if (modalTaskTitle) modalTaskTitle.textContent = title;
        if (modalTaskReason) modalTaskReason.textContent = reason;

        if (modalContextTags && currentEmployeeData) {
            const deptKey = (currentEmployeeData.department || "engineering").toLowerCase();
            const typeKey = (currentEmployeeData.employment_type || "full-time").toLowerCase();
            const typeClass = typeKey === "intern" ? "tag-type-intern" : (typeKey === "contract" ? "tag-type-contract" : "");

            modalContextTags.innerHTML = `
                <span class="meta-tag tag-dept-${deptKey}">🏢 ${currentEmployeeData.department}</span>
                <span class="meta-tag">💼 ${currentEmployeeData.role}</span>
                <span class="meta-tag">📍 ${currentEmployeeData.location}</span>
                <span class="meta-tag">🎓 ${currentEmployeeData.experience}</span>
                <span class="meta-tag ${typeClass}">📄 ${currentEmployeeData.employment_type}</span>
            `;
        }

        whyModal.classList.remove("hidden");
    }

    function closeWhyTaskModal() {
        if (whyModal) {
            whyModal.classList.add("hidden");
        }
    }

    if (modalCloseBtn) modalCloseBtn.addEventListener("click", closeWhyTaskModal);
    if (modalGotItBtn) modalGotItBtn.addEventListener("click", closeWhyTaskModal);
    if (whyModal) {
        whyModal.addEventListener("click", (e) => {
            if (e.target === whyModal) closeWhyTaskModal();
        });
    }
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && whyModal && !whyModal.classList.contains("hidden")) {
            closeWhyTaskModal();
        }
    });

    // Sample employee data for 1-click hackathon demonstration
    const sampleEmployee = {
        name: "Anu Sharma",
        department: "Engineering",
        role: "Software Developer",
        joiningDate: new Date().toISOString().split("T")[0],
        location: "Hybrid",
        experience: "Fresher",
        employmentType: "Full-time"
    };

    // Helper: Fill sample data
    function fillSampleData() {
        document.getElementById("employee-name").value = sampleEmployee.name;
        document.getElementById("department").value = sampleEmployee.department;
        document.getElementById("job-role").value = sampleEmployee.role;
        document.getElementById("joining-date").value = sampleEmployee.joiningDate;
        document.getElementById("work-location").value = sampleEmployee.location;
        document.getElementById("experience-level").value = sampleEmployee.experience;
        document.getElementById("employment-type").value = sampleEmployee.employmentType;

        const formSection = document.getElementById("form-section");
        if (formSection) {
            formSection.scrollIntoView({ behavior: "smooth" });
        }
    }

    if (btnQuickDemo) {
        btnQuickDemo.addEventListener("click", fillSampleData);
    }

    if (btnFillSample) {
        btnFillSample.addEventListener("click", fillSampleData);
    }

    if (btnNewChecklist) {
        btnNewChecklist.addEventListener("click", () => {
            // Reset active employee to allow creating a new hire
            localStorage.removeItem("onboardflow_active_emp_id");
            currentEmployeeId = null;
            if (employeeForm) employeeForm.reset();
            const formSection = document.getElementById("form-section");
            if (formSection) {
                formSection.scrollIntoView({ behavior: "smooth" });
            }
        });
    }

    // Helper: Update progress bar display and celebration banner
    function displayProgress(completedCount, totalTasks, percentage) {
        if (progressBarFill) progressBarFill.style.width = `${percentage}%`;
        if (progressPercent) progressPercent.textContent = `${percentage}%`;
        if (progressCount) progressCount.textContent = `${completedCount} of ${totalTasks} tasks completed`;

        // 100% Celebration Banner (Step 11)
        const celebrationBanner = document.getElementById("celebration-banner");
        const celebrationDesc = document.getElementById("celebration-desc");
        if (celebrationBanner) {
            if (percentage === 100 && totalTasks > 0) {
                celebrationBanner.classList.remove("hidden");
                if (currentEmployeeData && celebrationDesc) {
                    celebrationDesc.textContent = `${currentEmployeeData.name} has completed all ${totalTasks} onboarding tasks and is 100% ramped up!`;
                }
            } else {
                celebrationBanner.classList.add("hidden");
            }
        }
    }

    // =========================================================================
    // HR DASHBOARD: Fetch & Render Real-Time Stats (Step 9)
    // =========================================================================
    async function fetchDashboardStats() {
        if (!statTotalHires || !employeesTableBody) return;

        try {
            const response = await fetch("/api/dashboard/stats");
            if (!response.ok) return;

            const data = await response.json();

            // 1. Update 4 KPI Cards
            statTotalHires.textContent = data.total_employees;
            statActiveHires.textContent = data.active_onboardings;
            statCompletedHires.textContent = data.completed_onboardings;
            statAvgProgress.textContent = `${data.average_progress}%`;

            if (tableHiresCount) {
                tableHiresCount.textContent = `${data.total_employees} hire${data.total_employees === 1 ? '' : 's'} recorded`;
            }

            // 2. Render Recent Employees Table
            if (!data.recent_employees || data.recent_employees.length === 0) {
                employeesTableBody.innerHTML = `
                    <tr>
                        <td colspan="6" class="table-empty">No employees onboarded yet. Create your first checklist above!</td>
                    </tr>
                `;
                return;
            }

            let tableHtml = "";
            data.recent_employees.forEach((emp) => {
                const deptKey = (emp.department || "engineering").toLowerCase();
                const isComplete = emp.status === "Completed";
                const statusBadgeClass = isComplete ? "status-completed" : "status-active";

                tableHtml += `
                    <tr>
                        <td>
                            <div class="employee-cell-title">${emp.name}</div>
                            <div class="employee-cell-sub">${emp.role}</div>
                        </td>
                        <td>
                            <span class="meta-tag tag-dept-${deptKey}">🏢 ${emp.department}</span>
                        </td>
                        <td>
                            <div>${emp.joining_date}</div>
                            <div class="employee-cell-sub">📍 ${emp.location} · 💼 ${emp.employment_type}</div>
                        </td>
                        <td>
                            <div class="progress-cell-wrapper">
                                <div class="mini-progress-track">
                                    <div class="mini-progress-fill" style="width: ${emp.progress_percentage}%;"></div>
                                </div>
                                <span class="progress-cell-pct">${emp.progress_percentage}%</span>
                            </div>
                            <div class="employee-cell-sub">${emp.completed_tasks}/${emp.total_tasks} done</div>
                        </td>
                        <td>
                            <span class="status-pill ${statusBadgeClass}">${emp.status}</span>
                        </td>
                        <td>
                            <button type="button" class="btn-table-action" data-emp-id="${emp.id}">
                                Open Checklist ↗
                            </button>
                        </td>
                    </tr>
                `;
            });

            employeesTableBody.innerHTML = tableHtml;

            // Wire up "Open Checklist" buttons in the table
            const openButtons = employeesTableBody.querySelectorAll(".btn-table-action");
            openButtons.forEach((btn) => {
                btn.addEventListener("click", () => {
                    const empId = btn.getAttribute("data-emp-id");
                    loadEmployeeChecklist(empId);
                });
            });

        } catch (err) {
            console.error("Error updating dashboard:", err);
        }
    }

    // Load an employee checklist by ID and scroll to it
    async function loadEmployeeChecklist(empId) {
        try {
            const response = await fetch(`/api/employee/${empId}/checklist`);
            if (response.ok) {
                const data = await response.json();
                renderChecklist(data, false);
                showToast(`Loaded onboarding roadmap for ${data.employee.name}`, "info");
            }
        } catch (err) {
            console.error("Error loading employee checklist:", err);
        }
    }

    // Persistent Checkbox Toggle: Sync with SQLite Database
    async function toggleTaskInDatabase(taskId, isChecked, taskItemElement) {
        if (saveStatusText) {
            saveStatusText.textContent = "⏳ Saving to SQLite...";
            saveStatusText.style.color = "#f59e0b"; // Amber color while saving
        }

        try {
            const response = await fetch("/api/tasks/toggle", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    task_id: taskId,
                    completed: isChecked
                })
            });

            if (!response.ok) {
                let errorMsg = `Failed to update task (Status ${response.status})`;
                try {
                    const errData = await response.json();
                    if (errData && errData.error) errorMsg = errData.error;
                } catch (_) {}
                throw new Error(errorMsg);
            }

            const data = await response.json();

            // Update item completed class for strikethrough styling
            if (isChecked) {
                taskItemElement.classList.add("completed");
            } else {
                taskItemElement.classList.remove("completed");
            }

            // Update progress bar using exact database calculation
            displayProgress(data.completed_count, data.total_tasks, data.progress_percentage);

            if (saveStatusText) {
                saveStatusText.textContent = "✓ Saved in SQLite Database";
                saveStatusText.style.color = "#10b981"; // Green color
            }

            // Real-time Toast notification (Step 11)
            showToast(`✓ Task updated · Progress is now ${data.progress_percentage}%`, "success");

            // Keep the HR Dashboard in sync in real-time!
            fetchDashboardStats();

        } catch (err) {
            console.error("Error saving task status:", err);
            showToast("Could not save task to database: " + err.message, "info");
            // Revert checkbox state
            const cb = taskItemElement.querySelector(".task-checkbox");
            if (cb) cb.checked = !isChecked;
        }
    }

    // Helper: Render the checklist
    function renderChecklist(data, isInitialLoad = false) {
        currentEmployeeId = data.employee_id;
        currentEmployeeData = data.employee;
        localStorage.setItem("onboardflow_active_emp_id", currentEmployeeId);

        const emp = data.employee;
        const phases = data.phases;

        // Set Header details
        checklistName.textContent = `Onboarding Plan for ${emp.name}`;
        checklistMeta.textContent = `${emp.role} · ${emp.department} · Joining ${emp.joining_date}`;

        // Dynamic department and employment type badge styling
        const deptKey = (emp.department || "engineering").toLowerCase();
        const typeKey = (emp.employment_type || "full-time").toLowerCase();
        const typeClass = typeKey === "intern" ? "tag-type-intern" : (typeKey === "contract" ? "tag-type-contract" : "");

        // Set metadata badges with department & type theme
        checklistTags.innerHTML = `
            <span class="meta-tag tag-dept-${deptKey}">🏢 ${emp.department}</span>
            <span class="meta-tag">📍 ${emp.location}</span>
            <span class="meta-tag">🎓 ${emp.experience}</span>
            <span class="meta-tag ${typeClass}">💼 ${emp.employment_type}</span>
        `;

        // Update Phase Filter counts (Step 11)
        const countAll = document.getElementById("count-all");
        const countDay1 = document.getElementById("count-day-1");
        const countWeek1 = document.getElementById("count-week-1");
        const countDay30 = document.getElementById("count-day-30");
        const countDay90 = document.getElementById("count-day-90");

        if (countAll) countAll.textContent = data.total_tasks || 0;
        if (countDay1) countDay1.textContent = phases.day_1 ? phases.day_1.tasks.length : 0;
        if (countWeek1) countWeek1.textContent = phases.week_1 ? phases.week_1.tasks.length : 0;
        if (countDay30) countDay30.textContent = phases.day_30 ? phases.day_30.tasks.length : 0;
        if (countDay90) countDay90.textContent = phases.day_90 ? phases.day_90.tasks.length : 0;

        // Clear existing phases
        phasesContainer.innerHTML = "";

        // Iterate over the 4 phases
        const phaseKeys = ["day_1", "week_1", "day_30", "day_90"];
        phaseKeys.forEach((key) => {
            const phase = phases[key];
            if (!phase) return;

            const card = document.createElement("div");
            card.className = "phase-card";
            card.setAttribute("data-phase-key", key);

            let tasksHtml = "";
            phase.tasks.forEach((t) => {
                const priorityClass = t.priority.toLowerCase() === "high" 
                    ? "priority-high" 
                    : (t.priority.toLowerCase() === "medium" ? "priority-medium" : "priority-low");

                const isCheckedAttr = t.completed ? "checked" : "";
                const completedItemClass = t.completed ? "task-item completed" : "task-item";
                const cleanReason = t.reason.replace(/"/g, '&quot;');

                tasksHtml += `
                    <li class="${completedItemClass}" id="item-${t.id}">
                        <div class="task-checkbox-wrapper">
                            <input 
                                type="checkbox" 
                                id="task-cb-${t.id}" 
                                class="task-checkbox" 
                                data-task-id="${t.id}"
                                ${isCheckedAttr}
                            />
                        </div>
                        <div class="task-content">
                            <label for="task-cb-${t.id}" class="task-title">${t.title}</label>
                            <div class="task-meta">
                                <span class="priority-badge ${priorityClass}">${t.priority}</span>
                                <span class="owner-pill">👤 ${t.owner}</span>
                                <span class="due-date">📅 Due: ${t.due_date}</span>
                                <button type="button" class="btn-why-task" data-reason="${cleanReason}" data-title="${t.title.replace(/"/g, '&quot;')}">
                                    💡 Why this task?
                                </button>
                            </div>
                        </div>
                    </li>
                `;
            });

            card.innerHTML = `
                <div class="phase-header">
                    <div>
                        <h3 class="phase-title">${phase.label}</h3>
                        <p class="phase-desc">${phase.description}</p>
                    </div>
                    <div class="phase-header-actions">
                        <button type="button" class="btn-complete-phase" data-phase-key="${key}">
                            ⚡ Complete Phase
                        </button>
                        <span class="phase-count-badge">${phase.tasks.length} tasks</span>
                    </div>
                </div>
                <ul class="task-list">
                    ${tasksHtml}
                </ul>
            `;

            phasesContainer.appendChild(card);
        });

        // Attach event listeners to all task checkboxes for database persistence
        const checkboxes = document.querySelectorAll(".task-checkbox");
        checkboxes.forEach((cb) => {
            cb.addEventListener("change", (e) => {
                const taskId = e.target.getAttribute("data-task-id");
                const isChecked = e.target.checked;
                const taskItem = e.target.closest(".task-item");
                toggleTaskInDatabase(taskId, isChecked, taskItem);
            });
        });

        // Attach event listeners to all "Why this task?" buttons (Step 10 Modal)
        const whyButtons = document.querySelectorAll(".btn-why-task");
        whyButtons.forEach((btn) => {
            btn.addEventListener("click", () => {
                const title = btn.getAttribute("data-title");
                const reason = btn.getAttribute("data-reason");
                openWhyTaskModal(title, reason);
            });
        });

        // Attach event listeners to "⚡ Complete Phase" buttons (Step 11)
        const completePhaseButtons = document.querySelectorAll(".btn-complete-phase");
        completePhaseButtons.forEach((btn) => {
            btn.addEventListener("click", async () => {
                const card = btn.closest(".phase-card");
                if (!card) return;

                const unchecked = card.querySelectorAll(".task-checkbox:not(:checked)");
                if (unchecked.length === 0) {
                    showToast("All tasks in this phase are already completed!", "info");
                    return;
                }

                btn.disabled = true;
                btn.textContent = "Updating...";

                for (const cb of unchecked) {
                    const taskId = cb.getAttribute("data-task-id");
                    const taskItem = cb.closest(".task-item");
                    cb.checked = true;
                    await toggleTaskInDatabase(taskId, true, taskItem);
                }

                btn.disabled = false;
                btn.textContent = "⚡ Complete Phase";
                showToast(`⚡ All ${unchecked.length} tasks in this phase marked completed!`, "success");
            });
        });

        // Display current progress from database
        displayProgress(
            data.completed_tasks || 0,
            data.total_tasks || 0,
            data.progress_percentage || 0
        );

        // Reveal the checklist section
        checklistSection.classList.remove("hidden");

        // Only auto-scroll if this was triggered by form submit, not silent page refresh
        if (!isInitialLoad) {
            checklistSection.scrollIntoView({ behavior: "smooth" });
        }
    }

    // Step 11: Setup Phase Filter Tabs
    const filterButtons = document.querySelectorAll(".filter-btn");
    filterButtons.forEach((btn) => {
        btn.addEventListener("click", () => {
            filterButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            const selectedPhase = btn.getAttribute("data-phase");
            const allCards = document.querySelectorAll(".phase-card");
            allCards.forEach((c) => {
                if (selectedPhase === "all" || c.getAttribute("data-phase-key") === selectedPhase) {
                    c.style.display = "block";
                } else {
                    c.style.display = "none";
                }
            });
        });
    });

    // Auto-Restore Checklist from SQLite on Page Refresh!
    async function restoreChecklistIfSaved() {
        const savedEmpId = localStorage.getItem("onboardflow_active_emp_id");
        if (!savedEmpId) return;

        try {
            console.log(`Checking database for active employee ID: ${savedEmpId}...`);
            const response = await fetch(`/api/employee/${savedEmpId}/checklist`);
            if (response.ok) {
                const data = await response.json();
                console.log("Restored saved checklist from database:", data);
                renderChecklist(data, true);
            } else {
                localStorage.removeItem("onboardflow_active_emp_id");
            }
        } catch (err) {
            console.log("Could not auto-restore checklist:", err);
        }
    }

    // Initial Load Calls
    restoreChecklistIfSaved();
    fetchDashboardStats();

    // Handle Form Submit: Bridge to Python Backend & Save to SQLite
    if (employeeForm) {
        employeeForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            // Collect form fields
            const employeeData = {
                name: document.getElementById("employee-name").value.trim(),
                department: document.getElementById("department").value,
                role: document.getElementById("job-role").value.trim(),
                joining_date: document.getElementById("joining-date").value,
                location: document.getElementById("work-location").value,
                experience: document.getElementById("experience-level").value,
                employment_type: document.getElementById("employment-type").value
            };

            // Basic validation
            if (!employeeData.name || !employeeData.department || !employeeData.role || !employeeData.joining_date) {
                alert("Please fill in all required fields marked with *");
                return;
            }

            // Show loading state
            btnGenerate.disabled = true;
            btnText.textContent = "⚡ Generating & Saving to SQLite...";

            try {
                // HTTP POST to Python Flask backend
                const response = await fetch("/api/generate-checklist", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(employeeData)
                });

                if (!response.ok) {
                    let errorMsg = `Server error (${response.status})`;
                    try {
                        const errData = await response.json();
                        if (errData && errData.error) errorMsg = errData.error;
                    } catch (_) {
                        const rawText = await response.text();
                        if (rawText.includes("could not be found") || response.status === 404) {
                            errorMsg = "API endpoint not found (404). Backend serverless function is initializing.";
                        } else {
                            errorMsg = rawText.slice(0, 100);
                        }
                    }
                    throw new Error(errorMsg);
                }

                const data = await response.json();

                console.log("Checklist created & saved to SQLite:", data);

                // Show success feedback
                if (formFeedback) {
                    formFeedback.className = "form-feedback success";
                    formFeedback.innerHTML = `✅ <strong>Saved to SQLite!</strong> Created record #${data.employee_id} for <strong>${employeeData.name}</strong> with ${data.total_tasks} tasks. Scroll down to view!`;
                    formFeedback.classList.remove("hidden");
                }

                // Render checklist on the page
                renderChecklist(data, false);

                // Toast notification
                showToast(`🎉 Generated ${data.total_tasks} tasks for ${employeeData.name}!`, "success");

                // Update the Dashboard immediately with the new hire
                fetchDashboardStats();

            } catch (err) {
                console.error("Error communicating with backend:", err);
                if (formFeedback) {
                    formFeedback.className = "form-feedback error";
                    formFeedback.innerHTML = `❌ <strong>Error:</strong> ${err.message}`;
                    formFeedback.classList.remove("hidden");
                }
            } finally {
                // Restore button state
                btnGenerate.disabled = false;
                btnText.textContent = "Generate Personalized Checklist";
            }
        });
    }
});
