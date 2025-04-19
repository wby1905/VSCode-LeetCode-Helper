#!/usr/bin/env python3
"""
LeetCode代码测试和提交工具
用法:
    - 测试代码: python test_solution.py 题号 [语言]
    - 提取提交代码: python test_solution.py 题号 [语言] --extract
    - 提取代码并自动跳转: python test_solution.py 题号 [语言] --extract --open
示例:
    - python test_solution.py 100 cpp     # 测试第100题的C++解决方案
    - python test_solution.py 100 py --extract  # 提取第100题的Python解决方案用于提交
    - python test_solution.py 100 py --extract --open  # 提取代码并自动打开题目页面
支持的语言: cpp, py
"""

import os
import sys
import subprocess
import re
import webbrowser
from pathlib import Path


def find_solution_file(problem_id, lang):
    """查找题目的解决方案文件"""
    # 遍历Tags目录寻找对应题号的文件
    tags_dir = Path("Tags")

    for topic_dir in tags_dir.iterdir():
        if not topic_dir.is_dir():
            continue

        for difficulty_dir in topic_dir.iterdir():
            if not difficulty_dir.is_dir():
                continue

            problem_dir = difficulty_dir / problem_id
            if problem_dir.exists() and problem_dir.is_dir():
                solution_file = problem_dir / f"solution.{lang}"
                if solution_file.exists():
                    return solution_file

    return None


def get_problem_url(problem_id, solution_file):
    """获取题目的LeetCode链接

    首先尝试从README文件中提取链接，
    如果找不到，则根据题号生成标准链接
    """
    # 尝试从README中提取链接
    readme_file = solution_file.parent / "README.md"
    if readme_file.exists():
        try:
            with open(readme_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 先尝试提取中文链接
            cn_link_match = re.search(
                r"中文链接: (https://leetcode\.cn/problems/[\w-]+/)", content
            )
            if cn_link_match:
                return cn_link_match.group(1)

            # 再尝试提取英文链接
            link_match = re.search(
                r"题目链接: (https://leetcode\.com/problems/[\w-]+/)", content
            )
            if link_match:
                return link_match.group(1)
        except Exception as e:
            print(f"提取链接出错: {str(e)}")

    # 如果没有找到链接，生成默认链接
    # 优先使用中文链接
    return f"https://leetcode.cn/problems/{problem_id}/"


def test_solution(solution_file, lang):
    """测试解决方案"""
    if not solution_file.exists():
        print(f"错误: 找不到解决方案文件 {solution_file}")
        return False

    try:
        if lang == "cpp":
            # 编译并运行C++代码
            output_exe = solution_file.with_suffix(".exe")
            compile_cmd = f"g++ -std=c++17 {solution_file} -o {output_exe}"
            print(f"正在编译: {compile_cmd}")

            compile_process = subprocess.run(
                compile_cmd, shell=True, capture_output=True, text=True
            )

            if compile_process.returncode != 0:
                print("编译失败:")
                print(compile_process.stderr)
                return False

            print("编译成功，正在运行...")
            run_process = subprocess.run(
                str(output_exe), shell=True, capture_output=True, text=True
            )

            print("输出:")
            print(run_process.stdout)

            if run_process.stderr:
                print("错误:")
                print(run_process.stderr)

            return run_process.returncode == 0

        elif lang == "py":
            # 运行Python代码
            print(f"正在运行Python解决方案: {solution_file}")
            run_process = subprocess.run(
                f"python {solution_file}", shell=True, capture_output=True, text=True
            )

            print("输出:")
            print(run_process.stdout)

            if run_process.stderr:
                print("错误:")
                print(run_process.stderr)

            return run_process.returncode == 0

        else:
            print(f"不支持的语言: {lang}")
            return False

    except Exception as e:
        print(f"测试过程中出错: {str(e)}")
        return False


def extract_solution(solution_file, lang, problem_id, auto_open=False):
    """提取用于提交的解决方案代码"""
    if not solution_file.exists():
        print(f"错误: 找不到解决方案文件 {solution_file}")
        return

    try:
        with open(solution_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 根据不同语言提取Solution类
        if lang == "cpp":
            # 提取C++ Solution类
            match = re.search(r"class Solution\s*{.*?};", content, re.DOTALL)
            if match:
                solution = match.group(0)
                print("\n=== 用于提交的代码 ===\n")
                print(solution)

                # 保存到剪贴板
                try:
                    import pyperclip

                    pyperclip.copy(solution)
                    print("\n代码已复制到剪贴板")
                except ImportError:
                    print("\n提示: 安装pyperclip包可以自动复制代码到剪贴板")
                    print("运行命令: pip install pyperclip")

                # 获取题目链接
                problem_url = get_problem_url(problem_id, solution_file)

                if auto_open:
                    # 自动打开浏览器跳转到题目页面
                    print(f"\n正在自动打开浏览器，跳转到LeetCode题目页面...")
                    webbrowser.open(problem_url)
                else:
                    # 显示可点击的题目链接
                    print(f"\n【点击链接前往提交】: {problem_url}")
            else:
                print("错误: 无法提取Solution类")

        elif lang == "py":
            # 提取Python Solution类
            match = re.search(
                r"class Solution.*?(?=\n\n# 测试函数|$)", content, re.DOTALL
            )
            if match:
                solution = match.group(0)
                print("\n=== 用于提交的代码 ===\n")
                print(solution)

                # 保存到剪贴板
                try:
                    import pyperclip

                    pyperclip.copy(solution)
                    print("\n代码已复制到剪贴板")
                except ImportError:
                    print("\n提示: 安装pyperclip包可以自动复制代码到剪贴板")
                    print("运行命令: pip install pyperclip")

                # 获取题目链接
                problem_url = get_problem_url(problem_id, solution_file)

                if auto_open:
                    # 自动打开浏览器跳转到题目页面
                    print(f"\n正在自动打开浏览器，跳转到LeetCode题目页面...")
                    webbrowser.open(problem_url)
                else:
                    # 显示可点击的题目链接
                    print(f"\n【点击链接前往提交】: {problem_url}")
            else:
                print("错误: 无法提取Solution类")

        else:
            print(f"不支持的语言: {lang}")

    except Exception as e:
        print(f"提取过程中出错: {str(e)}")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python test_solution.py 题号 [语言] [--extract] [--open]")
        print("支持的语言: cpp, py")
        return

    problem_id = sys.argv[1]
    lang = sys.argv[2] if len(sys.argv) > 2 else "cpp"
    extract_mode = "--extract" in sys.argv
    auto_open = "--open" in sys.argv

    if lang not in ["cpp", "py"]:
        print(f"不支持的语言: {lang}")
        print("支持的语言: cpp, py")
        return

    # 查找解决方案文件
    solution_file = find_solution_file(problem_id, lang)

    if not solution_file:
        print(f"错误: 找不到题号 {problem_id} 的 {lang} 解决方案")
        return

    print(f"找到解决方案文件: {solution_file}")

    if extract_mode:
        # 提取用于提交的代码
        extract_solution(solution_file, lang, problem_id, auto_open)
    else:
        # 测试解决方案
        success = test_solution(solution_file, lang)

        if success:
            print("\n测试成功!")
            print("如果您希望提取用于提交的代码，请运行:")
            print(f"python test_solution.py {problem_id} {lang} --extract")
            print("若要提取代码并自动打开浏览器，请运行:")
            print(f"python test_solution.py {problem_id} {lang} --extract --open")
        else:
            print("\n测试失败，请检查代码并修复错误")


if __name__ == "__main__":
    main()
