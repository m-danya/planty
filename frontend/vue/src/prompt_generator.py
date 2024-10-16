from pathlib import Path
import sys

with open("prompt.txt", "w") as output_file:
    sys.stdout = output_file
    for filepath in Path("./frontend/src").rglob("*.vue"):
        print(f"// {filepath.name}")
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("<style"):
                    break
                print(line, end="")
        print()
