from setuptools import setup, find_packages

setup(
    name="easy-mcp-core",
    version="1.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.115.11",
        "mcp==1.5.0",
        "python-dotenv==1.0.1",
        "ninja2==0.1",
        "uvicorn==0.34.0",
    ],
    description="Core package for Easy MCP Python",
    url="https://github.com/ground-creative/easy-mcp-core-python",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Adjust as necessary
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Adjust as necessary
)
