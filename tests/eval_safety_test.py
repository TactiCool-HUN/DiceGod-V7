import os
import sys

found_unsafe = False

for root, _, files in os.walk("../"):
    for f in files:
        if f.endswith(".py"):
            path = os.path.join(root, f)
            with open(path, "r", encoding="utf-8") as file:
                for i, line in enumerate(file, 1):
                    if "eval(" in line and "# safety-wrapper-eval" not in line:
                        print(f"Unsafe eval found in {path}:{i}")
                        found_unsafe = True

if found_unsafe:
    sys.exit(1)
