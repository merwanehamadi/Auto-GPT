import contextlib
import functools
import json
import os
import random
from typing import Any, Callable, Dict, Generator, List, Optional, Tuple, Union

import pytest

from autogpt.agent import Agent


def generate_noise(noise_size: int) -> str:
    return "".join(
        random.choices(
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
            k=noise_size,
        )
    )


def run_multiple_times(times: int) -> Callable:
    """
    Decorator that runs a test function multiple times.

    :param times: The number of times the test function should be executed.
    """

    def decorator(test_func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(test_func)
        def wrapper(*args: Tuple[Any, ...], **kwargs: Dict[str, Any]) -> None:
            for _ in range(times):
                test_func(*args, **kwargs)

        return wrapper

    return decorator


def setup_mock_input(monkeypatch: pytest.MonkeyPatch, cycle_count: int) -> None:
    """
    Sets up the mock input for testing.

    :param monkeypatch: pytest's monkeypatch utility for modifying builtins.
    :param cycle_count: The number of cycles to mock.
    """
    input_sequence = ["y"] * (cycle_count) + ["EXIT"]

    def input_generator() -> Generator[str, None, None]:
        """
        Creates a generator that yields input strings from the given sequence.
        """
        yield from input_sequence

    gen = input_generator()
    monkeypatch.setattr("builtins.input", lambda _: next(gen))


def run_interaction_loop(
    monkeypatch: pytest.MonkeyPatch, agent: Agent, cycle_count: int
) -> None:
    setup_mock_input(monkeypatch, cycle_count)
    with contextlib.suppress(SystemExit):
        agent.start_interaction_loop()


def run_test_based_on_level(func: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(func)
    def wrapper(*args: Tuple[Any, ...], **kwargs: Dict[str, Any]) -> Any:
        # Read results.json and parse its content
        with open("results.json", "r") as f:
            results = json.load(f)

        # Extract folder name and find the corresponding key in the JSON content
        folder_name = os.path.dirname(os.path.abspath(func.__code__.co_filename)).split(
            os.sep
        )[-1]
        folder_key = next((key for key in results.keys() if folder_name in key), None)

        if folder_key:
            folder_key = folder_key[0]
            # Extract method name and find it in the dictionary
            method_name: str = func.__name__.replace("test_", "")
            if method_name in results[folder_key]:
                test_info = results[folder_key][method_name]
                # If current_level_beaten is -1, skip the test
                if test_info["current_level_beaten"] == -1:
                    pytest.skip("This test has not been unlocked yet.")
                # If max_level is not 1, pass the level to the test function
                if test_info["max_level"] != 1:
                    kwargs["level_to_run"] = test_info["current_level_beaten"]

        return func(*args, **kwargs)

    return wrapper
