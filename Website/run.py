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

def start_port_bridge(source_port: int, target_port: int):
    """Bridges alternative ports (e.g. 8000) to target_port (8055) so both work seamlessly."""
    import socket
    import threading

    def forward(src, dst):
        try:
            while True:
                data = src.recv(4096)
                if not data:
                    break
                dst.sendall(data)
        except Exception:
            pass
        finally:
            try: src.close()
            except Exception: pass
            try: dst.close()
            except Exception: pass

    def start_listener(host: str, is_ipv6: bool = False):
        try:
            family = socket.AF_INET6 if is_ipv6 else socket.AF_INET
            server = socket.socket(family, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((host, source_port))
            server.listen(15)
            while True:
                client_sock, _ = server.accept()
                try:
                    remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    remote_sock.connect(("127.0.0.1", target_port))
                    threading.Thread(target=forward, args=(client_sock, remote_sock), daemon=True).start()
                    threading.Thread(target=forward, args=(remote_sock, client_sock), daemon=True).start()
                except Exception:
                    try: client_sock.close()
                    except Exception: pass
        except Exception:
            pass

    threading.Thread(target=start_listener, args=("0.0.0.0", False), daemon=True).start()
    try:
        threading.Thread(target=start_listener, args=("::", True), daemon=True).start()
    except Exception:
        pass

def main():
    ensure_prerequisites()
    
    port = int(os.environ.get("PORT", 8055))
    
    # Enable dual-port bridge on port 8000 if different from port
    if port != 8000:
        start_port_bridge(8000, port)

    print("\n" + "=" * 65)
    print(" STARTING DEEPLEARNX WEB APPLICATION")
    print("=" * 65)
    print(f" * Primary URL:        http://localhost:{port}")
    if port != 8000:
        print(f" * Alternative URL:    http://localhost:8000 (Bridged)")
    print(f" * Interactive Docs:   http://localhost:{port}/docs")
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
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False, log_level="info")

if __name__ == "__main__":
    main()
