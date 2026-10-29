"""
Add probes for DL questions: q_bp_app_1, q_gd_app_1, q_cnn_app_1, q_reg_app_1, q_ann_app_1
"""

import json
from pathlib import Path

DL_PATH = Path("d:/DL PROJECT/dataset/questions_dl_fundamentals.json")
data = json.load(open(DL_PATH, "r", encoding="utf-8"))

reasoning_probes = {
    "q_bp_app_1": {
        "prompt": "Which fundamental calculus rule enables the recursive calculation of error gradients back through composite layers?",
        "options": {
            "A": "Chain Rule of Differential Calculus for composite functions",
            "B": "Product Rule of Partial Derivatives without layer composition",
            "C": "Integration by Parts across non-linear affine layers",
            "D": "First-order Taylor Series polynomial approximation"
        },
        "correct_probe": "A"
    },
    "q_gd_app_1": {
        "prompt": "Why does standard Gradient Descent take steps in the direction of the negative gradient -∇L?",
        "options": {
            "A": "The negative gradient represents the direction of steepest local descent on the loss surface",
            "B": "The negative gradient guarantees the global optimum without saddle points",
            "C": "Gradient vectors must always point along Cartesian coordinate axes",
            "D": "Negative gradients prevent activation values from exploding"
        },
        "correct_probe": "A"
    },
    "q_cnn_app_1": {
        "prompt": "Which inductive architectural bias of CNNs enables spatial feature extraction with minimal parameters?",
        "options": {
            "A": "Translation Equivariance via shared spatial kernel weights across pixels",
            "B": "Full all-to-all connectivity across spatial tensor channels",
            "C": "Recurrent temporal feedback loops across spatial image dimensions",
            "D": "Stochastic random dropout of input channel pixels"
        },
        "correct_probe": "A"
    },
    "q_reg_app_1": {
        "prompt": "What mathematical penalty mechanism in L2 Regularization (Weight Decay) prevents model overfitting?",
        "options": {
            "A": "Penalizes the squared L2 Euclidean norm of weights in the optimization objective",
            "B": "Clamps negative weight values to strictly zero after each step",
            "C": "Inverts the sign of the learning rate during backward pass",
            "D": "Decreases the number of training data mini-batches"
        },
        "correct_probe": "A"
    },
    "q_ann_app_1": {
        "prompt": "Why is an activation function essential between linear transformation layers W*x + b?",
        "options": {
            "A": "Without non-linear activations, consecutive linear layers collapse into a single affine transformation",
            "B": "Activations prevent network weights from ever taking negative values",
            "C": "Linear layers cannot accept floating-point input features",
            "D": "Activations replace backpropagation with closed-form inversion"
        },
        "correct_probe": "A"
    }
}

for q in data["questions"]:
    if q["id"] in reasoning_probes:
        q["reasoning_probe"] = reasoning_probes[q["id"]]

with open(DL_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Updated DL probes successfully!")
