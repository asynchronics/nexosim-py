"""Just a temporary playground--not a real test"""

from dataclasses import dataclass

import pytest

from nexosim import Simulation

# from nexosim.time import Duration, MonotonicTime
from nexosim.types import enumclass, UnitType, TupleType1Arg, tuple_type


@enumclass
class TestSubload:
    class VarA(UnitType): ...

    @dataclass
    class VarB: ...

    class VarC(tuple_type(int)): ...

    class VarD(tuple_type(str, float)): ...

    @dataclass
    class VarE:
        x: str
        y: bool

    type = VarA | VarB | VarC | VarD | VarE


# @dataclass
# class TestLoad: ...


@enumclass
class TestLoad:
    class VarA(tuple_type()): ...

    @dataclass
    class VarB: ...

    class VarC(tuple_type(int)): ...

    class VarD(tuple_type(str, float)): ...

    @dataclass
    class VarE:
        x: str
        y: bool

    class VarF(TupleType1Arg[TestSubload.type]): ...

    @dataclass
    class VarG:
        x: int
        y: TestSubload.type

    type = VarA | VarB | VarC | VarD | VarE | VarF | VarG

@pytest.mark.skip
def test_run():
    # sim = Simulation(address="localhost:41633")
    sim = Simulation(address="unix:///tmp/nexo")

    # load = TestLoad.VarF(TestSubload.VarC(123))
    load = TestLoad.VarC(123)

    sim.start(load)
    print("STARTED")
    print(load)
    sim.process_event("input", load)

    load2 = sim.read_events("output", TestLoad.type)[0]
    print(load2)
    print(load == load2)

