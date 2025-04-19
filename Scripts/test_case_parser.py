#!/usr/bin/env python3
"""
LeetCode测试用例解析器 - 解析测试用例基础功能
"""

import re
import json
from typing import List, Dict, Any, Tuple, Optional


class TestCaseParser:
    """测试用例解析器 - 提供通用的测试用例解析功能"""

    @staticmethod
    def parse_test_cases(
        test_cases: str, meta_data: Dict[str, Any], problem_content: str = None
    ) -> List[Dict[str, Any]]:
        """解析LeetCode测试用例字符串为格式化的用例列表

        参数:
            test_cases: LeetCode提供的测试用例字符串
            meta_data: 题目元数据，包含参数和返回类型信息
            problem_content: 可选，题目的完整描述内容，用于提取期望输出

        返回:
            解析后的测试用例列表，每个用例是一个字典，包含输入参数和期望输出
        """
        print("\n[调试] ===== 开始解析测试用例 =====")
        print(f"[调试] 测试用例原始字符串: {test_cases}")
        print(f"[调试] 元数据类型: {type(meta_data)}")
        print(f"[调试] 是否提供题目描述: {problem_content is not None}")

        if isinstance(meta_data, dict) and "params" in meta_data:
            params_info = meta_data.get("params", [])
            print(
                f"[调试] 参数信息: {json.dumps(params_info, indent=2, ensure_ascii=False)}"
            )
            print(f"[调试] 参数数量: {len(params_info)}")
            for i, param in enumerate(params_info):
                print(
                    f"[调试] 参数 {i+1}: 名称={param.get('name', f'param{i+1}')} 类型={param.get('type', '未知')}"
                )

        if not test_cases or not meta_data:
            print("[调试] 测试用例或元数据为空，返回空列表")
            return []

        # 获取参数数量
        params_info = meta_data.get("params", [])
        expected_param_count = len(params_info)
        print(f"[调试] 从元数据获取的参数数量: {expected_param_count}")

        # 使用完整题目描述（如果提供）或者测试用例字符串来尝试提取示例
        content_for_extraction = problem_content if problem_content else test_cases

        # 尝试从README中提取测试用例
        readme_cases = TestCaseParser._extract_cases_from_readme(
            content_for_extraction, meta_data
        )
        if readme_cases:
            print(f"[调试] 从题目描述中提取到 {len(readme_cases)} 个测试用例")

            # 解析从README提取的测试用例
            parsed_cases = []
            for case_idx, case in enumerate(readme_cases):
                inputs = case.get("inputs", [])
                output = case.get("output", "")

                if len(inputs) != expected_param_count:
                    print(f"[调试] 测试用例 {case_idx+1} 参数数量不匹配，跳过")
                    continue

                processed_params = []
                for i, (input_val, param_info) in enumerate(zip(inputs, params_info)):
                    param_type = param_info.get("type", "")
                    param_name = param_info.get("name", f"param{i+1}")
                    processed_value = TestCaseParser._process_param_value(
                        input_val, param_type
                    )
                    processed_params.append(
                        {
                            "name": param_name,
                            "type": param_type,
                            "value": processed_value,
                        }
                    )

                parsed_cases.append(
                    {
                        "case_idx": case_idx,
                        "params": processed_params,
                        "expected_output": output,
                    }
                )

            if parsed_cases:
                print(f"[调试] 成功解析 {len(parsed_cases)} 个题目描述中的测试用例")
                return parsed_cases

        # 分割测试用例为单独的用例
        cases = TestCaseParser._split_test_cases(test_cases, expected_param_count)
        print(f"[调试] 分割后的测试用例数量: {len(cases)}")
        for i, case in enumerate(cases):
            print(f"[调试] 测试用例 {i+1}: {case}")

        # 预处理参数信息
        params_info = meta_data.get("params", [])
        if isinstance(params_info, str):
            try:
                params_info = json.loads(params_info)
                print(f"[调试] 解析params_info字符串: {params_info}")
            except Exception as e:
                print(f"[调试] 解析params_info字符串失败: {str(e)}")
                params_info = []

        # 解析每个测试用例
        parsed_cases = []
        for case_idx, case in enumerate(cases):
            print(f"\n[调试] 开始解析测试用例 {case_idx+1}: {case}")
            try:
                # 分割为参数列表
                param_values = TestCaseParser._parse_params_from_case(
                    case, len(params_info)
                )
                print(f"[调试] 解析后的参数值: {param_values}")

                # 检查参数数量是否匹配
                if len(param_values) != len(params_info) and len(param_values) > 0:
                    print(
                        f"[调试] 参数数量不匹配: 解析到 {len(param_values)}，期望 {len(params_info)}，尝试修复"
                    )
                    # 尝试修复测试用例
                    param_values = TestCaseParser._fix_param_count(
                        param_values, len(params_info)
                    )
                    print(f"[调试] 修复后的参数值: {param_values}")

                # 如果仍然不匹配，跳过此用例
                if len(param_values) != len(params_info):
                    print(f"[调试] 参数数量仍不匹配，跳过此用例")
                    continue

                # 处理特殊类型的参数（如链表、二叉树等）
                processed_params = []
                for i, (param, param_info) in enumerate(zip(param_values, params_info)):
                    param_type = param_info.get("type", "")
                    param_name = param_info.get("name", f"param{i+1}")
                    print(
                        f"[调试] 处理参数 {param_name}，类型 {param_type}，原始值 {param}"
                    )
                    processed_value = TestCaseParser._process_param_value(
                        param, param_type
                    )
                    print(f"[调试] 处理后的参数值: {processed_value}")
                    processed_params.append(
                        {
                            "name": param_name,
                            "type": param_type,
                            "value": processed_value,
                        }
                    )

                # 提取期望输出（如果可用）
                # 使用题目描述内容（如果提供）或测试用例字符串
                content_for_output = content_for_extraction
                expected_output = TestCaseParser._extract_expected_output(
                    case, case_idx, content_for_output
                )
                print(f"[调试] 提取的期望输出: {expected_output}")

                parsed_cases.append(
                    {
                        "case_idx": case_idx,
                        "params": processed_params,
                        "expected_output": expected_output,
                    }
                )
                print(f"[调试] 测试用例 {case_idx+1} 解析完成")
            except Exception as e:
                print(f"[调试] 解析测试用例 {case_idx+1} 时出错: {str(e)}")
                continue

        print(
            f"[调试] ===== 测试用例解析完成，共解析 {len(parsed_cases)} 个用例 =====\n"
        )
        return parsed_cases

    @staticmethod
    def _extract_cases_from_readme(
        test_cases: str, meta_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """尝试从README格式的文本中提取示例测试用例"""
        cases = []
        params_info = meta_data.get("params", [])
        expected_param_count = len(params_info)

        if expected_param_count == 0:
            return []

        # 先检查测试用例是否来自示例测试用例代码块
        code_block_match = re.search(r"```\n(.*?)\n```", test_cases, re.DOTALL)
        if code_block_match:
            code_content = code_block_match.group(1).strip()
            lines = [line.strip() for line in code_content.split("\n") if line.strip()]

            # 使用元数据中的参数数量来分组行
            if len(lines) >= expected_param_count:
                for i in range(0, len(lines), expected_param_count):
                    if i + expected_param_count <= len(lines):
                        # 提取对应类型的参数
                        inputs = lines[i : i + expected_param_count]
                        cases.append(
                            {"inputs": inputs, "output": ""}  # 代码块中通常没有输出
                        )

                if cases:
                    return cases

        # 如果代码块解析失败，尝试从示例部分提取
        example_matches = re.finditer(r"示例\s*\d+\s*[:：]", test_cases, re.IGNORECASE)
        for match in example_matches:
            start_pos = match.end()
            # 查找下一个示例或文档结束
            next_match = re.search(
                r"示例\s*\d+\s*[:：]|## ", test_cases[start_pos:], re.IGNORECASE
            )
            end_pos = start_pos + next_match.start() if next_match else len(test_cases)

            example_text = test_cases[start_pos:end_pos].strip()

            # 提取输入和输出
            inputs_match = re.search(
                r"输入[:：](.*?)输出[:：]", example_text, re.DOTALL
            )
            if inputs_match:
                inputs_text = inputs_match.group(1).strip()
                output_text = example_text[inputs_match.end() :].strip()

                # 解析输入参数
                input_lines = [
                    line.strip() for line in inputs_text.split("\n") if line.strip()
                ]
                inputs = []
                for line in input_lines:
                    if line.startswith("nums =") or line.startswith("["):
                        # 数组参数
                        array_match = re.search(r"\[(.*?)\]", line)
                        if array_match:
                            array_str = "[" + array_match.group(1) + "]"
                            inputs.append(array_str)
                    elif re.match(r"(lower|upper)\s*=\s*\d+", line):
                        # 整数参数
                        num_match = re.search(r"\d+", line)
                        if num_match:
                            inputs.append(num_match.group(0))

                # 提取输出值
                output = ""
                output_match = re.search(r"\d+", output_text)
                if output_match:
                    output = output_match.group(0)

                if inputs and len(inputs) >= 2:  # 确保至少有两个参数
                    cases.append({"inputs": inputs, "output": output})

        # 如果找不到示例部分，尝试从代码块中提取
        if not cases:
            code_blocks = re.findall(r"```(.*?)```", test_cases, re.DOTALL)
            for block in code_blocks:
                lines = [line.strip() for line in block.split("\n") if line.strip()]
                if len(lines) >= 3:  # 至少需要3行: nums, lower, upper
                    try:
                        # 假设每行是一个参数
                        cases.append(
                            {"inputs": lines, "output": ""}  # 代码块中通常没有输出
                        )
                    except:
                        continue

        return cases

    @staticmethod
    def _split_test_cases(test_cases: str, expected_param_count: int) -> List[str]:
        """将测试用例字符串分割为单独的用例"""
        print(
            f"[调试] _split_test_cases: 开始分割测试用例，期望参数数量: {expected_param_count}"
        )
        test_cases = test_cases.strip()
        if not test_cases:
            print("[调试] 测试用例为空")
            return []

        # 移除注释和多余空白
        test_cases = re.sub(r"//.*", "", test_cases)
        test_cases = re.sub(r"/\*.*?\*/", "", test_cases, flags=re.DOTALL)
        print(f"[调试] 清理后的测试用例: {test_cases}")

        # 尝试找出是否在代码块中，这通常表示有结构化的测试用例
        lines = [line.strip() for line in test_cases.split("\n") if line.strip()]
        print(f"[调试] 按行分割后: {lines}")

        # 如果行数大于参数数量且能被参数数量整除，按参数数量分组
        if len(lines) >= expected_param_count and expected_param_count > 0:
            grouped_cases = TestCaseParser._group_lines_by_param_count(
                lines, expected_param_count
            )
            if grouped_cases:
                print(f"[调试] 分组后得到 {len(grouped_cases)} 个测试用例")
                for i, case in enumerate(grouped_cases):
                    print(f"[调试] 分组后的测试用例 {i+1}: {case}")
                return grouped_cases

        # 检查是否每行都是一个完整的测试参数
        valid_cases = True
        for line in lines:
            # 一个基本的启发式检查：如果行以有效的JSON形式开始(数组或对象)，则认为它是一个完整用例
            is_valid = (
                line.startswith("[")
                or line.startswith("{")
                or re.match(r'^".*"$', line)
                or re.match(r"^-?\d+$", line)
            )
            if not is_valid:
                valid_cases = False
                print(f"[调试] 行 '{line}' 不是有效的参数格式")
                break

        if valid_cases and lines:
            print("[调试] 使用按行分割的结果，但可能需要手动分组")
            return lines

        # 尝试将整个字符串作为一个JSON数组解析
        try:
            # 尝试将测试用例解析为JSON数组
            if test_cases.startswith("[") and test_cases.endswith("]"):
                print("[调试] 尝试解析整个字符串为JSON数组")
                parsed_cases = json.loads(test_cases)
                if isinstance(parsed_cases, list):
                    # 将每个元素转换回字符串形式
                    cases = [json.dumps(case) for case in parsed_cases]
                    print(f"[调试] JSON解析成功，得到 {len(cases)} 个用例")
                    return cases
        except Exception as e:
            print(f"[调试] JSON解析失败: {str(e)}")

        # 最后的手段：尝试简单地按空行分割
        if not cases:
            print("[调试] 尝试按空行分割")
            cases = re.split(r"\n\s*\n", test_cases)
            cases = [case.strip() for case in cases if case.strip()]
            print(f"[调试] 按空行分割得到 {len(cases)} 个用例")

        # 分析多行测试用例的特殊情况
        # 例如：第一行是数组，接下来几行是数字，这可能是一组测试用例
        if len(lines) > 1 and not cases:
            print("[调试] 尝试识别多行测试用例模式")
            # 这里添加针对多行测试用例的特殊处理
            # ...

        return cases

    @staticmethod
    def _group_lines_by_param_count(lines: List[str], param_count: int) -> List[str]:
        """将行按照每组param_count个参数分组"""
        if not lines or param_count <= 0:
            return []

        grouped_cases = []
        for i in range(0, len(lines), param_count):
            if i + param_count <= len(lines):
                # 获取一组参数
                case_lines = lines[i : i + param_count]
                # 将多行参数组合成一个测试用例字符串
                case_str = "\n".join(case_lines)
                grouped_cases.append(case_str)

        return grouped_cases

    @staticmethod
    def _parse_params_from_case(case: str, expected_param_count: int) -> List[str]:
        """从测试用例字符串中解析参数值"""
        print(
            f"[调试] _parse_params_from_case: 解析参数，期望参数数量: {expected_param_count}"
        )
        # 移除前后的空白
        case = case.strip()

        # 如果用例是一个JSON数组，直接拆分
        if case.startswith("[") and case.endswith("]"):
            try:
                # 尝试作为JSON解析
                print(f"[调试] 尝试解析JSON数组: {case}")
                params = json.loads(case)
                if isinstance(params, list):
                    # 将参数格式化为字符串
                    formatted = [TestCaseParser._format_param(p) for p in params]
                    print(f"[调试] JSON数组解析结果: {formatted}")
                    # 特殊情况：如果这是一个单独的数组参数，而不是包含多个参数的列表
                    if expected_param_count == 1:
                        print("[调试] 期望1个参数，可能整个数组就是一个参数")
                        return [case]
                    return formatted
            except Exception as e:
                print(f"[调试] JSON解析失败: {str(e)}")
                # 如果JSON解析失败，尝试其他方法
                pass

        # 尝试拆分为多行
        lines = [line.strip() for line in case.split("\n") if line.strip()]
        if len(lines) == expected_param_count:
            print(f"[调试] 按行分割得到与期望参数数量相同的行数: {lines}")
            # 每行是一个参数
            return [line for line in lines]

        # 尝试按逗号分割
        comma_split = [part.strip() for part in case.split(",")]
        if len(comma_split) == expected_param_count:
            print(f"[调试] 按逗号分割得到与期望参数数量相同的部分: {comma_split}")
            return comma_split

        # 可能是单个参数
        if expected_param_count == 1:
            print(f"[调试] 期望只有一个参数，直接返回整个字符串: {case}")
            return [case]

        # 尝试更复杂的解析：识别数组、字符串和基本类型
        print("[调试] 尝试更复杂的解析方法")
        params = []
        current_param = ""
        bracket_count = 0

        for char in case:
            if char == "[":
                bracket_count += 1
                current_param += char
            elif char == "]":
                bracket_count -= 1
                current_param += char
                if bracket_count == 0 and current_param.strip():
                    params.append(current_param.strip())
                    current_param = ""
            elif char == "," and bracket_count == 0:
                if current_param.strip():
                    params.append(current_param.strip())
                current_param = ""
            else:
                current_param += char

        # 添加最后一个参数（如果有）
        if current_param.strip():
            params.append(current_param.strip())

        print(f"[调试] 复杂解析结果: {params}")
        return params

    @staticmethod
    def _fix_param_count(params: List[str], expected_count: int) -> List[str]:
        """修复参数数量不匹配的问题"""
        print(
            f"[调试] _fix_param_count: 修复参数数量，当前 {len(params)}，期望 {expected_count}"
        )
        if len(params) < expected_count:
            # 参数数量不足，补充空值
            result = params + ["null"] * (expected_count - len(params))
            print(f"[调试] 添加空值后: {result}")
            return result
        elif len(params) > expected_count:
            # 参数数量过多，减少到预期数量
            result = params[:expected_count]
            print(f"[调试] 截断后: {result}")
            return result
        return params

    @staticmethod
    def _process_param_value(value_str: str, param_type: str) -> str:
        """处理参数值，根据参数类型进行特殊处理"""
        print(
            f"[调试] _process_param_value: 处理参数值 '{value_str}'，类型 '{param_type}'"
        )
        value_str = value_str.strip()

        # 处理空值和null
        if value_str.lower() in ("null", "none", ""):
            null_value = "null" if param_type in ("ListNode", "TreeNode") else "None"
            print(f"[调试] 空值处理为: {null_value}")
            return null_value

        # 特殊类型处理
        if param_type == "ListNode":
            # 将链表表示转换为数组
            if value_str.startswith("[") and value_str.endswith("]"):
                print(f"[调试] ListNode参数已经是数组形式: {value_str}")
                return value_str  # 已经是数组形式

            # 尝试从链表字符串中提取值，如 1->2->3
            match = re.findall(r"(\d+)", value_str)
            if match:
                result = f"[{','.join(match)}]"
                print(f"[调试] 从链表字符串提取数字: {result}")
                return result

            print("[调试] 无法解析链表，返回空数组")
            return "[]"  # 默认空链表

        elif param_type == "TreeNode":
            # 将树表示转换为数组
            if value_str.startswith("[") and value_str.endswith("]"):
                # 已经是层次遍历数组形式，确保null是小写的，适合Python
                value_str = value_str.replace("NULL", "null").replace("Null", "null")
                print(f"[调试] TreeNode参数已经是数组形式: {value_str}")
                return value_str

            # 尝试从树的字符串表示中提取值
            # 这里需要更复杂的解析逻辑，可以根据具体情况扩展
            print("[调试] 无法解析树，返回空数组")
            return "[]"  # 默认空树

        elif param_type.endswith("[]") or param_type.endswith("[][]"):
            # 处理数组类型
            print(f"[调试] 处理数组类型参数 '{value_str}'")
            # 确保数组参数是正确的JSON数组格式
            if value_str.startswith("[") and value_str.endswith("]"):
                print(f"[调试] 数组参数保持原样: {value_str}")
                return value_str
            else:
                try:
                    # 尝试将其解析为有效的JSON
                    json_value = json.loads(value_str)
                    if isinstance(json_value, list):
                        result = json.dumps(json_value)
                        print(f"[调试] 将字符串解析为JSON数组: {result}")
                        return result
                except:
                    # 如果不是有效的JSON，则进行简单处理
                    print(f"[调试] 无法将 '{value_str}' 解析为数组，尝试简单处理")
                    # 这里可以添加其他处理逻辑
                    # ...

            # 如果都失败了，尝试从字符串中提取数字作为数组
            nums = re.findall(r"-?\d+", value_str)
            if nums:
                result = f"[{','.join(nums)}]"
                print(f"[调试] 从字符串提取数字作为数组: {result}")
                return result

            print(f"[调试] 无法处理数组参数 '{value_str}'，保持原样")

        # 对于其他类型，尝试保持原样
        print(f"[调试] 保持参数值原样: {value_str}")
        return value_str

    @staticmethod
    def _extract_expected_output(case: str, case_idx: int, full_test_cases: str) -> str:
        """尝试从测试用例中提取期望输出值"""
        print(
            f"[调试] _extract_expected_output: 尝试提取期望输出值，测试用例索引 {case_idx}"
        )

        # 尝试从测试用例中查找 -> 标记后的输出
        arrow_match = re.search(r"->\s*(\S.*?)(?:\s*$|\s*//)", case)
        if arrow_match:
            result = arrow_match.group(1).strip()
            print(f"[调试] 从箭头表示法提取期望输出: {result}")
            return result

        # 检查README/题目描述中的示例部分
        # 尝试找出第case_idx+1个示例
        example_pattern = f"示例\\s*{case_idx + 1}\\s*[:：](.*?)(?:示例\\s*\\d+|$)"
        example_match = re.search(example_pattern, full_test_cases, re.DOTALL)

        if example_match:
            example_text = example_match.group(1).strip()
            print(f"[调试] 找到匹配示例 {case_idx + 1}: {example_text[:100]}...")

            # 在示例中查找输出部分 - 支持多种类型的输出格式
            # 数组类型输出 例如: [1,2,3]
            output_array_match = re.search(
                r"输出[:：]\s*(\[.*?\])", example_text, re.DOTALL
            )
            if output_array_match:
                output_val = output_array_match.group(1).strip()
                print(f"[调试] 从示例 {case_idx + 1} 提取数组期望输出: {output_val}")
                return output_val

            # 字符串类型输出 例如: "abc"
            output_string_match = re.search(r'输出[:：]\s*"(.*?)"', example_text)
            if output_string_match:
                output_val = f'"{output_string_match.group(1)}"'
                print(f"[调试] 从示例 {case_idx + 1} 提取字符串期望输出: {output_val}")
                return output_val

            # 布尔值类型输出 例如: true 或 false
            output_bool_match = re.search(
                r"输出[:：]\s*(true|false)", example_text, re.IGNORECASE
            )
            if output_bool_match:
                output_val = output_bool_match.group(1).lower()
                print(f"[调试] 从示例 {case_idx + 1} 提取布尔值期望输出: {output_val}")
                return output_val

            # 数字类型输出 例如: 5
            output_number_match = re.search(
                r"输出[:：]\s*(-?\d+(?:\.\d+)?)", example_text
            )
            if output_number_match:
                output_val = output_number_match.group(1)
                print(f"[调试] 从示例 {case_idx + 1} 提取数字期望输出: {output_val}")
                return output_val

        # 尝试按顺序查找所有示例中的输出，如果示例数量和测试用例索引匹配
        # 首先尝试提取数组
        all_array_outputs = re.findall(
            r"输出[:：]\s*(\[.*?\])", full_test_cases, re.DOTALL
        )
        if all_array_outputs and case_idx < len(all_array_outputs):
            output_val = all_array_outputs[case_idx]
            print(
                f"[调试] 按顺序从所有示例中提取第 {case_idx + 1} 个数组输出: {output_val}"
            )
            return output_val

        # 尝试提取字符串
        all_string_outputs = re.findall(r'输出[:：]\s*"(.*?)"', full_test_cases)
        if all_string_outputs and case_idx < len(all_string_outputs):
            output_val = f'"{all_string_outputs[case_idx]}"'
            print(
                f"[调试] 按顺序从所有示例中提取第 {case_idx + 1} 个字符串输出: {output_val}"
            )
            return output_val

        # 尝试提取布尔值
        all_bool_outputs = re.findall(
            r"输出[:：]\s*(true|false)", full_test_cases, re.IGNORECASE
        )
        if all_bool_outputs and case_idx < len(all_bool_outputs):
            output_val = all_bool_outputs[case_idx].lower()
            print(
                f"[调试] 按顺序从所有示例中提取第 {case_idx + 1} 个布尔值输出: {output_val}"
            )
            return output_val

        # 最后尝试提取数字
        all_number_outputs = re.findall(
            r"输出[:：]\s*(-?\d+(?:\.\d+)?)", full_test_cases
        )
        if all_number_outputs and case_idx < len(all_number_outputs):
            output_val = all_number_outputs[case_idx]
            print(
                f"[调试] 按顺序从所有示例中提取第 {case_idx + 1} 个数字输出: {output_val}"
            )
            return output_val

        # 通用提取方法 - 尝试提取输出后的任何非空字符串
        general_output_matches = re.finditer(
            r"输出[:：]\s*(.*?)(?:\n|$)", full_test_cases
        )
        outputs = []
        for match in general_output_matches:
            output_text = match.group(1).strip()
            if output_text:
                outputs.append(output_text)

        if outputs and case_idx < len(outputs):
            output_val = outputs[case_idx]
            print(f"[调试] 通用方法提取第 {case_idx + 1} 个输出: {output_val}")
            return output_val

        # 没有找到期望输出
        print("[调试] 无法提取期望输出")
        return ""

    @staticmethod
    def _format_param(param: Any) -> str:
        """将参数格式化为字符串表示"""
        print(f"[调试] _format_param: 格式化参数 {type(param).__name__}: {param}")
        if isinstance(param, (list, dict)):
            result = json.dumps(param, ensure_ascii=False)
            print(f"[调试] 格式化列表/字典为: {result}")
            return result
        elif isinstance(param, str):
            result = f'"{param}"'
            print(f"[调试] 格式化字符串为: {result}")
            return result
        elif param is None:
            print(f"[调试] 格式化None为: null")
            return "null"
        else:
            result = str(param)
            print(f"[调试] 格式化其他类型为: {result}")
            return result


# 测试函数
if __name__ == "__main__":
    # 示例测试
    test_cases = "[1,2,3,4]\n[2,7,11,15]\n9"
    meta_data = {
        "params": [
            {"name": "nums", "type": "integer[]"},
            {"name": "target", "type": "integer"},
        ]
    }

    parsed = TestCaseParser.parse_test_cases(test_cases, meta_data)
    print(json.dumps(parsed, indent=2))
