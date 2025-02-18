# pylint: disable=abstract-method, useless-super-delegation,too-many-ancestors
from typing import List

from src.ir.types import Builtin

import src.ir.builtins as bt
import src.ir.types as tp


class GroovyBuiltinFactory(bt.BuiltinFactory):
    def get_language(self):
        return "groovy"

    def get_builtin(self):
        return GroovyBuiltin

    def get_void_type(self):
        return VoidType(primitive=True)

    def get_any_type(self):
        return ObjectType()

    def get_number_type(self):
        return NumberType()

    def get_integer_type(self, primitive=False):
        return IntegerType(primitive=primitive)

    def get_byte_type(self, primitive=False):
        return ByteType(primitive=primitive)

    def get_short_type(self, primitive=False):
        return ShortType(primitive=primitive)

    def get_long_type(self, primitive=False):
        return LongType(primitive=primitive)

    def get_float_type(self, primitive=False):
        return FloatType(primitive=primitive)

    def get_double_type(self, primitive=False):
        return DoubleType(primitive=primitive)

    def get_big_decimal_type(self):
        return BigDecimalType()

    def get_boolean_type(self, primitive=False):
        return BooleanType(primitive=primitive)

    def get_char_type(self, primitive=False):
        return CharType(primitive=primitive)

    def get_string_type(self):
        return StringType()

    def get_array_type(self):
        return ArrayType()

    def get_function_type(self, nr_parameters=0):
        return FunctionType(nr_parameters)

    def get_big_integer_type(self):
        return BigIntegerType()

    def get_primitive_types(self):
        return [
            ByteType(primitive=True),
            ShortType(primitive=True),
            IntegerType(primitive=True),
            LongType(primitive=True),
            FloatType(primitive=True),
            DoubleType(primitive=True),
            CharType(primitive=True),
            BooleanType(primitive=True)
        ]

    def get_non_nothing_types(self):
        return super().get_non_nothing_types() + self.get_primitive_types()

    def get_number_types(self):
        return super().get_number_types() + self.get_primitive_types()[:-1]

    def get_raw_type(self, t_constructor):
        return RawType(t_constructor)

    def get_raw_cls(self):
        return RawType


class GroovyBuiltin(Builtin):
    def __init__(self, name, primitive):
        super().__init__(name)
        self.primitive = primitive

    def __str__(self):
        if not self.is_primitive():
            return str(self.name) + "(groovy-builtin)"
        return str(self.name).lower() + "(groovy-primitive)"

    def __hash__(self):
        return hash((self.__class__, self.name, self.primitive))

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self.name == other.name and
            self.primitive == other.primitive and
            self.supertypes == other.supertypes
        )

    def is_primitive(self):
        return self.primitive

    def box_type(self):
        raise NotImplementedError('box_type() must be implemented')


class ObjectType(GroovyBuiltin):
    def __init__(self, name="Object"):
        super().__init__(name, False)

    def get_builtin_type(self):
        return bt.Any

    def box_type(self):
        return self


class VoidType(GroovyBuiltin):
    def __init__(self, name="Void", primitive=False):
        super().__init__(name, primitive)
        if not self.primitive:
            self.supertypes.append(ObjectType())
        else:
            self.supertypes = set()

    def get_builtin_type(self):
        return bt.Void

    def box_type(self):
        return VoidType(self.name, primitive=False)

    def get_name(self):
        if self.is_primitive():
            return "void"
        return super().get_name()


class NumberType(ObjectType):
    def __init__(self, name="Number"):
        super().__init__(name)
        self.supertypes.append(ObjectType())

    def get_builtin_type(self):
        return bt.Number

    def box_type(self):
        return self


class IntegerType(NumberType):
    def __init__(self, name="Integer", primitive=False):
        super().__init__(name)
        self.primitive = primitive
        if not self.primitive:
            self.supertypes.append(NumberType())
        else:
            self.supertypes = set()

    def get_builtin_type(self):
        return bt.Integer

    def box_type(self):
        return IntegerType(self.name, primitive=False)

    def is_assignable(self, other):
        assignable_types = (NumberType, IntegerType,)
        return self.is_subtype(other) or type(other) in assignable_types

    def get_name(self):
        if self.is_primitive():
            return "int"
        return super().get_name()


