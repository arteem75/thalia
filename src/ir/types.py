# pylint: disable=abstract-method
from __future__ import annotations
from copy import copy
from collections import defaultdict
from typing import List, Dict, Set

from src.config import cfg
from src.ir.node import Node


class Variance(object):
    INVARIANT = 0
    COVARIANT = 1
    CONTRAVARIANT = 2

    def __init__(self, value):
        self.value = value

    def variance_to_str(self):
        if self.value == 1:
            return 'out'
        if self.value == 2:
            return 'in'
        return ''

    def is_covariant(self):
        return self.value == 1

    def is_contravariant(self):
        return self.value == 2

    def is_invariant(self):
        return self.value == 0

    def __hash__(self):
        return hash(self.value)

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self.value == other.value
        )


Invariant = Variance(Variance.INVARIANT)
Covariant = Variance(Variance.COVARIANT)
Contravariant = Variance(Variance.CONTRAVARIANT)


class Type(Node):
    def __init__(self, name):
        self.name = name
        self.supertypes = []

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return self.__str__()

    def has_type_variables(self):
        raise NotImplementedError("You have to implement has_type_variables()")

    def is_subtype(self, other: Type):
        raise NotImplementedError("You have to implement 'is_subtype()'")

    def is_assignable(self, other: Type):
        """
        Checks of a value of the current type is assignable to 'other' type.

        By default, the current type should be subtype of the other type.
        However, this is not always the case, e.g., in Groovy / Java,
        a value of type Short can be assigned to a value of type Integer,
        but Short is not subtype of Integer.
        """
        return self.is_subtype(other)

    def is_primitive(self):
        raise NotImplementedError("You have to implement 'is_primitive()'")

    def is_type_var(self):
        return False

    def is_wildcard(self):
        return False

    def is_parameterized(self):
        return False

    def is_type_constructor(self):
        return False

    def is_function_type(self):
        return False

    def get_supertypes(self):
        """Return self and the transitive closure of the supertypes"""
        stack = [self]
        visited = {self}
        while stack:
            source = stack.pop()
            for supertype in source.supertypes:
                if supertype not in visited:
                    visited.add(supertype)
                    stack.append(supertype)
        return visited

    def not_related(self, other: Type):
        return not(self.is_subtype(other) or other.is_subtype(self))

    def box_type(self):
        return self

    def get_name(self):
        return str(self.name)


class AbstractType(Type):
    def is_subtype(self, other):
        raise TypeError("You cannot call 'is_subtype()' in an AbstractType")

    def get_supertypes(self):
        return super().get_supertypes()

    def has_type_variables(self):
        return True

    def not_related(self, other):
        raise TypeError("You cannot call 'not_related()' in an AbstractType")

    def is_primitive(self):
        return False


class Builtin(Type):
    """https://kotlinlang.org/spec/type-system.html#built-in-types
    """

    def __init__(self, name: str):
        super().__init__(name)
        self.supertypes = []

    def has_type_variables(self):
        return False

    def __str__(self):
        return str(self.name) + "(builtin)"

    def __eq__(self, other: Type):
        """Check if two Builtin objects are of the same Type"""
        return self.__class__ == other.__class__

    def __hash__(self):
        """Hash based on the Type"""
        return hash((self.__class__, self.name))

    def is_subtype(self, other: Type) -> bool:
        return other == self or other in self.get_supertypes()

    def get_builtin_type(self):
        raise NotImplementedError("You have to implement get_builtin_type")


class Classifier(Type):
    def is_primitive(self):
        return False


class Object(Classifier):

    def __str__(self):
        return "object " + self.name


