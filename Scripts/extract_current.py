#!/usr/bin/env python3
"""
LeetCode提取代码辅助脚本
用于自动检测当前文件并提取提交代码

用法:
    python extract_current.py [--open]
"""

import os
import sys
import re
import subprocess
from pathlib import Path


def get_current_file():
    """获取当前VSCode打开文件的路径"""
    # 通过环境变量获取当前文件路径
    file_path = os.environ.get("VSCODE_FILE", "")

    if not file_path:
        print("错误: 无法获取当前文件信息")
        print("请确保通过VS Code任务运行此脚本")
        return None, None

    # 转换为Path对象
    path = Path(file_path)

    # 检查文件类型
    if path.suffix == ".py":
        lang = "py"
    elif path.suffix == ".cpp":
        lang = "cpp"
    else:
        print(f"不支持的文件类型: {path.suffix}")
        return None, None

    # 查找题号 - 通过分析文件路径
    # 预期路径如: Tags/标签/难度/题号/solution.py
    try:
        # 如果文件名是solution.py或solution.cpp
        if path.name.startswith("solution."):
            # 题号应该是父目录的名称
            problem_id = path.parent.name
            # 验证题号是否为数字
            if problem_id.isdigit():
                return problem_id, lang

        # 如果以上没找到，尝试从文件内容中查找题号
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            # 尝试查找"LeetCode - 数字"格式
            leetcode_match = re.search(r"LeetCode\s*[-–—]\s*(\d+)", content)
            if leetcode_match:
                return leetcode_match.group(1), lang
    except Exception as e:
        print(f"解析文件出错: {str(e)}")

    print("无法从当前文件确定题号，请手动指定")
    return None, None


def main():
    # 检查是否需要自动打开浏览器
    auto_open = "--open" in sys.argv

    # 获取当前文件信息
    problem_id, lang = get_current_file()

    if not problem_id or not lang:
        print("未能自动识别题号或语言类型")
        # 尝试让用户手动输入
        problem_id = input("请输入题号: ").strip()
        lang_input = input("请输入语言 (py/cpp): ").strip().lower()
        if lang_input in ["py", "cpp"]:
            lang = lang_input
        else:
            print(f"不支持的语言: {lang_input}")
            print("支持的语言: py, cpp")
            return

    # 调用test_solution.py提取代码
    cmd = [sys.executable, "Scripts/test_solution.py", problem_id, lang, "--extract"]

    if auto_open:
        cmd.append("--open")

    print(f"正在提取题号 {problem_id} 的 {lang} 解决方案...")

    # 执行命令
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"提取代码时出错: {str(e)}")
    except Exception as e:
        print(f"执行过程中出错: {str(e)}")


if __name__ == "__main__":
    main()
