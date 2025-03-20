from setuptools import setup, find_packages

setup(
    name="nebulaml",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.1",
        "pydantic>=2.5.2",
        "sqlalchemy>=2.0.23",
        "asyncpg>=0.29.0",
        "prometheus-client>=0.19.0",
        "docker>=6.1.3",
        "python-multipart>=0.0.6",
        "aiohttp>=3.9.1",
        "hvac>=1.2.0",
        "httpx>=0.25.2",
        "uvicorn>=0.24.0"
    ],
    python_requires=">=3.8",
) 