class SimpleClassifier(Classifier):
    """https://kotlinlang.org/spec/type-system.html#simple-classifier-types
    """

    def __init__(self, name: str, supertypes: List[Type] = None, check=False):
        super().__init__(name)
        self.supertypes = supertypes if supertypes is not None else []
        if check:
            self._check_supertypes()

    def has_type_variables(self):
        return False

    def __str__(self):
        return "Classifier[{}]".format(
            self.name
        )

    def __eq__(self, other: Type):
        """Check if two Builtin objects are of the same Type"""
        return (self.__class__ == other.__class__ and
                self.name == other.name and
                self.supertypes == other.supertypes)

    def __hash__(self):
        """Hash based on the Type"""
        return hash((self.__class__, self.name))

    def _check_supertypes(self):
        """The transitive closure of supertypes must be consistent, i.e., does
        not contain two parameterized types with different type arguments.
        """
        tconst = defaultdict(list)  # Type Constructors
        for supertype in filter(
                lambda x: x.is_parameterized(),
                self.get_supertypes()):
            tconst[supertype.t_constructor] = \
                tconst[supertype.t_constructor] + [supertype]
        for t_class in tconst.values():
            for ptype in t_class:
                assert ptype.type_args == t_class[0].type_args, \
                    "The concrete types of " + \
                    str(t_class[0].t_constructor) + " " + \
                    "do not have the same types"

    def is_subtype(self, other: Type) -> bool:
        supertypes = self.get_supertypes()
        # Since the subtyping relation is transitive, we must also check
        # whether any supertype of the current type is also subtype of the
        # given type.
        return other == self or any(
            st.is_subtype(other) for st in supertypes
            if st != self
        )


class TypeParameter(AbstractType):

    def __init__(self, name: str, variance=None, bound: Type = None):
        super().__init__(name)
        self.variance = variance or Invariant
        self.bound = bound

    def variance_to_string(self):
        return self.variance.variance_to_str()

    def is_covariant(self):
        return self.variance.is_covariant()

    def is_contravariant(self):
        return self.variance.is_contravariant()

    def is_invariant(self):
        return self.variance.is_invariant()

    def children(self):
        return []

    def is_type_var(self):
        return True

    def has_bound_of(self, other: Type) -> bool:
        if not self.bound:
            return False
        bound = self.bound
        if bound == other:
            return True
        if hasattr(bound, "get_type_variables"):
            return other in bound.get_type_variables(cfg.bt_factory)
        return False

    def has_recursive_bound(self, factory=None) -> bool:
        if not self.bound or not self.bound.is_parameterized():
            return False

        type_variable_names = {
            type_var.name
            for type_var in self.bound.get_type_variables(factory)
        }
        return self.name in type_variable_names

    def get_bound_rec(self, factory):
        """
        This function recursively gets the bound of the type parameter.
        """
        if not self.bound:
            return None
        t = self.bound
        if t.is_type_var():
            return t.get_bound_rec(factory)
        if not t.has_type_variables():
            return t
        # If the bound is a parameterized type that contains other type
        # variables, we have to convert this type into an equivalent type
        # that is type variable-free.
        # We do this, because the bound would contain type variables which
        # are out of scope in the context where we use this bound.
        if t.is_type_constructor():
            return t

        return t.to_type_variable_free(factory)

    def is_subtype(self, other):
        if not self.bound:
            return False
        return self.bound == other

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.name == other.name and
                self.variance == other.variance and
                self.bound == other.bound)

    def __hash__(self):
        return hash((self.name, self.variance))

    def __str__(self):
        return "{}{}{}".format(
            self.variance_to_string() +
            ' ' if self.variance != Invariant else '',
            self.name,
            ' <: ' + self.bound.get_name() if self.bound is not None else ''
        )


