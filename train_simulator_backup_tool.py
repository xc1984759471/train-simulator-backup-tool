#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import xml.etree.ElementTree as ET

# 尝试导入PyQt5，如果没有则尝试PyQt6，最后尝试GTK
try:
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                QHBoxLayout, QTreeWidget, QTreeWidgetItem, QLabel,
                                QPushButton, QListWidget, QListWidgetItem, QMessageBox,
                                QFileDialog, QLineEdit, QFormLayout, QDialog, QDialogButtonBox,
                                QGroupBox, QTextEdit, QSplitter)
    from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
    from PyQt5.QtGui import QIcon, QFont
    PYQT_VERSION = 5
except ImportError:
    try:
        from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                    QHBoxLayout, QTreeWidget, QTreeWidgetItem, QLabel,
                                    QPushButton, QListWidget, QListWidgetItem, QMessageBox,
                                    QFileDialog, QLineEdit, QFormLayout, QDialog, QDialogButtonBox,
                                    QGroupBox, QTextEdit, QSplitter)
        from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
        from PyQt6.QtGui import QIcon, QFont
        PYQT_VERSION = 6
    except ImportError:
        try:
            import gi
            gi.require_version('Gtk', '3.0')
            from gi.repository import Gtk, GLib, Pango
            PYGTK_AVAILABLE = True
            PYQT_VERSION = 0
        except ImportError:
            print("错误: 未找到PyQt5、PyQt6或GTK库。请安装其中一个库。")
            print("安装命令:")
            print("pip install PyQt5")
            print("或")
            print("pip install PyQt6")
            print("或")
            print("pip install PyGObject")
            sys.exit(1)


