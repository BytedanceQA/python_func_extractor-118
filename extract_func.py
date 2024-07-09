import ast
import os
import csv 
import astor
from remove_doc import RemoveDocstringsTransformer


def extract_functions(code, file_path):
    try:
        tree = ast.parse(code)
        transformer = RemoveDocstringsTransformer()
        transformer.visit(tree)

    except SyntaxError as e:
        print(f"文件 {file_path}有语法错误: {e}")
        return []    
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # 检查函数名是否以'test'开头
            if node.name.startswith('test'):
                print(f"过滤函数 '{node.name}'，原因：测试函数。")
                continue
            # 检查是否有文档字符串
            if not ast.get_docstring(node):
                print(f"过滤函数 '{node.name}'，原因：缺少函数注释。")
                continue
            # 检查是否被标记为废弃
            if any(decorator.id == 'deprecated' for decorator in node.decorator_list if isinstance(decorator, ast.Name)):
                print(f"过滤函数 '{node.name}'，原因：函数已被废弃。")
                continue
            function_code = astor.to_source(node)
            function_info = {
                'name': node.name,
                'file': file_path,
                'docstring': ast.get_docstring(node),
                'content': function_code,
                'raw_content': ast.get_source_segment(code, node),
                'start_line': node.lineno,
                'end_line': node.end_lineno
            }
            functions.append(function_info)
    return functions

def traverse_repository(repository_path):
    functions = []
    for root, _, files in os.walk(repository_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    code = f.read()
                    functions.extend(extract_functions(code, file_path))
   
    last_folder_name = os.path.basename(repository_path)
    
    # 确定当前工作目录
    current_working_directory = os.getcwd()

    # 设置目标文件夹路径
    target_folder_path = os.path.join(current_working_directory, "extract_history")

    # 如果目标文件夹不存在，则创建它
    if not os.path.exists(target_folder_path):
        os.makedirs(target_folder_path)

    # 设置输出文件的路径
    output_file = os.path.join(target_folder_path, last_folder_name + "_funcs.csv")    
       
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['name', 'file', 'docstring', 'content', 'start_line', 'end_line'])  
        for function in functions:
            writer.writerow(function.values())    
    print(f"共提取函数：{len(functions)} ；已保存在： {output_file}") 
    return functions

if __name__ == "__main__":
    repository_path = '/Users/bytedance/test_repo/BytedanceQA/'
    functions = traverse_repository(repository_path)