class WildCardType(Type):
    def __init__(self, bound=None, variance=Invariant):
        super().__init__("*")
        self.bound = bound
        self.variance = variance

    def is_subtype(self, other):
        if isinstance(other, WildCardType):
            if other.bound is not None:
                if self.variance.is_covariant() and (
                        other.variance.is_covariant()):
                    return self.bound.is_subtype(other.bound)
        return False

    def has_type_variables(self):
        return self.bound and self.bound.has_type_variables()

    def get_type_variables(self, factory):
        if not self.bound:
            return {}
        if self.bound.is_wildcard():
            return self.bound.get_type_variables(factory)
        elif self.bound.is_type_var():
            return {self.bound: {self.bound.get_bound_rec(factory)}}
        elif self.bound.is_parameterized():
            return self.bound.get_type_variables(factory)
        else:
            return {}

    def get_bound_rec(self):
        if not self.bound:
            return None
        t = self.bound
        if t.is_wildcard():
            return t.get_bound_rec()
        return t

    def is_wildcard(self):
        return True

    def is_invariant(self):
        return self.variance.is_invariant()

    def is_covariant(self):
        return self.variance.is_covariant()

    def is_contravariant(self):
        return self.variance.is_contravariant()

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.variance == other.variance and
                self.bound == other.bound)

    def __hash__(self):
        return hash((self.name, self.variance))

    def __str__(self):
        if not self.bound:
            return "*"
        else:
            return "{}{}".format(
                self.variance.variance_to_str() +
                ' ' if self.variance != Invariant else '',
                self.bound.get_name()
            )

    def is_primitive(self):
        return False


def _get_type_substitution(etype, type_map,
                           cond=lambda t: t.has_type_variables(),
                           substitute_bound=True):
    if etype.is_parameterized():
        return substitute_type_args(etype, type_map, cond)
    if etype.is_wildcard() and etype.bound is not None:
        new_bound = _get_type_substitution(etype.bound, type_map, cond,
                                           substitute_bound)
        return WildCardType(new_bound, variance=etype.variance)
    t = type_map.get(etype)
    if t is None or cond(t):
        # Perform type substitution on the bound of the current type variable.
        if etype.is_type_var() and etype.bound is not None and \
                substitute_bound:
            new_bound = _get_type_substitution(etype.bound, type_map, cond,
                                               substitute_bound)
            return (
                TypeParameter(etype.name, etype.variance, new_bound)
                if not etype.is_type_constructor()
                else TypeParameterConstructor(etype.name,
                                              etype.type_parameters,
                                              etype.variance, new_bound)
            )
        # The type parameter does not correspond to an abstract type
        # so, there is nothing to substitute.
        return etype
    return t


def substitute_type_args(etype, type_map,
                         cond=lambda t: t.has_type_variables(),
                         substitute_bound=True):
    assert etype.is_parameterized()
    type_args = []
    for t_arg in etype.type_args:
        type_args.append(_get_type_substitution(t_arg, type_map, cond,
                                                substitute_bound))
    type_con = etype.t_constructor
    t = type_map.get(type_con)
    if t is None or cond(t) or not type_con.is_type_var():
        return ParameterizedType(etype.t_constructor, type_args)

    assert t.is_type_constructor()
    assert len(t.type_parameters) == len(type_args)
    return t.new(type_args)


def substitute_type(t, type_map, substitute_bound=True):
    return _get_type_substitution(t, type_map, lambda t: False,
                                  substitute_bound)


def perform_type_substitution(etype, type_map,
                              cond=lambda t: t.has_type_variables(),
                              substitute_bound=True):
    """
    This function performs the following substitution.
    Imagine that we have the following case.

    class Y<T>
    class X<T>: Y<T>()

    When, we instantiate the type constructor X with a specific type
    argument (e.g., String), we must also substitute the type parameter
    of its supertype (i.e., Y<T>) with the given type argument.
    For example, the supertype of X<String> is Y<String> and not Y<T>.

    This also works for nested definitions. For example
    class X<T> : Y<Z<T>>()
    """
    supertypes = []
    for t in etype.supertypes:
        if t.is_parameterized():
            supertypes.append(substitute_type_args(t, type_map, cond,
                                                   substitute_bound))
        else:
            supertypes.append(t)
    type_params = []
    for t_param in etype.type_parameters:
        if t_param.bound is None:
            type_params.append(t_param)
            continue

        new_bound = t_param.bound
        if t_param.is_type_constructor():
            t_param = TypeParameterConstructor(
                t_param.name, t_param.type_parameters, t_param.variance,
                new_bound
            )
        else:
            t_param = TypeParameter(t_param.name, t_param.variance, new_bound)
        type_params.append(t_param)

    etype = copy(etype)
    etype.type_parameters = type_params
    etype.supertypes = supertypes
    return etype


