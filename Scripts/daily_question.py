#!/usr/bin/env python3
"""
LeetCode每日一题获取工具
用法: python daily_question.py [语言]
示例: python daily_question.py cpp     # 创建今天每日一题的C++解决方案
      python daily_question.py all     # 创建今天每日一题的所有语言解决方案
支持的语言: cpp, py, md, all
"""

import os
import sys
import subprocess
from pathlib import Path

# 导入LeetCode API客户端
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from leetcode_api import LeetCodeAPI


def create_daily_question(lang="all"):
    """创建每日一题的解决方案"""
    print("正在获取LeetCode每日一题...")

    try:
        # 使用API客户端获取每日一题
        api = LeetCodeAPI()
        daily_question = api.get_daily_question()

        if not daily_question:
            print("无法获取每日一题，请检查网络连接或稍后再试")
            return

        question_id = daily_question["id"]
        title = daily_question["title"]
        difficulty = daily_question["difficulty"]

        print(f"今日每日一题:")
        print(f"题号: {question_id}")
        print(f"标题: {title}")
        print(f"难度: {difficulty}")

        # 调用create_problem.py创建题目目录和文件
        create_problem_script = Path("Scripts") / "create_problem.py"

        if not create_problem_script.exists():
            print(f"错误: 找不到创建题目的脚本 {create_problem_script}")
            return

        print(f"\n正在创建题目 {question_id} 的解决方案...")

        # 使用subprocess调用create_problem.py脚本
        cmd = [sys.executable, str(create_problem_script), question_id, lang]
        subprocess.run(cmd, check=True)

        print(f"您可以开始解题了！")

    except Exception as e:
        print(f"创建每日一题时出错: {str(e)}")


def main():
    """主函数"""
    # 默认使用py创建Python语言的解决方案
    lang = sys.argv[1] if len(sys.argv) > 1 else "py"

    if lang not in ["cpp", "py", "md", "all"]:
        print(f"不支持的语言: {lang}")
        print("支持的语言: cpp, py, md, all")
        return

    create_daily_question(lang)


if __name__ == "__main__":
    main()
