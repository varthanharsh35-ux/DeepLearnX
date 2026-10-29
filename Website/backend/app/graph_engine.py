"""
Knowledge Dependency Graph Engine for DeepLearnX
Supports multi-domain concept DAG traversal:
Pokemon, Class 10 Chemistry, Class 10 Biology, Class 10 Math, and Deep Learning.
"""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional

try:
    from concept_guide import get_concept_guide, CONCEPT_GUIDE
except ImportError:
    from app.concept_guide import get_concept_guide, CONCEPT_GUIDE

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "database" / "deeplearnx.db"

# Visual status colors
STATUS_COLORS = {
    "mastered": {"bg": "#10b981", "border": "#059669", "text": "#ffffff", "label": "Strong Understanding"},
    "partial": {"bg": "#f59e0b", "border": "#d97706", "text": "#ffffff", "label": "Partial Understanding"},
    "misconception": {"bg": "#f97316", "border": "#ea580c", "text": "#ffffff", "label": "Conceptual Misconception"},
    "gap": {"bg": "#ef4444", "border": "#dc2626", "text": "#ffffff", "label": "Knowledge Gap"},
    "untested": {"bg": "#64748b", "border": "#475569", "text": "#ffffff", "label": "Not Evaluated"}
}

class KnowledgeGraphEngine:
    def __init__(self):
        pass

    def get_domain_concepts(self, domain_id: str = "deep_learning") -> Dict[str, Any]:
        """Loads concepts for the specified domain from SQLite."""
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM concepts WHERE domain_id = ? ORDER BY order_index ASC", (domain_id,)).fetchall()
        conn.close()

        concepts = {}
        for r in rows:
            concepts[r["id"]] = {
                "id": r["id"],
                "domain_id": r["domain_id"],
                "name": r["name"],
                "slug": r["slug"],
                "category": r["category"],
                "description": r["description"],
                "prerequisites": json.loads(r["prerequisites"] or "[]"),
                "order_index": r["order_index"]
            }
        return concepts

    def get_full_graph_structure(self, domain_id: str = "deep_learning") -> Dict[str, Any]:
        """Returns the foundational DAG structure for rendering."""
        concepts = self.get_domain_concepts(domain_id)
        nodes = []
        edges = []

        for c_id, c in concepts.items():
            nodes.append({
                "id": c_id,
                "label": c["name"],
                "category": c["category"],
                "description": c["description"],
                "order": c["order_index"],
                "status": "untested",
                "color": STATUS_COLORS["untested"]["bg"]
            })
            for p_id in c["prerequisites"]:
                if p_id in concepts:
                    edges.append({
                        "from": p_id,
                        "to": c_id,
                        "arrows": "to",
                        "label": "prerequisite"
                    })

        return {"nodes": nodes, "edges": edges, "domain_id": domain_id}

    def evaluate_student_graph(
        self,
        concept_scores: Dict[str, Dict[str, Any]],
        detected_misconceptions: List[Dict[str, Any]],
        primary_state: str,
        domain_id: str = "deep_learning"
    ) -> Dict[str, Any]:
        """
        Calculates per-node status and discovers root prerequisite gaps for a specific domain.
        """
        concepts = self.get_domain_concepts(domain_id)
        misc_concept_ids = {m.get("concept_id") for m in detected_misconceptions if m.get("concept_id")}

        node_status_map = {}

        for c_id, c in concepts.items():
            stats = concept_scores.get(c_id, {"correct": 0, "total": 0, "acc": 0.0})
            total = stats["total"]
            acc = stats["acc"] if total > 0 else None

            if total == 0:
                status = "untested"
            elif c_id in misc_concept_ids:
                status = "misconception"
            elif acc >= 0.75:
                status = "mastered"
            elif acc >= 0.50:
                status = "partial"
            else:
                status = "gap"

            node_status_map[c_id] = {
                "status": status,
                "accuracy": round(acc * 100, 1) if acc is not None else None,
                "correct": stats["correct"],
                "total": total,
                "color_info": STATUS_COLORS[status]
            }

        # Upstream DAG traversal to find root prerequisite gap
        troubled_concepts = [
            c_id for c_id, s in node_status_map.items()
            if s["status"] in ["gap", "misconception", "partial"]
        ]

        root_prereq_gaps = []
        for c_id in troubled_concepts:
            if c_id not in concepts:
                continue
            prereqs = concepts[c_id].get("prerequisites", [])
            for p in prereqs:
                p_status = node_status_map.get(p, {}).get("status", "untested")
                if p_status in ["gap", "misconception", "partial", "untested"]:
                    if p not in root_prereq_gaps:
                        root_prereq_gaps.append(p)

        primary_gap = None
        if root_prereq_gaps:
            primary_gap = root_prereq_gaps[0]
        elif troubled_concepts:
            sorted_troubled = sorted(troubled_concepts, key=lambda k: concepts[k]["order_index"] if k in concepts else 99)
            primary_gap = sorted_troubled[0]

        # Prepare Graph View for UI
        graph_view_nodes = []
        graph_view_edges = []

        for c_id, c in concepts.items():
            status_info = node_status_map.get(c_id, {"status": "untested", "accuracy": None})
            st = status_info["status"]
            color_meta = STATUS_COLORS[st]

            graph_view_nodes.append({
                "id": c_id,
                "label": c["name"],
                "sublabel": color_meta["label"],
                "category": c["category"],
                "status": st,
                "accuracy": status_info["accuracy"],
                "color": color_meta["bg"],
                "borderColor": color_meta["border"],
                "fontColor": color_meta["text"],
                "isRootGap": (c_id == primary_gap)
            })

            for p_id in c["prerequisites"]:
                if p_id in concepts:
                    is_critical_path = (p_id == primary_gap or c_id in troubled_concepts)
                    graph_view_edges.append({
                        "from": p_id,
                        "to": c_id,
                        "arrows": "to",
                        "color": "#ef4444" if is_critical_path and node_status_map.get(p_id, {}).get("status") in ["gap", "misconception"] else "#94a3b8",
                        "width": 2 if is_critical_path else 1
                    })

        return {
            "domain_id": domain_id,
            "node_status_map": node_status_map,
            "root_prerequisite_gaps": root_prereq_gaps,
            "primary_prerequisite_gap": primary_gap,
            "primary_gap_name": concepts[primary_gap]["name"] if (primary_gap and primary_gap in concepts) else "None Detected",
            "graph_nodes": graph_view_nodes,
            "graph_edges": graph_view_edges
        }

    def generate_recommendations(
        self,
        predicted_state: str,
        primary_gap_id: Optional[str],
        detected_misconceptions: List[Dict[str, Any]],
        troubled_concepts: List[str],
        domain_id: str = "deep_learning"
    ) -> List[Dict[str, Any]]:
        """Generates targeted academic recommendations for the student with rich concept explanations & examples."""
        concepts = self.get_domain_concepts(domain_id)
        recs = []
        step = 1

        if primary_gap_id and primary_gap_id in concepts:
            gap_c = concepts[primary_gap_id]
            guide = get_concept_guide(primary_gap_id, domain_id)
            recs.append({
                "step": step,
                "type": "Prerequisite Foundation Revision",
                "title": f"Review Key Starting Topic: {gap_c['name']}",
                "description": f"To master this subject, you need a strong foundation in {gap_c['name']}. Review the core idea and real-world example below before trying the practice drill.",
                "action": f"Read the {gap_c['name']} refresher below, then take the practice drill.",
                "concept_id": primary_gap_id,
                "concept_name": gap_c['name'],
                "guide": guide,
                "urgency": "High"
            })
            step += 1

        for m in detected_misconceptions:
            m_cid = m.get("concept_id")
            m_guide = get_concept_guide(m_cid, domain_id) if m_cid else None
            m_name = m.get("name", "Misconception")
            recs.append({
                "step": step,
                "type": "Misconception Correction",
                "title": f"Clear Up Mix-up: {m_name}",
                "description": m.get("description", "A small misunderstanding was detected in your answers."),
                "action": m.get("remediation", "Review the concept guide and example below."),
                "concept_id": m_cid,
                "concept_name": m_name,
                "guide": m_guide,
                "urgency": "Immediate"
            })
            step += 1

        if predicted_state == "False Mastery":
            target_cid = troubled_concepts[0] if troubled_concepts else (list(concepts.keys())[0] if concepts else "")
            fm_guide = get_concept_guide(target_cid, domain_id) if target_cid else None
            c_name = concepts.get(target_cid, {}).get("name", "Core Topic") if target_cid else "Core Topic"
            recs.append({
                "step": step,
                "type": "Application Practice",
                "title": f"Practice with Real-World Examples: {c_name}",
                "description": "You know the definitions well, but solving practical questions felt tricky. Working through real-world examples will help you master this topic.",
                "action": "Study the worked-out example below, then test your skills with a quick drill.",
                "concept_id": target_cid,
                "concept_name": c_name,
                "guide": fm_guide,
                "urgency": "High"
            })
            step += 1

        target_rem_cid = primary_gap_id or (troubled_concepts[0] if troubled_concepts else (list(concepts.keys())[0] if concepts else ""))
        rem_guide = get_concept_guide(target_rem_cid, domain_id) if target_rem_cid else None
        target_name = concepts.get(target_rem_cid, {}).get("name", "Topic") if target_rem_cid else "Topic"
        
        recs.append({
            "step": step,
            "type": "Remedial Assessment Drill",
            "title": f"Take 3-Question Practice Drill: {target_name}",
            "description": f"Test yourself on {target_name} with a quick 3-question drill. Scoring 2 out of 3 marks will turn your learning map Green (Mastered)!",
            "action": f"Click 'Start Remedial Assessment' below to practice.",
            "concept_id": target_rem_cid,
            "concept_name": target_name,
            "guide": rem_guide,
            "urgency": "Medium"
        })

        return recs
