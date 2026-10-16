"""
Balance Deep Learning fundamentals questions:
- Equalize option word counts (remove trailing explanations, symmetric distractors).
- Balance correct keys across A, B, C, D (~25% each).
- Add Reasoning Probes to application questions.
"""

import json
from pathlib import Path

DL_PATH = Path("d:/DL PROJECT/dataset/questions_dl_fundamentals.json")
data = json.load(open(DL_PATH, "r", encoding="utf-8"))

target_keys = ["A", "B", "C", "D", "B", "C", "D", "A", "C", "D", "A", "B", 
               "D", "A", "B", "C", "A", "B", "C", "D", "B", "C", "D", "A", 
               "C", "D", "A", "B", "D", "A"]

reasoning_probes = {
    "q_backprop_app_1": {
        "prompt": "Which fundamental calculus rule governs the recursive backward pass of error gradients across network layers?",
        "options": {
            "A": "Chain Rule of Differential Calculus for composite functions",
            "B": "Product Rule of Partial Derivation without functional composition",
            "C": "Integration by Parts across non-linear affine layers",
            "D": "Taylor Series First-Order polynomial approximation"
        },
        "correct_probe": "A"
    },
    "q_cnn_app_1": {
        "prompt": "Which core inductive bias of Convolutional Neural Networks enables drastic parameter reduction compared to dense layers?",
        "options": {
            "A": "Translation Equivariance via shared spatial kernel weights",
            "B": "Full all-to-all connectivity across tensor channels",
            "C": "Recurrent temporal feedback loops across spatial dimensions",
            "D": "Stochastic random drop of input image pixels"
        },
        "correct_probe": "A"
    },
    "q_reg_app_1": {
        "prompt": "What mathematical penalty mechanism in L2 Regularization (Weight Decay) prevents model overfitting?",
        "options": {
            "A": "Penalizes the squared magnitude of weights in the loss objective",
            "B": "Forcibly clamps negative weight values to strictly zero",
            "C": "Inverts the sign of learning rate during gradient descent",
            "D": "Decreases the number of training data mini-batches"
        },
        "correct_probe": "A"
    },
    "q_opt_app_1": {
        "prompt": "Why does Adam Optimizer accelerate convergence compared to standard Stochastic Gradient Descent?",
        "options": {
            "A": "Maintains per-parameter adaptive learning rates via first and second gradient moments",
            "B": "Computes exact second-order Hessian matrix inversions at each iteration",
            "C": "Completely eliminates the backpropagation backward pass step",
            "D": "Forces loss gradients to remain constant throughout training"
        },
        "correct_probe": "A"
    }
}

for i, q in enumerate(data["questions"]):
    curr_correct_key = q["correct_option"]
    curr_correct_text = q["options"][curr_correct_key]
    
    # Strip obvious trailing verbose explanations from correct text if any
    clean_correct = curr_correct_text.split(" (e.g.")[0].split(" (which")[0].split(" because ")[0].strip()
    
    # Prepare all 4 options cleaned
    opts = {}
    for k, v in q["options"].items():
        opts[k] = v.split(" (e.g.")[0].split(" (which")[0].strip()
    
    new_key = target_keys[i % len(target_keys)]
    
    if new_key != curr_correct_key:
        # Swap texts so that new_key gets correct text
        temp = opts[new_key]
        opts[new_key] = clean_correct
        opts[curr_correct_key] = temp
        q["correct_option"] = new_key
    else:
        opts[new_key] = clean_correct
        
    q["options"] = opts
    
    # Attach reasoning probe if in dict
    if q["id"] in reasoning_probes:
        q["reasoning_probe"] = reasoning_probes[q["id"]]

with open(DL_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

key_dist = {}
for q in data["questions"]:
    key_dist[q["correct_option"]] = key_dist.get(q["correct_option"], 0) + 1

print("Balanced DL questions saved! Key distribution:", key_dist)
