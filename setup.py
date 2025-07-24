"""
Setup script for Voice Assistant package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, "r", encoding="utf-8") as f:
        requirements = [
            line.strip() 
            for line in f 
            if line.strip() and not line.startswith("#")
        ]
        # Filter out development dependencies
        requirements = [
            req for req in requirements 
            if not any(dev_pkg in req for dev_pkg in ['pytest', 'mypy', 'black', 'flake8', 'isort', 'sphinx'])
        ]
else:
    requirements = [
        "SpeechRecognition>=3.10.0",
        "PyAudio>=0.2.11",
        "tinytuya>=1.12.0",
        "PyAutoGUI>=0.9.54",
        "psutil>=5.9.0",
    ]

setup(
    name="voice-assistant",
    version="1.0.0",
    author="AI Assistant",
    author_email="assistant@example.com",
    description="A voice-controlled personal assistant for Windows with Bahasa Indonesia support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/username/voice-assistant",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Desktop Environment",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "mypy>=1.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "isort>=5.10.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "voice-assistant=voice_assistant.main:main",
            "voice-assistant-config=voice_assistant.utils.config_tool:main",
        ],
    },
    include_package_data=True,
    package_data={
        "voice_assistant": [
            "config/*.json",
            "config/*.yaml",
        ],
    },
    zip_safe=False,
    keywords="voice assistant speech recognition bahasa indonesia automation",
    project_urls={
        "Bug Reports": "https://github.com/username/voice-assistant/issues",
        "Source": "https://github.com/username/voice-assistant",
        "Documentation": "https://voice-assistant.readthedocs.io/",
    },
)