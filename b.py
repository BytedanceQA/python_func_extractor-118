# import ast
# import sys

# # 定义可运行级别
# RUNNABLE_LEVELS = {
#     'SELF_CONTAINED': '自包含',
#     'STANDARD_LIB': '标准库可运行',
#     'THIRD_PARTY_LIB': '公共库可运行',
#     # 类可运行、文件可运行、项目可运行的判断需要更多上下文信息，这里不做演示
# }

# def analyze_dependencies(node):
#     """
#     分析AST节点的依赖，返回依赖类型。
#     """
#     if isinstance(node, ast.Import):
#         return 'STANDARD_LIB'
#     elif isinstance(node, ast.ImportFrom):
#         if node.module and 'third_party_lib' in node.module:  # 假设所有第三方库都包含'third_party_lib'，实际应用中需要具体判断
#             return 'THIRD_PARTY_LIB'
#         return 'STANDARD_LIB'
#     return 'SELF_CONTAINED'

# def determine_runnable_level(code):
#     """
#     确定Python代码中函数的可运行级别。
#     """
#     tree = ast.parse(code)
#     for node in ast.walk(tree):
#         if isinstance(node, ast.FunctionDef):
#             runnable_level = 'SELF_CONTAINED'
#             for child in ast.walk(node):
#                 dep_type = analyze_dependencies(child)
#                 if dep_type == 'THIRD_PARTY_LIB':
#                     runnable_level = 'THIRD_PARTY_LIB'
#                     break
#                 elif dep_type == 'STANDARD_LIB':
#                     runnable_level = 'STANDARD_LIB'
#             print(f"函数 {node.name} 的可运行级别是: {RUNNABLE_LEVELS[runnable_level]}")

# # 示例代码
# code = """
# import json
# def func1():
#     return json.dumps({'key': 'value'})

# import third_party_lib
# def func2():
#     return third_party_lib.do_something()
# """

# determine_runnable_level(code)

import ast
import sys
import pkgutil
import importlib.util

# 定义可运行级别
RUNNABLE_LEVELS = {
    'SELF_CONTAINED': '自包含',
    'STANDARD_LIB': '标准库可运行',
    'THIRD_PARTY_LIB': '公共库可运行',
    'PROJECT_SPECIFIC': '项目可运行',
    'UNKNOWN': '未知',
}

def is_standard_lib(module_name):
    """检查模块是否为标准库的一部分。"""
    if module_name in sys.builtin_module_names:
        return True
    try:
        file_path = importlib.util.find_spec(module_name).origin
        return 'site-packages' not in file_path
    except AttributeError:
        return False

def analyze_dependencies(node, project_modules):
    """
    分析AST节点的依赖，返回依赖类型。
    """
    if isinstance(node, (ast.Import, ast.ImportFrom)):
        for alias in node.names:
            module_name = alias.name.split('.')[0]  # 只获取模块的顶级名称
            if module_name in project_modules:
                return 'PROJECT_SPECIFIC'
            elif is_standard_lib(module_name):
                return 'STANDARD_LIB'
            else:
                return 'THIRD_PARTY_LIB'
    return 'SELF_CONTAINED'

def determine_runnable_level(code, project_modules):
    """
    确定Python代码中函数的可运行级别。
    """
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            runnable_level = 'SELF_CONTAINED'
            for child in ast.walk(node):
                dep_type = analyze_dependencies(child, project_modules)
                if dep_type == 'THIRD_PARTY_LIB':
                    runnable_level = 'THIRD_PARTY_LIB'
                    break
                elif dep_type == 'PROJECT_SPECIFIC':
                    runnable_level = 'PROJECT_SPECIFIC'
                elif dep_type == 'STANDARD_LIB' and runnable_level == 'SELF_CONTAINED':
                    runnable_level = 'STANDARD_LIB'
            print(f"函数 {node.name} 的可运行级别是: {RUNNABLE_LEVELS[runnable_level]}")

# 示例代码
code =  """
import os
from sys import path

class MyClass:
    pass

async def my_async_function():
    pass

def my_function(x: int) -> int:
    return x * 2

x = 10
y = "Hello"
for i in range(5):
    pass

with open('file.txt', 'r') as f:
    pass

z = [j for j in range(5)]
"""

# 假设的项目模块列表
project_modules = ['my_project_module']

determine_runnable_level(code, project_modules)