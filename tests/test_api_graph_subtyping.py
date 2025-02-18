from src.generators.api import api_graph as ag
from src.generators.api.builder import (JavaAPIGraphBuilder,
                                        ScalaAPIGraphBuilder)


DOCS1 = {
    "java.StringList": {
        "name": "java.StringList",
        "inherits": ["java.util.LinkedList<java.lang.String>"],
        "implements": [],
        "fields": [],
        "methods": [],
        "type_parameters": []
    },
    "java.IntegerList": {
        "name": "java.IntegerList",
        "inherits": ["java.util.LinkedList<java.lang.Integer>"],
        "implements": [],
        "fields": [],
        "methods": [],
        "type_parameters": []
    },
    "java.util.List": {
        "name": "java.util.List",
        "inherits": ["java.lang.Object"],
        "implements": [],
        "fields": [],
        "methods": [],
        "type_parameters": ["T"]
    },
    "java.util.LinkedList": {
        "name": "java.util.LinkedList",
        "inherits": ["java.util.List<T>"],
        "implements": [],
        "fields": [],
        "methods": [],
        "type_parameters": ["T"]
    }
}


DOCS2 = {
   "java.Number": {
        "name": "java.Number",
        "inherits": ["java.lang.Object"],
        "implements": [],
        "fields": [],
        "methods": [],
        "type_parameters": []
    },
    "java.Integer": {
        "name": "java.Integer",
        "inherits": ["java.Number"],
        "implements": [],
        "fields": [],
        "methods": [],
        "type_parameters": []
    },
    "java.Long": {
        "name": "java.Long",
        "inherits": ["java.Number"],
        "implements": [],
        "fields": [],
        "methods": [],
        "type_parameters": []
    },
    "java.String": {
        "name": "java.String",
        "inherits": ["java.lang.Object"],
        "implements": [],
        "fields": [],
        "methods": [],
        "type_parameters": []
    },
}


DOCS3 = {
    "java.Map": {
        "name": "java.Map",
        "inherits": ["java.lang.Object"],
        "implements": [],
        "fields": [],
        "methods": [],
        "type_parameters": ["K", "V"]
    },
    "java.HashMap": {
        "name": "java.HashMap",
        "inherits": ["java.Map<K,V>"],
        "implements": [],
        "fields": [],
        "methods": [],
        "type_parameters": ["K", "V"]
    },
    "java.Foo": {
        "name": "java.Foo",
        "inherits": ["java.HashMap<java.lang.String,T>"],
        "implements": [],
        "fields": [],
        "methods": [],
        "type_parameters": ["T"]
    },
    "java.Bar": {
        "name": "java.Bar",
        "inherits": ["java.Foo<java.Map<java.lang.String,java.lang.Integer>>"],
        "implements": [],
        "fields": [],
        "methods": [],
        "type_parameters": []
    }
}


DOCS4 = {
    "java.Map": {
        "name": "java.Map",
        "inherits": ["java.lang.Object"],
        "implements": [],
        "fields": [],
        "methods": [],
        "type_parameters": ["K", "V"]
    },
    "java.Stream": {
        "name": "java.Stream",
        "inherits": ["java.Map<T,java.Map<T,java.lang.String>>"],
        "implements": [],
        "fields": [],
        "methods": [],
        "type_parameters": ["T"]
    },
    "java.Foo": {
        "name": "java.Foo",
        "inherits": ["java.Stream<java.lang.Object>"],
        "implements": [],
        "fields": [],
        "methods": [],
        "type_parameters": []
    },
}


DOCS5 = {
    "java.util.Spliterator.OfInt": {
        "name": "java.util.Spliterator.OfInt",
        "type_parameters": [],
        "implements": [],
        "inherits": [
          "java.util.Spliterator.OfPrimitive<java.lang.Integer,java.lang.Integer,java.util.Spliterator.OfInt>"
        ],
        "methods": [],
        "fields": []

    },
    "java.util.Spliterator.OfPrimitive": {
        "name": "java.util.Spliterator.OfPrimitive",
        "type_parameters": [
          "T",
          "T_CONS",
          "T_SPLITR extends Spliterator.OfPrimitive<T,T_CONS,T_SPLITR>"
        ],
        "implements": [],
        "inherits": ["java.lang.Object"],
        "methods": [],
        "fields": []
    }
}


