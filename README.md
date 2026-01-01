中文 | [English](./README.en.md)

# Train Simulator Classic 存档备份管理工具

一个专为DTG Train Simulator Classic（火车模拟器经典版）设计的存档备份管理工具，解决Train Simulator Classic游戏只能在同一个场景下覆盖备份存档的问题，帮助玩家轻松备份、还原和管理游戏存档。

## 安装方式

### 方式一：使用预编译可执行文件（推荐）

1. 从Releases下载最新的可执行文件 `TrainSimulatorBackup.exe`
2. 直接从源码运行，需安装Python环境

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

### 功能使用说明

1. 打开游戏，在游戏过程中按F2或在暂停菜单中选择“保存”，保存游戏进度。![1767257570377](image/README/1767257570377.png)
2. 完成此操作后，打开TrainSimulatorBackup，找到刚刚保存存档的场景，点击“创建备份”，即可完成存档备份的创建，默认保存在场景目录的Saves文件夹中。
   ![1767258005528](image/README/1767258005528.png)
3. 如需还原某个存档，则选择备份列表中创建的项目，选择“还原备份”即可还原存档。

   ![1767258439070](image/README/1767258439070.png)
4. 如需删除，选择对应备份项目再点击“删除备份”即可。

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
2. 确保选择包含 `Railworks.exe`、`Railworks64.exe`或 `RailworksDX12_64.exe` 的目录

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

### 主要依赖

- **PyQt5/PyQt6**: GUI框架
- **xml.etree.ElementTree**: XML解析（Python标准库）
- **pywin32**: Windows注册表访问
- **pyinstaller**: 打包工具

### 许可证

本项目采用MIT许可证，详见LICENSE文件。

### 免责声明

本工具仅用于个人学习和备份目的，与Dovetail Games无任何关联，请遵守相关游戏的使用条款和版权规定。

部分源代码使用AI编写，已经过本人审查和修正。
