from collections import OrderedDict

from src import utils
from src.ir import types, context as ctx


GLOBAL_NAMESPACE = ('global',)


class Node(object):

    def accept(self, visitor):
        return visitor.visit(self)

    def children(self):
        raise NotImplementedError('children() must be implemented')

    def update_children(self, children):
        assert len(children) == len(self.children()), (
            'The number of the given children is not compatible'
            ' with the number of the node\'s children.')


class Program(Node):
    def __init__(self, context: ctx.Context):
        self.context = context

    def children(self):
        return self.context.get_declarations(GLOBAL_NAMESPACE,
                                             only_current=True).values()

    def update_children(self, children):
        super(Program, self).update_children(children)
        for c in children:
            self.add_declaration(c)

    @property
    def declarations(self):
        # Get declarations as list
        return self.get_declarations().values()

    def get_declarations(self):
        return self.context.get_declarations(GLOBAL_NAMESPACE,
                                             only_current=True)

    def add_declaration(self, decl):
        decl_types = {
            FunctionDeclaration: self.context.add_func,
            ClassDeclaration: self.context.add_class,
            VariableDeclaration: self.context.add_var,
        }
        decl_types[decl.__class__](GLOBAL_NAMESPACE, decl.name, decl)

    def remove_declaration(self, decl):
        decl_types = {
            FunctionDeclaration: self.context.remove_func,
            ClassDeclaration: self.context.remove_class,
            VariableDeclaration: self.context.remove_var,
        }
        decl_types[decl.__class__](GLOBAL_NAMESPACE, decl.name)

    def __str__(self):
        return "\n\n".join(map(str, self.children()))


class Block(Node):
    def __init__(self, body):
        self.body = body

    def children(self):
        return self.body

    def update_children(self, children):
        super(Block, self).update_children(children)
        self.body = children

    def __str__(self):
        return "{{\n  {}\n}}".format("\n  ".join(map(str, self.body)))


class Declaration(Node):
    def get_type(self):
        raise NotImplementedError('get_type() must be implemented')


class VariableDeclaration(Declaration):
    def __init__(self, name, expr, var_type=None):
        self.name = name
        self.expr = expr
        self.var_type = var_type

    def children(self):
        return [self.expr]

    def get_type(self):
        return self.var_type

    def update_children(self, children):
        super(VariableDeclaration, self).update_children(children)
        self.expr = children[0]

    def __str__(self):
        if self.var_type is None:
            return "val " + self.name + " = " + str(self.expr)
        else:
            return "val " + self.name + ": " + str(self.var_type) + \
                " = " + str(self.expr)


class FieldDeclaration(Declaration):
    def __init__(self, name, field_type, is_final=True, override=False):
        self.name = name
        self.field_type = field_type
        self.is_final = is_final
        self.override = override

    def children(self):
        return []

    def get_type(self):
        return self.field_type

    def update_children(self, children):
        pass

    def __str__(self):
        return str(self.name) + ": " + str(self.field_type)


class ObjectDecleration(Declaration):
    def __init__(self, name):
        self.name = name

    def get_type(self):
        return types.Object(self.name)

    def update_children(self, children):
        pass

    def __str__(self):
        return "object " + self.name


class SuperClassInstantiation(Node):
    def  __init__(self, class_type, args=[]):
        assert not isinstance(class_type, types.AbstractType)
        self.class_type = class_type
        self.args = args

    def children(self):
        return self.args or []

    def update_children(self, children):
        super(SuperClassInstantiation, self).update_children(children)
        if self.args is not None:
            self.args = children

    def __str__(self):
        if self.args is None:
            return self.class_type.name
        else:
            return self.class_type.name + "(" + ", ".join(map(str, self.args)) + ")"


class ClassDeclaration(Declaration):
    REGULAR = 0
    INTERFACE = 1
    ABSTRACT = 2

    def __init__(self, name, superclasses: SuperClassInstantiation,
                 class_type=None, fields=[], functions=[], is_final=True,
                 type_parameters=[]):
        self.name = name
        self.superclasses = superclasses
        self.class_type = class_type or self.REGULAR
        self.fields = fields
        self.functions = functions
        self.is_final = is_final
        self.type_parameters = type_parameters
        self.supertypes = [s.class_type for s in self.superclasses]

    @property
    def attributes(self):
        return self.fields + self.functions

    def children(self):
        return self.fields + self.superclasses + self.functions

    def update_children(self, children):
        super(ClassDeclaration, self).update_children(children)
        len_fields = len(self.fields)
        len_supercls = len(self.superclasses)
        for i, c in enumerate(children[:len_fields]):
            self.fields[i] = c
        for i, c in enumerate(children[len_fields:len_fields + len_supercls]):
            self.superclasses[i] = c
            self.supertypes[i] = c.class_type
        for i, c in enumerate(children[len_fields + len_supercls:]):
            self.functions[i] = c

    def get_type(self):
        if self.type_parameters:
            return types.TypeConstructor(
                self.name, self.type_parameters,
                self.supertypes)
        return types.SimpleClassifier(
            self.name, self.supertypes)

    def get_class_prefix(self):
        if self.class_type == self.REGULAR:
            return "class"
        if self.class_type == self.INTERFACE:
            return "interface"
        return "abstract class"

    def __str__(self):
        superclasses = " : " + ", ".join(map(str, self.superclasses)) \
            if len(self.superclasses) > 0 else ""
        if self.type_parameters:
            return "{} {}<{}>{} {{\n  {}\n  {} }}".format(
                self.get_class_prefix(), self.name,
                ", ".join(map(str, self.type_parameters)),
                superclasses,
                "\n  ".join(map(str, self.fields)),
                "\n  ".join(map(str, self.functions))
            )
        return "{} {}{} {{\n  {}\n  {} }}".format(
            self.get_class_prefix(), self.name,
            superclasses,
            "\n  ".join(map(str, self.fields)),
            "\n  ".join(map(str, self.functions))
        )


