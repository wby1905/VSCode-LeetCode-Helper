#!/usr/bin/env python3
"""
LeetCode代码生成器 - 抽象基类
"""

import os
import sys
from abc import ABC, abstractmethod

# 添加当前脚本所在目录的父目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from test_case_parser import TestCaseParser


class CodeGenerator(ABC):
    """代码生成器抽象基类"""

    @abstractmethod
    def extract_method_name(self, code_snippet):
        """从代码片段中提取方法名"""
        pass

    @abstractmethod
    def create_test_code(
        self, test_cases, meta_data, code_snippet, problem_content=None
    ):
        """创建测试代码

        Args:
            test_cases: 测试用例字符串
            meta_data: 元数据信息，包含参数和返回值类型
            code_snippet: 代码片段字符串
            problem_content: 可选，题目的完整内容，用于提取期望输出
        """
        pass

    @abstractmethod
    def replace_solution_class(self, template, code_snippet):
        """替换模板中的Solution类"""
        pass

    @abstractmethod
    def generate_test_statements(self, parsed_cases, params, method_name):
        """
        为特定编程语言生成测试语句

        Args:
            parsed_cases: 解析后的测试用例列表
            params: 参数信息列表
            method_name: 方法名称

        Returns:
            测试代码语句列表
        """
        pass

    def parse_test_cases(self, test_cases, meta_data, problem_content=None):
        """
        解析测试用例，使用测试用例解析器

        Args:
            test_cases: 测试用例字符串
            meta_data: 元数据字典，包含参数和返回值信息
            problem_content: 可选，题目的完整内容，用于提取期望输出

        Returns:
            parsed_cases: 解析后的测试用例列表
        """
        # 使用测试用例解析器解析测试用例
        return TestCaseParser.parse_test_cases(test_cases, meta_data, problem_content)
