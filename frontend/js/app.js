/**
 * DeepLearnX Main Application Controller
 * Handles routing, session management, persona switching, Chart.js visualizations,
 * and remedial adaptive drilling.
 */

// Global App State
window.currentUser = null;
window.currentDomain = localStorage.getItem("deeplearnx_domain") || "pokemon";
let currentRecommendations = [];
let currentRemedialQuestions = [];
let currentRemedialConcept = "poke_dual_types";
let tierChartInstance = null;
let facultyDistChartInstance = null;
let facultyDiffChartInstance = null;

// Predefined demo personas
const DEMO_PERSONAS = {
  student_b: { id: 3, username: "student_b", full_name: "Rahul Verma", role: "student" },
  student_a: { id: 2, username: "student_a", full_name: "Ananya Sharma", role: "student" },
  student_c: { id: 4, username: "student_c", full_name: "Sneha Patel", role: "student" },
  student_d: { id: 5, username: "student_d", full_name: "Karan Singh", role: "student" },
  admin:     { id: 1, username: "admin", full_name: "Prof. Dr. R. K. Murthy", role: "faculty" }
};

document.addEventListener("DOMContentLoaded", () => {
  // Initialize default persona (Student B: False Mastery to demonstrate primary project focus)
  const savedUser = localStorage.getItem("deeplearnx_user");
  if (savedUser) {
    try {
      window.currentUser = JSON.parse(savedUser);
    } catch (e) {
      window.currentUser = DEMO_PERSONAS.student_b;
    }
  } else {
    window.currentUser = DEMO_PERSONAS.student_b;
  }

  const domainSelect = document.getElementById("domainSelect");
  if (domainSelect) domainSelect.value = window.currentDomain;

  updateUserUI();
  navigate("landing");
  loadModelInsights();
  loadAllDomainsFromDatabase();
  loadSavedApiKey();
});

function switchDomain(domainId) {
  window.currentDomain = domainId;
  localStorage.setItem("deeplearnx_domain", domainId);
  const domainSelect = document.getElementById("domainSelect");
  if (domainSelect) domainSelect.value = domainId;

  // Highlight active subject cards in UI
  document.querySelectorAll(".subject-card").forEach(card => {
    if (card.getAttribute("data-domain") === domainId) {
      card.classList.add("active-subject");
    } else {
      card.classList.remove("active-subject");
    }
  });

  // Refresh current view if needed
  const activeView = document.querySelector(".view-section.active")?.id?.replace("view-", "");
  if (activeView === "graph-map") {
    renderKnowledgeGraph(window.currentUser ? window.currentUser.id : 3, domainId);
  } else if (activeView === "dashboard") {
    loadStudentDashboard();
  } else {
    // If on assessment, landing, or any other view, load this subject's questions immediately
    startAssessmentFlow(domainId);
  }
}

