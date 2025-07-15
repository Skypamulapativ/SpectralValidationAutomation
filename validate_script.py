import sys
import os
import subprocess

if len(sys.argv) != 2:
    print("Usage: python validate_script.py <filepath>")
    sys.exit(1)

filepath = sys.argv[1]

if not os.path.exists(filepath):
    print(f"❌ File not found: {filepath}")
    sys.exit(1)

try:
    print(f"Running command: spectral lint {filepath}")
    result = subprocess.run(["spectral", "lint", filepath], capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ YAML validation successful!")
        print(result.stdout)
    else:
        print("❌ YAML validation failed!")
        print(result.stderr)
        sys.exit(1)

except Exception as e:
    print(f"❌ Error running Spectral: {str(e)}")
    sys.exit(1)
