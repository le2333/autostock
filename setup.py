from setuptools import setup, find_packages

setup(
    name="autostock",
    version="0.1.0",
    packages=find_packages(),
    description="An automatic stock analysis tool.",
    author="Your Name",  # 请替换成您的名字
    author_email="your.email@example.com",  # 请替换成您的邮箱
    install_requires=[
        "alembic",
        "akshare",
        "duckdb",
        "duckdb-engine",
        "pandas",
        "sqlmodel",
        "tqdm",
        "pyarrow",
    ],
    entry_points={
        "console_scripts": [
            "autostock_app=autostock.app:main",
            "autostock_worker=autostock.main:main",
        ],
    },
    python_requires=">=3.9",
)