// View Navigation Router
function navigate(viewName) {
  const views = document.querySelectorAll(".view-section");
  views.forEach(v => v.classList.remove("active"));

  const target = document.getElementById(`view-${viewName}`);
  if (target) {
    target.classList.add("active");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  // Update active navbar button
  const navBtns = document.querySelectorAll(".nav-item");
  navBtns.forEach(btn => {
    if (btn.getAttribute("onclick")?.includes(`'${viewName}'`)) {
      btn.classList.add("active");
    } else {
      btn.classList.remove("active");
    }
  });

  // Lifecycle hooks per view
  if (viewName === "assessment") {
    startAssessmentFlow();
  } else if (viewName === "dashboard") {
    loadStudentDashboard();
  } else if (viewName === "graph-map") {
    renderKnowledgeGraph(window.currentUser.id, window.currentDomain);
  } else if (viewName === "faculty") {
    loadFacultyDashboard();
  } else if (viewName === "recommendations") {
    if (!currentRecommendations || currentRecommendations.length === 0) {
      loadStudentRecommendations();
    }
  } else if (viewName === "model-insights") {
    loadModelInsights();
  }
}

// User Profile & Persona Management
function updateUserUI() {
  const profileDiv = document.getElementById("userProfile");
  const authBtn = document.getElementById("authBtn");
  const userNameEl = document.getElementById("userName");
  const userRoleEl = document.getElementById("userRole");
  const personaSelect = document.getElementById("personaSelect");

  if (window.currentUser) {
    profileDiv.classList.remove("hidden");
    authBtn.classList.add("hidden");
    userNameEl.textContent = window.currentUser.full_name;
    userRoleEl.textContent = capitalize(window.currentUser.role);
    if (personaSelect) personaSelect.value = window.currentUser.username;

    // Toggle faculty/student links
    const isFaculty = window.currentUser.role === "faculty";
    document.querySelectorAll(".faculty-only").forEach(el => {
      el.style.display = isFaculty ? "inline-block" : "none";
    });
    document.querySelectorAll(".student-only").forEach(el => {
      el.style.display = isFaculty ? "none" : "inline-block";
    });
  } else {
    profileDiv.classList.add("hidden");
    authBtn.classList.remove("hidden");
  }
}

function switchPersona(username) {
  if (DEMO_PERSONAS[username]) {
    window.currentUser = DEMO_PERSONAS[username];
    localStorage.setItem("deeplearnx_user", JSON.stringify(window.currentUser));
    updateUserUI();

    if (window.currentUser.role === "faculty") {
      navigate("faculty");
    } else {
      navigate("dashboard");
    }
  }
}

function logout() {
  localStorage.removeItem("deeplearnx_user");
  window.currentUser = DEMO_PERSONAS.student_b;
  updateUserUI();
  navigate("landing");
}

// Auth Forms
function toggleAuthTab(tab) {
  const loginForm = document.getElementById("loginForm");
  const registerForm = document.getElementById("registerForm");
  const tabLogin = document.getElementById("tabLogin");
  const tabRegister = document.getElementById("tabRegister");

  if (tab === "login") {
    loginForm.classList.remove("hidden");
    registerForm.classList.add("hidden");
    tabLogin.classList.add("active");
    tabRegister.classList.remove("active");
  } else {
    loginForm.classList.add("hidden");
    registerForm.classList.remove("hidden");
    tabLogin.classList.remove("active");
    tabRegister.classList.add("active");
  }
}

async function handleLogin(e) {
  e.preventDefault();
  const u = document.getElementById("loginUsername").value.trim();
  const p = document.getElementById("loginPassword").value.trim();

  try {
    const res = await API.login(u, p);
    window.currentUser = res.user;
    localStorage.setItem("deeplearnx_user", JSON.stringify(window.currentUser));
    updateUserUI();
    if (res.user.role === "faculty") {
      navigate("faculty");
    } else {
      navigate("dashboard");
    }
  } catch (err) {
    alert("Login failed: " + err.message);
  }
}

async function handleRegister(e) {
  e.preventDefault();
  const fullName = document.getElementById("regFullName").value.trim();
  const username = document.getElementById("regUsername").value.trim();
  const email = document.getElementById("regEmail").value.trim();
  const password = document.getElementById("regPassword").value.trim();

  try {
    const res = await API.register({ full_name: fullName, username, email, password, role: "student" });
    alert("Account created successfully! Please sign in.");
    toggleAuthTab("login");
  } catch (err) {
    alert("Registration failed: " + err.message);
  }
}

// Student Dashboard Loader
async function loadStudentDashboard() {
  const u = window.currentUser;
  if (!u) return;

  document.getElementById("dashStudentName").textContent = `Welcome back, ${u.full_name}`;

  try {
    // Fetch student history for active domain
    const activeDomain = window.currentDomain || "pokemon";
    const history = await API.getStudentHistory(u.id, activeDomain);
    const tbody = document.getElementById("assessmentHistoryTableBody");
    tbody.innerHTML = "";

    if (!history || history.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" class="text-center">No assessments found. Click 'Take New Assessment' above!</td></tr>`;
      return;
    }

    // Populate history table
    history.forEach(h => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${h.created_at || "Recent"}</td>
        <td><strong>${h.score}/${h.total_questions}</strong></td>
        <td>${h.accuracy}%</td>
        <td><span class="badge-tag badge-${getStateBadgeColor(h.predicted_state)}">${h.predicted_state}</span></td>
        <td>${(h.confidence * 100).toFixed(1)}%</td>
        <td class="text-red">${h.primary_gap_name || "-"}</td>
        <td>
          <button class="btn btn-sm btn-outline" onclick="inspectSession('${h.id}')">Inspect</button>
        </td>
      `;
      tbody.appendChild(tr);
    });

    // Load latest session details for dashboard charts
    const latestId = history[0].id;
    const session = await API.getSessionDetails(latestId);

    // Update dashboard summary cards
    const stateEl = document.getElementById("dashCognitiveState");
    stateEl.textContent = session.predicted_state;
    stateEl.className = `stat-value-badge badge-${getStateBadgeColor(session.predicted_state)}`;

    document.getElementById("dashScoreValue").textContent = `${session.accuracy}%`;
    document.getElementById("dashPrimaryGap").textContent = session.primary_gap_name || "None Detected";

    const fm = session.false_mastery_data || {};
    document.getElementById("dashDivergence").textContent = `${fm.tier_divergence || 0}%`;

    document.getElementById("dlConfidenceBadge").textContent = `Model Confidence: ${(session.confidence * 100).toFixed(1)}%`;
    document.getElementById("diagnosisText").textContent = fm.diagnosis || "Performance analyzed by Deep Learning model.";

    // Render Misconceptions list
    const miscList = document.getElementById("dashMisconceptionList");
    miscList.innerHTML = "";
    const miscs = session.detected_misconceptions || [];
    if (miscs.length === 0) {
      miscList.innerHTML = `<p class="text-muted">No systemic misconceptions detected.</p>`;
    } else {
      miscs.forEach(m => {
        miscList.innerHTML += `
          <div class="misc-item">
            <div class="misc-item-title">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
              ${m.name}
            </div>
            <p class="misc-item-desc">${m.description}</p>
          </div>
        `;
      });
    }

    // Save recommendations
    currentRecommendations = session.recommendations || [];
    currentRemedialConcept = session.primary_gap_id || "ann_basics";

    // Render Chart.js Multi-Tier Breakdown
    renderTierChart(fm);

  } catch (err) {
    console.error("Error loading dashboard:", err);
  }
}

async function inspectSession(sessionId) {
  try {
    const session = await API.getSessionDetails(sessionId);
    displayAssessmentResults({
      session_id: session.id,
      score: session.score,
      total_questions: session.total_questions,
      accuracy: session.accuracy,
      deep_learning_analysis: {
        predicted_state: session.predicted_state,
        confidence: session.confidence,
        state_probabilities: session.state_probabilities,
        false_mastery_breakdown: session.false_mastery_data,
        detected_misconceptions: session.detected_misconceptions,
        metrics_summary: {
          basic_accuracy: session.false_mastery_data?.basic_accuracy,
          conceptual_accuracy: session.false_mastery_data?.conceptual_accuracy,
          application_accuracy: session.false_mastery_data?.application_accuracy
        }
      },
      knowledge_gap_detection: {
        primary_gap_name: session.primary_gap_name
      },
      recommendations: session.recommendations,
      question_reviews: session.question_reviews
    });
  } catch (err) {
    alert("Could not load session details: " + err.message);
  }
}

function renderTierChart(fmData) {
  const ctx = document.getElementById("tierBreakdownChart");
  if (!ctx) return;

  if (tierChartInstance) {
    tierChartInstance.destroy();
  }

  const basic = fmData.basic_accuracy !== undefined ? fmData.basic_accuracy : 100;
  const conc = fmData.conceptual_accuracy !== undefined ? fmData.conceptual_accuracy : 80;
  const app = fmData.application_accuracy !== undefined ? fmData.application_accuracy : 20;

  tierChartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["Basic Recall (Definitions)", "Conceptual Understanding", "Application & Reasoning"],
      datasets: [{
        label: "Accuracy Score (%)",
        data: [basic, conc, app],
        backgroundColor: [
          "#38bdf8",
          "#a855f7",
          app <= 30 ? "#ef4444" : "#f59e0b"
        ],
        borderRadius: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (item) => ` Accuracy: ${item.raw}%`
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          ticks: { color: "#94a3b8" },
          grid: { color: "#334155" }
        },
        x: {
          ticks: { color: "#94a3b8" },
          grid: { display: false }
        }
      }
    }
  });
}

// Recommendations Page Loader
async function loadStudentRecommendations() {
  if (currentRecommendations && currentRecommendations.length > 0) {
    renderRecommendationsList(currentRecommendations);
    return;
  }
  // Try loading from history
  try {
    const history = await API.getStudentHistory(window.currentUser.id);
    if (history && history.length > 0) {
      const sess = await API.getSessionDetails(history[0].id);
      currentRecommendations = sess.recommendations || [];
      renderRecommendationsList(currentRecommendations);
    }
  } catch (err) {
    console.error(err);
  }
}

async function renderRecommendationsList(recs) {
  const container = document.getElementById("recommendationsList");
  if (!container) return;

  if (!recs || recs.length === 0) {
    container.innerHTML = `
      <div class="card p-4 text-center" style="padding: 2.5rem 1.5rem;">
        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🎯</div>
        <h3 style="color: #f8fafc; margin-bottom: 0.5rem;">No Active Recommendations Yet</h3>
        <p style="color: #94a3b8; max-width: 540px; margin: 0 auto 1.25rem;">
          Take an assessment to get a personalized concept breakdown, or explore the interactive Knowledge Gap Map to view prerequisite relationships.
        </p>
        <button class="btn btn-primary" onclick="navigate('select-subject')">Take an Assessment Now &rarr;</button>
      </div>
    `;
    return;
  }

  // Ensure guide info is attached for all items
  for (let r of recs) {
    if (!r.guide && r.concept_id) {
      try {
        r.guide = await API.getConceptGuide(r.concept_id, window.currentDomain || "pokemon");
      } catch (e) {
        console.warn("Could not load guide for concept:", r.concept_id);
      }
    }
  }

  container.innerHTML = recs.map(r => {
    const g = r.guide;
    const targetCid = r.concept_id || currentRemedialConcept || "math_quadratics";
    
    // Concept refresher guide card block
    let guideHtml = "";
    if (g && (g.core_idea || g.example)) {
      guideHtml = `
        <div class="concept-study-box" style="margin-top: 1rem; background: rgba(15, 23, 42, 0.85); border: 1.5px solid rgba(99, 102, 241, 0.35); border-radius: 10px; padding: 1.15rem;">
          <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 0.75rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem; color: #a5b4fc; font-weight: 700; font-size: 0.95rem;">
              <span>📖</span> Concept Refresher: ${g.name || r.concept_name || "Foundational Topic"}
            </div>
            <span class="badge-tag" style="background: rgba(99, 102, 241, 0.2); color: #c7d2fe; font-size: 0.75rem;">Study Before Testing</span>
          </div>

          <div style="display: flex; flex-direction: column; gap: 0.75rem; font-size: 0.88rem; line-height: 1.5;">
            <!-- Core Idea -->
            <div style="background: rgba(30, 41, 59, 0.6); border-left: 3px solid #38bdf8; border-radius: 6px; padding: 0.7rem 0.9rem;">
              <strong style="color: #38bdf8; display: block; margin-bottom: 0.25rem;">💡 What is it? (Core Concept):</strong>
              <span style="color: #f1f5f9;">${g.core_idea}</span>
            </div>

            <!-- Practical Real-World Example -->
            <div style="background: rgba(30, 41, 59, 0.6); border-left: 3px solid #10b981; border-radius: 6px; padding: 0.7rem 0.9rem;">
              <strong style="color: #34d399; display: block; margin-bottom: 0.25rem;">🌍 Real-World / Practical Example:</strong>
              <span style="color: #f1f5f9;">${g.example}</span>
            </div>

            <!-- Common Mistake & Golden Rule -->
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 0.6rem;">
              <div style="background: rgba(239, 68, 68, 0.08); border-left: 3px solid #ef4444; border-radius: 6px; padding: 0.6rem 0.8rem;">
                <strong style="color: #f87171; display: block; margin-bottom: 0.2rem; font-size: 0.82rem;">⚠️ Watch Out For This Trap:</strong>
                <span style="color: #cbd5e1; font-size: 0.84rem;">${g.common_mistake || "Avoid rushing through formulas without checking given problem conditions."}</span>
              </div>
              <div style="background: rgba(245, 158, 11, 0.08); border-left: 3px solid #f59e0b; border-radius: 6px; padding: 0.6rem 0.8rem;">
                <strong style="color: #fbbf24; display: block; margin-bottom: 0.2rem; font-size: 0.82rem;">🔑 Golden Rule to Remember:</strong>
                <span style="color: #cbd5e1; font-size: 0.84rem;">${g.key_takeaway || "Understand the core logic behind the formula before calculating."}</span>
              </div>
            </div>
          </div>
        </div>
      `;
    }

    return `
      <div class="rec-card card" style="margin-bottom: 1.5rem; border: 1px solid rgba(51, 65, 85, 0.8); background: #1e293b; border-radius: 14px; padding: 1.4rem;">
        <div style="display: flex; gap: 1.1rem; align-items: flex-start;">
          <div class="rec-step-num" style="background: #4f46e5; color: #fff; width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; flex-shrink: 0; font-size: 1rem;">
            ${r.step}
          </div>
          <div class="rec-content" style="flex: 1;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
              <span class="badge-tag badge-${r.urgency === "Immediate" ? "red" : (r.urgency === "High" ? "amber" : "emerald")}">${r.type}</span>
              <span style="font-size: 0.78rem; color: #94a3b8;">${r.urgency} Priority</span>
            </div>
            
            <h3 style="margin: 0.5rem 0 0.35rem; color: #f8fafc; font-size: 1.15rem;">${r.title}</h3>
            <p style="color: #cbd5e1; font-size: 0.92rem; line-height: 1.45; margin: 0 0 0.65rem;">${r.description}</p>
            
            <!-- Injected Concept Explanation & Example Box -->
            ${guideHtml}

            <!-- Action & Drill Trigger Button -->
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.75rem; margin-top: 1rem; padding-top: 0.85rem; border-top: 1px solid rgba(51, 65, 85, 0.5);">
              <div style="font-size: 0.86rem; color: #94a3b8;">
                <strong style="color: #e2e8f0;">Next Step:</strong> <span>${r.action}</span>
              </div>
              <button class="btn btn-primary btn-sm" onclick="openRemedialModal('${targetCid}')" style="display: flex; align-items: center; gap: 0.4rem;">
                <span>🎯</span> Practice This Topic (3 Qs) &rarr;
              </button>
            </div>
          </div>
        </div>
      </div>
    `;
  }).join("");
}

// Remedial Modal Drill
async function openRemedialModal(conceptId) {
  const cId = conceptId || currentRemedialConcept || "math_quadratics";
  currentRemedialConcept = cId;

  const modal = document.getElementById("remedialModal");
  const content = document.getElementById("remedialQuizContent");
  const resultBox = document.getElementById("remedialResultBox");
  const footer = document.getElementById("remedialFooter");

  resultBox.classList.add("hidden");
  footer.classList.remove("hidden");
  content.innerHTML = `<div class="p-4 text-center">Loading targeted drill questions...</div>`;
  modal.classList.remove("hidden");

  try {
    const [questions, guide] = await Promise.all([
      API.getRemedialQuestions(cId, 3, window.currentDomain || "pokemon"),
      API.getConceptGuide(cId, window.currentDomain || "pokemon").catch(() => null)
    ]);
    currentRemedialQuestions = questions;

    let guideBanner = "";
    if (guide && guide.core_idea) {
      guideBanner = `
        <div style="background: rgba(99, 102, 241, 0.12); border-left: 4px solid #6366f1; border-radius: 8px; padding: 0.9rem 1rem; margin-bottom: 1.25rem;">
          <div style="display: flex; align-items: center; gap: 0.5rem; color: #a5b4fc; font-weight: 700; font-size: 0.92rem; margin-bottom: 0.3rem;">
            <span>💡</span> Quick Reminder: ${guide.name}
          </div>
          <p style="font-size: 0.88rem; color: #cbd5e1; margin: 0 0 0.4rem; line-height: 1.45;">${guide.core_idea}</p>
          <p style="font-size: 0.84rem; color: #94a3b8; margin: 0;"><strong style="color: #34d399;">Example:</strong> ${guide.example}</p>
        </div>
      `;
    }

    content.innerHTML = guideBanner + questions.map((q, idx) => `
      <div class="card-sub mb-4" data-qid="${q.id}">
        <strong>Question ${idx + 1}: ${q.concept_name} (${q.difficulty})</strong>
        <p class="mt-1">${q.question_text}</p>
        <div class="options-container mt-2">
          ${["A", "B", "C", "D"].map(opt => `
            <label class="quiz-option">
              <input type="radio" name="rem_q_${q.id}" value="${opt}" style="margin-right: 8px;">
              <strong>${opt}:</strong> ${q.options[opt]}
            </label>
          `).join("")}
        </div>
      </div>
    `).join("");

  } catch (err) {
    content.innerHTML = `<div class="p-4 text-red">Failed to load remedial questions: ${err.message}</div>`;
  }
}

function closeRemedialModal() {
  document.getElementById("remedialModal").classList.add("hidden");
}

async function submitRemedialDrill() {
  const answers = [];
  currentRemedialQuestions.forEach(q => {
    const selected = document.querySelector(`input[name="rem_q_${q.id}"]:checked`);
    answers.push({
      question_id: q.id,
      selected_option: selected ? selected.value : "A",
      response_time: 25.0,
      confidence: 4
    });
  });

  const payload = {
    user_id: window.currentUser.id,
    domain_id: window.currentDomain || "pokemon",
    original_session_id: "sess-demo-rahul-poke-falsemastery",
    target_concept_id: currentRemedialConcept,
    answers: answers
  };

  try {
    const res = await API.submitRemedial(payload);
    const resultBox = document.getElementById("remedialResultBox");
    const content = document.getElementById("remedialQuizContent");
    const footer = document.getElementById("remedialFooter");

    content.innerHTML = "";
    resultBox.classList.remove("hidden");
    footer.classList.add("hidden");

    resultBox.innerHTML = `
      <div class="alert-box ${res.passed ? "alert-emerald badge-emerald" : "alert-amber"} p-4 text-center">
        <h2>${res.passed ? "Remedial Drill Passed!" : "Revision Recommended"}</h2>
        <div class="stat-value my-2">${res.accuracy}% Score</div>
        <p>${res.message}</p>
        <div class="mt-4">
          <button class="btn btn-primary" onclick="closeRemedialModal(); navigate('graph-map');">
            View Updated Concept Dependency Map &rarr;
          </button>
        </div>
      </div>
    `;

  } catch (err) {
    alert("Remedial submission error: " + err.message);
  }
}

// Faculty Dashboard Analytics
async function loadFacultyDashboard() {
  try {
    const dash = await API.getFacultyDashboard();

    document.getElementById("facTotalStudents").textContent = dash.total_students;
    document.getElementById("facAvgScore").textContent = `${dash.average_accuracy}%`;

    const topGap = dash.common_prerequisite_bottlenecks?.[0]?.gap || "Chain Rule";
    document.getElementById("facTopGap").textContent = topGap;

    const topMisc = dash.most_prevalent_misconceptions?.[0]?.misconception || "Chain Rule Summation";
    document.getElementById("facTopMisc").textContent = topMisc;

    // Class State Distribution Chart (Doughnut)
    renderFacultyDistributionChart(dash.state_distribution);

    // Difficult Concepts Bar Chart
    renderFacultyDifficultyChart(dash.most_difficult_concepts);

    // Student Roster Table
    const rosterBody = document.getElementById("facultyRosterTableBody");
    rosterBody.innerHTML = "";

    dash.student_roster.forEach(st => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><strong>${st.full_name}</strong></td>
        <td><code>${st.username}</code></td>
        <td>${st.accuracy !== null ? `${st.accuracy}%` : "-"}</td>
        <td><span class="badge-tag badge-${getStateBadgeColor(st.predicted_state)}">${st.predicted_state}</span></td>
        <td class="text-red">${st.primary_gap}</td>
        <td>${st.created_at}</td>
        <td>
          <button class="btn btn-sm btn-outline" onclick="viewStudentDossier('${st.username}')">Inspect</button>
        </td>
      `;
      rosterBody.appendChild(tr);
    });

  } catch (err) {
    console.error("Error loading faculty dashboard:", err);
  }
}