DOCS6 = {
    "java.Comparable": {
        "name": "java.Comparable",
        "inherits": ["java.lang.Object"],
        "implements": [],
        "fields": [],
        "methods": [],
        "type_parameters": ["T"]
    },
    "java.String": {
        "name": "java.String",
        "inherits": ["java.Comparable<java.String>"],
        "implements": [],
        "fields": [],
        "methods": [],
        "type_parameters": []
    },
    "java.Foo": {
        "name": "java.Foo",
        "inherits": ["java.Comparable<java.Foo<T>>"],
        "implements": [],
        "fields": [],
        "methods": [],
        "type_parameters": ["T"]
    },
    "java.BaseStream": {
        "name": "java.BaseStream",
        "inherits": ["java.lang.Object"],
        "implements": [],
        "fields": [],
        "methods": [],
        "type_parameters": ["T", "S"]
    },
    "java.Stream": {
        "name": "java.Stream",
        "inherits": ["java.BaseStream<T,java.Stream<T>>"],
        "implements": [],
        "fields": [],
        "methods": [],
        "type_parameters": ["T"]
    }

}


def test_subtypes1():
    b = JavaAPIGraphBuilder("java")
    api_graph = b.build(DOCS1)

    # Case 1
    subtypes = api_graph.subtypes(b.parse_type(
        "java.util.List<java.lang.Object>"))
    assert subtypes == {
        b.parse_type("java.util.List<java.lang.Object>"),
        b.parse_type("java.util.LinkedList<java.lang.Object>"),
    }

    # Case 2
    subtypes = api_graph.subtypes(b.parse_type(
        "java.util.List<java.lang.String>"))
    assert subtypes == {
        b.parse_type("java.util.List<java.lang.String>"),
        b.parse_type("java.util.LinkedList<java.lang.String>"),
        b.parse_type("java.StringList")
    }

    # Case 3
    subtypes = api_graph.subtypes(b.parse_type(
        "java.util.List<java.lang.Integer>"))
    assert subtypes == {
        b.parse_type("java.util.List<java.lang.Integer>"),
        b.parse_type("java.util.LinkedList<java.lang.Integer>"),
        b.parse_type("java.IntegerList")
    }

    # Case 4
    subtypes = api_graph.subtypes(b.parse_type("java.util.List<T>"))
    assert subtypes == {
        b.parse_type("java.util.List<T>"),
        b.parse_type("java.util.LinkedList<T>"),
    }

    subtypes = api_graph.subtypes(b.parse_type(
        "java.util.List<? extends java.lang.String>"))
    assert subtypes == {
        b.parse_type("java.util.List<? extends java.lang.String>"),
        b.parse_type("java.util.List<java.lang.String>"),
        b.parse_type("java.util.LinkedList<java.lang.String>"),
        b.parse_type("java.StringList")
    }


def test_subtypes2():
    b = JavaAPIGraphBuilder("java")
    api_graph = b.build(DOCS2)

    # Case 1
    subtypes = api_graph.subtypes(b.parse_type("java.lang.Object"))
    assert subtypes == {
        b.parse_type("java.lang.Object"),
        b.parse_type("java.Number"),
        b.parse_type("java.Integer"),
        b.parse_type("java.Long"),
        b.parse_type("java.String"),
    }

    # Case 2
    subtypes = api_graph.subtypes(b.parse_type("java.Number"))
    assert subtypes == {
        b.parse_type("java.Number"),
        b.parse_type("java.Integer"),
        b.parse_type("java.Long"),
    }

    # Case 3
    subtypes = api_graph.subtypes(b.parse_type("java.String"))
    assert subtypes == { b.parse_type("java.String") }


def test_subtypes3():
    b = JavaAPIGraphBuilder("java")
    api_graph = b.build(DOCS3)
    subtypes = api_graph.subtypes(b.parse_type(
        "java.Map<T1,java.lang.String>"))
    assert subtypes == {
        b.parse_type("java.Map<T1,java.lang.String>"),
        b.parse_type("java.HashMap<T1,java.lang.String>"),
    }

    subtypes = api_graph.subtypes(b.parse_type(
        "java.HashMap<java.lang.String,java.lang.Integer>"))
    assert subtypes == {
        b.parse_type("java.HashMap<java.lang.String,java.lang.Integer>"),
        b.parse_type("java.Foo<java.lang.Integer>"),
    }

    subtypes = api_graph.subtypes(b.parse_type(
        "java.Map<java.lang.String,java.Map<java.lang.String,java.lang.Integer>>"))
    assert subtypes == {
        b.parse_type("java.Map<java.lang.String,java.Map<java.lang.String,java.lang.Integer>>"),
        b.parse_type("java.HashMap<java.lang.String,java.Map<java.lang.String,java.lang.Integer>>"),
        b.parse_type("java.Foo<java.Map<java.lang.String,java.lang.Integer>>"),
        b.parse_type("java.Bar"),
    }


