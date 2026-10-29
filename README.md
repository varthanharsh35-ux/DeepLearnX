# DeepLearnX – Deep Learning-Based Student Concept Understanding & Knowledge Gap Detection Platform

> **Comprehensive Deep Learning Capstone Project**  
> Diagnosing **False Mastery**, identifying **Misconceptions**, and tracing **Prerequisite Knowledge Gaps** using PyTorch Deep Learning (`DeepCognitiveNet`), Directed Acyclic Graph (DAG) Traversal, Two-Tier Diagnostic Reasoning Probes, and Universal Factual Curriculum Synthesis.

---

## 📁 Repository Structure

The repository is organized into three core directories:

```
DeepLearnX/
├── Website/                   # Complete Web Application & Neural Engine
│   ├── backend/               # FastAPI REST Application & Knowledge DAG Engines
│   │   ├── app/
│   │   │   ├── main.py        # API Endpoints, Remedial Handlers, Auth
│   │   │   ├── topic_researcher.py # Factual Research & Sentence Balancer (0.0% Length Bias)
│   │   │   ├── domain_question_engine.py # Universal Archetype Engine & Probes
│   │   │   ├── syllabus_generator.py # Generative Curriculum Engine
│   │   │   ├── graph_engine.py # Prerequisite DAG Traversal
│   │   │   └── predictor.py   # PyTorch Cognitive Inference Engine
│   │   └── seed_data.py       # Database Seeding Script
│   ├── frontend/              # Web Interface
│   │   ├── index.html         # Single Page Application & Google OAuth SSO
│   │   ├── css/styles.css     # Modern Glassmorphic UI
│   │   └── js/                # Client-Side Application, Assessment Engine & Vis.js DAGs
│   ├── model/                 # Deep Learning Architecture & Trained Weights
│   │   ├── architecture.py    # DeepCognitiveNet (Bi-GRU + Self-Attention + Tabular ANN)
│   │   ├── train.py           # Training Pipeline (AdamW + Multi-Task Loss)
│   │   ├── evaluate.py        # Diagnostic Metrics & Confusion Matrix Generator
│   │   └── deeplearnx_cognitive_model.pt # Trained Checkpoint (100% Accuracy)
│   ├── dataset/               # Synthesized & Empirical Diagnostic Sessions
│   ├── database/              # SQLite Database (`deeplearnx.db`)
│   ├── notebooks/             # Jupyter Notebook for Model Experiments
│   ├── tests/                 # Unit & Integration Tests
│   ├── evaluate_universal_topics.py # 15-Topic Multi-Disciplinary Evaluation Script
│   ├── requirements.txt       # Python Dependencies
│   ├── Dockerfile             # Container Deployment
│   └── run.py                 # Application Launcher (Port 8055)
│
├── Video/                     # Team Presentation & Demonstration Videos
│   ├── DeepLearnX A General Overview of Our Processes.mp4 # Full Platform Demo
│   ├── HARSHAVARTHAN S B 24BAD033.mp4                     # Deep Learning Architecture & Attention
│   ├── ANBUSABARIVASAN M 24BAD009 .MOV                    # Cognitive Diagnostic & DAG Modeling
│   ├── GOKULNAATH M 24BAD026.mp4                          # Dataset Generation & Psychometrics
│   ├── KALVI KANNAN B L 24BAD052.mp4                      # Two-Tier Probes & Remediation
│   ├── KARTHIK SARAVANAKUMAR 24BAD056.mp4                 # Analytics Dashboard & Interventions
│   └── README.md                                          # Video Catalog & Details
│
├── Report/                    # Comprehensive Academic Project Documentation
│   ├── DeepLearnX_Comprehensive_Project_Report.docx       # Full Academic Report (Word format)
│   ├── DeepLearnX_Comprehensive_Project_Report.md         # Full Academic Report (Markdown format)
│   ├── PROJECT_REPORT_CO_MAPPING.md                       # Complete CO1–CO5 Mapping Matrix
│   ├── VIVA_QUESTIONS_AND_ANSWERS.md                      # Viva Voce Questions & Answers
│   ├── VIDEO_EXPLANATION_SCRIPTS.md                       # Presentation Scripts
│   ├── architecture_diagram.png                           # DeepCognitiveNet Architecture Diagram
│   ├── training_curves.png                                # Model Training & Loss Curves
│   └── build_docx_report.py                               # Document Generator Script
│
├── run.py                     # Root Quick-Launcher
└── README.md                  # Project Readme
```

