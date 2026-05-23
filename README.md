# Cnblogs Image Downloader

English Version | [中文版](README-ZhCn.md)

## 1. Project Introduction
This project is a lightweight command-line tool designed to automatically download all images within the main content of Cnblogs articles. It automatically visits the specified Cnblogs article URL, uses the article title to create a local download directory, intelligently identifies and filters out non-content images (such as avatars, icons, etc.), batch downloads valid images from the article body to the local machine, and uniformly names them in the format of "ArticleName_Index".

## 2. Tech Stack

### 2.1 Frontend
- **Core Interaction**: Command Line Interface (CLI)
- **Technology Choice**: `argparse` (Python Standard Library)
- **Core Function**: Provides user-friendly parsing of command-line arguments, supporting the input of target article URLs and displaying help information.

### 2.2 Backend & Runtime
- **Programming Language**: Python 3
- **Runtime Environment**: Cross-platform (Supports Windows, macOS, Linux)
- **Core Function**: Handles core business logic, including network requests, HTML parsing, and file I/O operations.

### 2.3 Infrastructure
- **Storage System**: Local File System
- **Core Function**: Creates independent folders based on article titles for categorizing and persistently storing downloaded image files.

### 2.4 Toolchain & Dependencies
- **Network Requests (HTTP Client)**: `requests (>=2.31.0)`
  - **Core Function**: Responsible for sending HTTP requests to retrieve the target article's HTML source code and downloading the binary data of the images.
- **HTML Parser**: `beautifulsoup4 (>=4.12.0)` combined with `lxml (>=4.9.0)`
  - **Core Function**: Parses the web page DOM tree to precisely locate and extract the article title area and data from `<img>` tags within the main content.
- **Build & Packaging Tool**: `pyinstaller`
  - **Core Function**: Used to package the Python script into a standalone executable file (e.g., `.exe` for Windows), making it convenient for users without a Python environment to run directly.

## 3. Environment Requirements
- **Operating System**: Windows 10/11, macOS 10.15+, or mainstream Linux distributions
- **Python Version**: Python 3.7 or higher
- **Core Python Dependencies** (see `requirements.txt`):
  - `requests >= 2.31.0`
  - `beautifulsoup4 >= 4.12.0`
  - `lxml >= 4.9.0`
  - `pyinstaller` (Only used for building standalone executables)

## 4. Local Deployment and Startup Steps

### 4.1 General Prerequisites (Get Code and Install Dependencies)
Regardless of your operating system, please ensure a Python 3 environment is installed first. Then follow these steps to obtain and initialize the project:

```bash
# 1. Clone or download this repository to your local machine
git clone <repository_url>
cd <repository_directory>

# 2. (Optional) Create and activate a virtual environment to avoid polluting the global environment
python -m venv venv

# Activate virtual environment on Windows:
venv\Scripts\activate
# Activate virtual environment on macOS/Linux:
source venv/bin/activate

# 3. Install required project dependencies
pip install -r requirements.txt
```

### 4.2 Run the Tool
Execute the following command in your terminal or command prompt, passing the Cnblogs article URL as a parameter:

#### Windows
```cmd
python download_cnblogs_images.py https://www.cnblogs.com/wintersun/p/19390629
```

#### macOS / Linux
```bash
python3 download_cnblogs_images.py https://www.cnblogs.com/wintersun/p/19390629
```

### 4.3 Build Standalone Executable (Windows Example)
If you wish to generate an `.exe` file on Windows:
```cmd
# Run the provided batch script
build_windows_exe.bat
```
Or use PyInstaller directly:
```bash
pyinstaller cnblogs_downloader.spec --clean
```
After a successful build, the executable file will be generated in the `dist/` directory.

## 5. Project Structure

```text
.
├── build_windows_exe.bat       # Batch script for one-click exe generation on Windows
├── cnblogs_downloader.spec     # Packaging configuration file for PyInstaller
├── download_cnblogs_images.py  # Main program file containing web requests, parsing, and image download logic
├── requirements.txt            # List of project dependencies and their version requirements
├── README.md                   # English project documentation
└── README-ZhCn.md              # Chinese project documentation
```

## 6. Development Conventions
1. **Code Style**: Follow the PEP 8 standard to keep code clean; function names should have clear semantics (e.g., `sanitize_filename`, `extract_article_info`).
2. **Exception Handling**: Critical operations such as network requests (`requests.get`) and file reading/writing must include `try...except` blocks to catch and properly handle exceptions to prevent abnormal program crashes.
3. **Friendly Interaction**: Provide clear command-line log outputs, including current progress, success and failure records, and specific reasons when errors occur.
4. **Anti-Crawler Limits**: Carry an appropriate `User-Agent` in request headers, and introduce moderate delays (e.g., `time.sleep(0.5)`) when downloading multiple images consecutively to reduce the risk of the IP being blocked by the target website.

## 7. FAQ

**Q1: Getting a `ModuleNotFoundError: No module named 'requests'` when running the script?**
**A**: This indicates that you have not installed the required third-party dependencies for the project. Make sure you have executed the `pip install -r requirements.txt` command in the root directory of the project.

**Q2: Image download fails, showing a message that fetching web page content failed?**
**A**: Check your network connection and verify if the target Cnblogs article has been deleted or has access restrictions set. Additionally, frequent requests might have triggered the website's anti-crawler strategy; it is recommended to wait a moment before trying again.

**Q3: Expected images are not found in the generated folder?**
**A**: This tool automatically filters out non-article body images such as avatars and icons. If images indeed exist in the main content but fail to download successfully, it may be because the HTML structure of the article has changed, causing the existing parsing rules to become invalid. It is recommended to check if the selector logic in the `extract_images` function in `download_cnblogs_images.py` is still effective.

## 8. Unit Testing
This project uses `pytest` for unit testing. The tests are designed to run isolated from external dependencies by using `unittest.mock` (provided via `pytest-mock`).

### 8.1 Testing Requirements
Ensure the following packages are installed for running the tests. You can install them manually or use `pip`:
```bash
pip install pytest pytest-mock pytest-cov
```

### 8.2 Run Tests
To run the standard unit tests:
```bash
pytest test_download_cnblogs_images.py
```

### 8.3 Run Tests with Coverage
To see the code coverage report for the core script:
```bash
pytest --cov=download_cnblogs_images test_download_cnblogs_images.py
```
You should expect high coverage (usually around 99%) verifying all edge cases, exceptions, and typical flows.
