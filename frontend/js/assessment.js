/**
 * DeepLearnX Live Assessment Controller
 * Coordinates assessment questions, timers, confidence indicators, and backend inference
 */

let currentQuestions = [];
let currentQIndex = 0;
let userAnswers = {}; // { question_id: { selected_option, response_time, confidence } }
let questionTimerInterval = null;
let secondsOnCurrentQ = 0;

const DOMAIN_NAMES = {
  pokemon: "🎮 Pokemon Battle Mechanics",
  class10_chemistry: "🧪 Class 10 Chemistry",
  class10_biology: "🧬 Class 10 Biology",
  class10_math: "📐 Class 10 Mathematics",
  deep_learning: "🤖 Deep Learning Fundamentals"
};

async function startAssessmentFlow(explicitDomain = null) {
  if (explicitDomain) {
    window.currentDomain = explicitDomain;
    localStorage.setItem("deeplearnx_domain", explicitDomain);
    const domainSelect = document.getElementById("domainSelect");
    if (domainSelect) domainSelect.value = explicitDomain;
  }

  const domainSelect = document.getElementById("domainSelect");
  const domain = explicitDomain || (domainSelect ? domainSelect.value : window.currentDomain) || "pokemon";
  window.currentDomain = domain;
  window.loadedDomain = domain;

  // Direct view switch to avoid loop
  const views = document.querySelectorAll(".view-section");
  views.forEach(v => v.classList.remove("active"));
  const target = document.getElementById("view-assessment");
  if (target) target.classList.add("active");
  window.scrollTo({ top: 0, behavior: "smooth" });

  // Update active navbar button
  document.querySelectorAll(".nav-item").forEach(btn => {
    if (btn.getAttribute("onclick")?.includes("select-subject") || btn.getAttribute("onclick")?.includes("assessment")) {
      btn.classList.add("active");
    } else {
      btn.classList.remove("active");
    }
  });

  currentQIndex = 0;
  userAnswers = {};

  const customDomainMeta = (window.customDomains && window.customDomains[domain]) || null;
  const domainTitle = customDomainMeta 
    ? `${customDomainMeta.icon || '✨'} ${customDomainMeta.name}` 
    : (DOMAIN_NAMES[domain] || domain.replace(/^custom_/, '').replace(/_/g, ' '));

  const titleEl = document.getElementById("quizTitle");
  if (titleEl) titleEl.textContent = domainTitle;

  const subjectBadge = document.getElementById("quizSubjectBadge");
  if (subjectBadge) subjectBadge.textContent = domainTitle;

  const container = document.getElementById("optionsList");
  container.innerHTML = `<div class="p-4 text-center" style="color: #94a3b8; padding: 2rem;">Loading diagnostic questions for ${domainTitle}...</div>`;

  try {
    const qCount = (domain === "deep_learning" ? 15 : 10);
    const storedUser = JSON.parse(localStorage.getItem("deeplearnx_user") || "null");
    const userId = storedUser ? storedUser.id : null;
    currentQuestions = await API.getAssessmentQuestions(qCount, domain, userId);
    if (!currentQuestions || currentQuestions.length === 0) {
      container.innerHTML = `<div class="p-4 text-center text-red">No questions found for ${domainTitle}. Please select another domain.</div>`;
      return;
    }
    renderCurrentQuestion();
  } catch (err) {
    container.innerHTML = `<div class="p-4 text-center text-red">Error loading questions: ${err.message}</div>`;
  }
}

