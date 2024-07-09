import ast

class ExternalDependencyFinder(ast.NodeVisitor):
    def __init__(self, source):
        self.source = source
        self.tree = ast.parse(source)
        self.current_scope = None
        self.scopes = {}
        self.external_dependencies = {}

    def enter_scope(self, name):
        self.current_scope = name
        self.scopes[name] = set()
        self.external_dependencies[name] = set()

    def exit_scope(self):
        self.current_scope = None

    def visit_Attribute(self, node):
        if isinstance(node.value, ast.Name) and node.value.id not in self.scopes.get(self.current_scope, set()):
            if self.current_scope:
                self.external_dependencies[self.current_scope].add(f"{node.value.id}.{node.attr}")
        self.generic_visit(node)


    def visit_FunctionDef(self, node):
        if self.current_scope is None:  # Only consider top-level functions
            self.enter_scope(node.name)
            self.generic_visit(node)
            self.exit_scope()

    def visit_ClassDef(self, node):
        if self.current_scope is None:  # Only consider top-level classes
            self.enter_scope(node.name)
            self.generic_visit(node)
            self.exit_scope()

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load) and node.id not in self.scopes.get(self.current_scope, set()):
            if self.current_scope:
                self.external_dependencies[self.current_scope].add(node.id)
        self.generic_visit(node)

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.scopes[self.current_scope].add(target.id)
        self.generic_visit(node)

    def visit_Global(self, node):
        if self.current_scope:
            self.scopes[self.current_scope].update(node.names)
        self.generic_visit(node)

    def visit_Import(self, node):
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            if self.current_scope:
                self.scopes[self.current_scope].add(name)
            else:
                self.scopes.setdefault('global', set()).add(name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            if self.current_scope:
                self.scopes[self.current_scope].add(name)
            else:
                self.scopes.setdefault('global', set()).add(name)
        self.generic_visit(node)

    def report(self):
        return self.external_dependencies

def find_external_dependencies(source):
    finder = ExternalDependencyFinder(source)
    finder.visit(finder.tree)
    return finder.report()


if __name__ == "__main__":
    source_code = """
    import math

    class Circle:
        def __init__(self, radius):
            self.radius = radius

        def calculate_area(self):
            return math.pi * self.radius ** 2

    def main():
        circle = Circle(5)
        area = circle.calculate_area()
        print(area)
    """
    dependencies = find_external_dependencies(source_code)
    print(dependencies)