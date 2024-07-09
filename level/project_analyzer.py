import ast
import os
from dependencies import ExternalDependencyFinder

class ProjectAnalyzer:
    def __init__(self, root_directory):
        self.root_directory = root_directory
        self.files = {}
        self.dependencies = {}
        self.runnable_levels = {}

    def analyze(self):
        for root, dirs, files in os.walk(self.root_directory):
            for file in files:
                if file.endswith('.py'):
                    full_path = os.path.join(root, file)
                    with open(full_path, 'r') as f:
                        source = f.read()
                        self.files[full_path] = source
                        self.dependencies[full_path] = self.extract_dependencies(source)

        self.classify_runnable_levels()

    def extract_dependencies(self, source):
        finder = ExternalDependencyFinder(source)
        finder.visit(finder.tree)
        return finder.report()

    def classify_runnable_levels(self):
        for file_path, deps in self.dependencies.items():
            for function, dep_set in deps.items():
                level = self.determine_level(file_path, dep_set)
                self.runnable_levels[(file_path, function)] = level

    def determine_level(self, file_path, dep_set):
        if not dep_set:
            return 'self-contained'
        if all(self.is_in_same_file(file_path, dep) for dep in dep_set):
            return 'file-runnable'
        if all(self.is_in_same_project(file_path, dep) for dep in dep_set):
            return 'project-runnable'
        return 'plib-runnable'

    def is_in_same_file(self, file_path, dependency):
        # Simplified check
        return dependency in self.dependencies[file_path]

    def is_in_same_project(self, file_path, dependency):
        # Check across all files in the project
        for other_file, deps in self.dependencies.items():
            if dependency in deps:
                return True
        return False
    
# Example usage
project_path = '/Users/bytedance/工程/data'
analyzer = ProjectAnalyzer(project_path)
analyzer.analyze()
print(analyzer.runnable_levels)