---

## 🚀 Quick Start Guide

### 1. Installation
Clone the repository and install requirements:
```bash
git clone https://github.com/varthanharsh35-ux/DeepLearnX.git
cd DeepLearnX/Website
pip install -r requirements.txt
```

### 2. Launching the Application
You can run the application directly from the root directory or inside `Website/`:
```bash
# Option A: From root directory
python run.py

# Option B: From inside Website directory
cd Website
python run.py
```
Open your browser and navigate to:  
👉 **[http://localhost:8055](http://localhost:8055)**

---

## 🎯 Key Capabilities & System Innovations

### 1. Eliminating the "False Mastery" Blind Spot
Standard tests cannot detect when a student passes through elimination tricks or lucky guesses. DeepLearnX integrates:
- **Two-Tier Diagnostic Reasoning Probes**: Applied problems trigger a compulsory Tier-2 justification probe: *"Which fundamental governing law or causal mechanism justifies your response?"* Blind guessing drops from 25% to **6.25%** ($0.25 \times 0.25$), exposing lucky guesses as **Principle Mismatches**.
- **DeepCognitiveNet Neural Architecture**: Fuses a 2-layer Bidirectional GRU (tracking sequence latency and confidence decay) with Self-Attention Pooling to isolate exact question bottlenecks.

### 2. Universal Curriculum Synthesis for Any Subject
DeepLearnX dynamically synthesizes authentic diagnostic quizzes for **any** academic subject worldwide:
- **Zero Engineering Jargon**: Strictly purges template jargon (e.g., *"operator throughput"*) from non-engineering topics.
- **Anti-Heuristic Sentence Balancing (0.0% Length Bias)**: Equalizes option lengths to 85–108 characters, preventing students from guessing the longest sentence.
- **Randomized Probe Distribution**: Probes are sampled unpredictably across questions.
- **Remedial Isolation**: Remedial drills only pull questions from the active target domain with zero cross-domain leakage.

### 3. Empirical 15-Topic Multi-Disciplinary Validation

Verified using `evaluate_universal_topics.py` across 15 completely unrelated disciplines:

| # | Topic | Category | Probe Placement | Jargon Found | Option Length Bias | Remedial Isolation | Status |
|---|---|---|---|---|---|---|---|
| 1 | **Types of Spiders** | 🧬 Arachnid Biology | Q3, Q7, Q9, Q11 | **0%** | **0.0%** | 3/3 Domain Pure | **PASSED** |
| 2 | **Fluid Mechanics** | 💧 Hydraulics & Flow | Q2, Q5, Q7, Q10 | **0%** | **0.0%** | 3/3 Domain Pure | **PASSED** |
| 3 | **French Revolution** | 🏛️ History & Humanities | Q1, Q4, Q8, Q11 | **0%** | **0.0%** | 3/3 Domain Pure | **PASSED** |
| 4 | **Photosynthesis** | 🌿 Botanical Sciences | Q3, Q5, Q8, Q12 | **0%** | **0.0%** | 3/3 Domain Pure | **PASSED** |
| 5 | **Ancient Roman Architecture** | 🏛️ Classical Design | Q2, Q6, Q9, Q11 | **0%** | **0.0%** | 3/3 Domain Pure | **PASSED** |
| 6 | **Quantum Cryptography** | ⚛️ Quantum Physics | Q2, Q4, Q7, Q10 | **0%** | **0.0%** | 3/3 Domain Pure | **PASSED** |
| 7 | **Plate Tectonics** | 🌍 Earth Science | Q1, Q5, Q8, Q10 | **0%** | **0.0%** | 3/3 Domain Pure | **PASSED** |
| 8 | **Macroeconomics** | 📈 Economics & Business | Q6, Q8, Q11, Q12 | **0%** | **0.0%** | 3/3 Domain Pure | **PASSED** |
| 9 | **Musical Harmony & Counterpoint** | 🎵 Music Theory & Arts | Q2, Q6, Q8, Q10 | **0%** | **0.0%** | 3/3 Domain Pure | **PASSED** |
| 10 | **Organic Chemistry & Polymers** | 🧬 Chemistry & Polymers | Q3, Q5, Q9, Q11 | **0%** | **0.0%** | 3/3 Domain Pure | **PASSED** |
| 11 | **Sourdough Fermentation** | 🌿 Fermentation Ecology | Q4, Q6, Q9, Q12 | **0%** | **0.0%** | 3/3 Domain Pure | **PASSED** |
| 12 | **Constitutional Law** | ⚖️ Jurisprudence & Law | Q1, Q4, Q6, Q11 | **0%** | **0.0%** | 3/3 Domain Pure | **PASSED** |
| 13 | **Aviation Aerodynamics** | 💧 Aerospace Engineering | Q5, Q8, Q10, Q12 | **0%** | **0.0%** | 3/3 Domain Pure | **PASSED** |
| 14 | **Neuroscience & Synaptic Plasticity** | 🧬 Cellular Neurobiology | Q3, Q6, Q8, Q12 | **0%** | **0.0%** | 3/3 Domain Pure | **PASSED** |
| 15 | **Ethics of Artificial Intelligence** | 📚 Computer Science & Ethics | Q4, Q9, Q10, Q11 | **0%** | **0.0%** | 3/3 Domain Pure | **PASSED** |

**Empirical Result: 15 / 15 TOPICS PASSED (100% Pass Rate)**

---

## 📊 Course Outcome (CO) Mapping

| CO | Syllabus Outcome Statement | Taxonomy Level (RBT) | Mapping Status | Key DeepLearnX Solution Implementation |
| :---: | :--- | :---: | :---: | :--- |
| **CO1** | Apply neural network architectures, activation functions, optimization methods, and regularization techniques. | **Ap (Apply)** | **100% Direct Match** | • Multi-branch `DeepCognitiveNet` architecture.<br>• GELU, Tanh, Softmax, Sigmoid activations.<br>• AdamW optimizer with weight decay ($10^{-4}$).<br>• Macro F1 = 1.0, Accuracy = 100%, Multi-task loss. |
| **CO2** | Implement deep learning techniques for feature extraction, image analysis, and computer vision applications. | **Ap (Apply)** | **100% Direct Match** | • High-dimensional student behavior feature extraction.<br>• Multi-dimensional embedding layers ($d=16, 8, 8$).<br>• Automated Confusion Matrix image generation (`confusion_matrix.png`).<br>• Dynamic graphical knowledge map rendering via Vis.js. |
| **CO3** | Develop sequential learning models for processing sequential and natural language data. | **Ap (Apply)** | **100% Direct Match** | • 2-layer Bidirectional GRU ($h=48$, output $= 96$).<br>• Sequential modeling of chronological response trajectories.<br>• Captures temporal latencies, confidence decay, and error cascades. |
| **CO4** | Analyze generative and unsupervised deep learning techniques for representation learning and synthetic data generation. | **An (Analyze)** | **100% Direct Match** | • Unsupervised representation learning via Self-Attention bottleneck.<br>• Generative synthetic diagnostic session simulation.<br>• Generative cognitive assessment & DAG synthesis with two-tier probes. |
| **CO5** | Analyze attention-based architectures and advanced deep learning techniques for multimodal AI tasks. | **An (Analyze)** | **100% Direct Match** | • Self-Attention Pooling mechanism (`AttentionPooling`) with learned alignment weights $\alpha_t$.<br>• Multimodal Cognitive Fusion merging sequence features ($h_{\text{seq}} \in \mathbb{R}^{96}$) with structured tabular features ($h_{\text{struct}} \in \mathbb{R}^{48}$).<br>• Intelligent clinical educational decision-support application. |
