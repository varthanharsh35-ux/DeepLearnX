"""
Predictor service for DeepLearnX
Loads trained PyTorch DeepCognitiveNet weights and runs live inference on student assessment sessions.
"""

import json
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
import torch
import torch.nn.functional as F

from architecture import DeepCognitiveNet

BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR.parent / "dataset"

with open(DATASET_DIR / "questions_dl_fundamentals.json", "r") as f:
    QUESTION_BANK_DATA = json.load(f)

CONCEPTS = {c["id"]: c for c in QUESTION_BANK_DATA["concepts"]}
CONCEPT_ID_TO_IDX = {c["id"]: idx for idx, c in enumerate(QUESTION_BANK_DATA["concepts"])}
QUESTIONS_BY_ID = {q["id"]: q for q in QUESTION_BANK_DATA["questions"]}
MISCONCEPTIONS_BY_ID = {m["id"]: m for m in QUESTION_BANK_DATA["misconceptions"]}
MISCONCEPTION_IDX_TO_ID = {idx + 1: m["id"] for idx, m in enumerate(QUESTION_BANK_DATA["misconceptions"])}

CLASS_NAMES = [
    "Genuine Mastery",
    "False Mastery",
    "Conceptual Misconception",
    "Knowledge Gap"
]

import sqlite3

def get_question_info(q_id: str) -> Dict[str, Any]:
    db_file = BASE_DIR.parent / "database" / "deeplearnx.db"
    if db_file.exists():
        conn = sqlite3.connect(str(db_file))
        conn.row_factory = sqlite3.Row
        r = conn.execute("SELECT * FROM questions WHERE id = ?", (q_id,)).fetchone()
        conn.close()
        if r:
            return dict(r)
    if q_id in QUESTIONS_BY_ID:
        return QUESTIONS_BY_ID[q_id]
    return {}

def get_misconception_info(m_id: str) -> Dict[str, Any]:
    if m_id in MISCONCEPTIONS_BY_ID:
        return MISCONCEPTIONS_BY_ID[m_id]
    db_file = BASE_DIR.parent / "database" / "deeplearnx.db"
    if db_file.exists():
        conn = sqlite3.connect(str(db_file))
        conn.row_factory = sqlite3.Row
        r = conn.execute("SELECT * FROM misconceptions WHERE id = ?", (m_id,)).fetchone()
        conn.close()
        if r:
            return dict(r)
    return {}