class ShortType(NumberType):
    def __init__(self, name="Short", primitive=False):
        super().__init__(name)
        self.primitive = primitive
        if not self.primitive:
            self.supertypes.append(NumberType())
        else:
            self.supertypes = set()

    def get_builtin_type(self):
        return bt.Short

    def box_type(self):
        return ShortType(self.name, primitive=False)

    def is_assignable(self, other):
        assignable_types = (NumberType, ShortType,)
        return self.is_subtype(other) or type(other) in assignable_types

    def get_name(self):
        if self.is_primitive():
            return "short"
        return super().get_name()


class LongType(NumberType):
    def __init__(self, name="Long", primitive=False):
        super().__init__(name)
        self.primitive = primitive
        if not self.primitive:
            self.supertypes.append(NumberType())
        else:
            self.supertypes = set()

    def get_builtin_type(self):
        return bt.Long

    def box_type(self):
        return LongType(self.name, primitive=False)

    def is_assignable(self, other):
        assignable_types = (NumberType, LongType,)
        return self.is_subtype(other) or type(other) in assignable_types

    def get_name(self):
        if self.is_primitive():
            return "long"
        return super().get_name()


class BigIntegerType(NumberType):
    def __init__(self, name="BigInteger"):
        super().__init__(name)
        self.supertypes.append(NumberType())

    def get_builtin_type(self):
        return bt.BigIntegerType

    def box_type(self):
        return self

    def is_assignable(self, other):
        assignable_types = (NumberType, BigIntegerType,)
        return self.is_subtype(other) or type(other) in assignable_types


class ByteType(NumberType):
    def __init__(self, name="Byte", primitive=False):
        super().__init__(name)
        self.primitive = primitive
        if not self.primitive:
            self.supertypes.append(NumberType())
        else:
            self.supertypes = set()

    def get_builtin_type(self):
        return bt.Byte

    def box_type(self):
        return ByteType(self.name, primitive=False)

    def is_assignable(self, other):
        assignable_types = (NumberType, ByteType,)
        return self.is_subtype(other) or type(other) in assignable_types

    def get_name(self):
        if self.is_primitive():
            return "byte"
        return super().get_name()


class FloatType(NumberType):
    def __init__(self, name="Float", primitive=False):
        super().__init__(name)
        self.primitive = primitive
        if not self.primitive:
            self.supertypes.append(NumberType())
        else:
            self.supertypes = set()

    def get_builtin_type(self):
        return bt.Float

    def box_type(self):
        return FloatType(self.name, primitive=False)

    def is_assignable(self, other):
        assignable_types = (NumberType, FloatType,)
        return self.is_subtype(other) or type(other) in assignable_types

    def get_name(self):
        if self.is_primitive():
            return "float"
        return super().get_name()


class DoubleType(NumberType):
    def __init__(self, name="Double", primitive=False):
        super().__init__(name)
        self.primitive = primitive
        if not self.primitive:
            self.supertypes.append(NumberType())
        else:
            self.supertypes = set()

    def get_builtin_type(self):
        return bt.Double

    def box_type(self):
        return DoubleType(self.name, primitive=False)

    def is_assignable(self, other):
        assignable_types = (NumberType, DoubleType,)
        return self.is_subtype(other) or type(other) in assignable_types

    def get_name(self):
        if self.is_primitive():
            return "double"
        return super().get_name()


class BigDecimalType(NumberType):
    """Default decimal type in groovy.

    d = 10.5; assert d instanceof BigDecimal
    d = 10.5d; assert d instanceof Double
    d = 10.5f; assert d instanceof Float
    """
    def __init__(self, name="BigDecimal"):
        super().__init__(name)
        self.supertypes.append(NumberType())

    def get_builtin_type(self):
        return bt.BigDecimal

    def box_type(self):
        return self


class CharType(ObjectType):
    def __init__(self, name="Character", primitive=False):
        super().__init__(name)
        self.primitive = primitive
        if not self.primitive:
            self.supertypes.append(ObjectType())
        else:
            self.supertypes = set()

    def get_builtin_type(self):
        return bt.Char

    def box_type(self):
        return CharType(self.name, primitive=False)

    def get_name(self):
        if self.is_primitive():
            return "char"
        return super().get_name()


