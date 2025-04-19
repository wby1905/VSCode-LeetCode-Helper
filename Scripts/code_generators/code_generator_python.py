#!/usr/bin/env python3
"""
LeetCode代码生成器 - Python 实现
"""

import re
import json
import sys
import os

# 导入测试用例解析器
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from .code_generator_base import CodeGenerator


class PythonCodeGenerator(CodeGenerator):
    """Python代码生成器"""

    def extract_method_name(self, code_snippet):
        """从Python代码片段中提取方法名"""
        match = re.search(r"def\s+(\w+)\s*\(", code_snippet)
        if match:
            return match.group(1)
        return "solution"  # 默认方法名

    def create_test_code(
        self, test_cases, meta_data, code_snippet, problem_content=None
    ):
        """创建Python测试代码"""
        if not meta_data or "params" not in meta_data:
            return ""

        # 检查params类型并正确处理
        params = meta_data.get("params", [])
        if isinstance(params, str):
            try:
                params = json.loads(params)
            except:
                params = []

        # 获取返回类型信息
        return_info = meta_data.get("return", {})
        return_type = return_info.get("type", "None")

        # 提取方法名
        method_name = self.extract_method_name(code_snippet)

        # 使用测试用例解析器解析测试用例，传入题目描述
        parsed_cases = self.parse_test_cases(test_cases, meta_data, problem_content)

        # 检查测试用例是否为空或不完整
        if not parsed_cases:
            # 尝试直接从代码块中提取测试用例，使用元数据中的参数信息
            code_block_pattern = r"```\n(.*?)\n```"
            code_block_match = re.search(code_block_pattern, test_cases, re.DOTALL)
            if code_block_match:
                code_block = code_block_match.group(1).strip()
                lines = [
                    line.strip() for line in code_block.split("\n") if line.strip()
                ]
                expected_param_count = len(params)

                # 按参数数量分组
                if len(lines) >= expected_param_count and expected_param_count > 0:
                    param_names = [
                        p.get("name", f"param{i}") for i, p in enumerate(params)
                    ]
                    new_cases = []

                    for i in range(0, len(lines), expected_param_count):
                        if i + expected_param_count <= len(lines):
                            case_params = []
                            for j in range(expected_param_count):
                                param_value = lines[i + j]
                                param_type = params[j].get("type", "")
                                param_name = param_names[j]
                                case_params.append(
                                    {
                                        "name": param_name,
                                        "type": param_type,
                                        "value": param_value,
                                    }
                                )

                            new_cases.append(
                                {
                                    "case_idx": len(new_cases),
                                    "params": case_params,
                                    "expected_output": "",
                                }
                            )

                    if new_cases:
                        parsed_cases = new_cases

        # 对解析出的测试用例进行验证
        parsed_cases = self._validate_test_cases(parsed_cases, meta_data)

        # 如果没有有效的测试用例，返回基本的测试代码框架
        if not parsed_cases:
            test_code = [
                "\n# 测试函数",
                "def test_solution():",
                "    sol = Solution()",
                "    # 请添加测试用例",
                '    print("所有测试用例通过！")',
                "",
            ]
            return "\n".join(test_code)

        # 创建辅助函数代码（如创建链表、二叉树等）
        helper_functions = self._create_helper_functions(params)

        # 生成测试代码语句
        test_statements = self.generate_test_statements(
            parsed_cases, params, method_name
        )

        # 组装完整的测试代码
        test_code = []

        # 添加辅助函数（如有必要）
        if helper_functions:
            test_code.extend(helper_functions)

        test_code.append("\n# 测试函数")
        test_code.append("def test_solution():")
        test_code.append("    sol = Solution()")

        # 处理特殊数据结构的测试用例
        needs_preprocessing = self._needs_data_structure_preprocessing(params)
        if needs_preprocessing:
            test_statements = self._preprocess_test_statements(test_statements, params)

        test_code.extend(test_statements)
        test_code.append('\n    print("所有测试用例通过！")')

        return "\n".join(test_code)

    def _validate_test_cases(self, parsed_cases, meta_data):
        """验证测试用例，移除无效的测试用例"""
        if not parsed_cases:
            return []

        valid_cases = []
        params_info = meta_data.get("params", [])

        for case in parsed_cases:
            valid = True
            case_params = case["params"]

            # 确保所有参数都有有效值
            for param in case_params:
                param_value = param["value"]
                if param_value == "None" or param_value == "null":
                    # 检查参数是否可以为None
                    param_name = param["name"]
                    param_info = next(
                        (p for p in params_info if p.get("name") == param_name), None
                    )
                    if param_info and not param_info.get("nullable", False):
                        valid = False
                        break

            if valid:
                valid_cases.append(case)

        return valid_cases

    def replace_solution_class(self, template, code_snippet):
        """替换Python模板中的Solution类"""
        if "class Solution" in template and "class Solution" in code_snippet:
            return re.sub(
                r"class Solution:.*?pass", code_snippet, template, flags=re.DOTALL
            )
        return template

    def generate_test_statements(self, parsed_cases, params, method_name):
        """为Python生成测试语句"""
        if not parsed_cases:
            return []

        statements = []

        for case in parsed_cases:
            case_idx = case["case_idx"]
            case_params = case["params"]
            expected_output = case["expected_output"]

            # 添加测试用例标题
            statements.append(f"\n    # 测试用例 {case_idx + 1}")

            # 检查所有参数是否有效
            valid_params = True
            for param in case_params:
                if param["value"] == "None" or param["value"] == "null":
                    valid_params = False
                    break

            if not valid_params:
                continue

            # 声明参数变量
            for param in case_params:
                param_name = param["name"]
                param_type = param["type"]
                param_value = param["value"]
                statements.append(f"    {param_name} = {param_value}")

            # 调用方法
            param_names = [p["name"] for p in case_params]
            statements.append(
                f"    result = sol.{method_name}({', '.join(param_names)})"
            )
            statements.append(f'    print(f"测试用例 {case_idx + 1}:")')
            for param in case_params:
                # 修复字符串格式化问题，确保正确处理花括号
                statements.append(
                    f'    print(f"输入: {param["name"]}={{{param["name"]}}}")'
                )

            # 添加注释格式的期望输出值，不是针对特定题目硬编码
            if expected_output:
                statements.append(f"    # 输出：{expected_output}")
            else:
                statements.append(f"    # 输出：无")

            # 改进输出方式，处理列表格式问题
            statements.append(
                f"    # 处理结果格式，移除列表中逗号后的空格以匹配期望格式"
            )
            statements.append(f"    result_str = str(result).replace(', ', ',')")
            statements.append(f'    print(f"输出: {{result_str}}")')

            # 根据是否有期望输出决定是否显示验证信息
            if expected_output:
                statements.append('    print("期望: ' + expected_output + '")')
                # 修改比较逻辑，使用格式化后的结果字符串进行比较
                statements.append(
                    f'    print("通过!" if result_str == \'{expected_output}\' else "失败!")'
                )
            else:
                statements.append('    print("无期望值，请手动验证输出是否正确")')

        # 添加真实的测试验证代码
        statements.append("\n    # 验证所有测试用例是否真的通过")
        statements.append("    all_cases_passed = True")

        for case_idx, case in enumerate(parsed_cases):
            if case.get("expected_output"):
                case_params = case["params"]
                param_names = [p["name"] for p in case_params]
                param_values = [p["value"] for p in case_params]
                expected_output = case["expected_output"]

                # 添加实际验证逻辑
                statements.append(f"\n    # 验证测试用例 {case_idx + 1}")
                statements.append(
                    f"    test_result = sol.{method_name}({', '.join(param_values)})"
                )
                statements.append(
                    f"    test_result_str = str(test_result).replace(', ', ',')"
                )
                statements.append(f"    if test_result_str != '{expected_output}':")
                statements.append(f"        all_cases_passed = False")

        statements.append(
            '\n    print("所有测试用例" + ("通过！" if all_cases_passed else "未通过，请检查算法实现！"))'
        )
        statements.append("    return all_cases_passed")

        return statements

    def _create_helper_functions(self, params):
        """创建辅助函数，如链表构建、二叉树构建等"""
        helper_functions = []
        needs_listnode = any(p.get("type") == "ListNode" for p in params)
        needs_treenode = any(p.get("type") == "TreeNode" for p in params)

        if needs_listnode:
            # 添加链表相关辅助函数
            helper_functions.extend(
                [
                    "\n# Definition for singly-linked list.",
                    "class ListNode:",
                    "    def __init__(self, val=0, next=None):",
                    "        self.val = val",
                    "        self.next = next",
                    "",
                    "def create_linked_list(values):",
                    "    if not values:",
                    "        return None",
                    "    head = ListNode(values[0])",
                    "    current = head",
                    "    for val in values[1:]:",
                    "        current.next = ListNode(val)",
                    "        current = current.next",
                    "    return head",
                    "",
                    "def linked_list_to_string(head):",
                    "    if not head:",
                    '        return "[]"',
                    "    result = []",
                    "    while head:",
                    "        result.append(str(head.val))",
                    "        head = head.next",
                    '    return "[" + ",".join(result) + "]"',
                    "",
                ]
            )

        if needs_treenode:
            # 添加二叉树相关辅助函数
            helper_functions.extend(
                [
                    "\n# Definition for a binary tree node.",
                    "class TreeNode:",
                    "    def __init__(self, val=0, left=None, right=None):",
                    "        self.val = val",
                    "        self.left = left",
                    "        self.right = right",
                    "",
                    "def create_binary_tree(values):",
                    "    if not values or values[0] is None:",
                    "        return None",
                    "    root = TreeNode(values[0])",
                    "    queue = [root]",
                    "    i = 1",
                    "    while queue and i < len(values):",
                    "        node = queue.pop(0)",
                    "        if i < len(values) and values[i] is not None:",
                    "            node.left = TreeNode(values[i])",
                    "            queue.append(node.left)",
                    "        i += 1",
                    "        if i < len(values) and values[i] is not None:",
                    "            node.right = TreeNode(values[i])",
                    "            queue.append(node.right)",
                    "        i += 1",
                    "    return root",
                    "",
                    "def binary_tree_to_string(root):",
                    "    if not root:",
                    '        return "[]"',
                    "    result = []",
                    "    queue = [root]",
                    "    while any(queue):",
                    "        node = queue.pop(0)",
                    "        if node:",
                    "            result.append(str(node.val))",
                    "            queue.append(node.left)",
                    "            queue.append(node.right)",
                    "        else:",
                    '            result.append("null")',
                    '    while result[-1] == "null":',
                    "        result.pop()",
                    '    return "[" + ",".join(result) + "]"',
                    "",
                ]
            )

        return helper_functions

    def _needs_data_structure_preprocessing(self, params):
        """检查是否需要对特殊数据结构进行预处理"""
        for param in params:
            param_type = param.get("type", "")
            if param_type in ["ListNode", "TreeNode"]:
                return True
        return False

    def _preprocess_test_statements(self, statements, params):
        """为特殊数据结构类型处理测试语句"""
        processed = []
        param_types = {
            p.get("name", f"param{i+1}"): p.get("type", "")
            for i, p in enumerate(params)
        }

        # 扫描语句，找到参数声明并替换为构造函数调用
        i = 0
        while i < len(statements):
            line = statements[i]

            # 检查是否是参数声明行
            param_assign_match = re.match(r"\s+(\w+)\s*=\s*(.+)$", line)
            if param_assign_match:
                param_name = param_assign_match.group(1)
                param_value = param_assign_match.group(2)

                # 根据参数类型进行特殊处理
                if param_name in param_types:
                    param_type = param_types[param_name]

                    if param_type == "ListNode":
                        # 替换为链表创建函数调用
                        processed.append(f"    {param_name}_values = {param_value}")
                        processed.append(
                            f"    {param_name} = create_linked_list({param_name}_values)"
                        )
                    elif param_type == "TreeNode":
                        # 替换为二叉树创建函数调用
                        processed.append(f"    {param_name}_values = {param_value}")
                        processed.append(
                            f"    {param_name} = create_binary_tree({param_name}_values)"
                        )
                    else:
                        # 其他类型保持不变
                        processed.append(line)
                else:
                    processed.append(line)
            else:
                # 对于方法调用后结果显示进行调整
                result_print_match = re.match(r'\s+print\(f"输出: \{result\}"\)', line)
                if result_print_match and any(
                    p.get("type") in ["ListNode", "TreeNode"] for p in params
                ):
                    # 如果返回类型也可能是特殊数据结构，添加适当的转换
                    result_type = params[0].get("type") if params else ""
                    if result_type == "ListNode":
                        processed.append(
                            '    result_str = linked_list_to_string(result) if result else "[]"'
                        )
                        processed.append('    print(f"输出: {result_str}")')
                    elif result_type == "TreeNode":
                        processed.append(
                            '    result_str = binary_tree_to_string(result) if result else "[]"'
                        )
                        processed.append('    print(f"输出: {result_str}")')
                    else:
                        processed.append(line)
                else:
                    processed.append(line)

            i += 1

        return processed
