#!/usr/bin/env python3
"""
LeetCode编程环境配置工具
用法: python setup_environment.py
这个脚本会检查并配置C++和Python的运行环境
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path


def check_command(command):
    """检查命令是否可用"""
    try:
        subprocess.run(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return True
    except:
        return False


def setup_cpp_environment():
    """配置C++运行环境"""
    print("正在检查C++环境...")

    # 检查g++是否安装
    if check_command("g++ --version"):
        print("√ 已安装g++编译器")
    else:
        print("× 未检测到g++编译器")
        print("  请安装MinGW-w64或MSVC++编译器")
        print("  推荐下载地址: https://winlibs.com/ (MinGW-w64)")
        print("  或通过安装Visual Studio Community获取MSVC++编译器")

    # 创建C++运行配置文件 (tasks.json for VS Code)
    vscode_dir = Path(".vscode")
    vscode_dir.mkdir(exist_ok=True)

    cpp_task = {
        "version": "2.0.0",
        "tasks": [
            {
                "label": "C++: 编译并运行",
                "type": "shell",
                "command": "g++ -std=c++17 ${file} -o ${fileDirname}/${fileBasenameNoExtension}.exe && ${fileDirname}/${fileBasenameNoExtension}.exe",
                "group": {"kind": "build", "isDefault": True},
                "presentation": {"reveal": "always", "panel": "new"},
                "problemMatcher": ["$gcc"],
            }
        ],
    }

    with open(vscode_dir / "cpp_tasks.json", "w", encoding="utf-8") as f:
        import json

        json.dump(cpp_task, f, ensure_ascii=False, indent=4)

    print("√ 已创建C++运行配置文件: .vscode/cpp_tasks.json")

    # 添加C++的代码片段
    cpp_snippets = {
        "LeetCode Solutions Template": {
            "prefix": "lctemplate",
            "body": [
                "#include <iostream>",
                "#include <vector>",
                "#include <string>",
                "#include <unordered_map>",
                "#include <unordered_set>",
                "#include <stack>",
                "#include <queue>",
                "#include <algorithm>",
                "using namespace std;",
                "",
                "class Solution {",
                "public:",
                "    $1",
                "};",
                "",
                "int main() {",
                "    Solution sol;",
                "    $2",
                "    return 0;",
                "}",
            ],
            "description": "LeetCode C++ 解题模板",
        }
    }

    with open(vscode_dir / "cpp_snippets.json", "w", encoding="utf-8") as f:
        import json

        json.dump(cpp_snippets, f, ensure_ascii=False, indent=4)

    print("√ 已创建C++代码片段文件: .vscode/cpp_snippets.json")


def setup_python_environment():
    """配置Python运行环境"""
    print("\n正在检查Python环境...")

    # 检查Python是否安装
    if check_command("python --version"):
        python_version = subprocess.run(
            "python --version",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        print(
            f"√ 已安装Python: {python_version.stdout.strip() or python_version.stderr.strip()}"
        )
    else:
        print("× 未检测到Python")
        print("  请安装Python 3.6或更高版本")
        print("  下载地址: https://www.python.org/downloads/")

    # 为LeetCode问题创建虚拟环境
    print("正在创建Python虚拟环境...")

    if not Path("venv").exists():
        try:
            subprocess.run("python -m venv venv", shell=True, check=True)
            print("√ 已创建Python虚拟环境: venv/")

            # 安装必要的包
            if platform.system() == "Windows":
                pip_cmd = "venv\\Scripts\\pip"
                python_cmd = "venv\\Scripts\\python"
            else:
                pip_cmd = "venv/bin/pip"
                python_cmd = "venv/bin/python"

            print("正在安装必要的Python包...")

            # 首先升级pip
            try:
                subprocess.run(
                    f"{python_cmd} -m pip install --upgrade pip", shell=True, check=True
                )
                print("√ 已升级pip到最新版本")
            except:
                print("× 升级pip失败，将使用当前版本继续")

            # 安装依赖包
            packages = ["requests", "pyperclip"]
            for package in packages:
                try:
                    subprocess.run(
                        f"{pip_cmd} install {package}", shell=True, check=True
                    )
                    print(f"√ 已安装{package}")
                except:
                    print(f"× 安装{package}失败")

            # 创建一个批处理文件，用于激活虚拟环境
            with open("activate_venv.bat", "w") as f:
                f.write("@echo off\n")
                f.write("echo 正在激活Python虚拟环境...\n")
                f.write("call venv\\Scripts\\activate.bat\n")
                f.write("echo 虚拟环境已激活，可以开始使用！\n")
                f.write("cmd /k")

            print("√ 已创建虚拟环境激活脚本: activate_venv.bat")

        except Exception as e:
            print(f"× 创建虚拟环境失败: {str(e)}")
    else:
        print("√ 已存在Python虚拟环境: venv/")
        print("  如需重新创建，请先删除venv目录")

        # 检查是否需要更新依赖包
        print("正在检查依赖包...")

        if platform.system() == "Windows":
            pip_cmd = "venv\\Scripts\\pip"
        else:
            pip_cmd = "venv/bin/pip"

        packages = ["requests", "pyperclip"]
        for package in packages:
            try:
                subprocess.run(
                    f"{pip_cmd} show {package}",
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True,
                )
                print(f"√ 已安装{package}")
            except:
                print(f"× 未安装{package}，正在安装...")
                try:
                    subprocess.run(
                        f"{pip_cmd} install {package}", shell=True, check=True
                    )
                    print(f"√ 已安装{package}")
                except:
                    print(f"× 安装{package}失败")

    # 创建Python运行配置文件 (tasks.json for VS Code)
    vscode_dir = Path(".vscode")
    vscode_dir.mkdir(exist_ok=True)

    python_task = {
        "version": "2.0.0",
        "tasks": [
            {
                "label": "Python: 运行当前文件(venv)",
                "type": "shell",
                "command": "${workspaceFolder}\\venv\\Scripts\\python.exe ${file}",
                "group": {"kind": "build", "isDefault": True},
                "presentation": {"reveal": "always", "panel": "new"},
                "problemMatcher": [],
                "options": {"env": {"PYTHONPATH": "${workspaceFolder}"}},
            }
        ],
    }

    with open(vscode_dir / "python_tasks.json", "w", encoding="utf-8") as f:
        import json

        json.dump(python_task, f, ensure_ascii=False, indent=4)

    print("√ 已创建Python运行配置文件: .vscode/python_tasks.json")

    # 添加Python的代码片段
    python_snippets = {
        "LeetCode Solutions Template": {
            "prefix": "lctemplate",
            "body": [
                "from typing import List, Optional",
                "",
                "class Solution:",
                "    def $1(self, $2):",
                "        $3",
                "",
                "# 测试",
                'if __name__ == "__main__":',
                "    sol = Solution()",
                "    $4",
                '    print("测试通过！")',
            ],
            "description": "LeetCode Python 解题模板",
        }
    }

    with open(vscode_dir / "python_snippets.json", "w", encoding="utf-8") as f:
        import json

        json.dump(python_snippets, f, ensure_ascii=False, indent=4)

    print("√ 已创建Python代码片段文件: .vscode/python_snippets.json")


def setup_vscode_settings():
    """配置VS Code环境设置"""
    print("\n正在配置VS Code设置...")

    vscode_dir = Path(".vscode")
    vscode_dir.mkdir(exist_ok=True)

    # 创建settings.json
    settings = {
        "editor.snippetSuggestions": "top",
        "editor.tabSize": 4,
        "editor.insertSpaces": True,
        "files.associations": {"*.cpp": "cpp", "*.py": "python"},
        "[cpp]": {"editor.defaultFormatter": "ms-vscode.cpptools"},
        "[python]": {"editor.defaultFormatter": "ms-python.python"},
        "leetcode.workspaceFolder": ".",
        "leetcode.defaultLanguage": "cpp, python3",
        "terminal.integrated.env.windows": {
            "PATH": "${env:PATH};${workspaceFolder}\\venv\\Scripts"
        },
        "terminal.integrated.env.linux": {
            "PATH": "${env:PATH}:${workspaceFolder}/venv/bin"
        },
        "terminal.integrated.env.osx": {
            "PATH": "${env:PATH}:${workspaceFolder}/venv/bin"
        },
        "python.defaultInterpreterPath": "${workspaceFolder}/venv/Scripts/python.exe",
        "python.terminal.activateEnvironment": true,
    }

    with open(vscode_dir / "settings.json", "w", encoding="utf-8") as f:
        import json

        json.dump(settings, f, ensure_ascii=False, indent=4)

    print("√ 已创建VS Code设置文件: .vscode/settings.json")

    # 创建统一的tasks.json
    tasks = {
        "version": "2.0.0",
        "tasks": [
            {
                "label": "C++: 编译并运行",
                "type": "shell",
                "command": "g++ -std=c++17 ${file} -o ${fileDirname}/${fileBasenameNoExtension}.exe && ${fileDirname}/${fileBasenameNoExtension}.exe",
                "group": "build",
                "presentation": {"reveal": "always", "panel": "new"},
                "problemMatcher": ["$gcc"],
            },
            {
                "label": "Python: 运行当前文件",
                "type": "shell",
                "command": "${workspaceFolder}\\venv\\Scripts\\python.exe ${file}",
                "group": "build",
                "presentation": {"reveal": "always", "panel": "new"},
                "problemMatcher": [],
                "options": {"env": {"PYTHONPATH": "${workspaceFolder}"}},
            },
            {
                "label": "LeetCode: 创建题目",
                "type": "shell",
                "command": "${workspaceFolder}\\venv\\Scripts\\python.exe Scripts/create_problem.py ${input:problemId} ${input:language}",
                "presentation": {"reveal": "always", "panel": "new"},
                "problemMatcher": [],
                "options": {"env": {"PYTHONPATH": "${workspaceFolder}"}},
            },
            {
                "label": "LeetCode: 获取每日一题",
                "type": "shell",
                "command": "${workspaceFolder}\\venv\\Scripts\\python.exe Scripts/daily_question.py ${input:language}",
                "presentation": {"reveal": "always", "panel": "new"},
                "problemMatcher": [],
                "options": {"env": {"PYTHONPATH": "${workspaceFolder}"}},
            },
            {
                "label": "LeetCode: 测试解决方案",
                "type": "shell",
                "command": "${workspaceFolder}\\venv\\Scripts\\python.exe Scripts/test_solution.py ${input:problemId} ${input:language}",
                "presentation": {"reveal": "always", "panel": "new"},
                "problemMatcher": [],
                "options": {"env": {"PYTHONPATH": "${workspaceFolder}"}},
            },
            {
                "label": "LeetCode: 提取提交代码",
                "type": "shell",
                "command": "${workspaceFolder}\\venv\\Scripts\\python.exe Scripts/test_solution.py ${input:problemId} ${input:language} --extract",
                "presentation": {"reveal": "always", "panel": "new"},
                "problemMatcher": [],
                "options": {"env": {"PYTHONPATH": "${workspaceFolder}"}},
            },
        ],
        "inputs": [
            {
                "id": "problemId",
                "description": "请输入题号",
                "default": "",
                "type": "promptString",
            },
            {
                "id": "language",
                "description": "请选择编程语言",
                "default": "all",
                "type": "pickString",
                "options": ["cpp", "py", "all"],
            },
        ],
    }

    with open(vscode_dir / "tasks.json", "w", encoding="utf-8") as f:
        import json

        json.dump(tasks, f, ensure_ascii=False, indent=4)

    print("√ 已创建VS Code任务文件: .vscode/tasks.json")


def main():
    """主函数"""
    print("==== LeetCode编程环境配置工具 ====\n")

    # 配置C++环境
    setup_cpp_environment()

    # 配置Python环境
    setup_python_environment()

    # 配置VS Code设置
    setup_vscode_settings()

    print("\n==== 环境配置完成 ====")
    print("现在您可以使用VS Code打开此文件夹并开始LeetCode刷题了！")
    print("提示: 按下Ctrl+Shift+P并输入'Tasks: Run Task'可以看到可用的任务")
    print("\n注意: README.md文件已存在，未进行修改。")


if __name__ == "__main__":
    main()
