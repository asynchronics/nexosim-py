import multiprocessing
import shlex
import subprocess
import time

import pytest

from nexosim import Simulation


@pytest.fixture(scope="session", autouse=True)
def always_spawn():
    multiprocessing.set_start_method("spawn")


@pytest.fixture(scope="session")
def coffee_server():
    """Spawn a simulation server set up with the coffee machine bench."""
    address = "127.0.0.1:41635"
    subprocess.run(
        shlex.split("cargo build --manifest-path tests/bench/Cargo.toml"), check=True
    )
    with subprocess.Popen(
        shlex.split(
            f"./tests/bench/target/debug/grpc-python coffee -a {address} --http"
        )
    ) as proc:
        # wait for startup
        time.sleep(1)
        try:
            yield address
        finally:
            proc.terminate()


@pytest.fixture
def coffee(coffee_server):
    yield coffee_server
    with Simulation(coffee_server) as sim:
        sim.terminate()


@pytest.fixture(scope="session")
def rt_coffee_server():
    """Spawn a simulation server set up with the real time coffee machine bench."""
    address = "127.0.0.1:41636"
    subprocess.run(
        shlex.split("cargo build --manifest-path tests/bench/Cargo.toml"), check=True
    )
    with subprocess.Popen(
        shlex.split(
            f"./tests/bench/target/debug/grpc-python coffeert -a {address} --http"
        )
    ) as proc:
        # wait for startup
        time.sleep(1)
        try:
            yield address
        finally:
            proc.terminate()


@pytest.fixture
def rt_coffee(rt_coffee_server):
    yield rt_coffee_server
    with Simulation(rt_coffee_server) as sim:
        sim.terminate()


@pytest.fixture(scope="session")
def rt_coffee_ticker_server():
    """Spawn a simulation server set up with the real time coffee machine bench."""
    address = "127.0.0.1:41637"
    subprocess.run(
        shlex.split("cargo build --manifest-path tests/bench/Cargo.toml"), check=True
    )
    with subprocess.Popen(
        shlex.split(
            f"./tests/bench/target/debug/grpc-python coffeertticker -a {address} --http"
        )
    ) as proc:
        # wait for startup
        time.sleep(1)
        try:
            yield address
        finally:
            proc.terminate()


@pytest.fixture
def rt_coffee_ticker(rt_coffee_ticker_server):
    yield rt_coffee_ticker_server
    with Simulation(rt_coffee_ticker_server) as sim:
        sim.terminate()


@pytest.fixture(scope="session")
def types_bench_server():
    """Spawn a simulation server set up with bench2."""
    # Port 41638 to avoid conflict with rt_coffee_ticker_server which uses 41637.
    address = "127.0.0.1:41638"
    subprocess.run(
        shlex.split("cargo build --manifest-path tests/bench/Cargo.toml"), check=True
    )
    with subprocess.Popen(
        shlex.split(f"./tests/bench/target/debug/grpc-python types -a {address} --http")
    ) as proc:
        # wait for startup
        time.sleep(1)
        try:
            yield address
        finally:
            proc.terminate()


@pytest.fixture
def types_bench(types_bench_server):
    yield types_bench_server
    with Simulation(types_bench_server) as sim:
        sim.terminate()