class ParameterDeclaration(Declaration):
    def __init__(self, name, param_type, default=None):
        self.name = name
        self.param_type = param_type
        self.default = default

    def children(self):
        return []

    def update_children(self, children):
        pass

    def get_type(self):
        return self.param_type

    def __str__(self):
        if self.default is None:
            return self.name + ": " + str(self.param_type)
        else:
            return self.name + ": " + str(
                self.param_type) + " = " + str(self.expr)


class FunctionDeclaration(Declaration):
    CLASS_METHOD = 0
    FUNCTION = 1

    def __init__(self, name, params, ret_type, body, func_type,
                 is_final=True, override=False):
        self.name = name
        self.params = params
        self.ret_type = ret_type
        self.body = body
        self.func_type = func_type
        self.is_final = is_final
        self.override = override

    def children(self):
        if self.body is None:
            return self.params
        return self.params + [self.body]

    def update_children(self, children):
        super(FunctionDeclaration, self).update_children(children)
        len_params = len(self.params)
        for i, c in enumerate(children[:len_params]):
            self.params[i] = c
        if self.body is None:
            return
        self.body = children[-1]

    def get_type(self):
        return types.Function(
            self.name, [p.get_type() for p in self.params], self.ret_type)

    def __str__(self):
        if self.ret_type is None:
            return "fun {}({}) =\n  {}".format(
                self.name, ",".join(map(str, self.params)), str(self.body))
        else:
            return "fun {}({}): {} =\n  {}".format(
                self.name, ",".join(map(str, self.params)), str(self.ret_type),
                str(self.body))

class ParameterizedFunctionDeclaration(FunctionDeclaration):
    CLASS_METHOD = 0
    FUNCTION = 1

    def __init__(self, name, type_parameters, params, ret_type, body,
                 func_type, is_final=True, override=False):
        super(ParameterizedFunctionDeclaration, self).__init__(name, params,
              ret_type, body, func_type, is_final, override)
        self.type_parameters = type_parameters

    def get_type(self):
        return types.ParameterizedFunction(
            self.name, type_parameters,
            [p.get_type() for p in self.params], self.ret_type)

    def __str__(self):
        keywords = ""
        if len(keywords) > 0:
            keywords = " ".join(map(lambda x: x.name, self.keywords))
        if self.ret_type is None:
            return "{}fun<{}> {}({}) =\n  {}".format(
                keywords, ",".join(map(str, self.type_parameters)),
                self.name, ",".join(map(str, self.params)), str(self.body))
        else:
            return "{}fun<{}> {}({}): {} =\n  {}".format(
                keywords, ",".join(map(str, self.type_parameters)),
                self.name, ",".join(map(str, self.params)), str(self.ret_type),
                str(self.body))


class Expr(Node):
    pass


class Constant(Expr):
    def __init__(self, literal):
        self.literal = literal

    def children(self):
        return []

    def update_children(self, children):
        pass

    def __str__(self):
        return str(self.literal)


class IntegerConstant(Constant):
    # TODO: Support Hex Integer literals, binary integer literals?
    def __init__(self, literal, integer_type):
        assert isinstance(literal, int) or isinstance(literal, long), (
            'Integer literal must either int or long')
        super(IntegerConstant, self).__init__(literal)
        self.integer_type = integer_type


class RealConstant(Constant):

    def __init__(self, literal):
        suffix = None
        if literal.endswith('f') or literal.endswith('F'):
            literal_nums = literal[:-1]
            suffix = literal[-1]
        else:
            literal_nums = literal
        assert '.' in literal_nums and utils.is_number(literal_nums), (
            'Real literal is not valid')
        self.literal = literal_nums + ('' if suffix is None else suffix)


class BooleanConstant(Constant):
    def __init__(self, literal):
        assert literal == 'true' or literal == 'false', (
            'Boolean literal is not "true" or "false"')
        super(BooleanConstant, self).__init__(literal)


class CharConstant(Constant):
    def __init__(self, literal):
        assert len(literal) == 1, (
            'Character literal must be a single character')
        super(CharConstant, self).__init__(literal)

    def __str__(self):
        return "'{}'".format(self.literal)


