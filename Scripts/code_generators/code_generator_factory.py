#!/usr/bin/env python3
"""
LeetCode代码生成器工厂 - 负责创建不同语言的代码生成器
"""

from .code_generator_base import CodeGenerator
from .code_generator_cpp import CppCodeGenerator
from .code_generator_python import PythonCodeGenerator


class CodeGeneratorFactory:
    """代码生成器工厂类"""

    @staticmethod
    def get_generator(language):
        """获取指定语言的代码生成器"""
        if language == "cpp":
            return CppCodeGenerator()
        elif language == "py":
            return PythonCodeGenerator()
        else:
            raise ValueError(f"不支持的语言: {language}")