function renderCurrentQuestion() {
  if (currentQIndex < 0 || currentQIndex >= currentQuestions.length) return;

  const q = currentQuestions[currentQIndex];
  
  // Update Header & Progress
  const total = currentQuestions.length;
  const progressPct = ((currentQIndex + 1) / total) * 100;
  document.getElementById("quizProgressBar").style.width = `${progressPct}%`;
  document.getElementById("quizCounter").textContent = `Question ${currentQIndex + 1} of ${total}`;

  // Update Badges
  const tierEl = document.getElementById("questionTierBadge");
  tierEl.textContent = capitalize(q.question_type) + (q.question_type === "application" ? " Reasoning" : " Recall");
  tierEl.className = `tier-badge tier-${q.question_type}`;

  document.getElementById("questionConceptBadge").textContent = q.concept_name || q.concept_id;

  // Set Prompt
  document.getElementById("questionPrompt").textContent = q.question_text;

  // Render Options
  const optionsContainer = document.getElementById("optionsList");
  optionsContainer.innerHTML = "";

  const savedAns = userAnswers[q.id]?.selected_option;

  ["A", "B", "C", "D"].forEach(key => {
    const text = q.options[key];
    if (!text) return;

    const optDiv = document.createElement("div");
    optDiv.className = `quiz-option ${savedAns === key ? "selected" : ""}`;
    optDiv.onclick = () => selectOption(q.id, key);

    optDiv.innerHTML = `
      <div class="opt-key">${key}</div>
      <div class="opt-text">${text}</div>
    `;
    optionsContainer.appendChild(optDiv);
  });

  // Render Two-Tier Diagnostic Reasoning Probe if present
  renderReasoningProbe(q);

  // Confidence selector
  const savedConf = userAnswers[q.id]?.confidence || 3;
  setConfidenceUI(savedConf);

  // Nav buttons
  document.getElementById("btnPrevQ").disabled = (currentQIndex === 0);
  
  if (currentQIndex === total - 1) {
    document.getElementById("btnNextQ").classList.add("hidden");
    document.getElementById("btnSubmitQuiz").classList.remove("hidden");
  } else {
    document.getElementById("btnNextQ").classList.remove("hidden");
    document.getElementById("btnSubmitQuiz").classList.add("hidden");
  }

  // Reset & Start question timer
  startQuestionTimer();
}

function renderReasoningProbe(q) {
  const probeSection = document.getElementById("reasoningProbeSection");
  if (!probeSection) return;

  if (!q.reasoning_probe) {
    probeSection.classList.add("hidden");
    probeSection.innerHTML = "";
    return;
  }

  probeSection.classList.remove("hidden");
  const rp = q.reasoning_probe;
  const savedProbe = userAnswers[q.id]?.reasoning_selected;

  let optionsHtml = "";
  ["A", "B", "C", "D"].forEach(pk => {
    const text = rp.options[pk];
    if (!text) return;
    const isSel = (savedProbe === pk);
    optionsHtml += `
      <div class="probe-option ${isSel ? "selected" : ""}" onclick="selectProbeOption('${q.id}', '${pk}')" style="cursor: pointer; padding: 0.65rem 0.9rem; background: ${isSel ? 'rgba(99, 102, 241, 0.25)' : '#0f172a'}; border: 1.5px solid ${isSel ? '#6366f1' : '#334155'}; border-radius: 8px; font-size: 0.88rem; color: #f8fafc; display: flex; align-items: center; gap: 0.65rem; transition: all 0.2s;">
        <span style="font-weight: 700; color: #a5b4fc; min-width: 20px;">${pk}.</span>
        <span>${text}</span>
      </div>
    `;
  });

  probeSection.innerHTML = `
    <div style="border: 1px solid rgba(99, 102, 241, 0.4); border-radius: 12px; padding: 1.25rem; background: rgba(30, 41, 59, 0.7); margin-top: 1rem;">
      <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.65rem;">
        <span class="badge-tag" style="background: #4f46e5; color: #fff; font-size: 0.75rem; padding: 0.2rem 0.5rem;">🔍 Tier-2 Reasoning Probe</span>
        <span style="color: #94a3b8; font-size: 0.82rem;">Underlying Principle Verification (Required)</span>
      </div>
      <p style="font-weight: 600; color: #f8fafc; font-size: 0.95rem; margin-bottom: 0.75rem;">${rp.prompt}</p>
      <div class="probe-list" style="display: flex; flex-direction: column; gap: 0.5rem;">
        ${optionsHtml}
      </div>
    </div>
  `;
}

