import dataclasses

import pytest

from nexosim import Simulation
from nexosim.types import TupleType0Arg, UnitType, enumclass, tuple_type


@enumclass
class TestSubLoad:
    class VarA(UnitType): ...

    @dataclasses.dataclass
    class VarB: ...

    class VarC(tuple_type(int)): ...

    class VarD(tuple_type(str, float)): ...

    @dataclasses.dataclass
    class VarE:
        x: str
        y: bool


@enumclass
class TestLoad:
    class VarA(TupleType0Arg): ...

    @dataclasses.dataclass
    class VarB: ...

    class VarC(tuple_type(int)): ...

    class VarD(tuple_type(str, float)): ...

    @dataclasses.dataclass
    class VarE:
        x: str
        y: bool

    class VarF(tuple_type(TestSubLoad.type)): ...

    @dataclasses.dataclass
    class VarG:
        x: int
        y: TestSubLoad.type


@pytest.fixture
def sim(types_bench):
    with Simulation(types_bench) as sim:
        sim.build()
        sim.init()
        yield sim


class TestLoadRoundTrip:
    def test_var_a(self, sim):
        sim.process_event("input", TestLoad.VarA())
        result = sim.try_read_events("output", TestLoad.type)
        assert len(result) == 1
        assert isinstance(result[0], TestLoad.VarA)

    def test_var_b(self, sim):
        sim.process_event("input", TestLoad.VarB())
        result = sim.try_read_events("output", TestLoad.type)
        assert result == [TestLoad.VarB()]

    def test_var_c(self, sim):
        sim.process_event("input", TestLoad.VarC(42))
        result = sim.try_read_events("output", TestLoad.type)
        assert result == [TestLoad.VarC(42)]

    def test_var_d(self, sim):
        sim.process_event("input", TestLoad.VarD("hello", 3.14))
        result = sim.try_read_events("output", TestLoad.type)
        assert result == [TestLoad.VarD("hello", 3.14)]

    def test_var_e(self, sim):
        sim.process_event("input", TestLoad.VarE(x="hello", y=True))
        result = sim.try_read_events("output", TestLoad.type)
        assert result == [TestLoad.VarE(x="hello", y=True)]

    def test_var_f_sub_var_a(self, sim):
        sim.process_event("input", TestLoad.VarF(TestSubLoad.VarA()))
        result = sim.try_read_events("output", TestLoad.type)
        assert len(result) == 1
        assert isinstance(result[0], TestLoad.VarF)
        assert isinstance(result[0]._0, TestSubLoad.VarA)

    def test_var_f_sub_var_b(self, sim):
        sim.process_event("input", TestLoad.VarF(TestSubLoad.VarB()))
        result = sim.try_read_events("output", TestLoad.type)
        assert result == [TestLoad.VarF(TestSubLoad.VarB())]

    def test_var_f_sub_var_c(self, sim):
        sim.process_event("input", TestLoad.VarF(TestSubLoad.VarC(99)))
        result = sim.try_read_events("output", TestLoad.type)
        assert result == [TestLoad.VarF(TestSubLoad.VarC(99))]

    def test_var_f_sub_var_d(self, sim):
        sim.process_event("input", TestLoad.VarF(TestSubLoad.VarD("world", 2.71)))
        result = sim.try_read_events("output", TestLoad.type)
        assert result == [TestLoad.VarF(TestSubLoad.VarD("world", 2.71))]

    def test_var_f_sub_var_e(self, sim):
        sim.process_event("input", TestLoad.VarF(TestSubLoad.VarE(x="test", y=False)))
        result = sim.try_read_events("output", TestLoad.type)
        assert result == [TestLoad.VarF(TestSubLoad.VarE(x="test", y=False))]

    def test_var_g_sub_var_a(self, sim):
        # Unit variant in struct field — exercises the serialization fix.
        sim.process_event("input", TestLoad.VarG(x=1, y=TestSubLoad.VarA()))
        result = sim.try_read_events("output", TestLoad.type)
        assert len(result) == 1
        assert isinstance(result[0], TestLoad.VarG)
        assert result[0].x == 1
        assert isinstance(result[0].y, TestSubLoad.VarA)

    def test_var_g_sub_var_c(self, sim):
        sim.process_event("input", TestLoad.VarG(x=7, y=TestSubLoad.VarC(5)))
        result = sim.try_read_events("output", TestLoad.type)
        assert result == [TestLoad.VarG(x=7, y=TestSubLoad.VarC(5))]
