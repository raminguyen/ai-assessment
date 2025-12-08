from setuptools import setup, find_packages

setup(
    name="essay-automation",

    version="1.0.0",
    
    author="Rami",
    description="Essay generation and grading automation using multiple AI models",
    packages=find_packages(),
    install_requires=[
        "anthropic==0.75.0",
        "docx==0.2.4",
        "openai==2.9.0",
        "protobuf==6.33.2",
        "python-dotenv==1.2.1",
        "python-docx==1.2.0",
        "strip-markdown==1.3",
        "xai-sdk==1.5.0",
    ],
    python_requires=">=3.11",
)