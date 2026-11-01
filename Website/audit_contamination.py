import glob
import os

search_terms = [
    'feedback regulation',
    'system equilibrium',
    'non-linear saturation',
    'critical threshold',
    'governing mechanism',
    'fluctuating operational',
    'Foundational Premise Inversion',
    'Directional Causality Trap',
    'Boundary Limit Neglect',
    'Symptom vs. Root Cause Confusion',
    'an analyst extrapolates',
    'governing boundary constraints',
    'operational boundaries',
    'linear model extrapolation'
]

print("=== CODEBASE CONTAMINATION AUDIT ===")
found_map = {}
for root, dirs, files in os.walk('Website'):
    for file in files:
        if file.endswith(('.py', '.js', '.json', '.html')):
            p = os.path.join(root, file)
            try:
                with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                matches = [t for t in search_terms if t.lower() in content.lower()]
                if matches:
                    found_map[p] = matches
                    print(f"{p}: {matches}")
            except Exception as e:
                pass
