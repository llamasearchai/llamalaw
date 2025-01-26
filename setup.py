from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="llamalaw-llamasearch",
    version="0.1.0",
    author="LlamaSearch AI",
    author_email="nikjois@llamasearch.ai",
    description="Legal contract analysis and management for LlamaSearch.ai",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://llamasearch.ai",
    project_urls={
        "Bug Tracker": "https://github.com/llamasearch/llamalaw/issues",
        "Documentation": "https://docs.llamasearch.ai/llamalaw",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Office/Business :: Financial :: Accounting",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.9",
    install_requires=[
        "pydantic>=1.8.0",
        "fastapi>=0.70.0",
        "uvicorn>=0.15.0",
        "python-multipart>=0.0.5",
        "sqlalchemy>=1.4.0",
        "pdf2image>=1.16.0",
        "pytesseract>=0.3.8",
        "spacy>=3.2.0",
        "transformers>=4.16.0",
        "torch>=1.10.0",
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "jinja2>=3.0.0",
        "python-docx>=0.8.11",
        "requests>=2.26.0",
        "tqdm>=4.62.0",
        "click>=8.0.0",
        "rich>=10.12.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "black>=21.5b2",
            "isort>=5.9.0",
            "mypy>=0.800",
            "flake8>=3.9.0",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "sphinx-copybutton>=0.4.0",
        ],
        "pdf": [
            "pdfplumber>=0.6.0",
            "PyPDF2>=1.26.0",
            "fitz>=0.0.1",
            "pymupdf>=1.19.0",
        ],
        "ocr": [
            "pytesseract>=0.3.8",
            "pillow>=8.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "llamalaw=llamalaw.cli:main",
        ],
    },
) 
# Updated in commit 5 - 2025-04-04 17:33:46

# Updated in commit 13 - 2025-04-04 17:33:47

# Updated in commit 21 - 2025-04-04 17:33:48

# Updated in commit 29 - 2025-04-04 17:33:48

# Updated in commit 5 - 2025-04-05 14:36:32

# Updated in commit 13 - 2025-04-05 14:36:32

# Updated in commit 21 - 2025-04-05 14:36:33

# Updated in commit 29 - 2025-04-05 14:36:33

# Updated in commit 5 - 2025-04-05 15:23:02

# Updated in commit 13 - 2025-04-05 15:23:02

# Updated in commit 21 - 2025-04-05 15:23:02

# Updated in commit 29 - 2025-04-05 15:23:02

# Updated in commit 5 - 2025-04-05 15:57:20

# Updated in commit 13 - 2025-04-05 15:57:21

# Updated in commit 21 - 2025-04-05 15:57:21

# Updated in commit 29 - 2025-04-05 15:57:21

# Updated in commit 5 - 2025-04-05 17:02:47

# Updated in commit 13 - 2025-04-05 17:02:47

# Updated in commit 21 - 2025-04-05 17:02:47

# Updated in commit 29 - 2025-04-05 17:02:47

# Updated in commit 5 - 2025-04-05 17:34:49

# Updated in commit 13 - 2025-04-05 17:34:49

# Updated in commit 21 - 2025-04-05 17:34:49

# Updated in commit 29 - 2025-04-05 17:34:49

# Updated in commit 5 - 2025-04-05 18:21:35

# Updated in commit 13 - 2025-04-05 18:21:35