class TypeConstructor(AbstractType):
    def __init__(self, name: str, type_parameters: List[TypeParameter],
                 supertypes: List[Type] = None):
        super().__init__(name)
        assert len(type_parameters) != 0, "type_parameters is empty"
        self.type_parameters = list(type_parameters)
        self.supertypes = supertypes if supertypes is not None else []

    def __str__(self):
        return "{}<{}>".format(
            self.name,
            ', '.join(map(str, self.type_parameters)))

    def __eq__(self, other: AbstractType):
        return (self.__class__ == other.__class__ and
                self.name == other.name and
                str(self.type_parameters) == str(other.type_parameters))

    def __hash__(self):
        return hash((self.name, tuple(self.supertypes),
                     tuple(self.type_parameters)))

    def has_recursive_bounds(self, factory):
        return any(type_param.has_recursive_bound(factory)
                   for type_param in self.type_parameters)

    @property
    def arity(self):
        return len(self.type_parameters)

    def is_type_constructor(self):
        return True

    def is_subtype(self, other: Type):
        supertypes = self.get_supertypes()
        matched_supertype = None
        for supertype in supertypes:
            if other == supertype:
                matched_supertype = supertype
                break
        return matched_supertype is not None

    def new(self, type_args: List[Type]):
        try:
            type_map = {tp: type_args[i]
                    for i, tp in enumerate(self.type_parameters)}
        except:
            return None
        old_supertypes = self.supertypes
        type_con = perform_type_substitution(self, type_map, lambda t: False)
        etype = ParameterizedType(type_con, type_args)
        etype.t_constructor.supertypes = old_supertypes
        return etype

    def match_type_con(self, type_con: TypeConstructor):
        if not type_con.is_type_constructor():
            return False
        if self.arity != type_con.arity:
            return False

        for i, tparam in enumerate(type_con.type_parameters):
            self_tparam = self.type_parameters[i]
            if type(tparam) != type(self_tparam):
                return False
            if self_tparam.is_type_constructor() and \
                    not self_tparam.match_type_con(tparam):
                return False
            self_bound = self_tparam.bound
            self_bound = self_bound or cfg.bt_factory.get_any_type()
            bound = tparam.bound or cfg.bt_factory.get_any_type()
            if not self_bound.is_subtype(bound):
                return False
        return True


class TypeParameterConstructor(TypeParameter, TypeConstructor):
    def __init__(self, name: str, type_parameters: int,
                 variance=None, bound: Type = None):
        self.name = name
        self.variance = variance or Invariant
        self.bound = bound
        self.type_parameters = type_parameters
        self.supertypes = []

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.name == other.name and
                self.arity == other.arity and
                self.variance == other.variance and
                self.bound == other.bound)

    def __hash__(self):
        return hash((self.name, self.variance, self.arity))

    def __str__(self):
        return "{variance}{name}[{arity}]{bound}".format(
            variance=(
                self.variance_to_string() +
                ' ' if self.variance != Invariant else ''
            ),
            arity=self.arity,
            name=self.name,
            bound=(
                ' <: ' + self.bound.get_name()
                if self.bound is not None else ''
            )
        )

    @property
    def arity(self):
        return len(self.type_parameters)


def _to_type_variable_free(t: Type, t_param, factory) -> Type:
    if t.is_type_var():
        bound = t.get_bound_rec(factory)
        # If the type variable has no bound, then create
        # a variant type argument on the top type.
        # X<T> => X<? extends Object>
        #
        # If the corresponding type parameter is contravariant, then
        # use the wildcard type X<T> => X<?>
        bound, variance = (
            (None, Invariant)
            if t_param.is_contravariant()
            else (
                cfg.bt_factory.get_any_type() if bound is None else bound,
                Covariant
            )
        )
        return WildCardType(bound, variance)
    elif t.is_parameterized():
        return t.to_type_variable_free(factory)
    else:
        return t