function viewStudentDossier(username) {
  switchPersona(username);
}

function renderFacultyDistributionChart(distData) {
  const ctx = document.getElementById("facultyStateDistChart");
  if (!ctx) return;

  if (facultyDistChartInstance) facultyDistChartInstance.destroy();

  const labels = Object.keys(distData || {});
  const vals = Object.values(distData || {});

  facultyDistChartInstance = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: labels,
      datasets: [{
        data: vals,
        backgroundColor: [
          "#10b981", // Genuine
          "#f59e0b", // False Mastery
          "#f97316", // Misconception
          "#ef4444"  // Gap
        ],
        borderWidth: 2,
        borderColor: "#1e293b"
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: "bottom",
          labels: { color: "#cbd5e1", font: { family: "Plus Jakarta Sans" } }
        }
      }
    }
  });
}

function renderFacultyDifficultyChart(concepts) {
  const ctx = document.getElementById("facultyDifficultyChart");
  if (!ctx) return;

  if (facultyDiffChartInstance) facultyDiffChartInstance.destroy();

  const labels = (concepts || []).map(c => c.concept_name);
  const failureRates = (concepts || []).map(c => c.failure_rate);

  facultyDiffChartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "Failure Rate (%)",
        data: failureRates,
        backgroundColor: "#ef4444",
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          ticks: { color: "#94a3b8" },
          grid: { color: "#334155" }
        },
        x: {
          ticks: { color: "#94a3b8" },
          grid: { display: false }
        }
      }
    }
  });
}