function selectProbeOption(qId, probeKey) {
  if (!userAnswers[qId]) {
    userAnswers[qId] = {
      question_id: qId,
      selected_option: "A",
      response_time: secondsOnCurrentQ,
      confidence: 3,
      reasoning_selected: probeKey
    };
  } else {
    userAnswers[qId].reasoning_selected = probeKey;
  }

  const q = currentQuestions[currentQIndex];
  if (q && q.id === qId) {
    renderReasoningProbe(q);
  }
}

function selectOption(qId, key) {
  if (!userAnswers[qId]) {
    userAnswers[qId] = {
      question_id: qId,
      selected_option: key,
      response_time: secondsOnCurrentQ,
      confidence: 3
    };
  } else {
    userAnswers[qId].selected_option = key;
  }

  // Re-render selection highlight
  const options = document.querySelectorAll(".quiz-option");
  options.forEach(opt => {
    if (opt.querySelector(".opt-key").textContent.trim() === key) {
      opt.classList.add("selected");
    } else {
      opt.classList.remove("selected");
    }
  });
}

function setConfidence(val) {
  const q = currentQuestions[currentQIndex];
  if (!q) return;

  if (!userAnswers[q.id]) {
    userAnswers[q.id] = {
      question_id: q.id,
      selected_option: "A",
      response_time: secondsOnCurrentQ,
      confidence: val
    };
  } else {
    userAnswers[q.id].confidence = val;
  }

  setConfidenceUI(val);
}

function setConfidenceUI(val) {
  const btns = document.querySelectorAll(".conf-btn");
  btns.forEach((b, idx) => {
    if (idx + 1 === val) {
      b.classList.add("active");
    } else {
      b.classList.remove("active");
    }
  });
}

function nextQuestion() {
  saveCurrentTiming();
  if (currentQIndex < currentQuestions.length - 1) {
    currentQIndex++;
    renderCurrentQuestion();
  }
}

function prevQuestion() {
  saveCurrentTiming();
  if (currentQIndex > 0) {
    currentQIndex--;
    renderCurrentQuestion();
  }
}

function startQuestionTimer() {
  if (questionTimerInterval) clearInterval(questionTimerInterval);
  secondsOnCurrentQ = 0;
  updateTimerUI();

  questionTimerInterval = setInterval(() => {
    secondsOnCurrentQ++;
    updateTimerUI();
  }, 1000);
}