class ConfigManager:
    """配置文件管理器"""
    
    def __init__(self, config_file: str = "train_simulator_backup_config.json"):
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """加载配置文件"""
        default_config = {
            "railworks_path": "",
            "language": "zh",
            "window_geometry": {"width": 1200, "height": 800},
            "last_scan_time": ""
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # 合并默认配置
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            except Exception as e:
                print(f"加载配置文件失败: {e}")
                return default_config
        else:
            return default_config
    
    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def get_railworks_path(self) -> str:
        """获取RailWorks路径"""
        return self.config.get("railworks_path", "")
    
    def set_railworks_path(self, path: str):
        """设置RailWorks路径"""
        self.config["railworks_path"] = path
        self.save_config()
    
    def get_language(self) -> str:
        """获取语言设置"""
        return self.config.get("language", "zh")
    
    def set_language(self, language: str):
        """设置语言"""
        self.config["language"] = language
        self.save_config()


class XMLParser:
    """XML解析器，用于解析RouteProperties.xml和ScenarioProperties.xml"""
    
    @staticmethod
    def _is_chinese_language(lang_code: str) -> bool:
        """判断是否为中文语言代码"""
        if not lang_code:
            return False
        # 匹配所有中文变体：zh, zh-cn, zh-tw, zh-hk, zh-sg等
        return lang_code.lower().startswith('zh') or lang_code.lower() in ['chinese', 'zhongwen']
    
    @staticmethod
    def _matches_language(lang_code: str, target_language: str) -> bool:
        """判断语言代码是否匹配目标语言"""
        if not lang_code or not target_language:
            return False
        
        # 如果目标语言是中文，匹配所有中文变体
        if target_language.lower() == 'zh':
            return XMLParser._is_chinese_language(lang_code)
        
        # 其他语言精确匹配
        return lang_code.lower() == target_language.lower()

    @staticmethod
    def parse_display_name(xml_file_path: str, language: str = "zh") -> str:
        """解析DisplayName标签，获取显示名称"""
        try:
            if not os.path.exists(xml_file_path):
                return ""
            
            # 读取XML文件内容
            with open(xml_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析XML
            root = ET.fromstring(content)
            
            # 简化查找：直接使用简单的xpath查找
            # 不使用命名空间前缀，而是直接匹配标签名
            
            # 查找DisplayName节点
            display_name_node = root.find('.//DisplayName')
            if display_name_node is None:
                print(f"在 {xml_file_path} 中未找到DisplayName节点")
                return ""
            
            # 查找Localisation节点
            localisation_node = display_name_node.find('.//Localisation-cUserLocalisedString')
            if localisation_node is None:
                print(f"在 {xml_file_path} 中未找到Localisation-cUserLocalisedString节点")
                return ""
            
            # 首先尝试Other语言 - 支持所有中文变体
            other_node = localisation_node.find('.//Other')
            if other_node is not None:
                # 查找语言对
                for string_pair in other_node.findall('.//Localisation-cUserLocalisedString-cOtherStringLangPair'):
                    lang_node = string_pair.find('.//Language')
                    string_node = string_pair.find('.//String')
                    
                    if (lang_node is not None and string_node is not None and
                        string_node.text and XMLParser._matches_language(lang_node.text, language)):
                        return string_node.text
            
            # 如果Other中没有找到，尝试其他语言
            languages = ['English', 'French', 'German', 'Spanish', 'Italian', 'Russian', 'Dutch', 'Polish']
            for lang in languages:
                lang_node = localisation_node.find(f'.//{lang}')
                if (lang_node is not None and lang_node.text and 
                    lang_node.get('d:type') == 'cDeltaString'):
                    return lang_node.text
            
            # 尝试不带d:type检查的回退
            for lang in languages:
                lang_node = localisation_node.find(f'.//{lang}')
                if (lang_node is not None and lang_node.text):
                    return lang_node.text
            
            return ""
            
        except ET.ParseError as e:
            print(f"XML解析错误 {xml_file_path}: {e}")
            return ""
        except Exception as e:
            print(f"解析XML文件失败 {xml_file_path}: {e}")
            return ""


class TrainSimulatorBackupTool:
    """Train Simulator Classic存档备份工具主类"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.xml_parser = XMLParser()
        self.routes_data = {}  # 存储路线和场景数据
        self.backup_dir_name = "saves"
        
        # 尝试自动检测RailWorks路径
        self.railworks_path = self._auto_detect_railworks_path()
        if self.railworks_path:
            self.config_manager.set_railworks_path(self.railworks_path)
    
    def _auto_detect_railworks_path(self) -> str:
        """自动检测RailWorks安装路径"""
        # 默认Steam安装路径
        default_paths = [
            "D:/Program Files (x86)/Steam/steamapps/common/RailWorks",
            "C:/Program Files (x86)/Steam/steamapps/common/RailWorks",
            "E:/Program Files (x86)/Steam/steamapps/common/RailWorks",
            "D:/Program Files/Steam/steamapps/common/RailWorks",
            "C:/Program Files/Steam/steamapps/common/RailWorks"
        ]
        
        # 实际存在的RailWorks可执行文件
        possible_exes = [
            "Railworks.exe",           # 32位版本
            "Railworks64.exe",         # 64位版本  
            "RailworksDX12_64.exe"     # 64位DX12版本
        ]
        
        for path in default_paths:
            for exe_name in possible_exes:
                exe_path = os.path.join(path, exe_name)
                if os.path.exists(exe_path):
                    return path
        
        # 尝试从注册表读取（Windows）
        try:
            import winreg
            # 尝试从Steam注册表读取安装路径
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                  r"SOFTWARE\\WOW6432Node\\Valve\\Steam") as key:
                    steam_path = winreg.QueryValueEx(key, "InstallPath")[0]
                    railworks_path = os.path.join(steam_path, "steamapps\\common\\RailWorks")
                    if os.path.exists(railworks_path):
                        return railworks_path
            except:
                pass
        except:
            pass
        
        return ""
    
    def scan_content(self) -> bool:
        """扫描RailWorks内容目录"""
        if not self.railworks_path:
            return False
        
        content_path = os.path.join(self.railworks_path, "Content")
        if not os.path.exists(content_path):
            return False
        
        routes_path = os.path.join(content_path, "Routes")
        if not os.path.exists(routes_path):
            return False
        
        self.routes_data = {}
        language = self.config_manager.get_language()
        
        try:
            for route_uuid in os.listdir(routes_path):
                route_path = os.path.join(routes_path, route_uuid)
                if not os.path.isdir(route_path):  # 修正：使用完整路径而不是文件夹名
                    continue
                
                # 解析路线名称
                route_properties_path = os.path.join(route_path, "RouteProperties.xml")
                route_name = self.xml_parser.parse_display_name(route_properties_path, language)
                if not route_name:
                    route_name = route_uuid  # 如果解析失败，使用UUID作为名称
                
                # 扫描场景
                scenarios_path = os.path.join(route_path, "Scenarios")
                scenarios = []
                
                if os.path.exists(scenarios_path):
                    for scenario_uuid in os.listdir(scenarios_path):
                        scenario_path = os.path.join(scenarios_path, scenario_uuid)
                        if not os.path.isdir(scenario_path):
                            continue
                        
                        # 解析场景名称
                        scenario_properties_path = os.path.join(scenario_path, "ScenarioProperties.xml")
                        scenario_name = self.xml_parser.parse_display_name(scenario_properties_path, language)
                        if not scenario_name:
                            scenario_name = scenario_uuid  # 如果解析失败，使用UUID作为名称
                        
                        scenarios.append({
                            'uuid': scenario_uuid,
                            'name': scenario_name,
                            'path': scenario_path,
                            'save_path': os.path.join(scenario_path, self.backup_dir_name)
                        })
                
                if scenarios:  # 只添加有场景的路线
                    self.routes_data[route_uuid] = {
                        'name': route_name,
                        'path': route_path,
                        'scenarios': scenarios
                    }
            
            return True
            
        except Exception as e:
            print(f"扫描内容失败: {e}")
            return False
    
    def create_backup(self, scenario_path: str) -> bool:
        """创建存档备份"""
        try:
            save_file = os.path.join(scenario_path, "CurrentSave.bin")
            if not os.path.exists(save_file):
                return False
            
            backup_dir = os.path.join(scenario_path, self.backup_dir_name)
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            # 生成备份文件名
            timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            backup_file = f"CurrentSave-{timestamp}.bin"
            backup_path = os.path.join(backup_dir, backup_file)
            
            # 复制存档文件
            shutil.copy2(save_file, backup_path)
            
            # 复制MD5校验文件（如果存在）
            md5_file = os.path.join(scenario_path, "CurrentSave.bin.MD5")
            if os.path.exists(md5_file):
                backup_md5_path = os.path.join(backup_dir, f"CurrentSave-{timestamp}.bin.MD5")
                shutil.copy2(md5_file, backup_md5_path)
            
            return True
            
        except Exception as e:
            print(f"创建备份失败: {e}")
            return False
    
    def restore_backup(self, scenario_path: str, backup_filename: str) -> bool:
        """还原存档备份"""
        try:
            backup_path = os.path.join(scenario_path, self.backup_dir_name, backup_filename)
            if not os.path.exists(backup_path):
                return False
            
            save_file = os.path.join(scenario_path, "CurrentSave.bin")
            
            # 复制备份文件覆盖原存档
            shutil.copy2(backup_path, save_file)
            
            # 还原MD5校验文件（如果存在）
            md5_filename = backup_filename + ".MD5"
            backup_md5_path = os.path.join(scenario_path, self.backup_dir_name, md5_filename)
            if os.path.exists(backup_md5_path):
                original_md5_file = os.path.join(scenario_path, "CurrentSave.bin.MD5")
                shutil.copy2(backup_md5_path, original_md5_file)
            
            return True
            
        except Exception as e:
            print(f"还原备份失败: {e}")
            return False
    
    def delete_backup(self, scenario_path: str, backup_filename: str) -> bool:
        """删除备份"""
        try:
            backup_path = os.path.join(scenario_path, self.backup_dir_name, backup_filename)
            deleted = False
            
            # 删除存档文件
            if os.path.exists(backup_path):
                os.remove(backup_path)
                deleted = True
            
            # 删除对应的MD5校验文件
            md5_filename = backup_filename + ".MD5"
            backup_md5_path = os.path.join(scenario_path, self.backup_dir_name, md5_filename)
            if os.path.exists(backup_md5_path):
                os.remove(backup_md5_path)
                deleted = True
            
            return deleted
            
        except Exception as e:
            print(f"删除备份失败: {e}")
            return False
    
    def list_backups(self, scenario_path: str) -> List[str]:
        """列出所有备份文件"""
        backup_dir = os.path.join(scenario_path, self.backup_dir_name)
        if not os.path.exists(backup_dir):
            return []
        
        backups = []
        backup_sets = set()  # 用于跟踪已处理的备份集
        try:
            for filename in os.listdir(backup_dir):
                if filename.startswith("CurrentSave-") and filename.endswith(".bin"):
                    # 提取备份集标识（移除.bin后缀）
                    backup_id = filename[:-4]  # 移除.bin
                    if backup_id not in backup_sets:
                        backup_sets.add(backup_id)
                        backups.append(backup_id)
            backups.sort(reverse=True)  # 最新的在前面
        except Exception as e:
            print(f"列出备份失败: {e}")
        
        return backups


# PyQt5/6 GUI实现
if PYQT_VERSION in [5, 6]:
    class MainWindow(QMainWindow):
        """主窗口"""
        
        def __init__(self):
            super().__init__()
            self.tool = TrainSimulatorBackupTool()
            self.init_ui()
            self.setup_connections()
            
        def init_ui(self):
            """初始化用户界面"""
            self.setWindowTitle("Train Simulator Classic 存档备份管理工具")
            self.setGeometry(100, 100, 1200, 800)
            
            # 创建中央部件
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # 主布局
            main_layout = QHBoxLayout(central_widget)
            
            # 创建分割器
            splitter = QSplitter(Qt.Horizontal)
            main_layout.addWidget(splitter)
            
            # 左侧：路线和场景树
            left_widget = QWidget()
            left_layout = QVBoxLayout(left_widget)
            
            # 搜索框
            search_layout = QHBoxLayout()
            search_label = QLabel("搜索:")
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("输入路线或场景名称...")
            search_layout.addWidget(search_label)
            search_layout.addWidget(self.search_input)
            left_layout.addLayout(search_layout)
            
            # 路线标题
            route_label = QLabel("路线和场景:")
            left_layout.addWidget(route_label)
            
            # 路线树
            self.route_tree = QTreeWidget()
            self.route_tree.setHeaderLabels(["路线/场景"])
            left_layout.addWidget(self.route_tree)
            
            splitter.addWidget(left_widget)
            
            # 右侧：备份管理
            right_widget = QWidget()
            right_layout = QVBoxLayout(right_widget)
            
            # 场景信息
            scenario_group = QGroupBox("场景信息")
            scenario_layout = QFormLayout(scenario_group)
            
            self.scenario_name_label = QLabel("未选择场景")
            scenario_layout.addRow("当前场景:", self.scenario_name_label)
            
            self.scenario_path_label = QLabel("")
            scenario_layout.addRow("路径:", self.scenario_path_label)
            
            right_layout.addWidget(scenario_group)
            
            # 备份列表
            backup_group = QGroupBox("备份列表")
            backup_layout = QVBoxLayout(backup_group)
            
            self.backup_list = QListWidget()
            backup_layout.addWidget(self.backup_list)
            
            # 按钮布局
            button_layout = QHBoxLayout()
            
            self.backup_button = QPushButton("创建备份")
            self.restore_button = QPushButton("还原备份")
            self.delete_button = QPushButton("删除备份")
            
            self.backup_button.setEnabled(False)
            self.restore_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            
            button_layout.addWidget(self.backup_button)
            button_layout.addWidget(self.restore_button)
            button_layout.addWidget(self.delete_button)
            
            backup_layout.addLayout(button_layout)
            right_layout.addWidget(backup_group)
            
            splitter.addWidget(right_widget)
            
            # 设置分割器比例
            splitter.setSizes([400, 600])
            
            # 菜单栏
            self.create_menu_bar()
            
            # 状态栏
            self.statusBar().showMessage("就绪")
            
            # 初始扫描
            self.scan_content()
        
        def create_menu_bar(self):
            """创建菜单栏"""
            menubar = self.menuBar()
            
            # 文件菜单
            file_menu = menubar.addMenu('文件')
            
            # 设置路径动作
            set_path_action = file_menu.addAction('设置RailWorks路径')
            set_path_action.triggered.connect(self.set_railworks_path)
            
            file_menu.addSeparator()
            
            # 退出动作
            exit_action = file_menu.addAction('退出')
            exit_action.triggered.connect(self.close)
            
            # 工具菜单
            tools_menu = menubar.addMenu('工具')
            
            # 重新扫描动作
            rescan_action = tools_menu.addAction('重新扫描内容')
            rescan_action.triggered.connect(self.scan_content)
        
        def setup_connections(self):
            """设置信号连接"""
            self.route_tree.itemSelectionChanged.connect(self.on_item_selection_changed)
            self.backup_button.clicked.connect(self.create_backup)
            self.restore_button.clicked.connect(self.restore_backup)
            self.delete_button.clicked.connect(self.delete_backup)
            
            # 搜索框信号连接
            self.search_input.textChanged.connect(self.on_search_text_changed)
        
        def set_railworks_path(self):
            """设置RailWorks路径"""
            current_path = self.tool.config_manager.get_railworks_path()
            if current_path:
                default_dir = current_path
            else:
                default_dir = "D:/Program Files (x86)/Steam/steamapps/common"
            
            path = QFileDialog.getExistingDirectory(self, "选择RailWorks安装目录", default_dir)
            if path:
                # 检查是否存在RailWorks的可执行文件
                possible_exes = [
                    "Railworks.exe",           # 32位版本
                    "Railworks64.exe",         # 64位版本  
                    "RailworksDX12_64.exe"     # 64位DX12版本
                ]
                
                found_exe = None
                for exe_name in possible_exes:
                    exe_path = os.path.join(path, exe_name)
                    if os.path.exists(exe_path):
                        found_exe = exe_name
                        break
                
                if found_exe:
                    self.tool.railworks_path = path
                    self.tool.config_manager.set_railworks_path(path)
                    self.scan_content()
                else:
                    QMessageBox.warning(self, "警告", f"选择的目录中未找到RailWorks可执行文件！\n请确保目录包含以下任一文件：\n• Railworks.exe\n• Railworks64.exe\n• RailworksDX12_64.exe")
        
        def scan_content(self):
            """扫描内容"""
            if not self.tool.railworks_path:
                QMessageBox.information(self, "信息", "请先设置RailWorks安装路径！")
                return
            
            self.statusBar().showMessage("正在扫描内容...")
            
            if self.tool.scan_content():
                self.populate_route_tree()
                self.statusBar().showMessage(f"扫描完成，找到 {len(self.tool.routes_data)} 个路线")
            else:
                QMessageBox.warning(self, "警告", "扫描内容失败！请检查路径设置。")
                self.statusBar().showMessage("扫描失败")
        
        def populate_route_tree(self):
            """填充路线树"""
            self.route_tree.clear()
            
            for route_uuid, route_data in self.tool.routes_data.items():
                route_item = QTreeWidgetItem([route_data['name']])
                route_item.setData(0, Qt.UserRole, {'type': 'route', 'uuid': route_uuid})
                
                # 添加场景
                for scenario in route_data['scenarios']:
                    scenario_item = QTreeWidgetItem([scenario['name']])
                    scenario_item.setData(0, Qt.UserRole, {
                        'type': 'scenario', 
                        'route_uuid': route_uuid,
                        'scenario_uuid': scenario['uuid'],
                        'scenario_path': scenario['path']
                    })
                    route_item.addChild(scenario_item)
                
                self.route_tree.addTopLevelItem(route_item)
            
            # 不自动展开，让用户手动点击展开路线
        
        def on_item_selection_changed(self):
            """项目选择变化处理"""
            current_item = self.route_tree.currentItem()
            if not current_item:
                return
            
            data = current_item.data(0, Qt.UserRole)
            if not data or data['type'] != 'scenario':
                return
            
            # 更新场景信息
            scenario_path = data['scenario_path']
            scenario_name = current_item.text(0)
            
            self.scenario_name_label.setText(scenario_name)
            self.scenario_path_label.setText(scenario_path)
            
            # 更新备份列表
            self.update_backup_list(scenario_path)
            
            # 启用按钮
            self.backup_button.setEnabled(True)
            self.restore_button.setEnabled(False)
            self.delete_button.setEnabled(False)
        
        def update_backup_list(self, scenario_path: str):
            """更新备份列表"""
            self.backup_list.clear()
            
            backups = self.tool.list_backups(scenario_path)
            for backup in backups:
                item = QListWidgetItem(backup)
                item.setData(Qt.UserRole, backup + ".bin")  # 存储完整文件名
                self.backup_list.addItem(item)
            
            # 连接选择变化信号
            self.backup_list.itemSelectionChanged.connect(self.on_backup_selection_changed)
        
        def on_backup_selection_changed(self):
            """备份选择变化处理"""
            current_item = self.backup_list.currentItem()
            has_selection = current_item is not None
            
            self.restore_button.setEnabled(has_selection)
            self.delete_button.setEnabled(has_selection)
        
        def on_search_text_changed(self, text):
            """搜索文本变化处理"""
            # 使用定时器延迟处理，避免频繁调用
            if hasattr(self, '_search_timer'):
                self._search_timer.stop()
            
            self._search_timer = QTimer()
            self._search_timer.setSingleShot(True)
            self._search_timer.timeout.connect(lambda: self.filter_route_tree(text))
            self._search_timer.start(300)  # 300ms延迟
        
        def filter_route_tree(self, search_text):
            """过滤路线树显示"""
            if not search_text.strip():
                # 如果搜索框为空，显示所有项目但不展开
                self.show_all_items_collapsed()
                return
            
            search_text = search_text.lower()
            
            # 清除所有隐藏状态
            self.show_all_items()
            
            # 如果搜索文本很短，直接返回显示所有项目
            if len(search_text) < 2:
                return
            
            # 只处理前100个项目以避免卡顿
            root = self.route_tree.invisibleRootItem()
            route_count = min(root.childCount(), 50)  # 限制最多处理50个路线
            
            for i in range(route_count):
                route_item = root.child(i)
                route_name = route_item.text(0).lower()
                
                # 如果路线名称匹配，显示整个路线
                if search_text in route_name:
                    route_item.setHidden(False)
                    # 不自动展开，让用户手动点击
                    
                    # 检查并显示匹配的场景
                    scenario_count = min(route_item.childCount(), 20)  # 限制每个路线最多20个场景
                    for j in range(scenario_count):
                        scenario_item = route_item.child(j)
                        scenario_name = scenario_item.text(0).lower()
                        if search_text in scenario_name:
                            scenario_item.setHidden(False)
                        else:
                            scenario_item.setHidden(True)
                else:
                    # 检查路线下的场景是否匹配
                    has_matching_scenario = False
                    scenario_count = min(route_item.childCount(), 20)  # 限制每个路线最多20个场景
                    for j in range(scenario_count):
                        scenario_item = route_item.child(j)
                        scenario_name = scenario_item.text(0).lower()
                        if search_text in scenario_name:
                            scenario_item.setHidden(False)
                            has_matching_scenario = True
                        else:
                            scenario_item.setHidden(True)
                    
                    # 如果有匹配的场景，显示路线但隐藏不匹配的场景
                    route_item.setHidden(not has_matching_scenario)
        
        def show_all_items(self):
            """显示所有项目（保持当前展开状态）"""
            root = self.route_tree.invisibleRootItem()
            for i in range(root.childCount()):
                route_item = root.child(i)
                route_item.setHidden(False)
                
                # 显示该路线下的所有场景
                for j in range(route_item.childCount()):
                    scenario_item = route_item.child(j)
                    scenario_item.setHidden(False)
        
        def show_all_items_collapsed(self):
            """显示所有项目（默认折叠状态）"""
            root = self.route_tree.invisibleRootItem()
            for i in range(root.childCount()):
                route_item = root.child(i)
                route_item.setHidden(False)
                
                # 折叠路线（不展开子项目）
                self.route_tree.collapseItem(route_item)
                
                # 显示该路线下的所有场景
                for j in range(route_item.childCount()):
                    scenario_item = route_item.child(j)
                    scenario_item.setHidden(False)
        
        def create_backup(self):
            """创建备份"""
            current_item = self.route_tree.currentItem()
            if not current_item:
                return
            
            data = current_item.data(0, Qt.UserRole)
            if not data or data['type'] != 'scenario':
                return
            
            scenario_path = data['scenario_path']
            save_file = os.path.join(scenario_path, "CurrentSave.bin")
            
            if not os.path.exists(save_file):
                QMessageBox.warning(self, "警告", "未找到CurrentSave.bin文件！\n您需要在游戏中先按F2或\"暂停菜单\"中的\"保存\"选项保存存档。")
                return
            
            if self.tool.create_backup(scenario_path):
                QMessageBox.information(self, "成功", "备份创建成功！")
                self.update_backup_list(scenario_path)
            else:
                QMessageBox.warning(self, "失败", "备份创建失败！")
        
        def restore_backup(self):
            """还原备份"""
            scenario_item = self.route_tree.currentItem()
            backup_item = self.backup_list.currentItem()
            
            if not scenario_item or not backup_item:
                return
            
            scenario_data = scenario_item.data(0, Qt.UserRole)
            if not scenario_data or scenario_data['type'] != 'scenario':
                return
            
            scenario_path = scenario_data['scenario_path']
            backup_filename = backup_item.data(Qt.UserRole)
            
            # 确认对话框
            reply = QMessageBox.question(
                self, 
                "确认还原", 
                "还原操作将覆盖当前存档，确定要继续吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if self.tool.restore_backup(scenario_path, backup_filename):
                    QMessageBox.information(self, "成功", "备份还原成功！")
                else:
                    QMessageBox.warning(self, "失败", "备份还原失败！")
        
        def delete_backup(self):
            """删除备份"""
            scenario_item = self.route_tree.currentItem()
            backup_item = self.backup_list.currentItem()
            
            if not scenario_item or not backup_item:
                return
            
            scenario_data = scenario_item.data(0, Qt.UserRole)
            if not scenario_data or scenario_data['type'] != 'scenario':
                return
            
            scenario_path = scenario_data['scenario_path']
            backup_filename = backup_item.data(Qt.UserRole)
            backup_display = backup_item.text()
            
            # 确认对话框
            reply = QMessageBox.question(
                self, 
                "确认删除", 
                f"确定要删除备份 '{backup_display}' 吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if self.tool.delete_backup(scenario_path, backup_filename):
                    QMessageBox.information(self, "成功", "备份删除成功！")
                    self.update_backup_list(scenario_path)
                else:
                    QMessageBox.warning(self, "失败", "备份删除失败！")


# GTK GUI实现（备用）
elif PYGTK_AVAILABLE:
    class MainWindow(Gtk.ApplicationWindow):
        """GTK主窗口"""
        
        def __init__(self, app):
            super().__init__(application=app)
            self.tool = TrainSimulatorBackupTool()
            self.init_ui()
            
        def init_ui(self):
            """初始化用户界面"""
            self.set_title("Train Simulator Classic 存档备份管理工具")
            self.set_default_size(1200, 800)
            
            # 创建主容器
            main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            self.add(main_box)
            
            # 左侧：路线树
            left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
            main_box.pack_start(left_box, True, True, 0)
            
            route_label = Gtk.Label()
            route_label.set_text("路线和场景:")
            left_box.pack_start(route_label, False, False, 0)
            
            self.route_tree = Gtk.TreeView()
            left_box.pack_start(self.tree_store, True, True, 0)
            
            # 右侧：备份管理
            right_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
            main_box.pack_end(right_box, True, True, 0)
            
            # 这里需要实现完整的GTK界面...
            # 由于GTK实现较为复杂，建议使用PyQt版本


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    if PYQT_VERSION == 5:
        app.setApplicationName("Train Simulator Classic Backup Tool")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("MiniMax Agent")
    else:  # PyQt6
        app.setApplicationName("Train Simulator Classic Backup Tool")
        app.setApplicationDisplayName("Train Simulator Classic Backup Tool")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