// Model Insights Loader
async function loadModelInsights() {
  try {
    const data = await API.getModelMetrics();
    const mets = data.evaluation_metrics || {};

    const grid = document.getElementById("metricsDisplayGrid");
    if (!grid) return;

    grid.innerHTML = `
      <div class="metric-tile">
        <span class="label">Test Set Accuracy</span>
        <div class="val">${(mets.accuracy * 100).toFixed(1)}%</div>
      </div>
      <div class="metric-tile">
        <span class="label">Macro Precision</span>
        <div class="val">${(mets.precision_macro * 100).toFixed(1)}%</div>
      </div>
      <div class="metric-tile">
        <span class="label">Macro Recall</span>
        <div class="val">${(mets.recall_macro * 100).toFixed(1)}%</div>
      </div>
      <div class="metric-tile">
        <span class="label">Macro F1-Score</span>
        <div class="val">${(mets.f1_macro * 100).toFixed(1)}%</div>
      </div>
    `;

  } catch (err) {
    console.error("Failed to load model insights:", err);
  }
}

// =============================================================================
// CUSTOM SYLLABUS & TOPIC QUESTION BANK GENERATOR
// =============================================================================

window.customDomains = window.customDomains || {};
window.selectedSyllabusFile = null;

function fillCustomTopicPreset(title, syllabusNotes) {
  const titleInput = document.getElementById("customTopicTitleInput");
  const textInput = document.getElementById("customSyllabusTextInput");
  if (titleInput) titleInput.value = title;
  if (textInput) textInput.value = syllabusNotes;
  
  const statusBanner = document.getElementById("customGenStatusBanner");
  if (statusBanner) statusBanner.style.display = "none";
}

