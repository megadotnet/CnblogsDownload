# 博客园文章图片下载工具 (Cnblogs Image Downloader)

[English Version](README.md) | 中文版

## 1. 项目介绍
本项目是一个用于自动下载博客园（Cnblogs）文章正文中所有图片的轻量级命令行工具。它能够自动访问指定的博客园文章URL，提取文章标题作为本地下载目录名，智能识别并过滤非内容图片（如头像、图标等），将文章正文中的有效图片批量下载到本地，并按“文章名_序号”的格式进行规范命名。

## 2. 技术栈清单

### 2.1 前端 (Frontend)
- **核心交互**：命令行界面 (CLI)
- **技术选型**：`argparse` (Python标准库)
- **核心作用**：提供用户友好的命令行参数解析，支持传入目标文章的URL以及展示帮助信息。

### 2.2 后端及运行环境 (Backend & Runtime)
- **编程语言**：Python 3
- **运行环境**：跨平台（支持 Windows, macOS, Linux）
- **核心作用**：处理核心业务逻辑，包括网络请求、HTML解析、文件IO等操作。

### 2.3 基础设施 (Infrastructure)
- **存储系统**：本地文件系统 (Local File System)
- **核心作用**：以文章标题创建独立的文件夹，用于分类存储和持久化下载的图片文件。

### 2.4 工具链及第三方依赖 (Toolchain & Dependencies)
- **网络请求 (HTTP Client)**：`requests (>=2.31.0)`
  - **核心作用**：负责发送HTTP请求，获取目标文章的HTML源码以及下载图片的二进制数据。
- **HTML 解析 (HTML Parser)**：`beautifulsoup4 (>=4.12.0)` 配合 `lxml (>=4.9.0)`
  - **核心作用**：解析网页DOM树，精准定位并提取文章标题区域及正文中的 `<img>` 标签数据。
- **构建与打包工具**：`pyinstaller`
  - **核心作用**：用于将Python脚本打包为独立的可执行文件（如Windows的`.exe`），方便未配置Python环境的用户直接运行。

## 3. 环境依赖要求
- **操作系统**：Windows 10/11, macOS 10.15+, 或主流 Linux 发行版
- **Python 版本**：Python 3.7 及以上版本
- **核心 Python 依赖包**（详见 `requirements.txt`）：
  - `requests >= 2.31.0`
  - `beautifulsoup4 >= 4.12.0`
  - `lxml >= 4.9.0`
  - `pyinstaller` (仅用于构建独立运行程序)

## 4. 本地部署与启动步骤

### 4.1 通用前置步骤（获取代码与安装依赖）
无论您使用哪种操作系统，首先请确保已安装 Python 3 环境。然后按照以下步骤获取并初始化项目：

```bash
# 1. 克隆或下载本仓库代码到本地
git clone <repository_url>
cd <repository_directory>

# 2. (可选) 创建并激活虚拟环境，以避免污染全局环境
python -m venv venv

# Windows 下激活虚拟环境:
venv\Scripts\activate
# macOS/Linux 下激活虚拟环境:
source venv/bin/activate

# 3. 安装项目所需依赖
pip install -r requirements.txt
```

### 4.2 运行工具
在终端或命令行中执行以下命令，将博客园文章URL作为参数传入：

#### Windows
```cmd
python download_cnblogs_images.py https://www.cnblogs.com/wintersun/p/19390629
```

#### macOS / Linux
```bash
python3 download_cnblogs_images.py https://www.cnblogs.com/wintersun/p/19390629
```

### 4.3 构建独立可执行文件 (以 Windows 为例)
如果您希望在 Windows 上生成 `.exe` 文件：
```cmd
# 运行提供的批处理脚本
build_windows_exe.bat
```
或直接使用 PyInstaller：
```bash
pyinstaller cnblogs_downloader.spec --clean
```
构建成功后，可执行文件将生成在 `dist/` 目录下。

## 5. 项目结构说明

```text
.
├── build_windows_exe.bat       # Windows 平台下用于一键打包生成 exe 的批处理脚本
├── cnblogs_downloader.spec     # PyInstaller 的打包配置文件
├── download_cnblogs_images.py  # 项目的主程序文件，包含网页请求、解析和图片下载逻辑
├── requirements.txt            # 项目依赖包清单及其版本要求
├── README.md                   # 英文版项目说明文档
└── README-ZhCn.md              # 中文版项目说明文档
```

## 6. 开发规范
1. **代码风格**：遵循 PEP 8 规范，保持代码整洁，函数命名需具有明确语义（如 `sanitize_filename`, `extract_article_info`）。
2. **异常处理**：在网络请求（`requests.get`）、文件读写等关键操作中，必须包含 `try...except` 块以捕获并妥善处理异常，避免程序异常崩溃。
3. **友好交互**：提供清晰的命令行日志输出，包括当前进度、成功与失败的记录，以及发生错误时的具体原因。
4. **防爬虫限制**：在请求头中需携带恰当的 `User-Agent`，在连续下载多张图片时加入适度的延迟（如 `time.sleep(0.5)`），以降低被目标网站封禁IP的风险。

## 7. 常见问题排查 (FAQ)

**Q1: 运行脚本时提示 `ModuleNotFoundError: No module named 'requests'`?**
**A**: 这表示您尚未安装项目所需的第三方依赖库。请确保在项目根目录下执行了 `pip install -r requirements.txt` 命令。

**Q2: 图片下载失败，提示获取网页内容失败?**
**A**: 检查您的网络连接是否正常，确认目标博客园文章是否已被删除或设置了访问权限。此外，频繁请求可能触发了网站的反爬策略，建议稍作等待后重试。

**Q3: 生成的文件夹中没有找到预期的图片?**
**A**: 本工具会自动过滤掉诸如头像、图标等非文章正文的图片。如果正文中确实存在图片但未能成功下载，可能是因为文章的 HTML 结构发生了变更，导致现有的解析规则失效。建议检查 `download_cnblogs_images.py` 中 `extract_images` 函数的选择器逻辑是否仍有效。
