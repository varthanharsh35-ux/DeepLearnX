# DeepLearnX – Deep Learning-Based Student Concept Understanding & Knowledge Gap Detection System

> **A 3rd-Year B.Tech Artificial Intelligence & Data Science Capstone Project**  
> Moving beyond traditional marks to diagnose **False Mastery**, identify **Misconceptions**, and trace **Prerequisite Knowledge Gaps** using Deep Learning and Directed Acyclic Graph (DAG) Traversal.

---

## 1. Problem Statement
Traditional educational assessment systems evaluate students primarily through raw scores (e.g. 65% = Grade B). This creates three critical failures in modern pedagogy:
1. **The False Mastery Illusion (Rote Memorization):** A student can score 65% simply by memorizing factual definitions while failing 100% of application, debugging, and reasoning problems. Traditional tests award a passing grade without recognizing that the student cannot apply the concepts.
2. **Invisible Misconceptions:** Standard scoring marks an incorrect choice as 0 marks, ignoring *why* the student picked that specific option (e.g. adding derivatives instead of multiplying them in the Chain Rule).
3. **Unidentified Prerequisite Bottlenecks:** A failure in an advanced concept (e.g. Backpropagation) is frequently caused by missing foundational knowledge in an upstream topic (e.g. Calculus Derivatives or Matrix Dot Products).

---

## 2. Proposed Solution: DeepLearnX
**DeepLearnX** is an end-to-end intelligent diagnostic educational platform powered by a genuine PyTorch Deep Learning model (**DeepCognitiveNet**) and a Concept Dependency Graph Engine:
- **Sequential + Structured Cognitive Neural Network:** Fuses a Bidirectional GRU (encoding student attempt sequences, response latency, confidence, and distractor traps) with a multi-tier Cognitive Profile ANN (measuring Tier Divergence between Basic Recall and Applied Reasoning).
- **False Mastery Detection:** Flags situations where a student exhibits high basic/conceptual accuracy but collapses on applied problem-solving.
- **Pedagogical Misconception Isolation:** Maps student distractor selections to cataloged cognitive misconceptions and provides instant debiasing remediation.
- **DAG Prerequisite Gap Traversal:** Automatically traces downstream comprehension failures back through concept dependencies to isolate the root unlearned foundation.
- **Interactive Knowledge Gap Map:** Visualizes concept mastery in an interactive color-coded DAG:
  - 🟢 **Green:** Strong Understanding (Mastered)
  - 🟡 **Yellow:** Partial Understanding
  - 🟠 **Orange:** Conceptual Misconception / False Mastery
  - 🔴 **Red:** Prerequisite Knowledge Gap / Bottleneck
- **Adaptive Remedial Drills:** Allows students to take targeted 3-question remedial quizzes that dynamically update their mastery graph in real-time.
- **Faculty / Admin Analytics Portal:** Delivers class-level cohort intelligence on curriculum bottlenecks, failure rates, and misconception frequencies.

---

## 3. System Architecture & Technologies Used

```
DeepLearnX/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI REST Application & Static File Server
│   │   ├── database.py        # SQLite Database Engine & Table Definitions
│   │   ├── graph_engine.py    # Concept Dependency DAG Traversal Engine
│   │   └── predictor.py       # PyTorch Model Inference Pipeline
│   └── seed_data.py           # Database Seeder (Concepts, Questions, 5 Demo Personas)
├── frontend/
│   ├── index.html             # Single Page Application (8 Complete Views)
│   ├── css/styles.css         # Modern Glassmorphic Tech UI
│   └── js/
│       ├── api.js             # REST API Client
│       ├── app.js             # App Controller & Chart.js Visualizations
│       ├── assessment.js      # Assessment Quiz Engine & Timer
│       └── graph.js           # Vis-Network Interactive DAG Visualizer
├── model/
│   ├── architecture.py        # PyTorch DeepCognitiveNet (Bi-GRU + ANN + Multi-Task Heads)
│   ├── train.py               # Model Training Pipeline (AdamW + Cosine Annealing)
│   ├── evaluate.py            # Model Test Set Evaluation (Metrics + Confusion Matrix)
│   ├── deeplearnx_cognitive_model.pt # Trained PyTorch Weights Checkpoint
│   ├── metrics.json           # Evaluation Metrics File
│   ├── confusion_matrix.png   # Confusion Matrix Plot
│   └── training_history.json  # Loss Curves History
├── dataset/
│   ├── questions_dl_fundamentals.json # Tiered Question Bank (12 Concepts, 10 Misconceptions)
│   ├── generate_synthetic_dataset.py  # Realistic Cognitive Session Generator
│   ├── student_responses_train.csv    # 2,400 Training Sessions
│   └── student_responses_test.csv     # 600 Held-Out Test Sessions
├── database/
│   └── deeplearnx.db          # SQLite Database
├── notebooks/
│   └── model_training_and_experiments.ipynb # Jupyter Notebook for Viva & Defense
├── tests/
│   └── test_api.py            # Integration & API Unit Test Suite
├── documentation/
│   ├── ARCHITECTURE.md        # Mathematical Formulation & Layer Details
│   └── VIVA_QUESTIONS_AND_ANSWERS.md # 25+ Viva Defense Questions & Answers
├── run.py                     # 1-Command Launcher
└── README.md
```

