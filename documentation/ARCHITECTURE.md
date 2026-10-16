# DeepLearnX System Architecture & Technical Specification

## 1. Executive Summary

**Project Title:** DeepLearnX – Deep Learning-Based Student Concept Understanding and Knowledge Gap Detection System  
**Academic Target:** 3rd-Year B.Tech Artificial Intelligence and Data Science  

### The Problem with Traditional Grading:
Standard academic grading relies on total raw scores (e.g., 65% = Grade B). This creates three severe blind spots:
1. **False Mastery (The Illusion of Competence):** A student can achieve 65% simply by memorizing basic definitions and recall questions, yet fail 100% of application and problem-solving questions. Traditional tests award a passing grade without diagnosing that the student cannot apply the concept.
2. **Invisible Misconceptions:** An incorrect choice is treated as 0 marks, ignoring *why* the student picked that specific wrong answer (e.g., adding derivatives instead of multiplying in the Chain Rule).
3. **Unidentified Prerequisite Bottlenecks:** A failure in an advanced topic (e.g., Backpropagation) is often caused by an unaddressed defect in an upstream foundation (e.g., Derivatives or Matrix Operations).

---

## 2. End-to-End System Architecture

```
+-----------------------------------------------------------------------------------------+
|                                    STUDENT FRONTEND                                     |
|  - Assessment Quiz Interface (Basic, Conceptual, Application Tiers + Confidence + Timer)|
|  - Interactive Knowledge Dependency DAG Map (Vis-Network / Color-Coded Graph Nodes)     |
|  - Deep Learning Cognitive Diagnostic Report & Adaptive Remedial Drills                 |
+-----------------------------------------------------------------------------------------+
                                           | HTTP REST
                                           v
+-----------------------------------------------------------------------------------------+
|                                  FASTAPI BACKEND SERVER                                 |
|  - Assessment Controller & Orchestrator (/api/assessment/submit)                        |
|  - Concept Dependency DAG Engine (Upstream Traversal & Bottleneck Discovery)           |
|  - Adaptive Remedial Drill Engine & Faculty Analytics Dashboard                         |
+-----------------------------------------------------------------------------------------+
              |                                            |
              v                                            v
+-------------------------------+       +-------------------------------------------------+
|      SQLITE DATABASE          |       |     DEEPLEARNX COGNITIVE NEURAL NETWORK         |
|  - Users (Students, Faculty)  |       |               (DeepCognitiveNet)                |
|  - Concepts & Prerequisites   |       |                                                 |
|  - Misconceptions Catalog     |       |  [Branch 1: Sequential Cognitive Bi-GRU]        |
|  - Tiered Question Bank       |       |   - Concept, Tier & Misconception Embeddings   |
|  - Assessment & Remedial Logs |       |   - Response Latency & Confidence Normalization |
+-------------------------------+       |   - 2-Layer Bidirectional GRU + Self-Attention  |
                                        |                                                 |
                                        |  [Branch 2: Multi-Tier Cognitive ANN]           |
                                        |   - Structured Behavioral & Divergence Vectors  |
                                        |                                                 |
                                        |  [Multimodal Latent Cognitive Fusion]           |
                                        |                                                 |
                                        |  [Multi-Task Output Prediction Heads]           |
                                        |   - Head 1: Cognitive State Classifier (4-class)|
                                        |   - Head 2: Misconception Distractor Classifier|
                                        |   - Head 3: Prerequisite Risk Regressor (Sigmoid|
                                        +-------------------------------------------------+
```

---

## 3. Deep Learning Architecture Specification (`DeepCognitiveNet`)

### 3.1 Input Representations

1. **Sequential Input $\mathbf{X}_{seq} \in \mathbb{R}^{B \times T \times 35}$**:
   - $\mathbf{e}_{concept} \in \mathbb{R}^{16}$: Embedding of concept index $c \in \{0, \dots, 11\}$.
   - $\mathbf{e}_{tier} \in \mathbb{R}^{8}$: Embedding of question tier index $t \in \{0=\text{Basic}, 1=\text{Conceptual}, 2=\text{Application}\}$.
   - $\mathbf{e}_{misc} \in \mathbb{R}^{8}$: Embedding of chosen distractor misconception code $m \in \{0=\text{None}, 1..10\}$.
   - Continuous vector $\mathbf{v}_{cont} \in \mathbb{R}^{3}$: $[\text{is\_correct} \in \{0,1\}, \text{time\_norm} = \frac{\text{seconds}}{100}, \text{conf\_norm} = \frac{\text{confidence}}{5}]$.

