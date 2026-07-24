#!/usr/bin/env python3
"""Static repository checks that do not require the World of Tanks client."""

from __future__ import annotations

import ast
import json
import re
import sys
import tokenize
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
IGNORED_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    "__pycache__",
    "build",
    "source",
    "temp",
}

errors: list[str] = []
checked_files = 0


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def add_error(path: Path | str, message: str) -> None:
    name = relative(path) if isinstance(path, Path) else path
    errors.append(f"{name}: {message}")


def is_ignored(path: Path) -> bool:
    try:
        parts = path.relative_to(ROOT).parts
    except ValueError:
        return True
    return any(part in IGNORED_DIRS for part in parts)


def iter_files(pattern: str) -> Iterable[Path]:
    for path in ROOT.rglob(pattern):
        if path.is_file() and not is_ignored(path):
            yield path


def read_text(path: Path) -> str:
    global checked_files
    checked_files += 1
    return path.read_text(encoding="utf-8-sig", errors="strict")


def strip_as3_comments_and_strings(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"//[^\n]*", "", text)
    text = re.sub(r'"(?:\\.|[^"\\])*"', '""', text)
    text = re.sub(r"'(?:\\.|[^'\\])*'", "''", text)
    return text


required_paths = [
    "README.md",
    "build.py",
    "build.example.json",
    ".github/workflows/ci.yml",
    ".github/workflows/release.yml",
    "python/gui/mods/mod_under_pressure_marks.py",
    "as3/src_flash/MarksPanelHangar.as3proj",
    "as3/src_flash/MarksPanelBattle.as3proj",
    "resources/in/mods/under_pressure.marks/en.json",
    "resources/in/mods/under_pressure.marks/ru.json",
    "resources/in/mods/under_pressure.marks/uk.json",
]
for item in required_paths:
    path = ROOT / item
    if not path.is_file():
        add_error(item, "required file is missing")

forbidden_paths = [
    ".github/workflows/bootstrap-marks.yml",
    "repo_split.py",
    "source.zip",
]
for item in forbidden_paths:
    path = ROOT / item
    if path.exists():
        add_error(item, "one-time split/bootstrap artifact must not remain in Marks")

junk_names = {"EvalScript error.tmp", "source.zip", "repo_split.py"}
junk_suffixes = {".log", ".pyc", ".pyo", ".tmp", ".wotmod"}
for path in ROOT.rglob("*"):
    if is_ignored(path) or not path.is_file():
        continue
    if path.name in junk_names or path.suffix.lower() in junk_suffixes:
        add_error(path, "generated or temporary file is tracked")

for path in iter_files("*.json"):
    try:
        json.loads(read_text(path))
    except Exception as exc:  # noqa: BLE001 - report the parser error verbatim
        add_error(path, f"invalid JSON: {exc}")

project_outputs: set[str] = set()
project_targets: set[Path] = set()
xml_files = list(iter_files("*.xml")) + list(iter_files("*.as3proj"))
for path in xml_files:
    try:
        tree = ET.parse(str(path))
    except Exception as exc:  # noqa: BLE001
        add_error(path, f"invalid XML: {exc}")
        continue

    if path.suffix.lower() != ".as3proj":
        continue

    root_node = tree.getroot()
    outputs = [
        node.attrib.get("path", "").replace("\\", "/")
        for node in root_node.findall(".//output/movie")
        if node.attrib.get("path")
    ]
    if not outputs:
        add_error(path, "project has no SWF output path")
    for output in outputs:
        name = Path(output).name
        if name in project_outputs:
            add_error(path, f"duplicate SWF output: {name}")
        project_outputs.add(name)

    compile_nodes = root_node.findall(".//compileTargets/compile")
    if not compile_nodes:
        add_error(path, "project has no compile target")
    for node in compile_nodes:
        raw_target = node.attrib.get("path", "").replace("\\", "/")
        target = (path.parent / raw_target).resolve()
        project_targets.add(target)
        if not target.is_file():
            add_error(path, f"compile target does not exist: {raw_target}")

