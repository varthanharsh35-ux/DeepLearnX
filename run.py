"""
DeepLearnX – Entrypoint Runner
Single-command launcher:
python run.py
"""

import os
import sys
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
DB_FILE = ROOT_DIR / "database" / "deeplearnx.db"
MODEL_FILE = ROOT_DIR / "model" / "deeplearnx_cognitive_model.pt"

def ensure_prerequisites():
    print("=" * 65)
    print(" DeepLearnX: Concept Understanding & Knowledge Gap Detection")
    print(" Cognitive Diagnostic & Knowledge Gap Detection Platform")
    print("=" * 65)
    
    # 1. Check SQLite database
    if not DB_FILE.exists():
        print("[INIT] Database not found. Seeding database...")
        sys.path.insert(0, str(ROOT_DIR / "backend"))
        import seed_data
        seed_data.seed_database()
    else:
        print("[OK] SQLite database verified.")
        
    # 2. Check PyTorch model checkpoint
    if not MODEL_FILE.exists():
        print("[INIT] Trained PyTorch model not found. Training model now...")
        sys.path.insert(0, str(ROOT_DIR / "model"))
        import train
        train.train_model(epochs=15)
        import evaluate
        evaluate.evaluate_model()
    else:
        print("[OK] PyTorch DeepCognitiveNet model verified.")

def main():
    ensure_prerequisites()
    
    port = int(os.environ.get("PORT", 8055))
    
    print("\n" + "=" * 65)
    print(" STARTING DEEPLEARNX WEB APPLICATION")
    print("=" * 65)
    print(f" * Application Dashboard: http://127.0.0.1:{port}")
    print(f" * Interactive API Docs:  http://127.0.0.1:{port}/docs")
    print(" * Demo Accounts Available:")
    print("   - Student B (False Mastery): rahul / student123")
    print("   - Student A (Mastery):       ananya / student123")
    print("   - Student C (Prereq Gap):    sneha / student123")
    print("   - Student D (Misconception): karan / student123")
    print("   - Faculty / Admin:           admin / admin123")
    print("=" * 65 + "\n")
    
    # Launch uvicorn
    import uvicorn
    sys.path.insert(0, str(ROOT_DIR / "backend" / "app"))
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=False, log_level="info")

if __name__ == "__main__":
    main()
