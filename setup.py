from pathlib import Path
import re

from setuptools import setup  # type: ignore  # no typehints

root = Path(__file__).parent

requirements = (root / "requirements.txt").read_text("utf-8").strip().splitlines()

text = (root / "gd" / "bot" / "__init__.py").read_text("utf-8")

result = re.search(r"^__version__\s*=\s*[\"']([^\"']*)[\"']", text, re.MULTILINE)

if result is None:
    raise RuntimeError("Failed to find version.")

version = result.group(1)

readme = (root / "README.rst").read_text("utf-8")


setup(
    name="gd.bot",
    author="nekitdev",
    author_email="nekitdevofficial@gmail.com",
    url="https://github.com/nekitdev/gd.bot",
    project_urls={"Issue tracker": "https://github.com/nekitdev/gd.bot/issues"},
    version=version,
    packages=["gd", "gd.bot", "gd.bot.cogs"],
    license="MIT",
    description="Discord Bot which can interact with Geometry Dash servers, and much more!",
    long_description=readme,
    long_description_content_type="text/x-rst",
    include_package_data=True,
    install_requires=requirements,
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Natural Language :: English",
        "Operating System :: OS Independent",
    ],
    entry_points={"console_scripts": ["gd.bot = gd.bot.__main__:main"]},
)
