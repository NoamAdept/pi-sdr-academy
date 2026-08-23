"""Academy package setup."""

from setuptools import find_packages, setup

setup(
    name="pi-sdr-academy",
    version="0.1.0",
    description="Offline Raspberry Pi SDR / Systems / Cybersecurity Academy",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "PyYAML>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "academy=academy.cli:main",
            "next=academy.cli:main_next",
            "hint=academy.cli:main_hint",
            "submit=academy.cli:main_submit",
            "status=academy.cli:main_status",
            "list-challenges=academy.cli:main_list",
            "dojos=academy.cli:main_list",
        ],
    },
)