function handleSyllabusFileSelected(event) {
  const file = event.target.files && event.target.files[0];
  if (!file) return;

  window.selectedSyllabusFile = file;
  const notice = document.getElementById("fileSelectedNotice");
  if (notice) {
    notice.style.display = "block";
    notice.textContent = `✓ Document selected: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
  }

  // If text-like file, auto-extract text preview into textarea
  if (file.name.match(/\.(txt|json|md|csv)$/i)) {
    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target.result;
      const textInput = document.getElementById("customSyllabusTextInput");
      if (textInput && !textInput.value) {
        textInput.value = text.slice(0, 3000);
      }
    };
    reader.readAsText(file);
  }

  // Autofill topic title if empty
  const titleInput = document.getElementById("customTopicTitleInput");
  if (titleInput && !titleInput.value) {
    const rawName = file.name.replace(/\.[^/.]+$/, "").replace(/[_-]/g, " ");
    titleInput.value = rawName.charAt(0).toUpperCase() + rawName.slice(1);
  }
}

async function handleCustomSyllabusSubmit(event) {
  if (event) event.preventDefault();

  const titleInput = document.getElementById("customTopicTitleInput");
  const textInput = document.getElementById("customSyllabusTextInput");
  const btn = document.getElementById("generateSyllabusBtn");
  const btnText = document.getElementById("generateBtnText");
  const statusBanner = document.getElementById("customGenStatusBanner");

  const topicTitle = titleInput ? titleInput.value.trim() : "";
  const syllabusText = textInput ? textInput.value.trim() : "";

  if (!topicTitle) {
    alert("Please enter a Topic Name or Subject Title.");
    return;
  }

  // Loading UI
  if (btn) btn.disabled = true;
  if (btnText) btnText.textContent = "Synthesizing Question Bank & Prerequisite DAG...";
  if (statusBanner) {
    statusBanner.style.display = "block";
    statusBanner.style.background = "rgba(99, 102, 241, 0.15)";
    statusBanner.style.border = "1px solid #6366f1";
    statusBanner.style.color = "#c7d2fe";
    statusBanner.innerHTML = `
      <div style="display: flex; align-items: center; gap: 0.75rem;">
        <span class="spinner" style="display: inline-block; width: 18px; height: 18px; border: 2px solid #6366f1; border-top-color: transparent; border-radius: 50%; animation: spin 1s linear infinite;"></span>
        <span>Synthesizing 12 tiered diagnostic questions, concept dependency DAG, and misconception rules for <strong>${topicTitle}</strong>...</span>
      </div>
    `;
  }

  try {
    let result;
    const apiKey = localStorage.getItem("deeplearnx_ai_api_key") || document.getElementById("aiApiKeyInput")?.value?.trim() || null;
    const apiProvider = localStorage.getItem("deeplearnx_ai_provider") || document.getElementById("aiProviderSelect")?.value || "gemini";

    if (window.selectedSyllabusFile && window.selectedSyllabusFile.name.match(/\.(pdf)$/i)) {
      result = await API.uploadSyllabusFile(topicTitle, window.selectedSyllabusFile, apiKey, apiProvider);
    } else {
      const userId = window.currentUser ? window.currentUser.id : null;
      result = await API.customGenerateAssessment(topicTitle, syllabusText, userId, 12, apiKey, apiProvider);
    }

    // Success UI
    if (statusBanner) {
      statusBanner.style.background = "rgba(16, 185, 129, 0.15)";
      statusBanner.style.border = "1px solid #10b981";
      statusBanner.style.color = "#6ee7b7";
      statusBanner.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.75rem;">
          <div>
            <strong>✨ Successfully Generated!</strong>
            <p style="margin: 0.25rem 0 0; font-size: 0.85rem; color: #cbd5e1;">
              Created <strong>${result.concepts_count} concepts</strong>, <strong>${result.questions_count} diagnostic questions</strong>, and registered prerequisite DAG for <strong>${result.name}</strong>.
            </p>
          </div>
          <button class="btn btn-primary btn-sm" onclick="startAssessmentFlow('${result.domain_id}')" style="background: #10b981; border-color: #10b981;">
            Launch Assessment Now &rarr;
          </button>
        </div>
      `;
    }

    // Register in custom domains map
    window.customDomains[result.domain_id] = result;

    // Append custom card to subject hub grid
    renderCustomSubjectCard(result);

    // Also update domain select in navbar
    const domainSelect = document.getElementById("domainSelect");
    if (domainSelect) {
      const optExists = Array.from(domainSelect.options).some(o => o.value === result.domain_id);
      if (!optExists) {
        const newOpt = document.createElement("option");
        newOpt.value = result.domain_id;
        newOpt.textContent = `${result.icon || '✨'} ${result.name}`;
        domainSelect.appendChild(newOpt);
      }
      domainSelect.value = result.domain_id;
    }

  } catch (err) {
    if (statusBanner) {
      statusBanner.style.background = "rgba(239, 68, 68, 0.15)";
      statusBanner.style.border = "1px solid #ef4444";
      statusBanner.style.color = "#fca5a5";
      statusBanner.innerHTML = `<strong>Error generating assessment:</strong> ${err.message}`;
    }
  } finally {
    if (btn) btn.disabled = false;
    if (btnText) btnText.textContent = "Generate Custom Question Bank & DAG";
  }
}

