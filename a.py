import ast

class CodeAnalyzer(ast.NodeVisitor):
    def __init__(self):
        super().__init__()
        self.functions = []
        self.classes = []
        self.variables = set()
        self.constants = set()
        self.imports = []

    def visit_FunctionDef(self, node):
        self.functions.append(node.name)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self.functions.append(node.name)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.classes.append(node.name)
        self.generic_visit(node)

    def visit_Assign(self, node):
        self._handle_assignment(node.targets)
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        if isinstance(node.target, ast.Name):
            self.variables.add(node.target.id)
        self.generic_visit(node)

    def visit_Constant(self, node):
        self.constants.add(node.value)
        self.generic_visit(node)

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.imports.append(f"{node.module}.{alias.name}")
        self.generic_visit(node)

    def visit_For(self, node):
        if isinstance(node.target, ast.Name):
            self.variables.add(node.target.id)
        elif isinstance(node.target, (ast.Tuple, ast.List)):
            for elt in node.target.elts:
                if isinstance(elt, ast.Name):
                    self.variables.add(elt.id)
        self.generic_visit(node)

    def visit_ListComp(self, node):
        self._handle_comprehension(node.generators)
        self.generic_visit(node)

    def visit_DictComp(self, node):
        self._handle_comprehension(node.generators)
        self.generic_visit(node)

    def visit_SetComp(self, node):
        self._handle_comprehension(node.generators)
        self.generic_visit(node)

    def visit_GeneratorExp(self, node):
        self._handle_comprehension(node.generators)
        self.generic_visit(node)

    def visit_If(self, node):
        # 仅为示例，实际情况下需要更复杂的逻辑来处理条件语句中的变量
        self.generic_visit(node)

    def _handle_assignment(self, targets):
        for target in targets:
            if isinstance(target, ast.Name):
                self.variables.add(target.id)
            elif isinstance(target, (ast.Tuple, ast.List)):
                for elt in target.elts:
                    if isinstance(elt, ast.Name):
                        self.variables.add(elt.id)

    def _handle_comprehension(self, generators):
        for generator in generators:
            if isinstance(generator.target, ast.Name):
                self.variables.add(generator.target.id)
            elif isinstance(generator.target, (ast.Tuple, ast.List)):
                for elt in generator.target.elts:
                    if isinstance(elt, ast.Name):
                        self.variables.add(elt.id)

def analyze_code(source_code):
    tree = ast.parse(source_code)
    analyzer = CodeAnalyzer()
    analyzer.visit(tree)
    return analyzer

# 示例使用
source_code = """
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

analyzer = analyze_code(source_code)
print("Functions:", analyzer.functions)
print("Classes:", analyzer.classes)
print("Variables:", list(analyzer.variables))
print("Constants:", list(analyzer.constants))
print("Imports:", analyzer.imports)


# 通过程序分析识别函数的上下文依赖性主要分为三个步骤。我将结合自己的理解和例子来具体解释每一步：

# 1. 构建知识库
# 在开始分析之前，首先需要构建一个知识库。这个知识库包含了对Python/Java内置类型、函数、变量、常量以及标准库或公共库的不同引用的识别信息。

# 例子：假设我们正在分析一个Python项目，这个知识库将包含Python从3.0.0到3.10.0版本的所有内置类型（如int、str等）、函数（如print()）、变量和常量。此外，还会包括标准库的名称（如os、sys）和pypi.org上所有公开可用的第三方库（如requests、numpy）。

# 2. 解析源文件
# 利用构建好的知识库，分析工具将解析包含目标函数的源文件，以获取该文件中定义的类型、函数、变量和常量的列表。

# 例子：如果我们正在分析一个包含函数calculate_interest的Python文件，这一步骤将解析该文件，识别出所有在calculate_interest函数内部或外部定义的类型（如类定义）、函数、变量和常量。

# 3. 静态程序分析
# 在获取了源文件中定义的元素列表后，接下来进行静态程序分析，以识别所有依赖元素。这些依赖元素是指那些定义在目标函数外部，但被目标函数引用或调用的元素。这些元素根据它们的类型被分类为类型引用、变量引用和API调用。

# 类型引用（type_reference）：指的是用户定义的类或标准类型。例如，如果calculate_interest函数使用了一个名为BankAccount的用户定义类，或者使用了标准类型list，这些都会被识别为类型引用。
# 变量引用（variable_reference）：指的是用户定义的变量或对象。例如，如果函数外部定义了一个变量interest_rate，并且calculate_interest函数引用了这个变量，那么interest_rate就是一个变量引用。
# API调用（API invocation）：指的是用户定义的函数或标准/第三方库中的函数调用。例如，如果calculate_interest函数调用了标准库math中的pow函数，或者调用了第三方库numpy中的某个函数，这些都会被识别为API调用。
# 通过这三个步骤，分析工具能够准确地识别出目标函数的所有上下文依赖性，这对于理解函数的行为和它与项目其他部分的关系至关重要。这种方法特别适用于评估代码生成模型的能力，尤其是在处理需要理解和处理复杂依赖关系的编程任务时。

# 要解析Python文件并获取其中定义的类型、函数、变量和常量的列表，我们可以使用Python的ast模块。ast模块能够将Python源代码解析成抽象语法树（AST），通过遍历这棵树，我们可以识别出文件中的各种元素。

# 以下是一个简单的实现步骤：

# 使用ast.parse函数解析Python源代码，生成AST。
# 定义一个访问者类，继承自ast.NodeVisitor，用于遍历AST。
# 在访问者类中，实现对不同节点类型的处理方法，如visit_FunctionDef用于处理函数定义，visit_ClassDef用于处理类定义等。
# 实例化访问者类，并使用visit方法遍历AST，收集信息。


 
