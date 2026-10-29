"""
DeepLearnX – Root Entrypoint Launcher
Automatically runs the DeepLearnX server from the Website directory.
"""
import sys
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
WEBSITE_DIR = ROOT_DIR / "Website"

if __name__ == "__main__":
    if not (WEBSITE_DIR / "run.py").exists():
        print(f"[ERROR] Could not find run.py in {WEBSITE_DIR}")
        sys.exit(1)
    
    print("=" * 65)
    print(" DeepLearnX: Launching from Website directory...")
    print("=" * 65)
    
    cmd = [sys.executable, str(WEBSITE_DIR / "run.py")] + sys.argv[1:]
    try:
        subprocess.run(cmd, cwd=str(WEBSITE_DIR))
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped by user.")
