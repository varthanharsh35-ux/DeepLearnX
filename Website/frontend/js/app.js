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
  // Always initialize as unauthenticated visitor so the public Overview landing page is shown
  window.currentUser = null;
  localStorage.removeItem("deeplearnx_user");

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
function updateNavbarState(viewName) {
  const navLinks = document.getElementById("navLinks");
  const demoSwitcher = document.getElementById("demoSwitcher");
  const authActions = document.getElementById("authActions");
  const userProfile = document.getElementById("userProfile");
  const authNavBack = document.getElementById("authNavBack");

  if (viewName === "auth") {
    // When on login/auth page: completely unclutter navbar!
    if (navLinks) navLinks.style.display = "none";
    if (demoSwitcher) demoSwitcher.style.display = "none";
    if (authActions) authActions.style.display = "none";
    if (userProfile) userProfile.style.display = "none";
    if (authNavBack) authNavBack.classList.remove("hidden");
  } else {
    // On regular views:
    if (authNavBack) authNavBack.classList.add("hidden");
    if (navLinks) navLinks.style.display = "flex";

    if (window.currentUser) {
      if (demoSwitcher) demoSwitcher.style.display = "flex";
      if (authActions) authActions.style.display = "none";
      if (userProfile) {
        userProfile.style.display = "flex";
        userProfile.classList.remove("hidden");
      }
      const isFaculty = window.currentUser.role === "faculty";
      document.querySelectorAll(".faculty-only").forEach(el => el.style.display = isFaculty ? "inline-block" : "none");
      document.querySelectorAll(".student-only").forEach(el => el.style.display = isFaculty ? "none" : "inline-block");
    } else {
      // Unauthenticated public view: show only public tabs (Overview, DL Model Architecture)
      if (demoSwitcher) demoSwitcher.style.display = "none";
      if (authActions) authActions.style.display = "flex";
      if (userProfile) {
        userProfile.style.display = "none";
        userProfile.classList.add("hidden");
      }
      document.querySelectorAll(".faculty-only").forEach(el => el.style.display = "none");
      document.querySelectorAll(".student-only").forEach(el => el.style.display = "none");
    }
  }
}

