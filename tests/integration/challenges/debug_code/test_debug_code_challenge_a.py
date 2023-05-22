from pathlib import Path
from typing import Generator

import pytest
from pytest_mock import MockerFixture

from autogpt.agent import Agent
from autogpt.commands.execute_code import execute_python_file
from autogpt.commands.file_operations import append_to_file, write_to_file
from tests.integration.challenges.utils import run_interaction_loop
from tests.utils import requires_api_key

CYCLE_COUNT = 5


def input_generator(input_sequence: list) -> Generator[str, None, None]:
    """
    Creates a generator that yields input strings from the given sequence.
    :param input_sequence: A list of input strings.
    :return: A generator that yields input strings.
    """
    yield from input_sequence


# @pytest.skip("Nobody beat this challenge yet")
# @pytest.mark.parametrize("execution_number", range(3))
# @pytest.mark.vcr
@requires_api_key("OPENAI_API_KEY")
def test_debug_code_challenge_a(
    create_code_agent: Agent,
    monkeypatch: pytest.MonkeyPatch,
    patched_api_requestor: MockerFixture,
    execution_number: int,
) -> None:

    file_path = str(create_code_agent.workspace.get_path("code.py"))
    # use path, get code file in ../data/two_sum.py
    code_file_path = Path(__file__).parent / "data" / "two_sum.py"
    test_file_path = Path(__file__).parent / "data" / "two_sum_tests.py"
    # copy the contents of the code into the workspace
    write_to_file(file_path, code_file_path.read_text())

    run_interaction_loop(monkeypatch, create_code_agent, CYCLE_COUNT)

    # add the tests to the file:
    append_to_file(file_path, test_file_path.read_text())

    # asserts have been added to the file, make sure we don't run into assertion errors
    output = execute_python_file(file_path)
    assert "error" not in output.lower(), f"Errors found in output: {output}!"