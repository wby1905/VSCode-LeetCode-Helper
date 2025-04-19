#!/usr/bin/env python3
"""
LeetCode题目创建工具 - 根据题号自动创建题目目录和代码框架
用法: python create_problem.py 题号 [编程语言]
示例: python create_problem.py 100 cpp     # 创建第100题的C++解决方案
      python create_problem.py 100 all     # 创建第100题的所有语言解决方案
支持的语言: cpp, py, md, all
"""

import os
import sys
import json
import re
import html
from pathlib import Path

# 添加当前脚本所在目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from code_generators import CodeGeneratorFactory
from leetcode_api import LeetCodeAPI

# 语言映射
LANGUAGE_MAP = {
    "cpp": "cpp",
    "py": "python3",
}


def get_problem_info(problem_id):
    """从LeetCode获取题目信息"""
    try:
        # 使用API客户端获取题目信息
        api = LeetCodeAPI()
        problem_info = api.get_problem_by_id(problem_id)
        return problem_info
    except Exception as e:
        print(f"错误: {str(e)}")
        return None


def parse_test_cases(test_cases, meta_data):
    """解析测试用例"""
    print(f"\n[调试] 开始解析测试用例:")
    print(f"测试用例内容: {test_cases}")
    print(f"元数据类型: {type(meta_data)}")

    test_cases = test_cases.strip()
    if not test_cases:
        print("[调试] 警告: 测试用例为空")
        return []

    # 分割测试用例
    cases = test_cases.split("\n")
    print(f"[调试] 分割后的测试用例: {cases}")
    return cases


