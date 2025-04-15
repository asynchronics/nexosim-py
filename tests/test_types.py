import dataclasses

import pytest

from nexosim._config import cbor2_converter
from nexosim.types import UnitType, enumclass, tuple_type


@pytest.fixture
def tuple_type_0_arg():
    """A zero-arg tuple type class."""

    class MyTupleType(tuple_type()): ...

    return MyTupleType


@pytest.fixture
def tuple_type_1_arg():
    """A TupleType[float] class."""

    class MyTupleType(tuple_type(float)): ...

    return MyTupleType


@pytest.fixture
def tuple_type_2_arg():
    """A TupleType[float, str] class."""

    class MyTupleType(tuple_type(float, str)): ...

    return MyTupleType


@pytest.fixture
def unit_type():
    """A unit type class."""

    class MyUnitType(UnitType): ...

    return MyUnitType


@pytest.fixture
def struct_type():
    """A struct type class (dataclass)."""

    @dataclasses.dataclass
    class MyStructType:
        foo: int
        bar: str

    return MyStructType


@pytest.fixture
def enum_type(
    unit_type, tuple_type_0_arg, tuple_type_1_arg, tuple_type_2_arg, struct_type
):
    @enumclass
    class MyEnumType:
        MyUnitVariant = unit_type
        My0ArgTupleVariant = tuple_type_0_arg
        My1ArgTupleVariant = tuple_type_1_arg
        My2ArgTupleVariant = tuple_type_2_arg
        MyStructVariant = struct_type

    return MyEnumType


@pytest.fixture
def empty_class():
    """A class without any members."""

    class A: ...

    return A


class TestUnitType:
    def test_repr(self, unit_type):
        assert repr(unit_type()).endswith("MyUnitType")

    def test_structure_hook(self, unit_type):
        f = cbor2_converter.get_structure_hook(unit_type)

        assert isinstance(f(None, unit_type), unit_type)

    def test_unstructure_hook(self, unit_type):
        f = cbor2_converter.get_unstructure_hook(unit_type)

        assert f(unit_type()) is None


class TestTupleType:
    def test_structure_hook_0_arg(self, tuple_type_0_arg):
        f = cbor2_converter.get_structure_hook(tuple_type_0_arg)

        assert f(None, tuple_type_0_arg) == tuple_type_0_arg()

    def test_structure_hook_1_arg(self, tuple_type_1_arg):
        f = cbor2_converter.get_structure_hook(tuple_type_1_arg)

        assert f(0.0, tuple_type_1_arg) == tuple_type_1_arg(0.0)

    def test_structure_hook_2_arg(self, tuple_type_2_arg):
        f = cbor2_converter.get_structure_hook(tuple_type_2_arg)

        assert f((0.0, "s"), tuple_type_2_arg) == tuple_type_2_arg(0.0, "s")

    def test_unstructure_hook_0_arg(self, tuple_type_0_arg):
        f = cbor2_converter.get_unstructure_hook(tuple_type_0_arg)

        assert f(tuple_type_0_arg()) == []

    def test_unstructure_hook_1_arg(self, tuple_type_1_arg):
        f = cbor2_converter.get_unstructure_hook(tuple_type_1_arg)

        assert f(tuple_type_1_arg(0.0)) == 0.0

    def test_unstructure_hook_2_arg(self, tuple_type_2_arg):
        f = cbor2_converter.get_unstructure_hook(tuple_type_2_arg)

        assert f(tuple_type_2_arg(0.0, "s")) == [0.0, "s"]

    def test_repr_0_arg(self, tuple_type_0_arg):
        assert repr(tuple_type_0_arg()).endswith("MyTupleType()")

    def test_repr_1_arg(self, tuple_type_1_arg):
        assert repr(tuple_type_1_arg(0.0)).endswith("MyTupleType(0.0)")

    def test_repr_2_arg(self, tuple_type_2_arg):
        assert repr(tuple_type_2_arg(0.0, "s")).endswith("MyTupleType(0.0, 's')")


