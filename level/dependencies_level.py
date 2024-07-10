import ast
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import astor
from util.csv import save_to_csv

class DependencyAnalyzer(ast.NodeVisitor):
    """ Analyzes dependencies within Python files to classify functions based on their dependency levels. """
    
    def __init__(self):
        self.dependencies = {}
        self.current_class = None
        self.current_function = None
        self.imported_names = set() 
        self.class_defined_names = set() 

    def visit_FunctionDef(self, node):
        """ Visit a function definition, track its name and dependencies. """
        if node.name.startswith('test'):
            print(f"Skipping function '{node.name}' as it is a test function.")
            return  # Skip test functions
        if not ast.get_docstring(node):
            print(f"Skipping function '{node.name}' due to missing docstring.")
            return  # Skip functions without docstrings
        if any(decorator.id == 'deprecated' for decorator in node.decorator_list if isinstance(decorator, ast.Name)):
            print(f"Skipping function '{node.name}' as it is deprecated.")
            return  # Skip deprecated functions        
        if self.current_class:
            # Track methods defined within the class
            self.class_defined_names.add(node.name)
        self.current_function = node.name
        self.dependencies[self.current_function] = {
            'builtin': set(),
            'class_level': set(),
            'file_level': set(),
            'project_level': set()
        }
        self.generic_visit(node)
        self.current_function = None

    def visit_ClassDef(self, node):
        """ Visit a class definition, track its name and reset class-level names. """
        self.current_class = node.name
        self.class_defined_names = set()
        self.generic_visit(node)
        self.current_class = None
        self.class_defined_names = set()

    def visit_Import(self, node):
        """ Track names imported from other modules. """
        for alias in node.names:
            self.imported_names.add(alias.name)

    def visit_ImportFrom(self, node):
        """ Track names imported from specific modules. """
        for alias in node.names:
            self.imported_names.add(alias.name)



    def visit_Name(self, node):
        """ Classify dependencies based on where the name is defined. """
        if isinstance(node.ctx, ast.Load) and self.current_function:
            if node.id in __builtins__.__dict__:
                self.dependencies[self.current_function]['builtin'].add(node.id)
            elif 'self.' + node.id in self.class_defined_names or node.id in self.class_defined_names:
                self.dependencies[self.current_function]['class_level'].add(node.id)
            elif node.id in self.imported_names:
                self.dependencies[self.current_function]['project_level'].add(node.id)
            else:
                self.dependencies[self.current_function]['file_level'].add(node.id)    

def classify_dependencies(dependencies):
    """ Classify each function based on its dependencies. """
    classifications = {}
    for func, deps in dependencies.items():
        if not any(deps.values()):
            classifications[func] = ('self-contained', 'No dependencies')
        elif deps['project_level']:
            classifications[func] = ('project-runnable', f"Depends on project-level items: {deps['project_level']}")
        elif deps['file_level']:
            classifications[func] = ('file-runnable', f"Depends on file-level items: {deps['file_level']}")
        elif deps['class_level']:
            classifications[func] = ('class-runnable', f"Depends on class-level items: {deps['class_level']}")
        elif deps['builtin']:
            classifications[func] = ('self-contained', f"Only uses built-in items: {deps['builtin']}")
        else:
            classifications[func] = ('unknown', 'Unclassified dependencies')
    return classifications


def analyze_project(directory):
    """ 分析目录中所有 Python 文件的依赖关系，并将结果及函数信息保存到 CSV 文件中。 """
    results = {}
    all_functions = []  # 用于存储所有函数数据的列表
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                relative_path = os.path.relpath(path, start=directory)  # 使用相对路径
                with open(path, 'r') as file:
                    code = file.read()
                analyzer = DependencyAnalyzer()
                node = ast.parse(code, filename=path)
                analyzer.visit(node)
                deps = analyzer.dependencies
                classified_deps = classify_dependencies(deps)
                results[relative_path] = classified_deps  # 使用相对路径
                for func, (classification, reason) in classified_deps.items():
                    func_node = next((n for n in ast.walk(node) if isinstance(n, ast.FunctionDef) and n.name == func), None)
                    if func_node:
                        function_code = astor.to_source(func_node)
                        function_info = {
                            'name': func,
                            'file': relative_path,  # 使用相对路径
                            'docstring': ast.get_docstring(func_node),
                            'content': function_code,
                            'raw_content': ast.get_source_segment(code, func_node),
                            'start_line': func_node.lineno,
                            'end_line': func_node.end_lineno,
                            'classification': classification,
                            'reason': reason
                        }
                        all_functions.append(function_info)
    
    # 将结果写入 CSV
    fieldnames = ['name', 'file', 'docstring', 'content', 'raw_content', 'start_line', 'end_line', 'classification', 'reason']
    save_to_csv(all_functions, directory, fieldnames)
    return results

if __name__ == "__main__":
    project_path = "/Users/bytedance/工程/CodeEvalX/python_func_extractor/test"
    results = analyze_project(project_path)
    for file, funcs in results.items():
        print(f"File: {file}")
        for func, (classification, reason) in funcs.items():
            print(f"  Function: {func} - Classification: {classification} - Reason: {reason}")