class StringType(ObjectType):
    def __init__(self, name="String"):
        super().__init__(name)
        self.supertypes.append(ObjectType())

    def get_builtin_type(self):
        return bt.String

    def box_type(self):
        return self


class BooleanType(ObjectType):
    def __init__(self, name="Boolean", primitive=False):
        super().__init__(name)
        self.primitive = primitive
        if not self.primitive:
            self.supertypes.append(ObjectType())
        else:
            self.supertypes = set()

    def get_builtin_type(self):
        return bt.Boolean

    def box_type(self):
        return BooleanType(self.name, primitive=False)

    def get_name(self):
        if self.is_primitive():
            return "boolean"
        return super().get_name()


class RawType(tp.SimpleClassifier):
    def __init__(self, t_constructor: tp.TypeConstructor):
        self._name = t_constructor.name
        self.name = f"Raw{self._name}"
        self.t_constructor = t_constructor
        self.supertypes = []
        for supertype in t_constructor.supertypes:
            if not supertype.is_parameterized():
                self.supertypes.append(supertype)
            else:
                # Consider B<T> : A<T>
                # We convert the supertype A<T> to A<?>.
                sub = {type_param: tp.WildCardType()
                       for type_param in self.t_constructor.type_parameters}
                self.supertypes.append(tp.substitute_type(supertype, sub))
        self.supertypes.append(ObjectType())

    def get_name(self):
        return self._name


class ArrayType(tp.TypeConstructor, ObjectType):
    def __init__(self, name="Array"):
        # In Groovy, arrays are covariant.
        super().__init__(name, [tp.TypeParameter(
            "T", variance=tp.Covariant)])
        self.supertypes.append(ObjectType())


class FunctionType(tp.TypeConstructor, ObjectType):
    is_native = True

    def __init__(self, nr_type_parameters: int):
        name = "Function" + str(nr_type_parameters)
        type_parameters = [
            tp.TypeParameter("A" + str(i))
            for i in range(1, nr_type_parameters + 1)
        ] + [tp.TypeParameter("R")]
        self.nr_type_parameters = nr_type_parameters
        super().__init__(name, type_parameters)
        self.supertypes.append(ObjectType())

    @classmethod
    def match_function(cls, receiver_type: tp.Type, ret_type: tp.Type,
                       param_types: List[tp.Type],
                       target_type: tp.Type,
                       bt_factory: bt.BuiltinFactory,
                       func_metadata: dict = {}):
        import src.ir.type_utils as tu
        api_type = FunctionType(
            len(param_types)).new(param_types + [ret_type])
        sub = tu.unify_types(target_type, api_type, bt_factory, same_type=True)
        if any(v == bt_factory.get_void_type()
               for v in sub.values()):
            # We don't want to match something that is needed to be
            # instantiated with void, e.g.,
            # Consumer<Int> != Function<Int, void>
            return False, None
        if sub or target_type == api_type:
            return True, sub
        return False, None

    @classmethod
    def get_param_types(cls, etype: tp.ParameterizedType):
        return etype.type_args[:-1]

    @classmethod
    def get_ret_type(cls, etype: tp.ParameterizedType):
        return etype.type_args[-1]


Object = ObjectType()
Void = VoidType()
Number = NumberType()
Integer = IntegerType()
IntPrimitive = IntegerType(primitive=True)
Short = ShortType()
ShortPrimitive = ShortType(primitive=True)
Long = LongType()
LongPrimitive = LongType(primitive=True)
Byte = ByteType()
BytePrimitive = ByteType(primitive=True)
Float = FloatType()
FloatPrimitive = FloatType(primitive=True)
Double = DoubleType()
DoublePrimitive = DoubleType(primitive=True)
BigDecimal = BigDecimalType()
BigInteger = BigIntegerType()
Char = CharType()
CharPrimitive = CharType(primitive=True)
String = StringType()
Boolean = BooleanType()
BooleanPrimitive = BooleanType(primitive=True)
Array = ArrayType()
NonNothingTypes = [Object, Number, Integer, Short, Long, Byte, Float,
                   Double, BigDecimal, BigInteger, Char, String, Boolean,
                   Array]