class StringConstant(Constant):

    def __str__(self):
        return '"{}"'.format(self.literal)


class Variable(Expr):
    def __init__(self, name):
        self.name = name

    def children(self):
        return []

    def update_children(self, children):
        pass

    def __str__(self):
        return str(self.name)


class Conditional(Expr):
    def __init__(self, cond, true_branch, false_branch):
        self.cond = cond
        self.true_branch = true_branch
        self.false_branch = false_branch

    def children(self):
        return [self.cond, self.true_branch, self.false_branch]

    def update_children(self, children):
        super(Conditional, self).update_children(children)
        self.cond = children[0]
        self.true_branch = children[1]
        self.false_branch = children[2]

    def __str__(self):
        return "if ({})\n  {}\nelse\n  {}".format(
            str(self.cond), str(self.true_branch), str(self.false_branch))


class Operator(Node):
    def __init__(self, name, is_not=False):
        self.name = name
        self.is_not = is_not

    def children(self):
        return []

    def update_children(self, children):
        pass

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.name == other.name and
                self.is_not == other.is_not)

    def __hash__(self):
        hash(str(self.__class__) + str(self.name) + str(self.is_not))

    def __str__(self):
        if self.is_not:
            return "!" + self.name
        return self.name


class BinaryOp(Expr):
    VALID_OPERATORS = None

    def __init__(self, lexpr, rexpr, operator: Operator):
        if self.VALID_OPERATORS is not None:
            assert operator in self.VALID_OPERATORS, (
                'Binary operator ' + operator + ' is not valid')
        self.lexpr = lexpr
        self.rexpr = rexpr
        self.operator = operator

    def children(self):
        return [self.lexpr, self.rexpr]

    def update_children(self, children):
        super(BinaryOp, self).update_children(children)
        self.lexpr = children[0]
        self.rexpr = children[1]

    def __str__(self):
        return str(self.lexpr) + " " + str(self.operator) + " " + str(self.rexpr)


class LogicalExpr(BinaryOp):
    VALID_OPERATORS = [
        Operator('&&'),
        Operator('||')
    ]


class EqualityExpr(BinaryOp):
    VALID_OPERATORS = [
        Operator('=='),
        Operator('==='),
        Operator('=', is_not=True),
        Operator('==', is_not=True)
    ]


class ComparisonExpr(BinaryOp):
    VALID_OPERATORS = [
        Operator('>'),
        Operator('>='),
        Operator('<'),
        Operator('<=')
    ]


class ArithExpr(BinaryOp):
    VALID_OPERATORS = [
        Operator('+'),
        Operator('-'),
        Operator('/'),
        Operator('*')
    ]


class Is(BinaryOp):
    def __init__(self, expr: Expr, etype: types.Type, is_not=False):
        self.lexpr = expr
        self.rexpr = etype
        self.operator = Operator('is', is_not=is_not)

    def children(self):
        return [self.lexpr]

    def update_children(self, children):
        super(BinaryOp, self).update_children(children)
        self.lexpr = children[0]


class New(Expr):
    def __init__(self, class_type: types.Type, args):
        self.class_type = class_type
        self.args = args

    def children(self):
        return self.args

    def update_children(self, children):
        super(New, self).update_children(children)
        self.args = children

    def __str__(self):
        if getattr(self.class_type, 'type_args', None) is not None:
            return " new {}<{}> ({})".format(
                str(self.class_type.name),
                ", ".join(map(str, self.class_type.type_args)) + ")",
                ", ".join(map(str, self.args)) + ")"
            )

        return "new " + self.class_type.name + "(" + \
            ", ".join(map(str, self.args)) + ")"


class FieldAccess(Expr):
    def __init__(self, expr, field):
        self.expr = expr
        self.field = field

    def children(self):
        return [self.expr]

    def update_children(self, children):
        super(FieldAccess, self).update_children(children)
        self.expr = children[0]

    def __str__(self):
        return str(self.expr) + "." + self.field


class FunctionCall(Expr):
    def __init__(self, func, args, receiver=None):
        self.func = func
        self.args = args
        self.receiver = receiver

    def children(self):
        if self.receiver is None:
            return self.args
        return [self.receiver] + self.args

    def update_children(self, children):
        super(FunctionCall, self).update_children(children)
        if self.receiver is None:
            self.args = children
        else:
            self.receiver = children[0]
            self.args = children[1:]

    def __str__(self):
        if self.receiver is None:
            return self.func + "(" + ", ".join(map(str, self.args)) + ")"
        else:
            return str(self.receiver) + ".(" + \
                ", ".join(map(str, self.args)) + ")"

class Assignment(Expr):
    def __init__(self, var_name, expr):
        self.var_name = var_name
        self.expr = expr

    def children(self):
        return [self.expr]

    def update_children(self, children):
        super(Assignment, self).update_children(children)
        self.expr = children[0]

    def __str__(self):
        return str(self.var_name) + " = " + str(self.expr)
