#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Train Simulator Classic 存档备份管理工具 PyInstaller 打包脚本
用法: python build_exe.py
"""

import os
import sys
import subprocess
from pathlib import Path

def build_executable():
    """使用PyInstaller构建可执行文件"""
    
    # PyInstaller参数
    cmd = [
        'pyinstaller',
        '--onefile',                    # 打包成单个文件
        '--windowed',                   # Windows下不显示控制台窗口
        '--name=TrainSimulatorBackup',  # 可执行文件名称
        '--icon=none.ico',             # 图标文件（可选）
        '--add-data=requirements.txt;requirements.txt',  # 添加数据文件
        '--hidden-import=PyQt5.QtCore',  # 确保PyQt5模块被包含
        '--hidden-import=PyQt5.QtWidgets',
        '--hidden-import=PyQt5.QtGui',
        '--hidden-import=xml.etree.ElementTree',  # 确保标准库被包含
        '--hidden-import=xml.etree', 
        '--distpath=dist',             # 输出目录
        '--workpath=build',            # 工作目录
        '--specpath=.',                # spec文件位置
        'train_simulator_backup_tool.py'  # 主程序文件
    ]
    
    print("开始构建可执行文件...")
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        # 执行PyInstaller命令
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("构建成功！")
        print(result.stdout)
        
        # 检查输出文件
        exe_path = Path("dist/TrainSimulatorBackup.exe")
        if exe_path.exists():
            file_size = exe_path.stat().st_size / (1024 * 1024)  # MB
            print(f"可执行文件大小: {file_size:.1f} MB")
            print(f"文件位置: {exe_path.absolute()}")
        else:
            print("警告: 未找到生成的可执行文件")
            
    except subprocess.CalledProcessError as e:
        print("构建失败！")
        print(f"错误信息: {e.stderr}")
        return False
    except FileNotFoundError:
        print("错误: 未找到pyinstaller命令。请先安装pyinstaller:")
        print("pip install pyinstaller")
        return False
    
    return True

def clean_build_files():
    """清理构建文件"""
    import shutil
    
    dirs_to_clean = ['build', '__pycache__']
    files_to_clean = ['*.spec']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"删除目录: {dir_name}")
            shutil.rmtree(dir_name)
    
    for pattern in files_to_clean:
        import glob
        for file_path in glob.glob(pattern):
            print(f"删除文件: {file_path}")
            os.remove(file_path)

def main():
    """主函数"""
    print("Train Simulator Classic 存档备份管理工具 - 打包脚本")
    print("=" * 50)
    
    # 检查主程序文件是否存在
    main_file = "train_simulator_backup_tool.py"
    if not os.path.exists(main_file):
        print(f"错误: 未找到主程序文件 {main_file}")
        return
    
    # 清理之前的构建文件
    print("清理之前的构建文件...")
    clean_build_files()
    
    # 构建可执行文件
    if build_executable():
        print("\n构建完成！")
        print("可执行文件已生成在 dist/ 目录中")
    else:
        print("\n构建失败！")
        print("请检查错误信息并重试")

if __name__ == "__main__":
    main()