function updateTimerUI() {
  const m = Math.floor(secondsOnCurrentQ / 60);
  const s = secondsOnCurrentQ % 60;
  const str = `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  const el = document.getElementById("questionTimer");
  if (el) el.textContent = str;
}

function saveCurrentTiming() {
  const q = currentQuestions[currentQIndex];
  if (q && userAnswers[q.id]) {
    userAnswers[q.id].response_time = (userAnswers[q.id].response_time || 0) + secondsOnCurrentQ;
  }
}

async function submitAssessment() {
  saveCurrentTiming();
  if (questionTimerInterval) clearInterval(questionTimerInterval);

  // Fill default for unanswered
  currentQuestions.forEach(q => {
    if (!userAnswers[q.id]) {
      userAnswers[q.id] = {
        question_id: q.id,
        selected_option: "A", // fallback choice
        response_time: 25.0,
        confidence: 2
      };
    }
  });

  const payload = {
    user_id: window.currentUser ? window.currentUser.id : 3,
    domain_id: window.currentDomain || "pokemon",
    answers: Object.values(userAnswers)
  };

  const btnSubmit = document.getElementById("btnSubmitQuiz");
  btnSubmit.disabled = true;
  btnSubmit.innerHTML = `<span class="spinner"></span> Running Deep Learning Inference...`;

  try {
    const result = await API.submitAssessment(payload);
    displayAssessmentResults(result);
  } catch (err) {
    alert("Inference submission failed: " + err.message);
  } finally {
    btnSubmit.disabled = false;
    btnSubmit.innerHTML = `Submit to Deep Learning Engine`;
  }
}

function displayAssessmentResults(res) {
  navigate("results");

  document.getElementById("resultSessionId").textContent = res.session_id;

  const dl = res.deep_learning_analysis;
  const stateBadge = document.getElementById("resultStateBadge");
  stateBadge.textContent = dl.predicted_state;
  stateBadge.className = `state-pill pill-${getStateBadgeColor(dl.predicted_state)}`;

  document.getElementById("resultStateConf").textContent = `${(dl.confidence * 100).toFixed(1)}%`;
  document.getElementById("resultScorePct").textContent = `${res.accuracy}%`;

  const mets = dl.metrics_summary || {};
  document.getElementById("resBasicAcc").textContent = `${mets.basic_accuracy || 0}%`;
  document.getElementById("resConcAcc").textContent = `${mets.conceptual_accuracy || 0}%`;
  document.getElementById("resAppAcc").textContent = `${mets.application_accuracy || 0}%`;

  // Friendly state explanation
  const friendlyExplains = {
    "Genuine Mastery": "Awesome job! You have a solid grasp of the material and can comfortably use these concepts to solve new problems.",
    "False Mastery": "You did great on the definitions, but found practical problems tricky. Practicing with real-world examples will help you master this topic!",
    "Conceptual Misconception": "You are very close! There is just a small mix-up with one of the key rules. Review the explanation below to clear it up.",
    "Knowledge Gap": "You need a quick refresher on an earlier foundational topic that this subject builds on. Once you review that starting topic, this will feel much easier!"
  };
  document.getElementById("resultStateExplain").textContent = dl.false_mastery_breakdown?.diagnosis ||
    friendlyExplains[dl.predicted_state] || "Your diagnostic evaluation is complete.";

  // False mastery & Anti-gaming section
  const fmBox = document.getElementById("falseMasteryDetails");
  const fm = dl.false_mastery_breakdown || {};
  fmBox.innerHTML = `
    <div class="alert-box ${fm.gaming_detected ? "alert-amber" : (fm.is_false_mastery ? "alert-amber" : "")}">
      <strong>${fm.gaming_detected ? "🚨 Guessing Pattern Detected" : "Theory vs. Practice Gap: " + (fm.tier_divergence || 0) + "%"}</strong>
      <p>${fm.diagnosis}</p>
    </div>
    <div class="inspector-meta-grid mt-3">
      <div><strong>Basic Definitions:</strong> ${fm.basic_accuracy}%</div>
      <div><strong>Concept Understanding:</strong> ${fm.conceptual_accuracy}%</div>
      <div><strong>Problem Solving:</strong> ${fm.application_accuracy}%</div>
      <div><strong>Picked Longest Option:</strong> <span class="${(fm.heuristic_bias_index || 0) >= 60 ? "text-red" : "text-emerald"}">${fm.heuristic_bias_index || 0}%</span></div>
      <div><strong>Fast Guesses (<3.5s):</strong> <span class="${(fm.rapid_guessing_pct || 0) >= 40 ? "text-amber" : "text-dim"}">${fm.rapid_guessing_pct || 0}%</span></div>
      ${fm.two_tier_probes_tested ? `<div><strong>Reasoning Checks Passed:</strong> <span class="${(fm.two_tier_inconsistencies || 0) > 0 ? "text-amber" : "text-emerald"}">${fm.two_tier_probes_tested - (fm.two_tier_inconsistencies || 0)}/${fm.two_tier_probes_tested} verified</span></div>` : ""}
    </div>
  `;

  // Gaps & Misconceptions section
  const gapsBox = document.getElementById("resultGapsDetails");
  const miscs = dl.detected_misconceptions || [];
  const rootGap = res.knowledge_gap_detection?.primary_gap_name || "None Detected";

  let miscHtml = "";
  if (miscs.length === 0) {
    miscHtml = `<p class="text-muted">Great news! No repeated misunderstandings were found in your answers.</p>`;
  } else {
    miscHtml = miscs.map(m => `
      <div class="misc-item mt-2">
        <div class="misc-item-title">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          ${m.name}
        </div>
        <p class="misc-item-desc">${m.description}</p>
      </div>
    `).join("");
  }

  gapsBox.innerHTML = `
    <div class="card-sub mb-3">
      <span class="stat-label">Key Starting Topic to Review First</span>
      <h3 class="text-red">${rootGap}</h3>
      <p class="stat-sub">This foundational topic needs to be clear before moving forward.</p>
    </div>
    <h4 class="mt-3">Common Mix-ups Found (${miscs.length})</h4>
    ${miscHtml}
  `;

  // Render question-by-question diagnostic review & conceptual teaching
  if (res.question_reviews && res.question_reviews.length > 0) {
    renderQuestionReviews(res.question_reviews);
  } else if (res.session_id) {
    API.getSessionDetails(res.session_id).then(details => {
      if (details && details.question_reviews && details.question_reviews.length > 0) {
        renderQuestionReviews(details.question_reviews);
      }
    }).catch(err => {
      console.warn("Could not fetch session question reviews:", err);
    });
  }

  // Populate Recommendations page in advance
  renderRecommendationsList(res.recommendations);
}

function renderQuestionReviews(reviews) {
  const container = document.getElementById("questionReviewsList");
  const card = document.getElementById("questionReviewsCard");
  if (!container || !card) return;

  if (!reviews || reviews.length === 0) {
    card.classList.add("hidden");
    return;
  }
  card.classList.remove("hidden");

  let correctCount = 0;
  let incorrectCount = 0;
  let miscCount = 0;

  reviews.forEach(r => {
    if (r.is_correct) {
      correctCount++;
    } else {
      incorrectCount++;
    }
    if (r.misconception) {
      miscCount++;
    }
  });

  const corrEl = document.getElementById("qReviewCorrectCount");
  const incorrEl = document.getElementById("qReviewIncorrectCount");
  const miscEl = document.getElementById("qReviewMiscCount");
  if (corrEl) corrEl.textContent = `✓ ${correctCount} Correct`;
  if (incorrEl) incorrEl.textContent = `❌ ${incorrectCount} Incorrect`;
  if (miscEl) miscEl.textContent = `⚠️ ${miscCount} Misconceptions`;

  const tierMap = {
    basic: { label: "Basic Recall", cls: "tier-basic" },
    conceptual: { label: "Conceptual", cls: "tier-conceptual" },
    application: { label: "Applied Problem-Solving", cls: "tier-application" }
  };

  container.innerHTML = reviews.map((r, idx) => {
    const isCorr = Boolean(r.is_correct);
    const hasMisc = Boolean(r.misconception);
    const tier = tierMap[r.question_type] || { label: r.question_type || "Question", cls: "tier-basic" };

    // Card styling based on diagnosis
    let cardBorder = "1px solid rgba(16, 185, 129, 0.35)";
    let cardBg = "rgba(15, 23, 42, 0.65)";
    let statusPill = `<span class="badge-tag badge-emerald" style="font-weight: 600;">✓ Correct</span>`;

    if (!isCorr && hasMisc) {
      cardBorder = "1.5px solid rgba(245, 158, 11, 0.5)";
      cardBg = "rgba(30, 24, 16, 0.75)";
      statusPill = `<span class="badge-tag badge-orange" style="font-weight: 600;">⚠️ Misconception Identified</span>`;
    } else if (!isCorr) {
      cardBorder = "1.5px solid rgba(239, 68, 68, 0.4)";
      cardBg = "rgba(30, 18, 20, 0.75)";
      statusPill = `<span class="badge-tag badge-red" style="font-weight: 600;">❌ Incorrect</span>`;
    }

    // Answers section
    let answersHtml = "";
    if (isCorr) {
      answersHtml = `
        <div style="background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; padding: 0.75rem 1rem; display: flex; align-items: baseline; gap: 0.65rem;">
          <span style="font-weight: 700; color: #34d399; font-size: 0.9rem;">✓ Your Answer:</span>
          <span style="color: #f1f5f9; font-size: 0.92rem;"><strong style="color: #34d399;">Option ${r.selected_option}:</strong> ${r.selected_text || "Selected option"}</span>
        </div>
      `;
    } else {
      answersHtml = `
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 0.75rem;">
          <div style="background: rgba(239, 68, 68, 0.12); border: 1px solid rgba(239, 68, 68, 0.35); border-radius: 8px; padding: 0.75rem 1rem; display: flex; align-items: baseline; gap: 0.65rem;">
            <span style="font-weight: 700; color: #f87171; font-size: 0.9rem;">❌ Your Answer:</span>
            <span style="color: #f1f5f9; font-size: 0.92rem;"><strong style="color: #f87171;">Option ${r.selected_option}:</strong> ${r.selected_text || "Selected option"}</span>
          </div>
          <div style="background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 8px; padding: 0.75rem 1rem; display: flex; align-items: baseline; gap: 0.65rem;">
            <span style="font-weight: 700; color: #34d399; font-size: 0.9rem;">✓ Correct Answer:</span>
            <span style="color: #f1f5f9; font-size: 0.92rem;"><strong style="color: #34d399;">Option ${r.correct_option}:</strong> ${r.correct_text || ""}</span>
          </div>
        </div>
      `;
    }

    // Two-Tier Reasoning Probe Review (if tested)
    let probeHtml = "";
    if (r.reasoning_probe && r.reasoning_probe.prompt) {
      const rp = r.reasoning_probe;
      const isProbeCorr = Boolean(rp.is_correct);
      probeHtml = `
        <div style="margin-top: 0.85rem; padding: 0.85rem 1rem; background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(99, 102, 241, 0.35); border-radius: 8px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem; flex-wrap: wrap; gap: 0.4rem;">
            <span style="font-size: 0.8rem; font-weight: 700; color: #a5b4fc; text-transform: uppercase; letter-spacing: 0.5px;">🔍 Two-Tier Reasoning Probe Verification</span>
            ${isProbeCorr ? '<span class="badge-tag badge-emerald" style="font-size: 0.75rem;">Principle Aligned ✓</span>' : '<span class="badge-tag badge-amber" style="font-size: 0.75rem;">Principle Mismatch (Surface Guess) ⚠️</span>'}
          </div>
          <div style="font-size: 0.88rem; color: #e2e8f0; margin-bottom: 0.35rem; font-weight: 500;">${rp.prompt}</div>
          <div style="font-size: 0.82rem; color: #94a3b8; display: flex; flex-wrap: wrap; gap: 1rem;">
            <span>Selected Principle: <strong style="color: ${isProbeCorr ? '#34d399' : '#fbbf24'};">${rp.selected || "N/A"}. ${rp.selected_text || ""}</strong></span>
            ${!isProbeCorr ? `<span>Governing Law: <strong style="color: #34d399;">${rp.correct}. ${rp.correct_text || ""}</strong></span>` : ''}
          </div>
        </div>
      `;
    }

    // Conceptual Diagnosis & Teaching Remediation Mini-Lesson
    let teachingHtml = "";
    if (hasMisc) {
      teachingHtml = `
        <div style="margin-top: 1rem; background: rgba(245, 158, 11, 0.08); border: 1.5px solid rgba(245, 158, 11, 0.35); border-radius: 10px; padding: 1.1rem;">
          <div style="display: flex; align-items: center; gap: 0.5rem; color: #fbbf24; font-weight: 700; font-size: 0.95rem; margin-bottom: 0.35rem;">
            <span style="font-size: 1.15rem;">🧠</span> Cognitive Misconception: ${r.misconception.name}
          </div>
          <p style="font-size: 0.88rem; color: #cbd5e1; margin: 0 0 0.85rem; line-height: 1.5;">
            <strong style="color: #f8fafc;">Why this is a trap:</strong> ${r.misconception.description}
          </p>

          <!-- Interactive Teaching Lesson -->
          <div style="background: rgba(15, 23, 42, 0.9); border: 1px solid rgba(245, 158, 11, 0.4); border-left: 4px solid #f59e0b; border-radius: 8px; padding: 1rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem; color: #fde047; font-weight: 700; font-size: 0.92rem; margin-bottom: 0.4rem;">
              <span style="font-size: 1.15rem;">💡</span> DeepLearnX Teaching Mini-Lesson:
            </div>
            <p style="font-size: 0.9rem; color: #f1f5f9; margin: 0; line-height: 1.55; white-space: pre-line;">
              ${r.misconception.remediation}
            </p>
          </div>
        </div>
      `;
    } else if (!isCorr) {
      teachingHtml = `
        <div style="margin-top: 1rem; background: rgba(239, 68, 68, 0.08); border-left: 4px solid #ef4444; border-radius: 8px; padding: 1rem;">
          <div style="display: flex; align-items: center; gap: 0.5rem; color: #f87171; font-weight: 700; font-size: 0.92rem; margin-bottom: 0.35rem;">
            <span style="font-size: 1.15rem;">💡</span> Conceptual Explanation & Core Principle:
          </div>
          <p style="font-size: 0.9rem; color: #cbd5e1; margin: 0; line-height: 1.55;">
            ${r.explanation || "Review the governing formulas and principles for this topic before attempting again."}
          </p>
        </div>
      `;
    } else {
      teachingHtml = `
        <div style="margin-top: 0.85rem; background: rgba(16, 185, 129, 0.06); border-left: 4px solid #10b981; border-radius: 8px; padding: 0.75rem 1rem;">
          <div style="color: #34d399; font-weight: 600; font-size: 0.85rem; display: flex; align-items: center; gap: 0.5rem;">
            <span>✓</span> Key Conceptual Insight:
          </div>
          <p style="font-size: 0.85rem; color: #94a3b8; margin: 0.25rem 0 0; line-height: 1.45;">
            ${r.explanation || "Strong conceptual understanding demonstrated on this item."}
          </p>
        </div>
      `;
    }

    return `
      <div class="card" style="border: ${cardBorder}; background: ${cardBg}; border-radius: 12px; padding: 1.25rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 0.75rem;">
          <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
            <strong style="color: #f8fafc; font-size: 1rem;">Question ${idx + 1}</strong>
            <span class="tier-badge ${tier.cls}">${tier.label}</span>
            <span class="concept-badge">${r.concept_name || "General"}</span>
          </div>
          <div>${statusPill}</div>
        </div>

        <div style="font-size: 1rem; font-weight: 600; color: #f8fafc; margin-bottom: 1rem; line-height: 1.5;">
          ${r.question_text}
        </div>

        ${answersHtml}
        ${probeHtml}
        ${teachingHtml}
      </div>
    `;
  }).join("");
}

function getStateBadgeColor(state) {
  switch (state) {
    case "Genuine Mastery": return "emerald";
    case "False Mastery": return "amber";
    case "Conceptual Misconception": return "orange";
    case "Knowledge Gap": return "red";
    default: return "indigo";
  }
}

function capitalize(s) {
  if (!s) return "";
  return s.charAt(0).toUpperCase() + s.slice(1);
}
