# VS Code LeetCode Helper

![Languages](https://img.shields.io/badge/Languages-C++%20|%20Python-blue)
![Last Update](https://img.shields.io/badge/最近更新-2025年4月19日-brightgreen)
![License](https://img.shields.io/badge/许可证-MIT-green)

<p align="center">
  <img src="https://assets.leetcode.com/static_assets/public/images/LeetCode_logo.png" alt="LeetCode Logo" width="200"/>
</p>

这是一个用于LeetCode刷题的VS Code本地环境工具，支持C++和Python语言，提供自动化工具帮助创建、测试和管理LeetCode题目。本项目不包含具体题目的解答，仅提供刷题辅助工具。

## 📌 功能特点

- 🔄 **多语言支持**：同时支持C++和Python解决方案
- 🚀 **自动化工具**：一键创建题目、获取每日一题、本地测试
- 🗂️ **标签分类**：按照题目标签和难度进行分类
- 🧪 **测试用例**：自动生成测试代码和测试用例
- 📤 **代码提取**：自动提取符合提交格式的代码片段

## 🚀 使用方法

### 环境配置

```bash
# 克隆仓库
git clone https://github.com/wby1905/VSCode-LeetCode-Helper.git
cd VSCode-LeetCode-Helper

# 运行环境配置脚本
python Scripts/setup_environment.py
```

### 创建新题目

```bash
python Scripts/create_problem.py <题号> [语言]
```

**示例：**
- `python Scripts/create_problem.py 100 cpp` - 创建第100题的C++解决方案
- `python Scripts/create_problem.py 100 py` - 创建第100题的Python解决方案（默认）
- `python Scripts/create_problem.py 100 all` - 创建第100题的所有语言解决方案

### 获取每日一题

```bash
python Scripts/daily_question.py [语言]
```

**示例：**
- `python Scripts/daily_question.py` - 获取今天的每日一题（默认为Python）
- `python Scripts/daily_question.py cpp` - 获取今天的每日一题（C++版本）
- `python Scripts/daily_question.py all` - 获取今天的每日一题（所有语言版本）

### 本地测试

```bash
python Scripts/test_solution.py <题号> [语言]
```

**示例：**
- `python Scripts/test_solution.py 100 cpp` - 测试第100题的C++解决方案

### 提取提交代码

```bash
python Scripts/test_solution.py <题号> [语言] --extract
```

**示例：**
- `python Scripts/test_solution.py 100 py --extract` - 提取可提交到LeetCode的Python代码

## 📂 目录结构

```
LeetCode/
├── Scripts/               # 自动化脚本工具
│   ├── code_generators/   # 代码生成器
│   ├── create_problem.py  # 创建题目脚本
│   ├── daily_question.py  # 获取每日一题脚本
│   ├── leetcode_api.py    # LeetCode API客户端
│   ├── setup_environment.py # 环境配置脚本
│   └── test_solution.py   # 测试解决方案脚本
├── Tags/                  # 按标签分类的题目目录(自动创建)
├── Templates/             # 代码模板
│   ├── cpp_template.cpp   # C++模板
│   ├── py_template.py     # Python模板
│   └── md_template.md     # Markdown笔记模板
└── .vscode/               # VS Code配置(自动创建)
    ├── settings.json      # 编辑器设置
    └── tasks.json         # 任务配置
```

## 🛠️ VS Code 任务集成

本环境配置了多个VS Code任务，使刷题更为高效。按下`Ctrl+Shift+P`并输入`Tasks: Run Task`可以看到以下任务：

✅ **C++: 编译并运行** - 编译并运行当前C++文件  
✅ **Python: 运行当前文件** - 运行当前Python文件  
✅ **LeetCode: 创建题目** - 创建新的LeetCode题目  
✅ **LeetCode: 获取每日一题** - 获取今天的LeetCode每日一题  
✅ **LeetCode: 测试解决方案** - 测试LeetCode解决方案  
✅ **LeetCode: 提取提交代码** - 提取用于提交的代码片段  

## 💻 编程环境要求

- **C++**: MinGW-w64或MSVC++编译器（G++ 支持C++17）
- **Python**: Python 3.6或更高版本
- **IDE**: Visual Studio Code（推荐安装C/C++和Python扩展）

## ⚠️ 注意事项

1. 此项目仅包含刷题工具，不包含具体题目的解答。
2. 使用此工具生成的题目解答会保存在`Tags/`目录下，该目录已被添加到`.gitignore`文件中，不会上传到GitHub。
3. 如果您Fork本项目并进行修改，请确保不要上传您的个人刷题记录。

## 💡 贡献

欢迎提出改进建议或报告bug！请随时提交Issue或Pull Request。

## 📄 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。
