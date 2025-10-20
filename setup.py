from setuptools import setup, find_packages

setup(
    name="llm-memory-management",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "pymongo==4.6.0",
        "motor==3.3.2",
        "httpx==0.25.2",
        "numpy==1.24.3",
        "pydantic==2.5.0",
        "python-dotenv==1.0.0",
        "python-multipart==0.0.6",
    ],
)