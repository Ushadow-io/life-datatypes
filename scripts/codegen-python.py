#!/usr/bin/env python3
"""
Generate Pydantic models from JSON Schema
Run: python scripts/codegen-python.py
"""

import json
import subprocess
from pathlib import Path

def generate_python():
    schema_path = Path(__file__).parent.parent / "schema" / "conversation.json"
    output_dir = Path(__file__).parent.parent / "generated" / "python"
    output_file = output_dir / "life_datatypes" / "models.py"

    output_dir.mkdir(parents=True, exist_ok=True)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Create __init__.py
    init_file = output_file.parent / "__init__.py"
    init_file.write_text(
        '"""Life Datatypes - Shared conversation schema models"""\n'
        'from .models import Segment, Fragment, Thread, Conversation\n\n'
        '__all__ = ["Segment", "Fragment", "Thread", "Conversation"]\n'
    )

    try:
        cmd = [
            "datamodel-code-generator",
            "--input", str(schema_path),
            "--output", str(output_file),
            "--target-python-version", "3.10",
            "--class-config", "ConfigDict(extra='forbid')",
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"❌ Python codegen failed: {result.stderr}")
            return False

        # Add banner comment
        with open(output_file, 'r') as f:
            content = f.read()

        banner = (
            '"""\n'
            'Auto-generated from schema/conversation.json\n'
            'DO NOT EDIT DIRECTLY\n'
            'Run: python scripts/codegen-python.py\n'
            '"""\n\n'
        )

        with open(output_file, 'w') as f:
            f.write(banner + content)

        print(f"✓ Generated {output_file}")
        return True

    except Exception as e:
        print(f"❌ Python codegen error: {e}")
        return False

if __name__ == "__main__":
    success = generate_python()
    exit(0 if success else 1)