### Technology Stack:
- **Deep Learning Framework:** PyTorch 2.9 (CPU & CUDA compatible)
- **Backend API:** Python FastAPI + Uvicorn
- **Database:** SQLite (zero-configuration, embedded relational persistence)
- **Frontend:** Modern HTML5, Responsive CSS3, Vanilla ES6+ JavaScript
- **Visual Graph & Charts:** Vis-Network (interactive physics-based DAG), Chart.js (cohort analytics)

---

## 4. Deep Learning Architecture (`DeepCognitiveNet`)

The neural network fuses sequential learning patterns with holistic behavioral metrics:

```
[Student Attempt Sequence]             [Structured Performance Profile]
(Concept, Tier, Misconception,          (Accuracy, Basic Acc, Conceptual Acc,
 Time, Confidence)                      App Acc, Tier Divergence, Streaks)
            │                                           │
            ▼                                           ▼
[Embeddings + Projection]                      [BatchNorm + Dense(64)]
            │                                           │
            ▼                                           ▼
[2-Layer Bidirectional GRU (96d)]              [Dense(48) + GELU]
            │                                           │
            ▼                                           │
[Self-Attention Sequence Pooling (96d)]                 │
            │                                           │
            └─────────────────────┬─────────────────────┘
                                  ▼
                     [Multimodal Fusion (144d)]
                                  │
                                  ▼
                       [Dense(96) + LayerNorm]
                                  │
     ┌────────────────────────────┼────────────────────────────┐
     ▼                            ▼                            ▼
[Cognitive State Head]   [Misconception Head]      [Prerequisite Risk Head]
   4-Class Softmax         11-Class Softmax          Continuous Sigmoid [0-1]
  (Genuine Mastery,       (Identifies active       (Foundational vulnerability)
   False Mastery,          misconception)
   Misconception,
   Knowledge Gap)
```

---

## 5. Actual Model Evaluation Metrics
*Evaluated on 600 held-out student response sessions:*

| Metric | Result |
| :--- | :--- |
| **Test Accuracy** | **100.00%** |
| **Macro Precision** | **100.00%** |
| **Macro Recall** | **100.00%** |
| **Macro F1-Score** | **100.00%** |
| **Total Test Samples** | **600 sessions (150 per class)** |

### Confusion Matrix:
```
Predicted ──>   Genuine Mastery   False Mastery   Misconception   Knowledge Gap
Genuine Mastery        150               0               0              0
False Mastery            0             150               0              0
Misconception            0               0             150              0
Knowledge Gap            0               0               0            150
```

---

## 6. Installation & Quick Start

### Step 1: Clone / Navigate to Directory
```bash
cd "d:\DL PROJECT"
```

### Step 2: Install Dependencies (if not already installed)
```bash
pip install torch fastapi uvicorn scikit-learn pandas numpy matplotlib
```

### Step 3: Run the Application (Single Command!)
```bash
python run.py
```
This automatically verifies the SQLite database, checks the trained PyTorch model, and launches the web application.

- **Web Dashboard:** [http://127.0.0.1:8055](http://127.0.0.1:8055)
- **Interactive OpenAPI Docs:** [http://127.0.0.1:8055/docs](http://127.0.0.1:8055/docs)

---

## 7. Viva & Demonstration Workflow

For project presentations and examiner demonstrations, DeepLearnX includes a **1-Click Demo Persona Switcher** at the top right:

1. **Demonstrate False Mastery:**
   - Switch persona to **Rahul Verma (`student_b`)**.
   - Inspect Dashboard: Notice raw score is **60.0% (Passing)**, but Deep Learning flags **False Mastery**.
   - Show the Bar Chart: Basic Recall is **100%**, Conceptual is **80%**, but Application is **20%** (**Memorization Divergence = 80%**).
2. **Demonstrate Prerequisite Knowledge Gap:**
   - Switch persona to **Sneha Patel (`student_c`)**.
   - Open **Knowledge Gap Map**: Observe that `Backpropagation` is red, and the DAG Engine has traced the root gap back to `Chain Rule`!
3. **Demonstrate Misconception Detection:**
   - Switch persona to **Karan Singh (`student_d`)**.
   - Notice the detected misconception banner: *Confusing Activation Functions with Loss Functions*.
4. **Demonstrate Adaptive Remediation:**
   - Click **"Start Remedial Drill"** on any student.
   - Complete the 3-question drill $\to$ Submit $\to$ Observe the concept node update to **Green (Mastered)**!
5. **Demonstrate Faculty Analytics:**
   - Switch persona to **Prof. Dr. R. K. Murthy (`admin`)**.
   - View class-wide cognitive state distribution, concept failure rates, and the student roster.

---

## 8. Limitations & Future Enhancements

### Current Limitations:
- Initial question bank focuses on 12 concepts in *Deep Learning Fundamentals*.
- Synthetic student response data was used to train the initial weights (clearly labeled).

### Future Enhancements:
- **Transformer-based Free-Text Reflection Analysis:** Incorporate small LLMs (e.g., lightweight BERT/DistilRoBERTa) to analyze student open-ended essay explanations of why they chose an answer.
- **Reinforcement Learning Policy:** Use an RL policy network to choose the next optimal learning activity sequence.
- **Canvas / Moodle LMS Integration:** Direct LTI plugins to sync with university learning management systems.

---

## 9. Academic Credentials
- **Course:** B.Tech Artificial Intelligence and Data Science (3rd Year Capstone)
- **Domain:** Educational Data Mining & Deep Learning (Cognitive Student Modeling)
- **Frameworks:** PyTorch 2.9, FastAPI, SQLite, Vis-Network, Chart.js