def _is_type_arg_contained(t: Type, other: Type,
                           type_param: TypeParameter) -> bool:
    # We implement this function based on the containment rules described
    # here:
    # https://kotlinlang.org/spec/type-system.html#type-containment
    is_wildcard = isinstance(t, WildCardType)
    is_wildcard2 = isinstance(other, WildCardType)
    if not is_wildcard and not is_wildcard2:
        if type_param.is_invariant():
            return t == other
        elif type_param.is_covariant():
            return t.is_subtype(other)
        else:
            return other.is_subtype(t)
    if is_wildcard2 and not is_wildcard and other.bound:
        if other.variance.is_covariant():
            return t.is_subtype(other.bound)
        elif other.variance.is_contravariant():
            return other.bound.is_subtype(t)
    elif is_wildcard and is_wildcard2 and other.bound and t.bound:
        if t.variance.is_covariant() and other.variance.is_covariant():
            return t.bound.is_subtype(other.bound)
        elif t.variance.is_contravariant() and other.variance.is_contravariant():
            return other.bound.is_subtype(t.bound)
    elif is_wildcard and not is_wildcard2 and t.bound:
        if type_param.is_covariant():
            return t.bound.is_subtype(other)
        elif type_param.is_contravariant():
            return other.is_subtype(t.bound)
    if is_wildcard2 and not other.bound:
        if not (is_wildcard and not t.bound):
            return True
    return False