def test_subtypes4():
    b = JavaAPIGraphBuilder("java")
    api_graph = b.build(DOCS4)
    subtypes = api_graph.subtypes(b.parse_type(
        "java.Map<T1,java.lang.String>"))
    assert subtypes == {
        b.parse_type("java.Map<T1,java.lang.String>"),
    }

    subtypes = api_graph.subtypes(b.parse_type(
        "java.Map<F,java.Map<F,java.lang.Integer>>"))
    assert subtypes == {
        b.parse_type("java.Map<F,java.Map<F,java.lang.Integer>>"),
    }

    subtypes = api_graph.subtypes(b.parse_type(
        "java.Map<F,java.Map<F,java.lang.String>>"))
    assert subtypes == {
        b.parse_type("java.Map<F,java.Map<F,java.lang.String>>"),
        b.parse_type("java.Stream<F>"),
    }


def test_subtypes6():
    b = JavaAPIGraphBuilder("java")
    api_graph = b.build(DOCS2)

    # Case 1
    subtypes = api_graph.subtypes(b.parse_type("java.lang.Object[]"))
    assert subtypes == {
        b.parse_type("java.lang.Object[]"),
    }

    # Case 2
    subtypes = api_graph.subtypes(b.parse_type("java.Number[]"))
    assert subtypes == {
        b.parse_type("java.Number[]"),
        b.parse_type("java.Integer[]"),
        b.parse_type("java.Long[]"),
    }

    # Case 3
    subtypes = api_graph.subtypes(b.parse_type("java.String[]"))
    assert subtypes == { b.parse_type("java.String[]") }


def test_supertypes1():
    b = JavaAPIGraphBuilder("java")
    api_graph = b.build(DOCS1)

    supertypes = api_graph.supertypes(b.parse_type("java.lang.Object"))
    assert supertypes == set()

    supertypes = api_graph.supertypes(b.parse_type("java.StringList"))
    assert supertypes == {
        b.parse_type("java.lang.Object"),
        b.parse_type("java.util.List<java.lang.String>"),
        b.parse_type("java.util.LinkedList<java.lang.String>"),
    }

    supertypes = api_graph.supertypes(b.parse_type(
        "java.util.LinkedList<java.lang.Object>"))
    assert supertypes == {
        b.parse_type("java.lang.Object"),
        b.parse_type("java.util.List<java.lang.Object>"),
    }

    supertypes = api_graph.supertypes(b.parse_type(
        "java.util.List<java.lang.Object>"))
    assert supertypes == {
        b.parse_type("java.lang.Object"),
    }


def test_supertypes2():
    b = JavaAPIGraphBuilder("java")
    api_graph = b.build(DOCS2)

    supertypes = api_graph.supertypes(b.parse_type("java.String"))
    assert supertypes == {
        b.parse_type("java.lang.Object"),
    }

    supertypes = api_graph.supertypes(b.parse_type("java.Long"))
    assert supertypes == {
        b.parse_type("java.lang.Object"),
        b.parse_type("java.Number"),
    }


def test_supertypes3():
    b = JavaAPIGraphBuilder("java")
    api_graph = b.build(DOCS3)

    supertypes = api_graph.supertypes(b.parse_type(
        "java.Foo<java.lang.Integer>"))
    assert supertypes == {
        b.parse_type("java.HashMap<java.lang.String,java.lang.Integer>"),
        b.parse_type("java.Map<java.lang.String,java.lang.Integer>"),
        b.parse_type("java.lang.Object"),
    }

    supertypes = api_graph.supertypes(b.parse_type(
        "java.Bar"))
    assert supertypes == {
        b.parse_type("java.Foo<java.Map<java.lang.String,java.lang.Integer>>"),
        b.parse_type("java.HashMap<java.lang.String,java.Map<java.lang.String,java.lang.Integer>>"),
        b.parse_type("java.Map<java.lang.String,java.Map<java.lang.String,java.lang.Integer>>"),
        b.parse_type("java.lang.Object"),
    }


def test_supertypes4():
    b = JavaAPIGraphBuilder("java")
    api_graph = b.build(DOCS4)

    supertypes = api_graph.supertypes(b.parse_type("java.Stream<K>"))
    assert supertypes == {
        b.parse_type("java.Map<K,java.Map<K,java.lang.String>>"),
        b.parse_type("java.lang.Object"),
    }

    supertypes = api_graph.supertypes(b.parse_type(
        "java.Foo"))
    assert supertypes == {
        b.parse_type("java.Stream<java.lang.Object>"),
        b.parse_type("java.Map<java.lang.Object,java.Map<java.lang.Object,java.lang.String>>"),
        b.parse_type("java.lang.Object"),
    }


