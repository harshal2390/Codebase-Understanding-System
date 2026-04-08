import os
import networkx as nx


class DependencyGraph:
    def __init__(self):
        self.graph = nx.DiGraph()  # Directed graph

    # =========================
    # NODE ADDERS
    # =========================
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

    # =========================
    # BUILD GRAPH
    # =========================
    def build_graph(self, parsed_data):
        """
        Build graph from parsed files
        """
        for item in parsed_data:
            file_path = item["file"]

            # Add file node
            self.add_file_node(file_path)

            # =========================
            # FUNCTIONS
            # =========================
            for func in item.get("functions", []):
                func_node = self.add_function_node(func, file_path)
                self.graph.add_edge(func_node, file_path, relation="defined_in")

            # =========================
            # CLASSES
            # =========================
            for cls in item.get("classes", []):
                class_node = self.add_class_node(cls, file_path)
                self.graph.add_edge(class_node, file_path, relation="defined_in")

            # =========================
            # IMPORTS (FILE DEPENDENCY)
            # =========================
            for imp in item.get("imports", []):
                if imp.startswith("."):
                    normalized = os.path.normpath(
                        os.path.join(os.path.dirname(file_path), imp)
                    )

                    if not normalized.endswith(".js"):
                        normalized += ".js"

                    self.graph.add_node(normalized, type="file")
                    self.graph.add_edge(file_path, normalized, relation="imports")

            # =========================
            # FUNCTION CALL GRAPH 🔥
            # =========================
            for call in item.get("function_calls", []):
                call_node = f"{file_path}:{call}"

                self.graph.add_node(call_node, type="function_call")

                # file → function call
                self.graph.add_edge(file_path, call_node, relation="calls")

                # 🔥 link to actual function definition
                for node, attr in self.graph.nodes(data=True):
                    if attr.get("type") == "function" and node.endswith(f":{call}"):
                        self.graph.add_edge(call_node, node, relation="calls_function")

            # =========================
            # ROUTE → CONTROLLER 🔥🔥
            # =========================
            for method, path, controller, func in item.get("route_handlers", []):

                route_node = f"{file_path}:{method.upper()} {path}"
                handler_node = f"{controller}.{func}"

                self.graph.add_node(route_node, type="route")
                self.graph.add_node(handler_node, type="handler")

                # route → handler
                self.graph.add_edge(route_node, handler_node, relation="handled_by")

                # 🔥 Find controller file dynamically
                controller_file = None

                for node, attr in self.graph.nodes(data=True):
                    if attr.get("type") == "file" and controller.lower() in node.lower():
                        controller_file = node
                        break

                # 🔥 handler → controller file
                if controller_file:
                    self.graph.add_edge(handler_node, controller_file, relation="defined_in")

    # =========================
    # GET NEIGHBORS
    # =========================
    def get_neighbors(self, node):
        """
        Get meaningful neighbors only (no noise)
        """
        neighbors = []

        for n in self.graph.neighbors(node):
            relation = self.graph.edges[node, n].get("relation")

            if relation in ["imports", "handled_by", "calls_function", "defined_in"]:
                neighbors.append(n)

        return neighbors

    # =========================
    # FLOW TRACING (DFS)
    # =========================
    def trace_flow(self, start_node, depth=2):
        visited = set()
        flow = []

        def dfs(node, current_depth):
            if current_depth > depth or node in visited:
                return

            visited.add(node)
            flow.append(node)

            neighbors = self.get_neighbors(node)

            for neighbor in neighbors:
                dfs(neighbor, current_depth + 1)

        dfs(start_node, 0)
        return flow

    # =========================
    # SUMMARY
    # =========================
    def print_summary(self):
        print(f"Total Nodes: {self.graph.number_of_nodes()}")
        print(f"Total Edges: {self.graph.number_of_edges()}")