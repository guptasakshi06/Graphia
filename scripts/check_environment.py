"""Check the local Python dependencies and external Tesseract English data.

Run with the current checkout's .venv/bin/python. A nonzero exit code means
setup needs attention. This checks setup only, not OCR accuracy or the app.
"""

import argparse
import importlib
import importlib.metadata
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path


DEPENDENCIES = {
    "numpy": "numpy",
    "opencv-python-headless": "cv2",
    "matplotlib": "matplotlib",
    "pytesseract": "pytesseract",
    "streamlit": "streamlit",
    "Pillow": "PIL",
}


def check_environment():
    """Return serializable observations and problems without hiding failures."""
    report = {
        "python": platform.python_version(),
        "executable": sys.executable,
        "prefix": sys.prefix,
        "virtual_environment": sys.prefix != sys.base_prefix,
        "platform": platform.platform(),
        "packages": {},
        "tesseract": {"path": shutil.which("tesseract")},
        "problems": [],
    }
    if not report["virtual_environment"]:
        report["problems"].append("Use this checkout's .venv/bin/python.")

    for distribution, module_name in DEPENDENCIES.items():
        try:
            importlib.import_module(module_name)
            report["packages"][distribution] = {
                "version": importlib.metadata.version(distribution),
                "import": "PASS",
            }
        except Exception as exc:
            message = f"{type(exc).__name__}: {exc}"
            report["packages"][distribution] = {"import": "FAIL", "error": message}
            report["problems"].append(f"{distribution}: {message}")

    engine = report["tesseract"]["path"]
    if engine is None:
        report["problems"].append(
            "Tesseract not found on PATH; install tesseract-ocr and tesseract-ocr-eng."
        )
    else:
        try:
            version = subprocess.run(
                [engine, "--version"], capture_output=True, text=True,
                check=True, timeout=15,
            )
            report["tesseract"]["version"] = version.stdout.splitlines()[0]
            languages = subprocess.run(
                [engine, "--list-langs"], capture_output=True, text=True,
                check=True, timeout=15,
            )
            # The first line is a heading; following lines are language IDs.
            report["tesseract"]["languages"] = [
                line.strip() for line in languages.stdout.splitlines()[1:]
                if line.strip()
            ]
            if "eng" not in report["tesseract"]["languages"]:
                report["problems"].append("Tesseract English data (eng) is missing.")
        except (OSError, subprocess.SubprocessError, IndexError) as exc:
            report["problems"].append(f"Tesseract check failed: {exc}")

    report["status"] = "PASS" if not report["problems"] else "FAIL"
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, help="Also save observations to this file.")
    args = parser.parse_args()
    report = check_environment()
    payload = json.dumps(report, indent=2) + "\n"
    print(payload, end="")
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(payload, encoding="utf-8")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