function navigate(viewName) {
  const protectedViews = ["dashboard", "graph-map", "select-subject", "recommendations", "faculty"];
  if (protectedViews.includes(viewName) && !window.currentUser) {
    viewName = "auth";
  }

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

  // Dynamically update navbar tabs & switcher visibility based on view and auth state
  updateNavbarState(viewName);

  // Lifecycle hooks per view
  if (viewName === "assessment") {
    startAssessmentFlow();
  } else if (viewName === "dashboard") {
    if (!window.currentUser) {
      navigate("auth");
      return;
    }
    loadStudentDashboard();
  } else if (viewName === "graph-map") {
    const uid = window.currentUser ? window.currentUser.id : 3;
    renderKnowledgeGraph(uid, window.currentDomain, window.inspectedSessionId || null);
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
  const userNameEl = document.getElementById("userName");
  const userRoleEl = document.getElementById("userRole");
  const navAvatarEl = document.getElementById("navUserAvatar");

  if (window.currentUser) {
    if (userNameEl) userNameEl.textContent = window.currentUser.full_name;
    if (userRoleEl) userRoleEl.textContent = capitalize(window.currentUser.role);
    if (navAvatarEl) {
      const parts = (window.currentUser.full_name || "User").trim().split(" ");
      const initials = parts.length > 1 ? (parts[0][0] + parts[1][0]).toUpperCase() : parts[0].slice(0, 2).toUpperCase();
      navAvatarEl.textContent = initials;
    }
  }

  const activeView = document.querySelector(".view-section.active")?.id?.replace("view-", "") || "landing";
  updateNavbarState(activeView);
}

function switchPersona(username) {
  if (DEMO_PERSONAS[username]) {
    window.currentUser = DEMO_PERSONAS[username];
    window.inspectedSessionId = null;
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
  window.currentUser = null;
  window.inspectedSessionId = null;
  updateUserUI();
  navigate("landing");
}

// Password Visibility Toggle
function togglePasswordVisibility(inputId, iconId) {
  const input = document.getElementById(inputId);
  const iconSpan = document.getElementById(iconId);
  if (!input || !iconSpan) return;

  if (input.type === "password") {
    input.type = "text";
    iconSpan.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>`;
  } else {
    input.type = "password";
    iconSpan.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>`;
  }
}

// 1-Click Evaluator Demo Autofill
function quickFillLogin(username, password) {
  const uInput = document.getElementById("loginUsername");
  const pInput = document.getElementById("loginPassword");
  if (uInput && pInput) {
    uInput.value = username;
    pInput.value = password;
    const form = document.getElementById("loginForm");
    if (form) {
      form.dispatchEvent(new Event("submit", { cancelable: true }));
    }
  }
}

// Social Single Sign-On (Authentic Google / Microsoft Account Chooser)
let currentOAuthProvider = "Google";

function handleSocialAuthClick(provider) {
  currentOAuthProvider = provider.toLowerCase() === "microsoft" ? "Microsoft" : "Google";
  const modal = document.getElementById("oauthModal");
  if (!modal) return;
  modal.style.display = "flex";
  modal.classList.remove("hidden");

  // Reset to Account List View
  hideOAuthCustomInput();

  const title = document.getElementById("oauthModalTitle");
  const subtitle = document.getElementById("oauthModalSubtitle");
  const consent = document.getElementById("oauthConsentNotice");
  const iconContainer = document.getElementById("oauthProviderIcon");

  if (currentOAuthProvider === "Google") {
    if (title) title.textContent = "Sign in with Google";
    if (subtitle) subtitle.innerHTML = `Choose an account to continue to <strong style="color: #1f1f1f;">DeepLearnX</strong>`;
    if (iconContainer) {
      iconContainer.innerHTML = `<svg width="36" height="36" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/></svg>`;
    }
    if (consent) {
      consent.innerHTML = `To continue, Google will share your name, email address, language preference, and profile picture with <strong>DeepLearnX</strong>. Before using this app, you can review DeepLearnX's <a href="javascript:void(0)" onclick="alert('DeepLearnX Privacy Policy: Student diagnostic sessions are stored securely.')" style="color: #1a73e8; text-decoration: none;">Privacy Policy</a> and <a href="javascript:void(0)" onclick="alert('DeepLearnX Terms: Open educational diagnostic engine.')" style="color: #1a73e8; text-decoration: none;">Terms of Service</a>.`;
    }
  } else {
    if (title) title.textContent = "Sign in to Microsoft";
    if (subtitle) subtitle.innerHTML = `Pick an account to continue to <strong style="color: #1f1f1f;">DeepLearnX</strong>`;
    if (iconContainer) {
      iconContainer.innerHTML = `<svg width="34" height="34" viewBox="0 0 23 23"><path fill="#f35325" d="M1 1h10v10H1z"/><path fill="#81bc06" d="M12 1h10v10H12z"/><path fill="#05a6f0" d="M1 12h10v10H1z"/><path fill="#ffba08" d="M12 12h10v10H12z"/></svg>`;
    }
    if (consent) {
      consent.innerHTML = `You are signing in with Microsoft Identity Services. Microsoft will share your profile name and email with <strong>DeepLearnX</strong>.`;
    }
  }
}

function closeOAuthModal() {
  const modal = document.getElementById("oauthModal");
  if (modal) {
    modal.style.display = "none";
    modal.classList.add("hidden");
  }
}

function showOAuthCustomInput() {
  const listView = document.getElementById("oauthAccountListView");
  const inputView = document.getElementById("oauthCustomInputView");
  if (listView) listView.style.display = "none";
  if (inputView) {
    inputView.style.display = "block";
    const nameInput = document.getElementById("oauthCustomFullName");
    if (nameInput) setTimeout(() => nameInput.focus(), 50);
  }
}

function hideOAuthCustomInput() {
  const listView = document.getElementById("oauthAccountListView");
  const inputView = document.getElementById("oauthCustomInputView");
  if (listView) listView.style.display = "block";
  if (inputView) inputView.style.display = "none";
}

async function selectOAuthAccount(provider, email, fullName) {
  try {
    const res = await API.oauthLogin(provider, email, fullName);
    window.currentUser = res.user;
    localStorage.setItem("deeplearnx_user", JSON.stringify(res.user));
    closeOAuthModal();
    updateUserUI();
    navigate("dashboard");
  } catch (err) {
    alert("Single Sign-On authentication error: " + err.message);
  }
}

async function submitCustomOAuthAccount() {
  const fullName = document.getElementById("oauthCustomFullName")?.value.trim();
  const email = document.getElementById("oauthCustomEmail")?.value.trim();
  if (!fullName || !email) {
    alert("Please enter both your name and email address to continue.");
    return;
  }
  const submitBtn = document.getElementById("oauthCustomSubmitBtn");
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.textContent = "Signing in...";
  }
  try {
    await selectOAuthAccount(currentOAuthProvider, email, fullName);
  } finally {
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.textContent = "Next →";
    }
  }
}

