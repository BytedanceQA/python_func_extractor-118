import ast
import astor  # 如果使用Python 3.9或更高版本，可以使用ast.unparse代替

class RemoveDocstringsTransformer(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        # 移除函数的docstring
        if ast.get_docstring(node):
            node.body = node.body[1:]  # 移除第一个元素，即docstring
        self.generic_visit(node)  # 继续处理函数体内的其他节点
        return node

def print_functions_without_docstrings(source_code):
    # 解析源代码为AST
    tree = ast.parse(source_code)
    
    # 使用自定义的Transformer移除所有函数的docstring
    transformer = RemoveDocstringsTransformer()
    transformer.visit(tree)
    
    # 遍历AST，找到所有的函数定义并打印
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # 将AST节点转换回源代码字符串
            function_code = astor.to_source(node) 
            print(function_code)

# # 示例使用
# source_code = """
# def example_function():
#     \"\"\"This is a docstring.\"\"\"
#     print("Hello, world!")
# """

# print_functions_without_docstrings(source_code)