class DeepLearnXPredictor:
    def __init__(self, model_path: Path = None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        if model_path is None:
            model_path = BASE_DIR / "deeplearnx_cognitive_model.pt"
            
        self.model_path = model_path
        self.model = None
        self._load_model()
        
    def _load_model(self):
        if not self.model_path.exists():
            print(f"Warning: Model file {self.model_path} not found. Running in heuristic fallback mode until trained.")
            return
            
        checkpoint = torch.load(self.model_path, map_location=self.device)
        config = checkpoint.get("config", {
            "num_concepts": 12,
            "num_tiers": 3,
            "num_misconceptions": 11,
            "structured_dim": 9,
            "gru_hidden": 48,
            "num_classes": 4
        })
        
        self.model = DeepCognitiveNet(
            num_concepts=config["num_concepts"],
            num_tiers=config["num_tiers"],
            num_misconceptions=config["num_misconceptions"],
            structured_dim=config["structured_dim"],
            gru_hidden=config["gru_hidden"],
            num_classes=config["num_classes"]
        ).to(self.device)
        
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.model.eval()
        print("DeepLearnX DeepCognitiveNet model loaded successfully.")

    def analyze_session(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyzes a list of student responses.
        Each response dict:
        {
            "question_id": str,
            "selected_option": str ("A", "B", "C", "D"),
            "response_time": float (seconds),
            "confidence": int (1 to 5)
        }
        """
        if not responses:
            return {
                "predicted_state": "Knowledge Gap",
                "confidence": 0.0,
                "state_probabilities": {},
                "false_mastery_breakdown": {},
                "detected_misconceptions": [],
                "prerequisite_risk": 1.0,
                "attention_weights": []
            }
            
        # Parse responses
        seq_items = []
        basic_correct, basic_total = 0, 0
        conc_correct, conc_total = 0, 0
        app_correct, app_total = 0, 0
        
        detected_misconceptions = []
        heuristic_bias_count = 0
        rapid_guessing_count = 0
        two_tier_inconsistency_count = 0
        two_tier_passed_count = 0
        two_tier_total_count = 0
        concept_error_counts = {}
        candidate_misconceptions = []
        
        for r in responses:
            q_id = r.get("question_id")
            q_info = get_question_info(q_id)
            c_id = q_info.get("concept_id", "ann_basics")
            q_type = q_info.get("question_type", "basic")
            tier_idx = 0 if q_type == "basic" else (1 if q_type == "conceptual" else 2)
            
            selected = r.get("selected_option")
            correct = q_info.get("correct_option")
            is_correct = 1 if (selected == correct) else 0
            
            if not is_correct:
                concept_error_counts[c_id] = concept_error_counts.get(c_id, 0) + 1
            
            # Check option lengths for Length Cue Heuristic Gaming detection
            opts_dict = {}
            if "options" in q_info and isinstance(q_info["options"], dict):
                opts_dict = q_info["options"]
            else:
                opts_dict = {
                    "A": q_info.get("option_a", ""),
                    "B": q_info.get("option_b", ""),
                    "C": q_info.get("option_c", ""),
                    "D": q_info.get("option_d", "")
                }
            opt_lens = {k: len(str(v).split()) for k, v in opts_dict.items() if v}
            if opt_lens:
                longest_opt = max(opt_lens, key=opt_lens.get)
                if selected == longest_opt:
                    heuristic_bias_count += 1
            
            time_spent = float(r.get("response_time", 30.0))
            if time_spent < 3.5:
                rapid_guessing_count += 1
                
            # Check Two-Tier Reasoning Probe consistency
            reasoning_selected = r.get("reasoning_selected")
            rp = q_info.get("reasoning_probe")
            probe_passed = False
            if rp:
                if isinstance(rp, str):
                    try:
                        rp = json.loads(rp)
                    except Exception:
                        rp = None
                if rp and isinstance(rp, dict):
                    two_tier_total_count += 1
                    correct_probe = str(rp.get("correct_probe", "A")).strip().upper()
                    if reasoning_selected and str(reasoning_selected).strip().upper() == correct_probe:
                        two_tier_passed_count += 1
                        probe_passed = True
                    else:
                        if is_correct:
                            # Correct on main question but failed reasoning probe -> false mastery / surface guess
                            two_tier_inconsistency_count += 1

            # Check if selected distractor corresponds to misconception
            misc_id = q_info.get("misconception_id")
            selected_misc_idx = 0
            if not is_correct and misc_id:
                m_info = get_misconception_info(misc_id)
                if m_info:
                    # Stash candidate misconception; only confirm if supported by conceptual/application error or repeated misses
                    candidate_misconceptions.append({
                        "m_info": m_info,
                        "concept_id": c_id,
                        "q_type": q_type,
                        "probe_failed": (not probe_passed) if rp else False
                    })
                selected_misc_idx = 1 # flags non-zero misconception embedding
                        
            conf = int(r.get("confidence", 3))
            
            if q_type == "basic":
                basic_total += 1
                if is_correct: basic_correct += 1
            elif q_type == "conceptual":
                conc_total += 1
                if is_correct: conc_correct += 1
            else:
                app_total += 1
                if is_correct: app_correct += 1
                
            seq_items.append({
                "question_id": q_id,
                "concept_id": c_id,
                "concept_idx": CONCEPT_ID_TO_IDX.get(c_id, abs(hash(c_id)) % 12),
                "tier_idx": tier_idx,
                "is_correct": is_correct,
                "response_time": time_spent,
                "confidence": conf,
                "selected_misc_idx": selected_misc_idx
            })
            
        # Confirm misconceptions: require evidence from conceptual/application traps, failed probes, or repeated misses (2+)
        for cand in candidate_misconceptions:
            m = cand["m_info"]
            cid = cand["concept_id"]
            q_t = cand["q_type"]
            probe_fail = cand["probe_failed"]
            err_count = concept_error_counts.get(cid, 0)
            
            # An isolated error on a basic recall question without repeated misses is a simple knowledge gap, NOT a cognitive misconception
            if q_t in ["conceptual", "application"] or probe_fail or err_count >= 2:
                if m not in detected_misconceptions:
                    detected_misconceptions.append(m)

        total_q = len(seq_items)
        acc_basic = (basic_correct / basic_total) if basic_total > 0 else 0.0
        acc_conc = (conc_correct / conc_total) if conc_total > 0 else 0.0
        acc_app = (app_correct / app_total) if app_total > 0 else 0.0
        acc_overall = sum(s["is_correct"] for s in seq_items) / total_q
        tier_divergence = acc_basic - acc_app
        
        hbi = (heuristic_bias_count / total_q) if total_q > 0 else 0.0
        rgb = (rapid_guessing_count / total_q) if total_q > 0 else 0.0
        
        avg_conf = np.mean([s["confidence"] for s in seq_items]) / 5.0
        avg_time = np.mean([s["response_time"] for s in seq_items]) / 100.0
        
        misc_count = sum(1 for s in seq_items if s["selected_misc_idx"] > 0)
        distractor_ratio = misc_count / total_q
        
        max_streak = 0
        curr_streak = 0
        for s in seq_items:
            if s["is_correct"] == 0:
                curr_streak += 1
                max_streak = max(max_streak, curr_streak)
            else:
                curr_streak = 0
        streak_norm = max_streak / float(total_q)

        # 4 Behavioral Psychometric Features
        avg_switches = np.mean([float(r.get("switch_count", 1)) for r in responses]) / 5.0
        
        # Word counts per question for reading speed normalization
        time_per_words = []
        for r, s in zip(responses, seq_items):
            q_text = get_question_info(r.get("question_id")).get("question_text", "")
            w_cnt = max(len(q_text.split()), 6)
            time_per_words.append(s["response_time"] / float(w_cnt))
        avg_time_per_word = min(1.0, np.mean(time_per_words) / 3.0) if time_per_words else 0.35

        # Calibration gap (overconfidence on errors)
        cal_gaps = [max(0.0, (float(s["confidence"]) / 5.0) - float(s["is_correct"])) for s in seq_items]
        mean_calibration_gap = np.mean(cal_gaps) if cal_gaps else 0.2

        # Two-tier probe consistency
        if two_tier_total_count > 0:
            mean_probe_consistency = max(0.0, 1.0 - (two_tier_inconsistency_count / float(two_tier_total_count)))
        else:
            mean_probe_consistency = 0.85 if acc_overall > 0.7 else 0.40
        
        structured_feats = np.array([
            acc_overall, acc_basic, acc_conc, acc_app,
            tier_divergence, avg_conf, avg_time, distractor_ratio, streak_norm,
            avg_switches, avg_time_per_word, mean_calibration_gap, mean_probe_consistency
        ], dtype=np.float32)

        # If model expects 9 dims, slice gracefully
        if hasattr(self, "model") and self.model and hasattr(self.model, "structured_ann"):
            expected_in = self.model.structured_ann[0].in_features
            if expected_in == 9:
                structured_feats = structured_feats[:9]
        
        # Prepare PyTorch Tensors
        max_len = 18
        T = min(total_q, max_len)
        t_concepts = np.zeros(max_len, dtype=np.int64)
        t_tiers = np.zeros(max_len, dtype=np.int64)
        t_miscs = np.zeros(max_len, dtype=np.int64)
        t_cont = np.zeros((max_len, 3), dtype=np.float32)
        
        for t in range(T):
            item = seq_items[t]
            t_concepts[t] = item["concept_idx"]
            t_tiers[t] = item["tier_idx"]
            t_miscs[t] = item["selected_misc_idx"]
            t_cont[t, 0] = float(item["is_correct"])
            t_cont[t, 1] = float(item["response_time"]) / 100.0
            t_cont[t, 2] = float(item["confidence"]) / 5.0
            
        tensor_c = torch.tensor(t_concepts, dtype=torch.long).unsqueeze(0).to(self.device)
        tensor_t = torch.tensor(t_tiers, dtype=torch.long).unsqueeze(0).to(self.device)
        tensor_m = torch.tensor(t_miscs, dtype=torch.long).unsqueeze(0).to(self.device)
        tensor_cont = torch.tensor(t_cont, dtype=torch.float32).unsqueeze(0).to(self.device)
        tensor_s = torch.tensor(structured_feats, dtype=torch.float32).unsqueeze(0).to(self.device)
        
        if self.model is not None:
            with torch.no_grad():
                pred_state, pred_misc, pred_risk, attn_w = self.model(
                    tensor_c, tensor_t, tensor_m, tensor_cont, tensor_s
                )
                state_probs = F.softmax(pred_state, dim=1).cpu().numpy()[0]
                misc_probs = F.softmax(pred_misc, dim=1).cpu().numpy()[0]
                risk_val = float(pred_risk.cpu().numpy()[0][0])
                
                # Attention weights over sequence
                attn_vals = attn_w.cpu().numpy()[0].flatten()[:T].tolist()
        else:
            # Fallback heuristic calculation if model not yet loaded
            state_probs = [0.25, 0.25, 0.25, 0.25]
            risk_val = 0.5
            attn_vals = [1.0 / T] * T
            
        pred_class_idx = int(np.argmax(state_probs))
        predicted_state = CLASS_NAMES[pred_class_idx]
        
        is_gaming_detected = False
        gaming_reason = None
        
        # 1. Anti-Gaming Heuristic Detection: Length Cue Bias Exploitation
        if hbi >= 0.60:
            is_gaming_detected = True
            predicted_state = "False Mastery"
            pred_class_idx = 1
            gaming_reason = f"Heads up! It looks like you chose the longest answer in {round(hbi * 100)}% of questions. The longest choice isn't always the right one—take your time to read each question carefully!"
        elif rgb >= 0.50 and hbi >= 0.40:
            is_gaming_detected = True
            predicted_state = "False Mastery"
            pred_class_idx = 1
            gaming_reason = f"You answered {round(rgb * 100)}% of questions in under 3.5 seconds. Slowing down just a bit will help you avoid simple mistakes and understand the problems better!"
        elif two_tier_inconsistency_count >= 2:
            predicted_state = "Conceptual Misconception"
            pred_class_idx = 2
            gaming_reason = f"You picked some correct answers, but missed {two_tier_inconsistency_count} follow-up reasoning checks. Let's make sure the core principle makes sense to you!"
        elif tier_divergence >= 0.40 and acc_basic >= 0.70 and acc_app <= 0.40:
            predicted_state = "False Mastery"
            pred_class_idx = 1
        elif detected_misconceptions and predicted_state == "Genuine Mastery":
            predicted_state = "Conceptual Misconception"
            pred_class_idx = 2
        elif acc_overall >= 0.85 and acc_app >= 0.80 and not detected_misconceptions and not is_gaming_detected and two_tier_inconsistency_count < 2:
            predicted_state = "Genuine Mastery"
            pred_class_idx = 0
            
        # Detailed false mastery diagnostics
        false_mastery_breakdown = {
            "is_false_mastery": (predicted_state == "False Mastery"),
            "basic_accuracy": round(acc_basic * 100, 1),
            "conceptual_accuracy": round(acc_conc * 100, 1),
            "application_accuracy": round(acc_app * 100, 1),
            "tier_divergence": round(tier_divergence * 100, 1),
            "divergence_significance": "HIGH" if tier_divergence >= 0.4 else ("MODERATE" if tier_divergence >= 0.2 else "LOW"),
            "heuristic_bias_index": round(hbi * 100, 1),
            "rapid_guessing_pct": round(rgb * 100, 1),
            "gaming_detected": is_gaming_detected,
            "two_tier_probes_tested": two_tier_total_count,
            "two_tier_probes_passed": two_tier_passed_count,
            "two_tier_inconsistencies": two_tier_inconsistency_count,
            "diagnosis": (
                gaming_reason if gaming_reason
                else (
                    "You did great with basic definitions, but got stuck on practical, applied questions. This happens when formulas are memorized without seeing how they work in real problems. Practice a few real examples to bridge this gap!"
                    if (tier_divergence >= 0.35 or predicted_state == "False Mastery")
                    else (
                        "You understand some core concepts, but encountered specific conceptual traps or missed key reasoning checks. Review the diagnostic breakdown below to correct these mix-ups!"
                        if (predicted_state == "Conceptual Misconception" or len(detected_misconceptions) > 0)
                        else (
                            "You are encountering gaps in foundational prerequisite concepts. Reviewing the recommended starting concept will help everything click into place!"
                            if predicted_state == "Knowledge Gap"
                            else (
                                "Awesome job! You have a solid grasp of both fundamental principles and practical problem solving."
                                if acc_overall >= 0.80
                                else "You have made a good start! With targeted practice on the challenging questions below, you'll reach full mastery."
                            )
                        )
                    )
                )
            )
        }
        
        state_probs_dict = {
            CLASS_NAMES[i]: round(float(state_probs[i]), 4)
            for i in range(len(CLASS_NAMES))
        }
        
        return {
            "predicted_state": predicted_state,
            "confidence": round(float(state_probs[pred_class_idx]), 4),
            "state_probabilities": state_probs_dict,
            "false_mastery_breakdown": false_mastery_breakdown,
            "detected_misconceptions": detected_misconceptions,
            "prerequisite_risk": round(risk_val, 3),
            "attention_weights": [round(w, 4) for w in attn_vals],
            "metrics_summary": {
                "overall_accuracy": round(acc_overall * 100, 1),
                "basic_accuracy": round(acc_basic * 100, 1),
                "conceptual_accuracy": round(acc_conc * 100, 1),
                "application_accuracy": round(acc_app * 100, 1),
                "avg_response_time": round(float(np.mean([s["response_time"] for s in seq_items])), 1),
                "avg_confidence": round(float(np.mean([s["confidence"] for s in seq_items])), 2)
            }
        }
