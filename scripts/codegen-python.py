#!/usr/bin/env python3
"""
Generate Pydantic v2 models from the JSON Schema.
Run: python scripts/codegen-python.py   (needs datamodel-code-generator on PATH)
"""

import ast
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent.parent
SCHEMA = ROOT / "schema" / "conversation.json"
PACKAGE = ROOT / "generated" / "python" / "life_datatypes"
MODELS = PACKAGE / "models.py"

BANNER = (
    '"""\n'
    "Auto-generated from schema/conversation.json\n"
    "DO NOT EDIT DIRECTLY\n"
    "Run: python scripts/codegen-python.py\n"
    '"""\n\n'
)


def generate_python() -> bool:
    PACKAGE.mkdir(parents=True, exist_ok=True)
    cmd = [
        "datamodel-codegen",
        "--input", str(SCHEMA),
        "--input-file-type", "jsonschema",
        "--output", str(MODELS),
        "--output-model-type", "pydantic_v2.BaseModel",
        "--target-python-version", "3.10",
        "--use-annotated",
        "--field-constraints",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Python codegen failed: {result.stderr}")
        return False

    MODELS.write_text(BANNER + MODELS.read_text())

    # Export every generated class except the schema's unused root wrapper.
    tree = ast.parse(MODELS.read_text())
    names = [
        node.name
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name != "LifeDataTypes"
    ]
    (PACKAGE / "__init__.py").write_text(
        '"""Life Datatypes - shared capture and conversation schema models"""\n'
        f"from .models import {', '.join(names)}\n\n"
        f"__all__ = {names!r}\n"
    )
    print(f"✓ Generated {MODELS} ({len(names)} types)")
    return True


if __name__ == "__main__":
    raise SystemExit(0 if generate_python() else 1)