class TestEnumType:
    def test_unstructure_unit_variant(self, enum_type):
        cls = enum_type.MyUnitVariant
        f = cbor2_converter.get_unstructure_hook(cls)

        assert f(cls) == {"MyUnitVariant": None}

    def test_unstructure_0_arg_tuple_variant(self, enum_type):
        cls = enum_type.My0ArgTupleVariant
        f = cbor2_converter.get_unstructure_hook(cls)

        assert f(cls()) == {"My0ArgTupleVariant": []}

    def test_unstructure_1_arg_tuple_variant(self, enum_type):
        cls = enum_type.My1ArgTupleVariant
        f = cbor2_converter.get_unstructure_hook(cls)

        assert f(cls(0.0)) == {"My1ArgTupleVariant": 0.0}

    def test_unstructure_2_arg_tuple_variant(self, enum_type):
        cls = enum_type.My2ArgTupleVariant
        f = cbor2_converter.get_unstructure_hook(cls)

        assert f(cls(0.0, "s")) == {"My2ArgTupleVariant": [0.0, "s"]}

    def test_unstructure_struct_variant(self, enum_type):
        cls = enum_type.MyStructVariant
        f = cbor2_converter.get_unstructure_hook(cls)

        assert f(cls(1, "s")) == {"MyStructVariant": {"foo": 1, "bar": "s"}}

    def test_structure_unit_variant(self, enum_type):
        cls = enum_type.MyUnitVariant
        f = cbor2_converter.get_structure_hook(enum_type.type)

        assert isinstance(f("MyUnitVariant", enum_type.type), cls)

    def test_structure_0_arg_tuple_variant(self, enum_type):
        cls = enum_type.My0ArgTupleVariant
        f = cbor2_converter.get_structure_hook(enum_type.type)

        assert f({"My0ArgTupleVariant": []}, enum_type.type) == cls()

    def test_structure_1_arg_tuple_variant(self, enum_type):
        cls = enum_type.My1ArgTupleVariant
        f = cbor2_converter.get_structure_hook(enum_type.type)

        assert f({"My1ArgTupleVariant": 0.0}, enum_type.type) == cls(0.0)

    def test_structure_2_arg_tuple_variant(self, enum_type):
        cls = enum_type.My2ArgTupleVariant
        f = cbor2_converter.get_structure_hook(enum_type.type)

        assert f({"My2ArgTupleVariant": [0.0, "s"]}, enum_type.type) == cls(0.0, "s")

    def test_structure_struct_variant(self, enum_type):
        cls = enum_type.MyStructVariant
        f = cbor2_converter.get_structure_hook(enum_type.type)

        assert f({"MyStructVariant": {"foo": 1, "bar": "s"}}, enum_type.type) == cls(
            1, "s"
        )

    def test_structure_multi_key_dict_value_error(self, enum_type):
        f = cbor2_converter.get_structure_hook(enum_type.type)

        with pytest.raises(ValueError):
            f({"foo": 1, "bar": "s"}, enum_type.type)

    def test_structure_unexpected_type_value_error(self, enum_type):
        f = cbor2_converter.get_structure_hook(enum_type.type)

        with pytest.raises(ValueError):
            f(1, enum_type.type)

    def test_structure_unknown_variant_value_error(self, enum_type):
        f = cbor2_converter.get_structure_hook(enum_type.type)

        with pytest.raises(ValueError):
            f("MyUnknownVariant", enum_type.type)

    def test_explicit_type_mismatch_raises_error(self, unit_type, tuple_type_1_arg):
        with pytest.raises(TypeError):

            @enumclass
            class _:
                MyUnitVariant = unit_type
                MyTupleVariant = tuple_type_1_arg

                type = MyUnitVariant

    def test_zero_variant_enum_type_value_error(self):
        with pytest.raises(ValueError):

            @enumclass
            class _: ...
