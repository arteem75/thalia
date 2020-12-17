from typing import Tuple
from collections import defaultdict

from src.ir import ast
from src.visitors import DefaultVisitor
from src.transformations.base import change_namespace


def get_decl(context, namespace, decl_name: str, limit=None) -> Tuple[str, ast.Declaration]:
    def stop_cond(ns):
        # If 'limit' is provided, we search the given declaration 'node'
        # up to a certain namespace.
        return (len(ns)
                if limit is None
                else any(limit == ns[:i]
                         for i in range(1, len(limit) + 1))

    while stop_cond(namespace):
        decls = context.get_declarations(namespace, True)
        decl = decls.get(decl_name)
        if decl:
            return namespace, decl
        namespace = namespace[:-1]
    return None


class UseAnalysis(DefaultVisitor):
    def __init__(self):
        # The type of each node is: Tuple[String, ast.Declaration]
        self._use_graph = defaultdict(lambda: list())  # node => [node]
        self._namespace = ast.GLOBAL_NAMESPACE

    def get_none_node(self):
        gnode = (self._namespace, "None")
        return gnode

    def result(self):
        return self._use_graph

    @change_namespace
    def visit_class_decl(self, node):
        self._selected_namespace = self._namespace
        super(UseAnalysis, self).visit_class_decl(node)

    def visit_field_decl(self, node):
        gnode = (self._namespace, node)
        self._use_graph[gnode]  # initialize the node

    def visit_param_decl(self, node):
        gnode = (self._namespace, node)
        self._use_graph[gnode]  # initialize the node

    def visit_variable(self, node):
        # self.parent_node in stack graph[variable] => None
        gnode = (self._namespace, node)
        self._use_graph[gnode]  # Safely initialize node
        self._use_graph[gnode].append(self.get_none_node())

    def visit_var_decl(self, node):
        """Add variable to _var_decl_stack to add flows from it to other
        variables in visit_variable.
        """
        gnode = (self._namespace, node.name)
        self._use_graph[gnode]  # initialize the node
        if type(node.expr) is ast.Variable:
            # Find the node corresponding to the variable of the right-hand
            # side.
            var_node = get_decl(self.program.context,
                                self._namespace, node.expr.name,
                                limit=self._selected_namespace)
            # If node is None, this means that we referring to a variable
            # outside the context of class.
            if var_node:
                self._use_graph[var_node].append(gnode)
        else:
            super(UseAnalysis, self).visit_var_decl(node)

    @change_namespace
    def visit_func_decl(self, node):
        # TODO handle return types.
        pass

    def visit_func_call(self, node):
        """Add flows from function call arguments to function declaration
        parameters.
        """
        # Find the namespace and the declaration of the functions that is
        # being called.
        fun_nsdecl = get_decl(
            self.program.context, self._namespace, node.func,
            limit=self._selected_namespace)
        add_none = False
        if not fun_nsdecl:
            # The function is outer, so, if we pass a variable to this function
            # we must add an edge from this variable to the None node.
            add_none = True

        for i, arg in enumerate(node.args):
            if type(arg) is not ast.Variable:
                self.visit(arg)
                continue
            var_node = get_decl(self.program.context, self._namespace,
                                arg.name, limit=self._selected_namespace)
            # Case 1: we have a variable reference 'x' in a function declared
            # in the current class.
            # So, we add an edge from 'x' to the parameter of the function.
            if var_node and not add_none:
                namespace, func_decl = fun_nsdecl
                param_namespace = namespace + (func_decl.node,)
                self._use_graph[var_node].append((param_namespace,
                                                  func_decl.params[i]))
            if var_node and add_none:
                self._use_graph[var_node].append(self.get_none_node())
