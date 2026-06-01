#!/usr/bin/env python3
# build.py - Générateur statique pour Projects/ -> dist/

import re
import os
import shutil
import html
import argparse
from pathlib import Path

# --- Config ---
ROOT = Path(__file__).parent.resolve()
PROJECTS_DIR = ROOT / "Projects"
DIST_DIR = ROOT / "dist"
CSS_SRC = ROOT / "homepage_style.css"
BASE_URL = "/"  # reste "/" pour hébergement statique racine

# --- Helpers ---
def slugify(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    return s.strip("-")

def read_description(project_folder: Path) -> str:
    desc_file = project_folder / "description.txt"
    if desc_file.exists():
        try:
            return desc_file.read_text(encoding="utf-8").strip()
        except Exception:
            return desc_file.read_text(errors="ignore").strip()
    return "Pas de description."

# --- Templates ---
INDEX_TEMPLATE = """<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Nadia Crisetig - Projets</title>
  <link rel="stylesheet" href="{css_path}">
</head>
<body>
  <div class="container">
    <header>
      <h1>Nadia Crisetig</h1>
      <div class="subtitle">Étudiante ✨</div>
    </header>
    <section>
      <h2>Projets</h2>
      <div id="projects-list">
        {cards}
      </div>
    </section>
  </div>
</body>
</html>
"""

CARD_TEMPLATE = """<div class="card">
  <a href="{project_url}"><strong>{titre}</strong></a>
  <p>{description}</p>
</div>"""




def build(dist: Path = DIST_DIR):
    if not PROJECTS_DIR.exists():
        print(f"Erreur: dossier {PROJECTS_DIR} introuvable.")
        return



    cards_html = []
    projects_dist_root = "projects"

    for folder in sorted(PROJECTS_DIR.iterdir(), key=lambda p: p.name.lower()):
        if not folder.is_dir():
            continue
        titre = folder.name
        slug = slugify(titre) or "project"
        project_dist = projects_dist_root / slug
        project_dist.mkdir(parents=True, exist_ok=True)


        description = html.escape(read_description(folder)).replace("\n", "<br>")
        project_url = f"./projects/{slug}/index.html"
        cards_html.append(CARD_TEMPLATE.format(project_url=project_url, titre=html.escape(titre), description=description))

        # extras_html: lister fichiers copiés pour la page du projet
        extras = []
        for f in sorted(project_dist.iterdir()):
            if f.name == "index.html":
                continue
            extras.append(f'<li><a href="{f.name}">{html.escape(f.name)}</a></li>')
        extras_html = ""
        if extras:
            extras_html = "<h3>Fichiers</h3><ul>" + "\n".join(extras) + "</ul>"

        # css path relative depuis project page
        css_rel = os.path.relpath(str(css_dest), start=str(project_dist)).replace(os.sep, "/")

        project_page = PROJECT_PAGE_TEMPLATE.format(
            titre=html.escape(titre),
            description=description,
            extras_html=extras_html,
            css_path=css_rel,
            base_url=BASE_URL
        )
        (project_dist / "index.html").write_text(project_page, encoding="utf-8")
        print(f"Generated project page: {project_dist / 'index.html'}")

    # écrire index.html
    index_html = INDEX_TEMPLATE.format(cards="\n".join(cards_html), css_path=f"./{css_dest.name}")
    (dist / "index.html").write_text(index_html, encoding="utf-8")
    print(f"Site généré dans {dist.resolve()}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Génère un site statique à partir du dossier Projects/")
    parser.add_argument("--out", "-o", help="Dossier de sortie (default: dist)", default=str(DIST_DIR))
    args = parser.parse_args()
    DIST_DIR = Path(args.out)
    build(DIST_DIR)
