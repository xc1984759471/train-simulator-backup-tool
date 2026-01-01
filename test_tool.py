#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Train Simulator Classic 存档备份管理工具 - 测试脚本
用于测试工具的核心功能
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from train_simulator_backup_tool import ConfigManager, XMLParser, TrainSimulatorBackupTool

def test_config_manager():
    """测试配置管理器"""
    print("测试配置管理器...")
    
    # 使用临时文件测试
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config_file = f.name
    
    try:
        config_manager = ConfigManager(config_file)
        
        # 测试设置和获取路径
        test_path = "D:/test/railworks"
        config_manager.set_railworks_path(test_path)
        retrieved_path = config_manager.get_railworks_path()
        
        assert retrieved_path == test_path, f"路径设置/获取失败: {retrieved_path} != {test_path}"
        
        # 测试语言设置
        config_manager.set_language("en")
        assert config_manager.get_language() == "en", "语言设置失败"
        
        print("✓ 配置管理器测试通过")
        
    finally:
        # 清理临时文件
        if os.path.exists(config_file):
            os.unlink(config_file)

def test_xml_parser():
    """测试XML解析器"""
    print("测试XML解析器...")
    
    # 创建测试XML文件
    test_xml_content = '''<?xml version="1.0" encoding="utf-8"?>
<RouteProperties>
    <DisplayName>
        <Localisation-cUserLocalisedString>
            <English></English>
            <Other>
                <Localisation-cUserLocalisedString-cOtherStringLangPair>
                    <Language>zh</Language>
                    <String>测试路线</String>
                </Localisation-cUserLocalisedString-cOtherStringLangPair>
            </Other>
            <Key>test-key-123</Key>
        </Localisation-cUserLocalisedString>
    </DisplayName>
</RouteProperties>'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False, encoding='utf-8') as f:
        f.write(test_xml_content)
        xml_file = f.name
    
    try:
        parser = XMLParser()
        
        # 测试中文解析
        result_zh = parser.parse_display_name(xml_file, "zh")
        assert result_zh == "测试路线", f"中文解析失败: {result_zh}"
        
        # 测试英文解析（应该找到英文内容，因为没有中文匹配）
        # 注意：如果XML中Other节点有zh配置，查找"en"应该回退到English节点
        result_en = parser.parse_display_name(xml_file, "en")  
        # 如果当前中文设置是zh，应该优先返回中文内容，而不是英文
        if result_en == "":
            # 如果没有找到匹配的回退到默认（可能是英文或其他）
            result_en = parser.parse_display_name(xml_file, "")  # 测试默认解析
        print(f"英文解析结果: '{result_en}'")  # 调试输出
        
        print("✓ XML解析器测试通过")
        
    finally:
        # 清理临时文件
        if os.path.exists(xml_file):
            os.unlink(xml_file)

def test_file_operations():
    """测试文件操作功能"""
    print("测试文件操作功能...")
    
    # 创建临时目录结构
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建模拟场景目录
        scenario_dir = Path(temp_dir) / "scenario_test"
        scenario_dir.mkdir()
        
        # 创建模拟CurrentSave.bin文件
        save_file = scenario_dir / "CurrentSave.bin"
        save_file.write_text("模拟存档数据")
        
        # 创建工具实例
        tool = TrainSimulatorBackupTool()
        
        # 测试备份创建
        success = tool.create_backup(str(scenario_dir))
        assert success, "备份创建失败"
        
        # 检查备份文件是否存在
        backup_dir = scenario_dir / "saves"
        assert backup_dir.exists(), "备份目录未创建"
        
        backup_files = list(backup_dir.glob("CurrentSave-*.bin"))
        assert len(backup_files) > 0, "未找到备份文件"
        
        # 测试备份列表
        backups = tool.list_backups(str(scenario_dir))
        assert len(backups) > 0, "备份列表为空"
        
        # 测试备份删除
        backup_filename = backup_files[0].name
        success = tool.delete_backup(str(scenario_dir), backup_filename)
        assert success, "备份删除失败"
        
        # 验证备份已删除
        assert not backup_files[0].exists(), "备份文件未被删除"
        
        print("✓ 文件操作功能测试通过")

def test_main_tool():
    """测试主工具类"""
    print("测试主工具类...")
    
    tool = TrainSimulatorBackupTool()
    
    # 测试路径检测（即使没有实际RailWorks安装）
    assert hasattr(tool, 'railworks_path'), "工具缺少railworks_path属性"
    assert hasattr(tool, 'config_manager'), "工具缺少config_manager属性"
    assert hasattr(tool, 'xml_parser'), "工具缺少xml_parser属性"
    
    # 测试核心方法存在
    assert hasattr(tool, 'scan_content'), "缺少scan_content方法"
    assert hasattr(tool, 'create_backup'), "缺少create_backup方法"
    assert hasattr(tool, 'restore_backup'), "缺少restore_backup方法"
    assert hasattr(tool, 'delete_backup'), "缺少delete_backup方法"
    assert hasattr(tool, 'list_backups'), "缺少list_backups方法"
    
    print("✓ 主工具类测试通过")

def run_all_tests():
    """运行所有测试"""
    print("Train Simulator Classic 存档备份管理工具 - 测试套件")
    print("=" * 50)
    
    tests = [
        test_config_manager,
        test_xml_parser,
        test_file_operations,
        test_main_tool
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__} 失败: {e}")
            failed += 1
    
    print("=" * 50)
    print(f"测试完成: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("🎉 所有测试通过！工具功能正常。")
        return True
    else:
        print("❌ 部分测试失败，请检查代码。")
        return False

def main():
    """主函数"""
    if run_all_tests():
        print("\n工具已准备就绪！")
        print("运行命令: python train_simulator_backup_tool.py")
    else:
        print("\n测试失败，工具可能无法正常工作。")
        sys.exit(1)

if __name__ == "__main__":
    main()