#!/usr/bin/env python3
"""Render project cards in README.md from .profile/projects.json."""

import html
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

START = "<!-- PROJECTS:START -->"
END = "<!-- PROJECTS:END -->"
OWNER = "Kartik-IN"


def esc(value):
    return html.escape(str(value), quote=True)


def repo_name(project):
    return urlparse(project.get("url", "")).path.strip("/").split("/")[-1] or project["repo"]


def render_card(project, width):
    repo = repo_name(project)
    url = project.get("url", f"https://github.com/{OWNER}/{repo}")
    lines = [
        f'<td width="{width}%" valign="top">',
        "",
        f'### [{esc(project["icon"])} {esc(project["name"])}]({esc(url)})',
        f'`{esc(project["stack"])}`',
        "",
        esc(project["summary"]),
        "",
    ]
    lines.extend(f'- {esc(item)}' for item in project["bullets"])
    lines.extend([
        "",
        f'<a href="{esc(url)}"><img src="https://img.shields.io/github/last-commit/{OWNER}/{repo}?style=flat-square&label=updated" alt="{esc(project["name"])} last commit"/></a>',
    ])
    workflow = project.get("workflow")
    if workflow:
        workflow_url = f"{url}/actions/workflows/{workflow}"
        lines.append(f'<a href="{esc(workflow_url)}"><img src="https://img.shields.io/github/actions/workflow/status/{OWNER}/{repo}/{workflow}?branch=main&style=flat-square&label={esc(project.get("workflow_label", "CI"))}" alt="{esc(project["name"])} workflow status"/></a>')
    lines.extend(["", "</td>"])
    return "\n".join(lines)


def render(projects):
    width = 100 // len(projects)
    cards = [render_card(project, width) for project in projects]
    return "<table width=\"100%\">\n<tr>\n" + "\n".join(cards) + "\n</tr>\n</table>"


def main():
    root = Path(__file__).resolve().parents[1]
    readme = root / "README.md"
    registry = root / ".profile" / "projects.json"
    projects = json.loads(registry.read_text(encoding="utf-8"))
    content = readme.read_text(encoding="utf-8")
    if content.count(START) != 1 or content.count(END) != 1:
        raise SystemExit("README project markers must each occur exactly once")
    before, remainder = content.split(START, 1)
    _, after = remainder.split(END, 1)
    updated = before + START + "\n" + render(projects) + "\n" + END + after
    readme.write_text(updated, encoding="utf-8")
    print(f"Updated {readme} with {len(projects)} projects")


if __name__ == "__main__":
    try:
        main()
    except (OSError, KeyError, json.JSONDecodeError) as error:
        print(f"profile update failed: {error}", file=sys.stderr)
        raise SystemExit(1)
