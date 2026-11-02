"""
DeepLearnX backend application package marker.
Synchronizes module namespace aliases across varying entrypoint execution styles.
"""

import sys

# Ensure canonical module aliasing in sys.modules
_current_mod = sys.modules.get(__name__)
if _current_mod:
    for _alias in ("backend.app", "app", "Website.backend.app"):
        sys.modules.setdefault(_alias, _current_mod)
