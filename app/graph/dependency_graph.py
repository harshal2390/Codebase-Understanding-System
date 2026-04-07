import os
import networkx as nx


class DependencyGraph:
    def __init__(self):
        self.graph = nx.DiGraph()  # Directed graph

    def add_file_node(self, file_path):
        self.graph.add_node(file_path, type="file")

    def add_function_node(self, func_name, file_path):
        node_id = f"{file_path}:{func_name}"
        self.graph.add_node(node_id, type="function", file=file_path)
        return node_id

    def add_class_node(self, class_name, file_path):
        node_id = f"{file_path}:{class_name}"
        self.graph.add_node(node_id, type="class", file=file_path)
        return node_id

    def build_graph(self, parsed_data):
        """
        Build graph from parsed files
        """
        for item in parsed_data:
            file_path = item["file"]

            # Add file node
            self.add_file_node(file_path)

            # Add functions
            for func in item["functions"]:
                func_node = self.add_function_node(func, file_path)

                # Link function to file
                self.graph.add_edge(func_node, file_path, relation="defined_in")

            # Add classes
            for cls in item["classes"]:
                class_node = self.add_class_node(cls, file_path)

                # Link class to file
                self.graph.add_edge(class_node, file_path, relation="defined_in")

            # Add imports (file-level dependency)
            for imp in item["imports"]:
                self.graph.add_edge(file_path, imp, relation="imports")

    def get_neighbors(self, node):
        """
        Get connected nodes
        """
        return list(self.graph.neighbors(node))

    def print_summary(self):
        print(f"Total Nodes: {self.graph.number_of_nodes()}")
        print(f"Total Edges: {self.graph.number_of_edges()}")