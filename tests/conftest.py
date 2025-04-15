import shlex
import subprocess
import time

import pytest


@pytest.fixture(scope="session")
def coffee():
    """Spawn a simulation server set up with the coffee machine bench."""
    address = "0.0.0.0:41635"
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


@pytest.fixture(scope="session")
def rt_coffee():
    """Spawn a simulation server set up with the real time coffee machine bench."""
    address = "0.0.0.0:41636"
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


@pytest.fixture(scope="session")
def types_bench():
    """Spawn a simulation server set up with bench2."""
    address = "0.0.0.0:41637"
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