def create_directory_structure(problem_info, lang=None):
    """创建题目目录结构"""
    problem_id = problem_info["id"]
    difficulty = {"Easy": "Easy", "Medium": "Medium", "Hard": "Hard"}.get(
        problem_info["difficulty"], "Unknown"
    )

    # 如果没有标签，使用"其他"作为默认标签
    topics = problem_info["topics"] if problem_info["topics"] else ["其他"]

    # 选择主标签作为目录名
    main_topic = topics[0]

    # 创建主目录 - Tags/主标签/难度/题号
    base_dir = Path(f"Tags/{main_topic}/{difficulty}/{problem_id}")
    base_dir.mkdir(parents=True, exist_ok=True)

    # 清理HTML标签
    content = re.sub(r"<[^>]+>", "", problem_info["content"])
    content = html.unescape(content)  # 解码HTML实体

    # 尝试提取数据范围信息
    data_range = ""
    modified_content = content
    try:
        # 查找提示部分
        hints_match = re.search(r"提示[：:](.*?)(?=##|\Z)", content, re.DOTALL)
        if hints_match:
            data_range = hints_match.group(1).strip()
            # 从原始内容中移除提示部分，避免重复
            modified_content = re.sub(
                r"提示[：:].*?(?=##|\Z)", "", content, flags=re.DOTALL
            )
    except Exception as e:
        print(f"提取数据范围时出错: {str(e)}")

    # 创建README.md文件记录题目信息
    with open(base_dir / "README.md", "w", encoding="utf-8") as f:
        f.write(f"# {problem_id}. {problem_info['title']}\n\n")
        f.write(f"- 难度: {difficulty}\n")
        f.write(
            f"- 题目链接: https://leetcode.com/problems/{problem_info['title_slug']}/\n"
        )
        f.write(
            f"- 中文链接: https://leetcode.cn/problems/{problem_info['title_slug']}/\n\n"
        )
        f.write("## 标签\n\n")
        for topic in topics:
            f.write(f"- {topic}\n")
        f.write("\n## 题目描述\n\n")
        # 使用修改后的内容，不包含提示/数据范围部分
        f.write(modified_content.strip())

        # 添加数据范围部分
        f.write("\n\n## 数据范围\n\n")
        if data_range:
            f.write(data_range)
        else:
            f.write("暂无数据范围信息")

        # 添加测试用例
        if problem_info["test_cases"]:
            f.write("\n\n## 示例测试用例\n\n```\n")
            f.write(problem_info["test_cases"])
            f.write("\n```\n")

    # 获取代码片段和测试用例
    code_snippets = problem_info["code_snippets"]
    test_cases = problem_info["test_cases"]
    meta_data = problem_info["meta_data"]

    # 打印调试信息
    print(f"\n[调试] 创建解决方案文件前:")
    print(f"测试用例: {test_cases}")
    print(f"元数据类型: {type(meta_data)}")
    if meta_data:
        print(
            f"元数据内容: {json.dumps(meta_data, indent=2, ensure_ascii=False)[:200]}..."
        )

    # 复制并填充对应语言的模板
    languages = ["cpp", "py", "md"] if lang == "all" else [lang]
    template_dir = Path("Templates")

    for lang in languages:
        if lang == "md" and difficulty != "Hard":
            # 只为Hard题目创建md笔记
            continue

        template_file = {
            "cpp": template_dir / "cpp_template.cpp",
            "py": template_dir / "py_template.py",
            "md": template_dir / "md_template.md",
        }.get(lang)

        if not template_file or not template_file.exists():
            print(f"警告: 找不到{lang}的模板文件")
            continue

        output_file = base_dir / f"solution.{lang}"

        with open(template_file, "r", encoding="utf-8") as f:
            template = f.read()

        # 替换模板中的标记
        template = template.replace("{{problem_id}}", problem_id)
        template = template.replace("{{problem_title}}", problem_info["title"])
        template = template.replace("{{problem_slug}}", problem_info["title_slug"])
        template = template.replace("{{difficulty}}", difficulty)

        # 添加LeetCode提供的代码片段
        leetcode_lang = LANGUAGE_MAP.get(lang)
        if leetcode_lang and leetcode_lang in code_snippets:
            code_snippet = code_snippets[leetcode_lang]
            print(f"\n[调试] 处理{lang}语言的代码片段:")
            print(f"代码片段前几行: {code_snippet.split('\n')[:3]}")

            # 使用代码生成器工厂获取对应语言的代码生成器
            try:
                if lang in ["cpp", "py"]:
                    generator = CodeGeneratorFactory.get_generator(lang)
                    print(f"[调试] 使用代码生成器: {type(generator).__name__}")

                    # 替换Solution类
                    template = generator.replace_solution_class(template, code_snippet)

                    # 查找模板中的测试函数部分
                    test_function_patterns = {
                        "cpp": r"// 测试函数\nvoid test_solution\(\)[^{]*\{(?:(?!\n}$)[\s\S])*\n}",
                        "py": r"# 测试函数\ndef test_solution\(\):.+?(?=\n\n|\Z)",
                    }

                    pattern = test_function_patterns.get(lang)
                    if pattern:
                        # 生成测试代码
                        print(f"[调试] 为{lang}生成测试代码")
                        print(f"测试用例: {test_cases}")
                        print(
                            f"元数据: {json.dumps(meta_data, indent=2, ensure_ascii=False)[:200]}..."
                        )

                        # 修改: 将完整的题目描述内容传递给测试用例解析器
                        # 使用原始内容而不是修改后的内容，确保包含所有示例
                        test_code = generator.create_test_code(
                            test_cases, meta_data, code_snippet, content
                        )
                        print(
                            f"[调试] 生成的测试代码前几行: {test_code.split('\n')[:3]}"
                        )

                        # 替换模板中的测试函数部分
                        template = re.sub(pattern, test_code, template, flags=re.DOTALL)
            except Exception as e:
                print(f"警告: 生成测试代码时出错 ({lang}): {str(e)}")
                # 失败时使用原来的方式
                if lang == "cpp":
                    # 替换Solution类
                    if (
                        "class Solution" in template
                        and "class Solution" in code_snippet
                    ):
                        template = re.sub(
                            r"class Solution\s*{[^}]*}", code_snippet, template
                        )
                elif lang == "py":
                    # 替换Solution类
                    if (
                        "class Solution" in template
                        and "class Solution" in code_snippet
                    ):
                        template = re.sub(
                            r"class Solution:.*?pass",
                            code_snippet,
                            template,
                            flags=re.DOTALL,
                        )

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(template)

    print(f"题目 {problem_id} 的目录结构和文件已创建在: {base_dir}")
    print(f"题目标签: {', '.join(topics)}")

    # 返回创建的目录路径，方便后续操作
    return base_dir


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python create_problem.py 题号 [编程语言]")
        print("支持的语言: cpp, py, md, all")
        return

    problem_id = sys.argv[1]
    lang = sys.argv[2] if len(sys.argv) > 2 else "py"  # 默认为py，而不是all

    if lang not in ["cpp", "py", "md", "all"]:
        print(f"不支持的语言: {lang}")
        print("支持的语言: cpp, py, md, all")
        return

    print(f"正在获取题目 {problem_id} 的信息...")
    problem_info = get_problem_info(problem_id)

    if not problem_info:
        return

    print(f"题目信息获取成功: {problem_info['title']}")
    print(f"已获取LeetCode预设的代码模板和测试用例")

    # 创建目录结构和文件
    base_dir = create_directory_structure(problem_info, lang)

    # 提示用户可以开始解题
    print("\n您可以开始解题了！")

    # 根据生成的语言显示对应的提示
    if lang == "all" or lang == "cpp":
        print(f"- C++文件: {base_dir}/solution.cpp")
    if lang == "all" or lang == "py":
        print(f"- Python文件: {base_dir}/solution.py")
    if (lang == "all" or lang == "md") and problem_info["difficulty"] == "Hard":
        print(f"- 解题笔记: {base_dir}/solution.md")


if __name__ == "__main__":
    main()
