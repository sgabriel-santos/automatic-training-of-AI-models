from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="llm_image_classifier",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "jinja2",
        "tf_keras",
        "scikit-learn",
        "matplotlib",
        "chromadb",
        "sentence-transformers",
        "groq",
        "python-multipart"
    ],
    entry_points={
        'console_scripts': [
            'llm_image_classifier=main:app',  # Aponta para o FastAPI app no main.py
        ],
    },
    author="Gabriel Batista",
    author_email="gabrielpjl27@gmail.com",
    description="Ferramenta de suporte para treinamentoe análise de modelo de classificação de imagem com assistente virtual integrado",
    long_description=long_description,   # Usar o README.md para descrição longa
    long_description_content_type="text/markdown",  # Indicar que o README.md está em Markdown
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: FastAPI",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    include_package_data=True
)
