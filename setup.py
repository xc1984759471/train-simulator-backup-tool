#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Train Simulator Classic 存档备份管理工具安装脚本
"""

from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

# 读取requirements.txt
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    requirements = []
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    requirements.append(line)
    return requirements

setup(
    name="train-simulator-backup-tool",
    version="1.0.0",
    author="MiniMax Agent",
    author_email="agent@minimax.chat",
    description="Train Simulator Classic存档备份管理工具",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/minimax/train-simulator-backup-tool",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Topic :: Games/Entertainment :: Simulation",
        "Topic :: Utilities",
    ],
    python_requires=">=3.10",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "train-simulator-backup=train_simulator_backup_tool:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.xml", "*.txt"],
    },
    zip_safe=False,
)