async function submitStandardOAuth() {
  const emailInput = document.getElementById("oauthEmailInput");
  const email = emailInput ? emailInput.value.trim() : "";
  if (!email) {
    alert("Please enter your email or phone to sign in.");
    return;
  }
  
  let name = "Google User";
  if (email.includes("@")) {
    const userPart = email.split("@")[0];
    if (userPart.toLowerCase().includes("harsh")) {
      name = "Harsha";
    } else {
      name = userPart.replace(/[._0-9]/g, ' ').trim();
      name = name ? name.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ') : "Google User";
    }
  }

  const submitBtn = document.getElementById("oauthSubmitBtn");
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.textContent = "Signing in...";
  }

  try {
    await selectOAuthAccount("Google", email, name);
  } finally {
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.textContent = "Next";
    }
  }
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
async function loadStudentDashboard(isReset = false) {
  const u = window.currentUser;
  if (!u) {
    navigate("auth");
    return;
  }

  const studentNameEl = document.getElementById("dashStudentName");
  if (studentNameEl) {
    studentNameEl.textContent = `Welcome back, ${u.full_name}`;
  }

  try {
    // 1. Fetch & display User Profile Dossier
    const profileRes = await API.getUserProfile(u.id);
    const userMeta = profileRes.user || profileRes;
    const statsMeta = profileRes.stats || {};

    const avatarEl = document.getElementById("dossierAvatar");
    if (avatarEl) avatarEl.textContent = userMeta.avatar_initials || "ST";

    const nameEl = document.getElementById("dossierFullName");
    if (nameEl) nameEl.textContent = userMeta.full_name;

    const emailEl = document.getElementById("dossierEmail");
    if (emailEl) emailEl.textContent = userMeta.email || `${userMeta.username}@deeplearnx.edu`;

    const roleBadge = document.getElementById("dossierRoleBadge");
    if (roleBadge) {
      roleBadge.textContent = capitalize(userMeta.role);
      roleBadge.className = `badge-tag ${userMeta.role === "faculty" ? "badge-blue" : "badge-emerald"}`;
    }

    const totalTestsEl = document.getElementById("dossierTotalTests");
    if (totalTestsEl) totalTestsEl.textContent = statsMeta.total_assessments || 0;

    const avgAccEl = document.getElementById("dossierAvgAccuracy");
    if (avgAccEl) avgAccEl.textContent = `${statsMeta.average_accuracy || 0}%`;

    const latestStateEl = document.getElementById("dossierCurrentState");
    if (latestStateEl) {
      latestStateEl.textContent = statsMeta.latest_state || "Ready";
      latestStateEl.className = `stat-value-badge badge-${getStateBadgeColor(statsMeta.latest_state || "Ready")}`;
    }

    // 2. Fetch student history across ALL domains
    const history = await API.getStudentHistory(u.id, null);
    const tbody = document.getElementById("assessmentHistoryTableBody");
    tbody.innerHTML = "";

    if (!history || history.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="8" style="padding: 3rem 1.5rem; text-align: center; background: rgba(15, 23, 42, 0.4);">
            <div style="font-size: 2.2rem; margin-bottom: 0.5rem;">🎯</div>
            <h4 style="margin: 0 0 0.4rem; color: #f8fafc; font-size: 1.15rem;">No Assessments Recorded Yet</h4>
            <p style="margin: 0 auto 1.25rem; max-width: 500px; color: #94a3b8; font-size: 0.88rem; line-height: 1.5;">
              Welcome, <strong>${userMeta.full_name}</strong>! You haven't taken any diagnostic quizzes yet. Select any subject or generate a custom topic to launch your first cognitive assessment and build your personalized Knowledge Gap Map!
            </p>
            <button class="btn btn-primary btn-sm" onclick="navigate('select-subject')" style="padding: 0.55rem 1.25rem; font-weight: 600;">
              ⚡ Launch Your First Assessment &rarr;
            </button>
          </td>
        </tr>
      `;
      document.getElementById("dashCognitiveState").textContent = "Ready to Begin";
      document.getElementById("dashCognitiveState").className = "stat-value-badge badge-blue";
      document.getElementById("dashScoreValue").textContent = "0.0%";
      document.getElementById("dashPrimaryGap").textContent = "None (Take Test)";
      document.getElementById("dashDivergence").textContent = "0.0%";
      document.getElementById("dashMisconceptionList").innerHTML = `<p class="text-muted" style="padding: 1rem 0; text-align: center;">Take your first assessment to analyze potential misconceptions and prerequisite gaps.</p>`;
      if (tierChartInstance) {
        tierChartInstance.destroy();
        tierChartInstance = null;
      }
      return;
    }

    // 3. Populate history table with multi-subject badges and "Inspect in Dashboard"
    history.forEach(h => {
      const tr = document.createElement("tr");
      tr.id = `history-row-${h.id}`;
      tr.style.cursor = "pointer";
      tr.title = "Click to reflect this subject throughout the entire platform";
      tr.addEventListener("click", (e) => {
        if (!e.target.closest("button")) {
          inspectSessionInDashboard(h.id);
        }
      });
      const domainName = h.domain_name || h.domain_id;
      const domainIcon = h.domain_icon || "📚";
      tr.innerHTML = `
        <td style="white-space: nowrap; font-size: 0.85rem; color: #cbd5e1;">${h.created_at || "Recent"}</td>
        <td>
          <span class="subject-badge" style="display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.25rem 0.6rem; border-radius: 6px; background: rgba(99, 102, 241, 0.15); border: 1px solid rgba(99, 102, 241, 0.3); font-size: 0.82rem; font-weight: 600; color: #c7d2fe;">
            <span>${domainIcon}</span> ${domainName}
          </span>
        </td>
        <td><strong>${h.score}/${h.total_questions}</strong></td>
        <td><strong>${h.accuracy}%</strong></td>
        <td><span class="badge-tag badge-${getStateBadgeColor(h.predicted_state)}">${h.predicted_state}</span></td>
        <td style="font-size: 0.85rem; color: #94a3b8;">${(h.confidence * 100).toFixed(1)}%</td>
        <td class="text-red" style="font-weight: 500;">${h.primary_gap_name || "-"}</td>
        <td>
          <div style="display: flex; gap: 0.4rem; align-items: center; flex-wrap: wrap;">
            <button class="btn btn-sm btn-primary" onclick="inspectSessionInDashboard('${h.id}')" title="Reflect this past quiz across the entire dashboard">Inspect in Dashboard ↗</button>
            <button class="btn btn-sm btn-outline" onclick="inspectSession('${h.id}')" title="Review questions and answer drill">Review 👁</button>
          </div>
        </td>
      `;
      tbody.appendChild(tr);
    });

    // 4. Default reflection: Reflect latest session if not explicitly inspecting a past quiz
    const banner = document.getElementById("subjectReflectionBanner");
    const isBannerVisible = banner && banner.style.display !== "none";
    if (isReset || !isBannerVisible) {
      const latestId = history[0].id;
      await reflectSessionData(latestId, false);
    }

  } catch (err) {
    console.error("Error loading dashboard:", err);
  }
}

// Global Subject & Past Quiz Reflection Engine
async function reflectSessionData(sessionId, isExplicitInspection = true) {
  try {
    const session = await API.getSessionDetails(sessionId);
    if (!session) return;

    // Update active domain
    window.currentDomain = session.domain_id;
    localStorage.setItem("deeplearnx_domain", session.domain_id);
    const domainSelect = document.getElementById("domainSelect");
    if (domainSelect) domainSelect.value = session.domain_id;

    // Reflection Alert Banner
    const banner = document.getElementById("subjectReflectionBanner");
    if (banner) {
      if (isExplicitInspection) {
        banner.style.display = "flex";
        const titleEl = document.getElementById("reflectSubjectTitle");
        const dateEl = document.getElementById("reflectSessionDate");
        if (titleEl) titleEl.textContent = `${session.domain_icon || '📚'} ${session.domain_name || session.domain_id}`;
        if (dateEl) dateEl.textContent = `${session.created_at || 'Recorded Assessment'} (Score: ${session.accuracy}%)`;
      } else {
        banner.style.display = "none";
      }
    }

    // Highlight active history row
    document.querySelectorAll("#assessmentHistoryTableBody tr").forEach(r => r.style.backgroundColor = "");
    const activeRow = document.getElementById(`history-row-${session.id}`);
    if (activeRow) activeRow.style.backgroundColor = "rgba(99, 102, 241, 0.15)";

    // Update dashboard summary cards
    const stateEl = document.getElementById("dashCognitiveState");
    if (stateEl) {
      stateEl.textContent = session.predicted_state;
      stateEl.className = `stat-value-badge badge-${getStateBadgeColor(session.predicted_state)}`;
    }

    const scoreEl = document.getElementById("dashScoreValue");
    if (scoreEl) scoreEl.textContent = `${session.accuracy}%`;

    const gapEl = document.getElementById("dashPrimaryGap");
    if (gapEl) gapEl.textContent = session.primary_gap_name || "None Detected";

    const fm = session.false_mastery_data || {};
    const divEl = document.getElementById("dashDivergence");
    if (divEl) divEl.textContent = `${fm.tier_divergence || 0}%`;

    const confEl = document.getElementById("dlConfidenceBadge");
    if (confEl) confEl.textContent = `Model Confidence: ${(session.confidence * 100).toFixed(1)}%`;

    const diagEl = document.getElementById("diagnosisText");
    if (diagEl) diagEl.textContent = fm.diagnosis || "Performance analyzed by Deep Learning model.";

    // Render Misconceptions list
    const miscList = document.getElementById("dashMisconceptionList");
    if (miscList) {
      miscList.innerHTML = "";
      const miscs = session.detected_misconceptions || [];
      if (miscs.length === 0) {
        miscList.innerHTML = `<p class="text-muted">No systemic misconceptions detected for this assessment.</p>`;
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
    }

    // Save recommendations and remedial concept for this subject
    currentRecommendations = session.recommendations || [];
    currentRemedialConcept = session.primary_gap_id || "ann_basics";

    // Render Chart.js Multi-Tier Breakdown
    renderTierChart(fm);

    // Reflect session directly onto Vis.js Concept Dependency Graph Map
    renderKnowledgeGraph(session.user_id, session.domain_id, session.id);

    if (isExplicitInspection) {
      const targetScroll = banner || document.getElementById("dashStudentName");
      if (targetScroll) {
        targetScroll.scrollIntoView({ behavior: "smooth", block: "center" });
      }
    }

  } catch (err) {
    console.error("Error reflecting session details:", err);
  }
}

async function inspectSessionInDashboard(sessionId) {
  window.inspectedSessionId = sessionId;
  await reflectSessionData(sessionId, true);
}

function resetDashboardToLatest() {
  window.inspectedSessionId = null;
  const banner = document.getElementById("subjectReflectionBanner");
  if (banner) banner.style.display = "none";
  loadStudentDashboard(true);
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
    const targetCid = r.concept_id || currentRemedialConcept || "";
    
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
              <button class="btn btn-primary btn-sm" onclick="openRemedialModal('${targetCid}', '${window.currentDomain || ''}')" style="display: flex; align-items: center; gap: 0.4rem;">
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
async function openRemedialModal(conceptId, domainId) {
  const activeDomain = domainId || window.currentDomain || "pokemon";
  const cId = conceptId || currentRemedialConcept || "";
  currentRemedialConcept = cId;

  const modal = document.getElementById("remedialModal");
  const content = document.getElementById("remedialQuizContent");
  const resultBox = document.getElementById("remedialResultBox");
  const footer = document.getElementById("remedialFooter");

  resultBox.classList.add("hidden");
  footer.classList.remove("hidden");
  content.innerHTML = `<div class="p-4 text-center">Loading targeted drill questions for active topic...</div>`;
  modal.classList.remove("hidden");

  try {
    const [questions, guide] = await Promise.all([
      API.getRemedialQuestions(cId, 3, activeDomain),
      (cId ? API.getConceptGuide(cId, activeDomain).catch(() => null) : Promise.resolve(null))
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
  let stageTimer = null;
  if (statusBanner) {
    statusBanner.style.display = "block";
    statusBanner.style.background = "rgba(99, 102, 241, 0.15)";
    statusBanner.style.border = "1px solid #6366f1";
    statusBanner.style.color = "#c7d2fe";
    statusBanner.innerHTML = `
      <div style="display: flex; align-items: center; gap: 0.75rem;">
        <span class="spinner" style="display: inline-block; width: 18px; height: 18px; border: 2px solid #6366f1; border-top-color: transparent; border-radius: 50%; animation: spin 1s linear infinite;"></span>
        <span id="customGenStatusText">🔍 Researching global encyclopedic knowledge for <strong>${topicTitle}</strong>...</span>
      </div>
    `;

    let stageIndex = 0;
    const stages = [
      `🔍 Researching global encyclopedic knowledge for <strong>${topicTitle}</strong>...`,
      `🧠 Synthesizing 4 progressive concept modules & prerequisite DAG for <strong>${topicTitle}</strong>...`,
      `📝 Formulating 12 tiered diagnostic questions with Two-Tier Reasoning Probes...`,
      `⚙️ Calibrating answer options and cognitive misconception rules...`
    ];
    stageTimer = setInterval(() => {
      stageIndex = (stageIndex + 1) % stages.length;
      const statusText = document.getElementById("customGenStatusText");
      if (statusText) statusText.innerHTML = stages[stageIndex];
    }, 1400);
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

    if (stageTimer) clearInterval(stageTimer);

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
    if (stageTimer) clearInterval(stageTimer);
    if (statusBanner) {
      statusBanner.style.background = "rgba(239, 68, 68, 0.15)";
      statusBanner.style.border = "1px solid #ef4444";
      statusBanner.style.color = "#fca5a5";
      statusBanner.innerHTML = `<strong>Error generating assessment:</strong> ${err.message}`;
    }
  } finally {
    if (stageTimer) clearInterval(stageTimer);
    if (btn) btn.disabled = false;
    if (btnText) btnText.textContent = "Generate Custom Question Bank & DAG";
  }
}

// Auto-load custom domain metadata without cluttering the default 5 subjects
async function loadAllDomainsFromDatabase() {
  try {
    const domains = await API.getDomains();
    domains.forEach(d => {
      if (d.id && d.id.startsWith("custom_")) {
        window.customDomains[d.id] = d;
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

