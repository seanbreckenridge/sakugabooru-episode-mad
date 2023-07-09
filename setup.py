from pathlib import Path
from setuptools import setup, find_packages

long_description = Path("README.md").read_text()
reqs = Path("requirements.txt").read_text().strip().splitlines()

pkg = "sakugabooru_episode_mad"
setup(
    name=pkg,
    version="0.1.0",
    url="https://github.com/seanbreckenridge/sakugabooru_episode_mad",
    author="Sean Breckenridge",
    author_email="seanbrecke@gmail.com",
    description=(
        """downloads all sakugabooru posts for a tag and combines them based on their source episode using ffmpeg"""
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    packages=find_packages(include=[pkg]),
    install_requires=reqs,
    package_data={pkg: ["py.typed"]},
    zip_safe=False,
    keywords="sakuga anime ffmpeg",
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "sakugabooru_episode_mad = sakugabooru_episode_mad.__main__:main"
        ]
    },
    extras_require={
        "testing": [
            "mypy",
            "flake8",
        ]
    },
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
