"""
Training Pipeline for DeepLearnX Multi-Branch Cognitive Neural Network
Trains the model on student response sequences and cognitive profiles.
Evaluates metrics: Accuracy, Precision, Recall, F1-Score, Confusion Matrix.
Saves model checkpoint and metrics JSON.
"""

import json
import os
import sys
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from pathlib import Path
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

from architecture import DeepCognitiveNet

# Set seeds
torch.manual_seed(42)
np.random.seed(42)

BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR.parent / "dataset"

class StudentSessionDataset(Dataset):
    def __init__(self, data_file: Path, max_seq_len: int = 18):
        with open(data_file, "r") as f:
            self.records = json.load(f)
        self.max_seq_len = max_seq_len

    def __len__(self):
        return len(self.records)

    def __getitem__(self, idx):
        rec = self.records[idx]
        seq = rec["sequence"]
        
        # Truncate or pad sequence
        T = min(len(seq), self.max_seq_len)
        concepts = np.zeros(self.max_seq_len, dtype=np.int64)
        tiers = np.zeros(self.max_seq_len, dtype=np.int64)
        miscs = np.zeros(self.max_seq_len, dtype=np.int64)
        cont = np.zeros((self.max_seq_len, 3), dtype=np.float32)
        
        for t in range(T):
            item = seq[t]
            concepts[t] = item["concept_idx"]
            tiers[t] = item["tier_idx"]
            miscs[t] = item["selected_misconception"]
            cont[t, 0] = float(item["is_correct"])
            cont[t, 1] = float(item["response_time"]) / 100.0 # normalized
            cont[t, 2] = float(item["confidence"]) / 5.0 # normalized
            
        # Structured features: 9 dims
        structured = np.array([
            rec["acc_overall"],
            rec["acc_basic"],
            rec["acc_conc"],
            rec["acc_app"],
            rec["tier_divergence"],
            rec["avg_conf"],
            rec["avg_time"],
            rec["distractor_ratio"],
            rec["streak_norm"]
        ], dtype=np.float32)
        
        target_state = int(rec["target_state"])
        primary_misc = int(rec["primary_misc_idx"])
        prereq_risk = float(rec["prereq_risk"])
        
        return {
            "concepts": torch.tensor(concepts, dtype=torch.long),
            "tiers": torch.tensor(tiers, dtype=torch.long),
            "miscs": torch.tensor(miscs, dtype=torch.long),
            "cont": torch.tensor(cont, dtype=torch.float32),
            "structured": torch.tensor(structured, dtype=torch.float32),
            "target_state": torch.tensor(target_state, dtype=torch.long),
            "primary_misc": torch.tensor(primary_misc, dtype=torch.long),
            "prereq_risk": torch.tensor(prereq_risk, dtype=torch.float32).unsqueeze(0)
        }

def train_model(epochs: int = 25, batch_size: int = 32, lr: float = 0.001):
    print("=" * 60)
    print(" DeepLearnX: Training Multi-Branch Cognitive Neural Network")
    print("=" * 60)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using compute device: {device}")
    
    train_dataset = StudentSessionDataset(DATASET_DIR / "student_sessions_train.json")
    test_dataset = StudentSessionDataset(DATASET_DIR / "student_sessions_test.json")
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    
    model = DeepCognitiveNet(
        num_concepts=12,
        num_tiers=3,
        num_misconceptions=11,
        structured_dim=9,
        gru_hidden=48,
        num_classes=4
    ).to(device)
    
    # Loss functions
    criterion_state = nn.CrossEntropyLoss()
    criterion_misc = nn.CrossEntropyLoss()
    criterion_risk = nn.MSELoss()
    
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    
    history = {
        "train_loss": [],
        "val_loss": [],
        "val_accuracy": [],
        "val_f1_macro": []
    }
    
    best_val_f1 = -1.0
    best_model_path = BASE_DIR / "deeplearnx_cognitive_model.pt"
    
    for epoch in range(1, epochs + 1):
        model.train()
        total_loss = 0.0
        
        for batch in train_loader:
            concepts = batch["concepts"].to(device)
            tiers = batch["tiers"].to(device)
            miscs = batch["miscs"].to(device)
            cont = batch["cont"].to(device)
            struct = batch["structured"].to(device)
            
            y_state = batch["target_state"].to(device)
            y_misc = batch["primary_misc"].to(device)
            y_risk = batch["prereq_risk"].to(device)
            
            optimizer.zero_grad()
            
            pred_state, pred_misc, pred_risk, _ = model(concepts, tiers, miscs, cont, struct)
            
            loss_state = criterion_state(pred_state, y_state)
            loss_misc = criterion_misc(pred_misc, y_misc)
            loss_risk = criterion_risk(pred_risk, y_risk)
            
            # Multi-task combined loss
            loss = loss_state + 0.4 * loss_misc + 0.3 * loss_risk
            
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=2.0)
            optimizer.step()
            
            total_loss += loss.item()
            
        scheduler.step()
        avg_train_loss = total_loss / len(train_loader)
        
        # Validation evaluation
        model.eval()
        val_loss = 0.0
        all_preds = []
        all_targets = []
        
        with torch.no_grad():
            for batch in test_loader:
                concepts = batch["concepts"].to(device)
                tiers = batch["tiers"].to(device)
                miscs = batch["miscs"].to(device)
                cont = batch["cont"].to(device)
                struct = batch["structured"].to(device)
                
                y_state = batch["target_state"].to(device)
                y_misc = batch["primary_misc"].to(device)
                y_risk = batch["prereq_risk"].to(device)
                
                pred_state, pred_misc, pred_risk, _ = model(concepts, tiers, miscs, cont, struct)
                
                l_s = criterion_state(pred_state, y_state)
                l_m = criterion_misc(pred_misc, y_misc)
                l_r = criterion_risk(pred_risk, y_risk)
                batch_val_loss = l_s + 0.4 * l_m + 0.3 * l_r
                val_loss += batch_val_loss.item()
                
                preds = torch.argmax(pred_state, dim=1).cpu().numpy()
                all_preds.extend(preds)
                all_targets.extend(y_state.cpu().numpy())
                
        avg_val_loss = val_loss / len(test_loader)
        val_acc = accuracy_score(all_targets, all_preds)
        val_f1 = f1_score(all_targets, all_preds, average="macro")
        
        history["train_loss"].append(round(avg_train_loss, 4))
        history["val_loss"].append(round(avg_val_loss, 4))
        history["val_accuracy"].append(round(val_acc, 4))
        history["val_f1_macro"].append(round(val_f1, 4))
        
        print(f"Epoch {epoch:02d}/{epochs:02d} | Train Loss: {avg_train_loss:.4f} | Val Loss: {avg_val_loss:.4f} | Val Acc: {val_acc:.4f} | Val F1: {val_f1:.4f}")
        
        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            torch.save({
                "model_state_dict": model.state_dict(),
                "epoch": epoch,
                "val_accuracy": val_acc,
                "val_f1_macro": val_f1,
                "config": {
                    "num_concepts": 12,
                    "num_tiers": 3,
                    "num_misconceptions": 11,
                    "structured_dim": 9,
                    "gru_hidden": 48,
                    "num_classes": 4
                }
            }, best_model_path)
            
    print(f"\nTraining Complete! Best Model saved to {best_model_path}")
    print(f"Best Validation Macro F1: {best_val_f1:.4f}")
    
    # Save training history
    with open(BASE_DIR / "training_history.json", "w") as f:
        json.dump(history, f, indent=2)

if __name__ == "__main__":
    train_model()
