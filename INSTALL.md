# Train Simulator Classic 存档备份管理工具 - 安装说明

## 快速开始

### 方式一：直接运行可执行文件（推荐）
1. 下载 `TrainSimulatorBackup.exe`
2. 双击运行
3. 设置游戏路径即可使用

### 方式二：从源码运行
1. 确保安装了Python 3.10-3.14
2. 安装依赖：
   ```
   pip install -r requirements.txt
   ```
3. 运行程序：
   ```
   python train_simulator_backup_tool.py
   ```

### 方式三：创建可执行文件
1. 安装开发依赖：
   ```
   pip install -r requirements.txt
   pip install pyinstaller
   ```
2. 运行打包脚本：
   ```
   python build_exe.py
   ```
3. 在 `dist/` 目录中找到生成的可执行文件

## 首次使用

1. **启动程序**后，菜单栏选择 `文件` → `设置RailWorks路径`
2. **浏览选择**您的Train Simulator Classic安装目录（包含Railworks.exe、Railworks64.exe或RailworksDX12_64.exe的目录）
3. 程序会自动**扫描**所有路线和场景
4. **开始备份**您的存档！

## 常见问题

**Q: 程序无法找到游戏路径？**
A: 手动设置路径，选择包含Railworks.exe、Railworks64.exe或RailworksDX12_64.exe的目录

**Q: 路线名称显示为UUID？**
A: 检查游戏文件完整性，或尝试重新扫描内容

**Q: 备份失败？**
A: 确保游戏已关闭，有足够磁盘空间，且有写入权限

## 技术支持

如有问题，请查看：
- 详细说明：README.md
- 测试脚本：python test_tool.py
- 控制台日志输出

---
**版权声明**: 本工具仅供学习和备份使用，请遵守游戏使用条款。