python3_files = [ROOT / "build.py"] + sorted((ROOT / "tools").glob("*.py"))
for path in python3_files:
    if not path.is_file():
        continue
    try:
        ast.parse(read_text(path), filename=relative(path))
    except Exception as exc:  # noqa: BLE001
        add_error(path, f"Python 3 syntax error: {exc}")

mod_python = ROOT / "python/gui/mods/mod_under_pressure_marks.py"
if mod_python.is_file():
    try:
        checked_files += 1
        with mod_python.open("rb") as stream:
            list(tokenize.tokenize(stream.readline))
    except Exception as exc:  # noqa: BLE001
        add_error(mod_python, f"Python tokenization error: {exc}")

as3_classes: dict[str, Path] = {}
as3_references: set[str] = set()
for path in iter_files("*.as"):
    try:
        text = read_text(path)
    except Exception as exc:  # noqa: BLE001
        add_error(path, f"cannot read UTF-8 source: {exc}")
        continue

    clean = strip_as3_comments_and_strings(text)
    if clean.count("{") != clean.count("}"):
        add_error(path, "unbalanced braces")

    package_match = re.search(r"\bpackage\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)", clean)
    class_match = re.search(r"\bpublic\s+class\s+([A-Za-z_]\w*)", clean)
    if not package_match:
        add_error(path, "package declaration is missing")
    if not class_match:
        add_error(path, "public class declaration is missing")
        continue

    class_name = class_match.group(1)
    if path.stem != class_name:
        add_error(path, f"filename must match public class {class_name}")
    previous = as3_classes.get(class_name)
    if previous is not None:
        add_error(path, f"duplicate class {class_name}; first defined in {relative(previous)}")
    as3_classes[class_name] = path

    if package_match:
        expected_dir = ROOT / "as3/src_flash/src" / package_match.group(1).replace(".", "/")
        if path.parent.resolve() != expected_dir.resolve():
            add_error(path, f"package path does not match {package_match.group(1)}")

    as3_references.update(
        re.findall(r"\b(?:new|extends|implements)\s+((?:Mastery|Marks)[A-Za-z0-9_]*)", clean)
    )

for class_name in sorted(as3_references):
    if class_name not in as3_classes:
        add_error("AS3", f"referenced local class is missing: {class_name}")

for target in sorted(project_targets):
    class_name = target.stem
    if class_name not in as3_classes:
        add_error("AS3 projects", f"compile target class is missing: {class_name}")

if mod_python.is_file():
    try:
        python_text = mod_python.read_text(encoding="utf-8-sig")
        linkage_values = re.findall(
            r"^_LINKAGE_[A-Z0-9_]+\s*=\s*['\"]([^'\"]+)['\"]",
            python_text,
            flags=re.MULTILINE,
        )
        swf_values = re.findall(
            r"^_SWF_[A-Z0-9_]+\s*=\s*['\"]([^'\"]+\.swf)['\"]",
            python_text,
            flags=re.MULTILINE,
        )
        for value in sorted(set(linkage_values)):
            if value not in as3_classes:
                add_error(mod_python, f"Scaleform linkage has no AS3 class: {value}")
        for value in sorted(set(swf_values)):
            built_file = ROOT / "as3/bin" / value
            if value not in project_outputs and not built_file.is_file():
                add_error(mod_python, f"SWF constant has no project/output: {value}")
    except Exception as exc:  # noqa: BLE001
        add_error(mod_python, f"cannot validate Scaleform constants: {exc}")

text_suffixes = {".as", ".as3proj", ".json", ".md", ".py", ".ps1", ".yml", ".yaml"}
for path in ROOT.rglob("*"):
    if is_ignored(path) or not path.is_file() or path.suffix.lower() not in text_suffixes:
        continue
    try:
        text = path.read_text(encoding="utf-8-sig", errors="ignore")
    except OSError:
        continue
    if "Masters" + "-Marks" in text:
        add_error(path, "obsolete combined-repository reference remains")

if errors:
    print("Repository validation failed:")
    for item in errors:
        print(f"[ERROR] {item}")
    sys.exit(1)

print(
    "Repository validation passed: "
    f"{checked_files} text files, {len(as3_classes)} AS3 classes, "
    f"{len(project_outputs)} SWF projects"
)