function renderCustomSubjectCard(domainMeta) {
  const grid = document.getElementById("subjectHubGrid");
  if (!grid) return;

  const cardId = domainMeta.domain_id || domainMeta.id;
  // Check if card already exists
  const existingCard = document.getElementById(`card-${cardId}`);
  if (existingCard) return;

  const name = domainMeta.name;
  const icon = domainMeta.icon || "✨";
  const desc = domainMeta.description || "Custom synthesized diagnostic assessment.";
  const qCount = domainMeta.questions_count || 12;

  const conceptBadges = (domainMeta.concepts || []).map(c => 
    `<span class="badge-tag">${c.name.split(':')[0]}</span>`
  ).join("") || `<span class="badge-tag">Custom Curriculum</span>`;

  const cardEl = document.createElement("div");
  cardEl.id = `card-${cardId}`;
  cardEl.className = "subject-card card";
  cardEl.setAttribute("data-domain", cardId);
  cardEl.style.cssText = "background: #1e293b; border: 2px solid #6366f1; border-radius: 14px; padding: 1.5rem; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 8px 24px rgba(99, 102, 241, 0.2);";

  cardEl.innerHTML = `
    <div>
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
        <span style="font-size: 2.2rem;">${icon}</span>
        <span class="badge-tag badge-emerald" style="font-size: 0.75rem;">✨ Custom Generated (${qCount} Qs)</span>
      </div>
      <h3 style="color: #818cf8; font-size: 1.25rem; margin-bottom: 0.5rem;">${name}</h3>
      <p style="color: #cbd5e1; font-size: 0.9rem; line-height: 1.4; margin-bottom: 1rem;">
        ${desc}
      </p>
      <div style="font-size: 0.8rem; color: #94a3b8; margin-bottom: 1.25rem;">
        <strong>DAG Concepts:</strong>
        <div style="display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.4rem;">
          ${conceptBadges}
        </div>
      </div>
    </div>
    <button class="btn btn-primary" style="width: 100%; background: linear-gradient(135deg, #6366f1, #4f46e5); border: none;" onclick="startAssessmentFlow('${cardId}')">
      Start Custom Assessment &rarr;
    </button>
  `;

  // Prepend to top of grid
  grid.prepend(cardEl);
}

