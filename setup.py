"""
Définit les métadonnées du package GameOfLife et permet son installation.
"""
import setuptools

with open("README.md", "r", encoding="utf-8") as f:
    description_longue = f.read()

__version__ = "0.0.1"

REPO_NAME = "game-of-life"
AUTHOR_USER_NAME = "eloidieme"
SRC_REPO = "GameOfLife"
AUTHOR_EMAIL = "eloi.dieme@student-cs.fr"

setuptools.setup(
    name=SRC_REPO,
    version=__version__,
    author=AUTHOR_USER_NAME,
    author_email=AUTHOR_EMAIL,
    description="Une implémentation du jeu de la vie en Python.",
    long_description=description_longue,
    long_description_content_type="text/markdown",
    url=f"https://github.com/{AUTHOR_USER_NAME}/{REPO_NAME}",
    project_urls={
        "Bug Tracker": f"https://github.com/{AUTHOR_USER_NAME}/{REPO_NAME}/issues",
    },
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src")
)