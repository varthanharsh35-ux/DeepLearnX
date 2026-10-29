/**
 * DeepLearnX API Client
 * Wraps all backend endpoints with standard fetch requests
 * Supports Multi-Domain Learning: Pokemon, Class 10 Chemistry, Class 10 Biology, Class 10 Math, Deep Learning
 */

const API_BASE = ""; // Relative paths match same-origin backend

const API = {
  // Authentication
  login: async (username, password) => {
    const res = await fetch(`${API_BASE}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });
    if (!res.ok) throw new Error((await res.json()).detail || "Login failed");
    return await res.json();
  },

  oauthLogin: async (provider, email, fullName, avatarUrl = null) => {
    const res = await fetch(`${API_BASE}/api/auth/oauth-login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        provider: provider,
        email: email,
        full_name: fullName,
        avatar_url: avatarUrl
      })
    });
    if (!res.ok) throw new Error((await res.json()).detail || "Social authentication failed");
    return await res.json();
  },

  register: async (userData) => {
    const res = await fetch(`${API_BASE}/api/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(userData)
    });
    if (!res.ok) throw new Error((await res.json()).detail || "Registration failed");
    return await res.json();
  },

  getUserProfile: async (userId) => {
    const res = await fetch(`${API_BASE}/api/user/profile/${userId}`);
    if (!res.ok) throw new Error((await res.json()).detail || "Failed to fetch user profile");
    return await res.json();
  },

  getDemoUsers: async () => {
    const res = await fetch(`${API_BASE}/api/auth/demo-users`);
    return await res.json();
  },

  // Domains & Concepts
  getDomains: async () => {
    const res = await fetch(`${API_BASE}/api/domains`);
    return await res.json();
  },

  getConcepts: async (domain = "pokemon") => {
    const res = await fetch(`${API_BASE}/api/concepts?domain=${encodeURIComponent(domain)}`);
    return await res.json();
  },

  getConceptGuide: async (conceptId = null, domain = "pokemon") => {
    const url = conceptId 
      ? `${API_BASE}/api/concepts/guide?concept_id=${encodeURIComponent(conceptId)}&domain=${encodeURIComponent(domain)}`
      : `${API_BASE}/api/concepts/guide?domain=${encodeURIComponent(domain)}`;
    const res = await fetch(url);
    return await res.json();
  },

  getBaseGraph: async (domain = "pokemon") => {
    const res = await fetch(`${API_BASE}/api/graph/base?domain=${encodeURIComponent(domain)}`);
    return await res.json();
  },

  getStudentKnowledgeMap: async (userId, domain = "pokemon", sessionId = null) => {
    let url = `${API_BASE}/api/graph/student/${userId}?domain=${encodeURIComponent(domain)}`;
    if (sessionId) {
      url += `&session_id=${encodeURIComponent(sessionId)}`;
    }
    const res = await fetch(url);
    return await res.json();
  },

  // Assessment & Deep Learning
  getAssessmentQuestions: async (limit = 10, domain = "pokemon", userId = null) => {
    let url = `${API_BASE}/api/assessment/questions?limit=${limit}&domain=${encodeURIComponent(domain)}`;
    if (userId) url += `&user_id=${encodeURIComponent(userId)}`;
    const res = await fetch(url);
    return await res.json();
  },

  customGenerateAssessment: async (topicTitle, syllabusText = "", userId = null, numQuestions = 12, apiKey = null, apiProvider = "gemini", modelName = null) => {
    const res = await fetch(`${API_BASE}/api/assessment/custom-generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        topic_title: topicTitle,
        syllabus_text: syllabusText,
        user_id: userId,
        num_questions: numQuestions,
        api_key: apiKey,
        api_provider: apiProvider,
        model_name: modelName
      })
    });
    if (!res.ok) throw new Error((await res.json()).detail || "Failed to generate custom assessment");
    return await res.json();
  },

  uploadSyllabusFile: async (topicTitle, file, apiKey = null, apiProvider = "gemini") => {
    const formData = new FormData();
    formData.append("file", file);
    let url = `${API_BASE}/api/assessment/upload-syllabus-file?topic_title=${encodeURIComponent(topicTitle)}`;
    if (apiKey) url += `&api_key=${encodeURIComponent(apiKey)}`;
    if (apiProvider) url += `&api_provider=${encodeURIComponent(apiProvider)}`;
    const res = await fetch(url, {
      method: "POST",
      body: formData
    });
    if (!res.ok) throw new Error((await res.json()).detail || "Failed to upload syllabus file");
    return await res.json();
  },

  submitAssessment: async (submission) => {
    const res = await fetch(`${API_BASE}/api/assessment/submit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(submission)
    });
    if (!res.ok) throw new Error((await res.json()).detail || "Assessment submission failed");
    return await res.json();
  },

  getStudentHistory: async (userId, domain = null) => {
    const url = domain ? `${API_BASE}/api/assessment/history/${userId}?domain=${encodeURIComponent(domain)}` : `${API_BASE}/api/assessment/history/${userId}`;
    const res = await fetch(url);
    return await res.json();
  },

  getSessionDetails: async (sessionId) => {
    const res = await fetch(`${API_BASE}/api/assessment/session/${sessionId}`);
    return await res.json();
  },

  // Remedial Quiz
  getRemedialQuestions: async (conceptId, count = 3, domain = "pokemon") => {
    const res = await fetch(`${API_BASE}/api/remedial/questions?concept_id=${encodeURIComponent(conceptId)}&count=${count}&domain=${encodeURIComponent(domain)}`);
    return await res.json();
  },

  submitRemedial: async (submission) => {
    const res = await fetch(`${API_BASE}/api/remedial/submit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(submission)
    });
    if (!res.ok) throw new Error((await res.json()).detail || "Remedial submission failed");
    return await res.json();
  },

  // Faculty Dashboard
  getFacultyDashboard: async () => {
    const res = await fetch(`${API_BASE}/api/faculty/dashboard`);
    return await res.json();
  },

  // Model Transparency
  getModelMetrics: async () => {
    const res = await fetch(`${API_BASE}/api/model/metrics`);
    return await res.json();
  }
};