// Auto-load all domains including custom ones from database
async function loadAllDomainsFromDatabase() {
  try {
    const domains = await API.getDomains();
    const domainSelect = document.getElementById("domainSelect");
    
    domains.forEach(d => {
      if (d.id && d.id.startsWith("custom_")) {
        window.customDomains[d.id] = d;
        renderCustomSubjectCard(d);

        if (domainSelect) {
          const exists = Array.from(domainSelect.options).some(o => o.value === d.id);
          if (!exists) {
            const opt = document.createElement("option");
            opt.value = d.id;
            opt.textContent = `${d.icon || '✨'} ${d.name}`;
            domainSelect.appendChild(opt);
          }
        }
      }
    });
  } catch (e) {
    console.error("Error loading domains:", e);
  }
}

// AI API Key UI Management
function toggleApiKeyConfig() {
  const body = document.getElementById("apiKeyConfigBody");
  const icon = document.getElementById("apiKeyToggleIcon");
  if (!body) return;
  const isHidden = body.style.display === "none";
  body.style.display = isHidden ? "block" : "none";
  if (icon) icon.textContent = isHidden ? "▲ Close Settings" : "▼ Configure Key";
}

function toggleApiKeyVisibility() {
  const input = document.getElementById("aiApiKeyInput");
  const eye = document.getElementById("apiKeyEyeIcon");
  if (!input) return;
  if (input.type === "password") {
    input.type = "text";
    if (eye) eye.textContent = "🙈 Hide";
  } else {
    input.type = "password";
    if (eye) eye.textContent = "👁️ Show";
  }
}

