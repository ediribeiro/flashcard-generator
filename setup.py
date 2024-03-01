from setuptools import find_packages,setup

setup(
    name='flashcard-generator',
    version='0.0.1',
    author='eduardo ribeiro',
    author_email='edu.alri@gmail.com',
    install_requires=["openai","langchain","streamlit","python-dotenv","PyPDF2","datetime","pathlib","google-generativeai"],
    packages=find_packages()
)