def test_supertypes5():
    b = JavaAPIGraphBuilder("java")
    api_graph = b.build(DOCS5)

    supertypes = api_graph.supertypes(b.parse_type(
        "java.util.Spliterator.OfInt"))
    assert supertypes == {
        b.parse_type("java.lang.Object"),
        b.parse_type(
            "java.util.Spliterator.OfPrimitive<java.lang.Integer,java.lang.Integer,java.util.Spliterator.OfInt>")
    }


DOCS7 = {
    "scala.IterableOps": {
        "language": "scala",
        "name": "scala.IterableOps",
        "inherits": ["scala.AnyRef"],
        "implements": [],
        "fields": [],
        "methods": [],
        "type_parameters": ["+A", "+CC[_]", "+C"]
    },
    "scala.IterableFactoryDefaults": {
        "language": "scala",
        "name": "scala.IterablefactoryDefaults",
        "inherits": ["scala.IterableOps[A,CC,CC[A]]"],
        "implements": [],
        "fields": [],
        "methods": [],
        "type_parameters": [
            "+A",
            "+CC[x] <: scala.IterableOps[x,CC,CC[x]]"
        ]
    },
    "scala.View": {
        "language": "scala",
        "name": "scala.View",
        "inherits": ["scala.IterableOps[A,scala.View,scala.View[A]]"],
        "implements": [],
        "fields": [],
        "methods": [],
        "type_parameters": ["+A"]
    },
    "scala.Iterable": {
        "language": "scala",
        "name": "scala.Iterable",
        "inherits": ["scala.IterableOps[A,scala.Iterable,scala.Iterable[A]]"],
        "implements": [],
        "fields": [],
        "methods": [],
        "type_parameters": ["+A"]
    },
    "scala.SeqView": {
        "language": "scala",
        "name": "scala.SeqView",
        "inherits": ["scala.View[A]"],
        "implements": [],
        "fields": [],
        "methods": [],
        "type_parameters": ["+A"]
    },
    "scala.MyView": {
        "language": "scala",
        "name": "scala.MyView",
        "inherits": ["scala.IterableOps[scala.String,scala.View,scala.View[scala.String]]"],
        "implements": [],
        "fields": [],
        "methods": [],
        "type_parameters": ["+A"]
    }

}


def test_get_instantiations_of_recursive_bound():
    b = JavaAPIGraphBuilder("java")
    api_graph = b.build(DOCS6)

    # Case 1
    type_param = b.parse_type("R extends java.Comparable<R>")
    types = api_graph.get_instantiations_of_recursive_bound(
        type_param, {}, {b.parse_type("java.lang.String")})
    assert types == {b.parse_type("java.String"),
                     b.parse_type("java.Foo<java.lang.String>")}

    # Case 2
    type_param = b.parse_type("R extends java.Comparable<java.lang.Integer>")
    types = api_graph.get_instantiations_of_recursive_bound(type_param, {})
    assert types == set()

    # Case 3
    type_param = b.parse_type("R extends java.Comparable<java.String>")
    types = api_graph.get_instantiations_of_recursive_bound(type_param, {})
    assert types == {b.parse_type("java.String")}

    # Case 4 / BaseStream
    b._class_name = "java.BaseStream"
    type_param = b.parse_type("L extends java.BaseStream<K,L>")
    type_var_map = {b.parse_type("K"): b.parse_type("java.lang.Object")}
    types = api_graph.get_instantiations_of_recursive_bound(
        type_param, type_var_map)
    assert types == { b.parse_type("java.Stream<java.lang.Object>") }


def test_get_instantiations_of_recursive_bound_hk_types():
    b = ScalaAPIGraphBuilder("scala")
    api_graph = b.build(DOCS7)

    # Case 1
    type_param = b.parse_type("CC[x] <: scala.IterableOps[x,CC,CC[x]]")
    types = api_graph.get_instantiations_of_recursive_bound(
        type_param, {}, api_graph.get_reg_types())
    assert types == {b.parse_type("scala.Iterable"), b.parse_type("scala.View")}

    # Case 2
    type_param = b.parse_type("CC[x] <: scala.IterableOps[scala.Int,CC,CC[x]]")
    types = api_graph.get_instantiations_of_recursive_bound(
        type_param, {}, api_graph.get_reg_types())
    assert types == set()

    # Case 3
    type_param = b.parse_type("CC[x] <: scala.IterableOps[scala.String,scala.View,scala.View[scala.String]]")
    types = api_graph.get_instantiations_of_recursive_bound(
        type_param, {}, api_graph.get_reg_types())
    assert types == {b.parse_type("scala.MyView")}

    # Case 4
    type_param = b.parse_type("CC[x] <: scala.IterableOps[scala.String,CC,CC[x]]")
    types = api_graph.get_instantiations_of_recursive_bound(
        type_param, {}, api_graph.get_reg_types())
    assert types == set()