function saveApiKeyToStorage() {
  const input = document.getElementById("aiApiKeyInput");
  const provider = document.getElementById("aiProviderSelect");
  const badge = document.getElementById("apiKeySavedBadge");
  const key = input ? input.value.trim() : "";
  const prov = provider ? provider.value : "gemini";
  
  if (key) {
    localStorage.setItem("deeplearnx_ai_api_key", key);
    localStorage.setItem("deeplearnx_ai_provider", prov);
    if (badge) {
      badge.style.display = "inline";
      badge.textContent = `✓ ${prov.toUpperCase()} Key Saved in Browser`;
      badge.style.color = "#10b981";
      setTimeout(() => { badge.style.display = "none"; }, 4000);
    }
  } else {
    localStorage.removeItem("deeplearnx_ai_api_key");
    if (badge) {
      badge.style.display = "inline";
      badge.textContent = "Cleared Saved Key";
      badge.style.color = "#94a3b8";
      setTimeout(() => { badge.style.display = "none"; }, 3000);
    }
  }
}

function handleAiProviderChange() {
  const provider = document.getElementById("aiProviderSelect");
  const input = document.getElementById("aiApiKeyInput");
  if (provider && input) {
    if (provider.value === "openai") {
      input.placeholder = "Enter OpenAI API Key (sk-...)";
    } else {
      input.placeholder = "Enter Gemini API Key (AIzaSy...)";
    }
  }
}

function loadSavedApiKey() {
  const savedKey = localStorage.getItem("deeplearnx_ai_api_key");
  const savedProv = localStorage.getItem("deeplearnx_ai_provider") || "gemini";
  const input = document.getElementById("aiApiKeyInput");
  const provider = document.getElementById("aiProviderSelect");
  const badge = document.getElementById("apiKeySavedBadge");
  if (input && savedKey) {
    input.value = savedKey;
    if (badge) {
      badge.style.display = "inline";
      badge.textContent = "✓ Key Loaded from Storage";
      badge.style.color = "#10b981";
    }
  }
  if (provider && savedProv) {
    provider.value = savedProv;
    handleAiProviderChange();
  }
}

