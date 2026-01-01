# Train Simulator Classic 存档备份管理工具

一个专为Train Simulator Classic（火车模拟器经典版）设计的存档备份管理工具，帮助玩家轻松备份、还原和管理游戏存档。

## 功能特点

- 🔍 **自动检测游戏路径** - 支持Steam版本的默认安装路径
- 📁 **智能内容扫描** - 自动解析XML文件获取路线和场景的中文名称
- 💾 **一键备份** - 快速创建带时间戳的存档备份
- 🔄 **安全还原** - 支持备份还原，带确认提示防止误操作
- 🗑️ **备份管理** - 支持删除不需要的备份文件
- 🎨 **图形界面** - 简洁直观的GUI操作界面
- ⚙️ **配置保存** - 自动保存设置，无需重复配置

## 系统要求

- **操作系统**: Windows 7/8/10/11
- **Python版本**: 3.10 - 3.14
- **Train Simulator Classic**: 已安装的Steam版本

## 安装方式

### 方式一：使用预编译可执行文件（推荐）

1. 下载最新的可执行文件 `TrainSimulatorBackup.exe`
2. 直接运行，无需安装Python环境

### 方式二：从源码运行

1. **安装Python依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **运行程序**
   ```bash
   python train_simulator_backup_tool.py
   ```

### 方式三：使用PyInstaller打包

1. **安装打包工具**
   ```bash
   pip install pyinstaller
   ```

2. **执行打包脚本**
   ```bash
   python build_exe.py
   ```

3. **获取可执行文件**
   - 打包完成后，可执行文件位于 `dist/TrainSimulatorBackup.exe`

## 使用说明

### 首次使用

1. **启动程序** - 运行 `TrainSimulatorBackup.exe`
2. **设置游戏路径** - 菜单栏 → 文件 → 设置RailWorks路径
3. **选择游戏目录** - 浏览到RailWorks安装目录（包含Railworks.exe、Railworks64.exe或RailworksDX12_64.exe的目录）
4. **自动扫描** - 程序会自动扫描所有路线和场景

### 界面说明

#### 左侧面板：路线和场景树
- **搜索框**: 在顶部输入路线或场景名称进行实时搜索和过滤
- 显示所有已安装的路线
- 点击路线可展开查看场景列表
- 场景显示为中文名称（从XML文件中解析）
- 搜索功能支持模糊匹配，自动展开包含匹配内容的路线

#### 右侧面板：备份管理
- **场景信息**: 显示当前选中场景的名称和路径
- **备份列表**: 显示该场景的所有备份文件
- **操作按钮**:
  - **创建备份**: 为当前场景创建新的备份
  - **还原备份**: 将选中的备份还原到游戏存档
  - **删除备份**: 删除选中的备份文件

### 操作流程

#### 创建备份
1. 在左侧树中选择要备份的场景
2. 点击"创建备份"按钮
3. 程序会自动创建带时间戳的备份文件

#### 还原备份
1. 选择要还原的场景
2. 在右侧备份列表中选择要还原的备份
3. 点击"还原备份"按钮
4. 在确认对话框中点击"是"确认操作

#### 删除备份
1. 选择场景和要删除的备份
2. 点击"删除备份"按钮
3. 在确认对话框中点击"是"确认删除

## 备份文件说明

### 文件命名格式
- 备份文件命名: `CurrentSave-YYYY-mm-dd-HH-MM-SS.bin`
- 例如: `CurrentSave-2025-01-01-14-30-25.bin`

### 存储位置
- 备份文件存储在场景目录下的 `saves` 文件夹中
- 路径结构: `[场景UUID]/saves/CurrentSave-[时间戳].bin`

### 备份策略
- 支持同一场景的多个备份版本
- 备份文件按创建时间倒序排列（最新的在前面）
- 备份文件可以安全删除，不影响游戏正常存档

## 技术实现

### 核心组件

1. **ConfigManager** - 配置文件管理
   - 保存游戏路径设置
   - 持久化用户偏好

2. **XMLParser** - XML解析器
   - 解析RouteProperties.xml和ScenarioProperties.xml
   - 支持多语言显示名称解析
   - 智能回退机制

3. **TrainSimulatorBackupTool** - 核心业务逻辑
   - 自动检测RailWorks路径
   - 内容扫描和解析
   - 备份创建、还原、删除操作

4. **GUI界面** - 图形用户界面
   - 基于PyQt5/PyQt6的现代化界面
   - 响应式布局设计
   - 完整的用户交互流程

### 兼容性支持

- **Python版本**: 3.10 - 3.14
- **GUI库**: PyQt5、PyQt6、GTK3
- **操作系统**: Windows（主要支持）
- **游戏版本**: Train Simulator Classic Steam版

## 故障排除

### 常见问题

#### Q: 程序无法检测到游戏路径
**A**: 
1. 手动设置路径：菜单 → 文件 → 设置RailWorks路径
2. 确保选择包含 `Railworks.exe`、`Railworks64.exe`或`RailworksDX12_64.exe` 的目录

#### Q: 路线或场景名称显示为UUID
**A**: 
1. 检查XML文件是否损坏或缺失
2. 确保游戏文件完整性
3. 尝试重新扫描（工具 → 重新扫描内容）

#### Q: 备份创建失败
**A**: 
1. 确保有足够的磁盘空间
2. 检查游戏是否正在运行（关闭游戏后重试）
3. 确保对游戏目录有写入权限

#### Q: 还原后游戏无法读取存档
**A**: 
1. 备份文件可能已损坏，尝试其他备份
2. 确保备份文件与当前游戏版本兼容
3. 检查游戏目录权限

### 日志和调试

程序会在控制台输出详细的操作日志，包括：
- 路径检测结果
- XML解析过程
- 文件操作状态
- 错误信息

如果遇到问题，请查看控制台输出获取详细信息。

## 开发信息

### 项目结构
```
train-simulator-backup-tool/
├── train_simulator_backup_tool.py  # 主程序文件
├── requirements.txt                # 依赖文件
├── setup.py                       # 安装脚本
├── build_exe.py                   # PyInstaller打包脚本
└── README.md                      # 说明文档
```

### 主要依赖
- **PyQt5/PyQt6**: GUI框架
- **xml.etree.ElementTree**: XML解析（Python标准库）
- **pywin32**: Windows注册表访问
- **pyinstaller**: 打包工具

### 许可证
本项目采用MIT许可证，详见LICENSE文件。

## 更新日志

### v1.0.0 (2025-01-01)
- 初始版本发布
- 支持基本的备份、还原、删除功能
- 实现自动路径检测和XML解析
- 提供图形化操作界面

## 贡献指南

欢迎提交Issue和Pull Request来改进这个工具！

### 开发环境设置
1. 克隆项目仓库
2. 安装开发依赖: `pip install -r requirements.txt`
3. 运行程序: `python train_simulator_backup_tool.py`

### 代码规范
- 遵循PEP 8代码风格
- 添加必要的注释和文档字符串
- 确保向后兼容性

## 联系方式

- 项目维护者: MiniMax Agent
- 邮箱: agent@minimax.chat
- GitHub: https://github.com/minimax/train-simulator-backup-tool

---

**免责声明**: 本工具仅用于个人学习和备份目的，请遵守相关游戏的使用条款和版权规定。