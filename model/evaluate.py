"""
Evaluation & Metrics Pipeline for DeepLearnX
Loads the trained PyTorch model and computes:
- Accuracy
- Precision (Macro & Weighted)
- Recall (Macro & Weighted)
- F1-Score (Macro & Weighted)
- Per-class performance breakdown
- Confusion Matrix (saved as JSON and PNG plot)
"""

import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch
from pathlib import Path
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)

from architecture import DeepCognitiveNet
from train import StudentSessionDataset

BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR.parent / "dataset"

CLASS_NAMES = [
    "Genuine Mastery",
    "False Mastery",
    "Conceptual Misconception",
    "Knowledge Gap"
]

def evaluate_model():
    print("=" * 60)
    print(" DeepLearnX: Model Evaluation on Held-Out Test Set")
    print("=" * 60)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_path = BASE_DIR / "deeplearnx_cognitive_model.pt"
    
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found at {model_path}. Please train first.")
        
    checkpoint = torch.load(model_path, map_location=device)
    config = checkpoint["config"]
    
    model = DeepCognitiveNet(
        num_concepts=config["num_concepts"],
        num_tiers=config["num_tiers"],
        num_misconceptions=config["num_misconceptions"],
        structured_dim=config["structured_dim"],
        gru_hidden=config["gru_hidden"],
        num_classes=config["num_classes"]
    ).to(device)
    
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    
    test_dataset = StudentSessionDataset(DATASET_DIR / "student_sessions_test.json")
    from torch.utils.data import DataLoader
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
    
    all_preds = []
    all_targets = []
    all_risk_preds = []
    all_risk_targets = []
    
    with torch.no_grad():
        for batch in test_loader:
            concepts = batch["concepts"].to(device)
            tiers = batch["tiers"].to(device)
            miscs = batch["miscs"].to(device)
            cont = batch["cont"].to(device)
            struct = batch["structured"].to(device)
            
            y_state = batch["target_state"].to(device)
            y_risk = batch["prereq_risk"].to(device)
            
            pred_state, _, pred_risk, _ = model(concepts, tiers, miscs, cont, struct)
            
            preds = torch.argmax(pred_state, dim=1).cpu().numpy()
            all_preds.extend(preds)
            all_targets.extend(y_state.cpu().numpy())
            
            all_risk_preds.extend(pred_risk.cpu().numpy().flatten())
            all_risk_targets.extend(y_risk.cpu().numpy().flatten())
            
    # Compute metrics
    acc = accuracy_score(all_targets, all_preds)
    prec_macro = precision_score(all_targets, all_preds, average="macro")
    prec_weighted = precision_score(all_targets, all_preds, average="weighted")
    rec_macro = recall_score(all_targets, all_preds, average="macro")
    rec_weighted = recall_score(all_targets, all_preds, average="weighted")
    f1_mac = f1_score(all_targets, all_preds, average="macro")
    f1_wt = f1_score(all_targets, all_preds, average="weighted")
    cm = confusion_matrix(all_targets, all_preds)
    
    # Per-class metrics
    report = classification_report(all_targets, all_preds, target_names=CLASS_NAMES, output_dict=True)
    
    # Prerequisite risk MAE
    risk_mae = float(np.mean(np.abs(np.array(all_risk_preds) - np.array(all_risk_targets))))
    
    metrics = {
        "accuracy": round(float(acc), 4),
        "precision_macro": round(float(prec_macro), 4),
        "precision_weighted": round(float(prec_weighted), 4),
        "recall_macro": round(float(rec_macro), 4),
        "recall_weighted": round(float(rec_weighted), 4),
        "f1_macro": round(float(f1_mac), 4),
        "f1_weighted": round(float(f1_wt), 4),
        "risk_mae": round(risk_mae, 4),
        "confusion_matrix": cm.tolist(),
        "class_names": CLASS_NAMES,
        "per_class": {
            name: {
                "precision": round(float(report[name]["precision"]), 4),
                "recall": round(float(report[name]["recall"]), 4),
                "f1_score": round(float(report[name]["f1-score"]), 4),
                "support": int(report[name]["support"])
            }
            for name in CLASS_NAMES
        }
    }
    
    # Save metrics JSON
    with open(BASE_DIR / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
        
    print(f"Overall Accuracy:  {acc * 100:.2f}%")
    print(f"Macro Precision:   {prec_macro * 100:.2f}%")
    print(f"Macro Recall:      {rec_macro * 100:.2f}%")
    print(f"Macro F1-Score:    {f1_mac * 100:.2f}%")
    print("\nConfusion Matrix:")
    print(cm)
    
    # Generate Confusion Matrix Heatmap Plot
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    ax.figure.colorbar(im, ax=ax)
    
    ax.set(
        xticks=np.arange(cm.shape[1]),
        yticks=np.arange(cm.shape[0]),
        xticklabels=CLASS_NAMES,
        yticklabels=CLASS_NAMES,
        title="DeepLearnX Confusion Matrix\nStudent Understanding State Classification",
        ylabel="True Cognitive State",
        xlabel="Predicted Cognitive State"
    )
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right", rotation_mode="anchor")
    
    # Loop over data dimensions and create text annotations
    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, format(cm[i, j], 'd'),
                    ha="center", va="center",
                    color="white" if cm[i, j] > thresh else "black",
                    fontweight="bold")
    fig.tight_layout()
    plt.savefig(BASE_DIR / "confusion_matrix.png", dpi=150)
    plt.close()
    
    print(f"Confusion Matrix plot saved to {BASE_DIR / 'confusion_matrix.png'}")
    print(f"Detailed metrics saved to {BASE_DIR / 'metrics.json'}")
    return metrics

if __name__ == "__main__":
    evaluate_model()