2. **Structured Cognitive Vector $\mathbf{x}_{struct} \in \mathbb{R}^{B \times 9}$**:
   - `acc_overall`: Total correct / Total attempted.
   - `acc_basic`: Correct Basic questions / Total Basic questions.
   - `acc_conc`: Correct Conceptual questions / Total Conceptual questions.
   - `acc_app`: Correct Application questions / Total Application questions.
   - `tier_divergence`: $\Delta_{tier} = \text{acc\_basic} - \text{acc\_app}$.
   - `avg_conf`: Normalized mean student self-reported confidence.
   - `avg_time`: Normalized mean time per question.
   - `distractor_ratio`: Ratio of wrong choices matching known misconception codes.
   - `streak_norm`: Maximum consecutive incorrect attempt streak normalized by sequence length.

---

### 3.2 Mathematical Formulation of Layers

#### Branch 1: Sequential Bi-GRU with Self-Attention Pooling
$$\mathbf{h}_t = \text{BiGRU}\left(\text{LayerNorm}(\mathbf{W}_{in}\mathbf{x}_t + \mathbf{b}_{in})\right), \quad \mathbf{h}_t \in \mathbb{R}^{96}$$
$$\alpha_t = \frac{\exp(\mathbf{v}^T \tanh(\mathbf{W}_a \mathbf{h}_t))}{\sum_{k=1}^T \exp(\mathbf{v}^T \tanh(\mathbf{W}_a \mathbf{h}_k))}$$
$$\mathbf{z}_{seq} = \sum_{t=1}^T \alpha_t \mathbf{h}_t \in \mathbb{R}^{96}$$

#### Branch 2: Structured Cognitive ANN
$$\mathbf{z}_{struct} = \text{GELU}\left(\mathbf{W}_2 \cdot \text{Dropout}(\text{GELU}(\text{BatchNorm}(\mathbf{W}_1 \mathbf{x}_{struct} + \mathbf{b}_1))) + \mathbf{b}_2\right) \in \mathbb{R}^{48}$$

#### Fusion & Multi-Task Heads
$$\mathbf{z}_{fused} = \text{LayerNorm}\left(\mathbf{W}_f [\mathbf{z}_{seq} \,\|\, \mathbf{z}_{struct}] + \mathbf{b}_f\right) \in \mathbb{R}^{96}$$
$$\hat{\mathbf{y}}_{state} = \text{Softmax}(\mathbf{W}_{state} \mathbf{z}_{fused}) \in \mathbb{R}^4$$
$$\hat{\mathbf{y}}_{misc} = \text{Softmax}(\mathbf{W}_{misc} \mathbf{z}_{fused}) \in \mathbb{R}^{11}$$
$$\hat{r}_{prereq} = \sigma(\mathbf{W}_{risk} \mathbf{z}_{fused}) \in [0, 1]$$

#### Multi-Task Loss Objective:
$$\mathcal{L}_{total} = \mathcal{L}_{CE}(\hat{\mathbf{y}}_{state}, \mathbf{y}_{state}) + 0.4 \cdot \mathcal{L}_{CE}(\hat{\mathbf{y}}_{misc}, \mathbf{y}_{misc}) + 0.3 \cdot \mathcal{L}_{MSE}(\hat{r}_{prereq}, r_{prereq})$$

---

## 4. Concept Dependency Graph & Traversal Algorithm

The Deep Learning fundamentals domain is structured as a Directed Acyclic Graph (DAG) $G = (V, E)$, where $V$ represents concepts and directed edges $(u, v) \in E$ assert that concept $u$ is a prerequisite of $v$.

### Root Prerequisite Traversal:
```python
def find_root_prerequisite_bottleneck(troubled_concepts, graph, node_status_map):
    root_gaps = []
    for concept in troubled_concepts:
        # Check prerequisites
        for prereq in graph[concept].prerequisites:
            if node_status_map[prereq] in ["gap", "misconception", "partial"]:
                root_gaps.append(prereq)
    # Return topological earliest root
    return min(root_gaps, key=lambda c: graph[c].order_index) if root_gaps else troubled_concepts[0]
```
