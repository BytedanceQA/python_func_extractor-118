import ast
import os

class ModuleInfo:
    def __init__(self, file_path):
        self.file_path = file_path
        self.imports = set()
        self.definitions = {}
        self.dependencies = {}

    def add_import(self, module_name, alias=None):
        self.imports.add((module_name, alias))

    def add_definition(self, name, type):
        self.definitions[name] = type

    def add_dependency(self, name, dependency):
        if name in self.definitions:
            self.dependencies.setdefault(name, set()).add(dependency)

class ProjectStructure:
    def __init__(self, root_directory):
        self.root_directory = root_directory
        self.modules = {}

    def analyze(self):
        for root, dirs, files in os.walk(self.root_directory):
            for file in files:
                if file.endswith('.py'):
                    full_path = os.path.join(root, file)
                    self.modules[full_path] = self.analyze_module(full_path)

    def analyze_module(self, file_path):
        with open(file_path, 'r') as file:
            source = file.read()
        tree = ast.parse(source)
        module_info = ModuleInfo(file_path)
        analyzer = ModuleAnalyzer(module_info)
        analyzer.visit(tree)
        return module_info

class ModuleAnalyzer(ast.NodeVisitor):
    def __init__(self, module_info):
        self.module_info = module_info

    def visit_Import(self, node):
        for alias in node.names:
            self.module_info.add_import(alias.name, alias.asname)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            full_import_name = f"{node.module}.{alias.name}" if node.module else alias.name
            self.module_info.add_import(full_import_name, alias.asname)

    def visit_FunctionDef(self, node):
        self.module_info.add_definition(node.name, 'function')
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.module_info.add_definition(node.name, 'class')
        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.module_info.add_dependency(self.module_info.file_path, node.id)

# Example usage
project_path = '/path/to/your/python/project'
project_structure = ProjectStructure(project_path)
project_structure.analyze()