class ParameterizedType(SimpleClassifier):
    def __init__(self, t_constructor: TypeConstructor,
                 type_args: List[Type],
                 can_infer_type_args=False):
        self.t_constructor = copy(t_constructor)
        self.type_args = list(type_args)
        assert len(self.t_constructor.type_parameters) == len(type_args), \
            "You should provide {} types for {}".format(
                len(self.t_constructor.type_parameters), self.t_constructor)
        self._can_infer_type_args = can_infer_type_args
        super().__init__(self.t_constructor.name,
                         self.t_constructor.supertypes)
        # XXX revisit
        self.supertypes = [
            substitute_type(st, self.get_type_variable_assignments())
            for st in self.t_constructor.supertypes
        ]

    def is_parameterized(self):
        return True

    def is_function_type(self):
        return self.t_constructor.name.startswith('Function')

    def is_instance_type(self):
        return isinstance(self.t_constructor, InstanceTypeConstructor)

    def get_type_variable_assignments(self):
        return {
            t_param: self.type_args[i]
            for i, t_param in enumerate(self.t_constructor.type_parameters)
        }

    def has_type_variables(self):
        return any(t_arg.has_type_variables() for t_arg in self.type_args)

    def has_wildcards(self):
        return any(
            t_arg.is_wildcard() or (
                t_arg.is_parameterized() and t_arg.has_wildcards()
            )
            for t_arg in self.type_args
        )

    def has_invariant_wildcards(self):
        return any(
            t_arg.is_wildcard() and t_arg.is_invariant()
            for t_arg in self.type_args
        )

    def to_variance_free(self, type_var_map=None):
        type_args = []
        for i, t_arg in enumerate(self.type_args):
            if t_arg.is_wildcard() and t_arg.bound:
                t_param = self.t_constructor.type_parameters[i]
                bound = t_arg.get_bound_rec()
                t = bound if not type_var_map else type_var_map.get(t_param,
                                                                    bound)
            else:
                t = t_arg
            type_args.append(t)
        return self.t_constructor.new(type_args)

    def to_type_variable_free(self, factory):
        # We translate a parameterized type that contains
        # type variables into a parameterized type that is
        # type variable free.
        type_args = []
        for i, t_arg in enumerate(self.type_args):
            t_param = self.t_constructor.type_parameters[i]
            if t_arg.is_wildcard() and t_arg.is_contravariant():
                if t_arg.bound.has_type_variables():
                    bound, variance = (
                        (None, Invariant)
                        if t_param.is_contravariant()
                        else (factory.get_any_type(), Covariant)
                    )
                    type_args.append(WildCardType(bound, variance))
                else:
                    type_args.append(t_arg)
            elif t_arg.is_wildcard() and t_arg.is_covariant():
                bound = t_arg.get_bound_rec()
                if bound.has_type_variables():
                    type_args.append(
                        _to_type_variable_free(bound, t_param, factory))
                else:
                    type_args.append(t_arg)
            else:
                type_args.append(_to_type_variable_free(t_arg, t_param,
                                                        factory))
        return self.t_constructor.new(type_args)

    def get_type_variables(self, factory) -> Dict[TypeParameter, Set[Type]]:
        # This function actually returns a dict of the enclosing type variables
        # along with the set of their bounds.
        type_vars = defaultdict(set)
        for i, t_arg in enumerate(self.type_args):
            t_arg = t_arg
            if t_arg.is_type_var():
                type_vars[t_arg].add(
                    t_arg.get_bound_rec(factory))
            elif t_arg.is_parameterized() or t_arg.is_wildcard():
                for k, v in t_arg.get_type_variables(factory).items():
                    type_vars[k].update(v)
            else:
                continue
        return type_vars

    @property
    def can_infer_type_args(self):
        return self._can_infer_type_args

    @can_infer_type_args.setter
    def can_infer_type_args(self, value):
        if not isinstance(value, bool):
            raise TypeError("Must be bool")
        self._can_infer_type_args = value

    def __eq__(self, other: Type):
        if not isinstance(other, ParameterizedType):
            return False
        return (self.name == other.name and
                self.t_constructor.__class__ == other.t_constructor.__class__ and
                self.t_constructor == other.t_constructor and
                self.type_args == other.type_args)

    def __hash__(self):
        return hash((self.__class__, self.name, tuple(self.type_args),
                     tuple(self.t_constructor.type_parameters)))

    def __str__(self):
        return "{}<{}>".format(self.name,
                               ", ".join(map(str, self.type_args)))

    def get_name(self):
        return "{}<{}>".format(self.name, ", ".join([t.get_name()
                                                     for t in self.type_args]))

    def is_subtype(self, other: Type) -> bool:
        if super().is_subtype(other):
            return True
        if other.is_parameterized():
            if self.t_constructor == other.t_constructor:
                for tp, sarg, targ in zip(self.t_constructor.type_parameters,
                                          self.type_args, other.type_args):
                    if not _is_type_arg_contained(sarg, targ, tp):
                        return False
                return True
        return False

    def get_supertypes(self):
        """Return self and the transitive closure of the supertypes"""
        supertypes = super().get_supertypes()
        new_supertypes = set()
        assignments = self.get_type_variable_assignments()
        for st in supertypes:
            if st.is_parameterized() and st.name != self.name:
                new_supertypes.add(substitute_type(st, assignments))
            else:
                new_supertypes.add(st)
        return new_supertypes

    def is_assignable(self, other: Type):
        # Import here to prevent circular dependency.
        from src.ir import java_types as jt
        # We should handle Java primitive arrays
        # In Java Byte[] is not assignable to byte[] and vice versa.
        if (self.t_constructor == jt.Array and
                other.is_parameterized() and
                other.t_constructor == jt.Array):
            self_t = self.type_args[0]
            other_t = other.type_args[0]
            self_is_primitive = getattr(self_t, 'primitive', False)
            other_is_primitive = getattr(other_t, 'primitive', False)
            if self_is_primitive or other_is_primitive:
                if (self_t == other_t and
                        self_is_primitive and other_is_primitive):
                    return True
                return False
        return self.is_subtype(other)


class InstanceTypeConstructor(TypeConstructor):
    def __init__(self, name: str, enclosing_type: TypeConstructor,
                 basename: str,
                 extra_type_params: List[TypeParameter] = [],
                 supertypes: List[Type] = []):
        assert enclosing_type is not None and \
            enclosing_type.is_type_constructor()
        self.enclosing_type = enclosing_type
        self.extra_type_params = extra_type_params
        self.basename = basename
        type_parameters = enclosing_type.type_parameters + extra_type_params
        super().__init__(name, type_parameters, supertypes)


class NothingType(Classifier):
    def __init__(self):
        super().__init__("Nothing")

    def is_subtype(self, other: Type):
        return True


Nothing = NothingType()
