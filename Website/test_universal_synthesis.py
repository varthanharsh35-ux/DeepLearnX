import sys
import re
import random
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "backend" / "app"))
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from backend.app.topic_researcher import fetch_wikipedia_knowledge
from backend.app.quiz_validator import validate_curriculum_package, check_sentence_completeness, check_distractor_contamination

print("Writing domain-general synthesis test...")
