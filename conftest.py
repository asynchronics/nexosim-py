import shlex
import subprocess
import time

import pytest
from sybil import Sybil
from sybil.document import PythonDocStringDocument
from sybil.evaluators.python import PythonEvaluator
from sybil.parsers.markdown import (
    CodeBlockParser,
    PythonCodeBlockParser,
    SkipParser,
)
from sybil.sybil import SybilCollection

from nexosim import Simulation


@pytest.fixture(scope="session")
def docs_bench_server():
    """Spawn a simulation server set up with the docs bench."""
    address = "127.0.0.1:41633"
    subprocess.run(
        shlex.split("cargo build --manifest-path tests/bench/Cargo.toml"), check=True
    )
    with subprocess.Popen(
        shlex.split(f"./tests/bench/target/debug/grpc-python docs -a {address} --http")
    ) as proc:
        # wait for startup
        time.sleep(1)
        try:
            yield address
        finally:
            proc.terminate()


@pytest.fixture
def docs_bench(docs_bench_server):
    yield docs_bench_server
    with Simulation(docs_bench_server) as sim:
        sim.tear_down()


@pytest.fixture(scope="session")
def rt_docs_bench_server():
    """Spawn a simulation server set up with the real time docs bench."""
    address = "127.0.0.1:41634"
    subprocess.run(
        shlex.split("cargo build --manifest-path tests/bench/Cargo.toml"), check=True
    )
    with subprocess.Popen(
        shlex.split(
            f"./tests/bench/target/debug/grpc-python docsrt -a {address} --http"
        )
    ) as proc:
        # wait for startup
        time.sleep(1)
        try:
            yield address
        finally:
            proc.terminate()


@pytest.fixture
def rt_docs_bench(rt_docs_bench_server):
    yield rt_docs_bench_server
    with Simulation(rt_docs_bench_server) as sim:
        sim.tear_down()


def _parsers():
    return [
        PythonCodeBlockParser(),
        CodeBlockParser(language="py", evaluator=PythonEvaluator()),
        SkipParser(),
    ]


readme = Sybil(
    parsers=_parsers(),
    path=".",
    patterns=["README.md"],
    excludes=["*/README.md"],  # only the root one
    fixtures=["docs_bench"],
    name="readme",
)

user_guide = Sybil(
    parsers=_parsers(),
    path="docs",
    patterns=["*.md"],
    fixtures=["docs_bench", "rt_docs_bench"],
)


docstrings_server = Sybil(
    parsers=_parsers(),
    path="src/nexosim",
    patterns=["__init__.py"],
    excludes=["aio/*"],
    fixtures=["docs_bench"],
    document_types={".py": PythonDocStringDocument},
)

docstrings_server_rt = Sybil(
    parsers=_parsers(),
    path="src/nexosim/aio",
    patterns=["__init__.py"],
    fixtures=["rt_docs_bench"],
    document_types={".py": PythonDocStringDocument},
)

docstrings = Sybil(
    parsers=_parsers(),
    path="src/nexosim",
    patterns=["*.py"],
    excludes=["__init__.py"],
    document_types={".py": PythonDocStringDocument},
)

pytest_collect_file = SybilCollection(
    [
        readme,
        user_guide,
        docstrings_server_rt,
        docstrings_server,
        docstrings,
    ]
).pytest()
