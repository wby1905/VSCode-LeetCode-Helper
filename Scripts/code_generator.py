#!/usr/bin/env python3
"""
LeetCode代码生成器 - 使用工厂模式实现的不同编程语言的测试代码生成器
"""

import os
import sys

# 添加当前脚本所在目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# 现在导入应该可以正常工作了
from code_generators import CodeGeneratorFactory


# 使用示例
if __name__ == "__main__":
    # 这里只是一个示例，实际使用时可以从外部传入参数
    language = 'cpp'
    generator = CodeGeneratorFactory.get_generator(language)
    
    test_cases = "[1,2,3,4]"
    meta_data = {"params": [{"name": "nums", "type": "integer[]"}]}
    code_snippet = "class Solution {\npublic:\n    int countBadPairs(vector<int>& nums) {\n        // 实现代码\n    }\n};"
    
    test_code = generator.create_test_code(test_cases, meta_data, code_snippet)
    print(test_code)