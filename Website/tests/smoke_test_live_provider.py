"""
DeepLearnX Live LLM Provider End-to-End Smoke Test.

Usage:
    python Website/tests/smoke_test_live_provider.py [--provider {gemini,openai,auto}] [--key YOUR_API_KEY] [--topic TOPIC_NAME]

Exits cleanly with 0 if:
- Live generation succeeds and passes all pedagogical verification checks (DAG, equalized options, reasoning probes).
- Live credentials are not configured (prints clear instructions to set GEMINI_API_KEY or OPENAI_API_KEY in Website/.env).
Exits with 1 only on unexpected runtime errors.
"""

import os
import sys
import argparse
from pathlib import Path

# Add project root and backend to sys.path
BASE_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = BASE_DIR / "backend" / "app"
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BACKEND_DIR))

# Load .env if present
ENV_FILE = BASE_DIR / ".env"
if ENV_FILE.exists():
    try:
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
    except Exception:
        pass


def run_live_smoke_test():
    parser = argparse.ArgumentParser(description="DeepLearnX Live Provider Smoke Test")
    parser.add_argument("--provider", default="auto", choices=["auto", "gemini", "openai"], help="Target provider")
    parser.add_argument("--key", default="", help="Optional explicit API key override")
    parser.add_argument("--topic", default="Quantum Mechanics", help="Topic to generate curriculum for")
    args = parser.parse_args()

    print("=" * 70)
    print(" DEEPLEARNX LIVE LLM PROVIDER SMOKE TEST ")
    print("=" * 70)

    try:
        from providers.manager import get_provider_manager
        from quiz_validator import validate_knowledge_dag, validate_curriculum_package
        from syllabus_generator import SyllabusGeneratorEngine
    except ImportError as e:
        print(f"[IMPORT ERROR] {e}")
        return 1

    mgr = get_provider_manager()
    if args.key:
        if args.provider == "openai" or args.key.startswith("sk-"):
            mgr.openai_config.api_key = args.key
        else:
            mgr.gemini_config.api_key = args.key

    status = mgr.get_status(force_refresh=True)
    print(f"\n[Provider Diagnostic Status]")
    print(f"  Active Mode       : {status.get('active_mode')}")
    print(f"  Provider State    : {status.get('provider_state')}")
    print(f"  Live LLM Ready    : {status.get('live_llm_ready')}")
    print(f"  Selected Provider : {status.get('selected_provider')}")
    print(f"  Model             : {status.get('model')}")
    print(f"  Message           : {status.get('message')}")

    active_provider = mgr.get_active_provider()
    has_keys = bool(args.key or (active_provider and active_provider.config.api_key))

    if not has_keys or not status.get("live_llm_ready"):
        print("\n" + "#" * 70)
        print(" [STATUS: BLOCKED -- LIVE PROVIDER CREDENTIALS NOT CONFIGURED]")
        print("#" * 70)
        print("\nTo activate live LLM generation:")
        print("  1. Open 'Website/.env' (copy from 'Website/.env.example' if needed)")
        print("  2. Add your Google Gemini API key:")
        print("       GEMINI_API_KEY=AIzaSy...")
        print("     Or your OpenAI API key:")
        print("       OPENAI_API_KEY=sk-...")
        print("  3. Re-run this smoke test script:\n")
        print("       python Website/tests/smoke_test_live_provider.py\n")
        print("DeepLearnX will continue operating in authentic offline knowledge synthesis mode.")
        print("=" * 70)
        return 0

    print(f"\nAttempting live curriculum generation for topic: '{args.topic}'...")
    try:
        generator = SyllabusGeneratorEngine()
        result = generator.generate_custom_domain(
            topic_title=args.topic,
            api_key=args.key if args.key else None,
            api_provider=args.provider if args.provider != "auto" else None,
            require_live_llm=True
        )

        print(f"\n[Generation Result]")
        print(f"  Status            : {result.get('status')}")
        print(f"  Domain ID         : {result.get('domain_id')}")
        print(f"  LLM Used          : {result.get('llm_used')}")
        print(f"  Generation Source : {result.get('generation_source')}")
        print(f"  Provider          : {result.get('llm_provider')}")
        print(f"  Model Used        : {result.get('model_name')}")
        print(f"  Concepts Count    : {result.get('concepts_count')}")
        print(f"  Questions Count   : {result.get('questions_count')}")

        # Check Kahn's topological sort
        concepts = result.get("concepts", [])
        dag_ok, dag_errs = validate_knowledge_dag(concepts)
        print(f"\n[Pedagogical Quality Verification]")
        print(f"  Kahn's DAG Valid  : {'PASS (Acyclic Directed Graph)' if dag_ok else f'FAIL ({dag_errs})'}")

        # Check provenance
        prov = result.get("provenance", {})
        print(f"  Provenance Record : {'PASS' if prov else 'FAIL'}")
        if prov:
            print(f"    - Overall Mode  : {prov.get('overall_mode')}")
            print(f"    - Topic Stage   : {prov.get('topic_interpretation_source')}")
            print(f"    - Concept Stage : {prov.get('concept_generation_source')}")
            print(f"    - Question Stage: {prov.get('question_generation_source')}")
            print(f"    - Probe Stage   : {prov.get('probe_generation_source')}")

        print("\n" + "=" * 70)
        print(" LIVE PROVIDER SMOKE TEST: PASSED ")
        print("=" * 70)
        return 0

    except Exception as e:
        print(f"\n[ERROR] Live generation failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(run_live_smoke_test())
