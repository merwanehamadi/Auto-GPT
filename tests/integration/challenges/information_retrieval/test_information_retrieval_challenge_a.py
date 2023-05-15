import contextlib
from functools import wraps
from typing import Generator

import pytest

from autogpt.commands.file_operations import read_file, write_to_file
from tests.integration.agent_utils import run_interaction_loop
from tests.integration.challenges.utils import run_multiple_times, record_test_result, setup_mock_input
from tests.utils import requires_api_key

CYCLE_COUNT = 6

def test_information_retrieval_challenge_a(
    get_company_revenue_agent, monkeypatch, patched_api_requestor
) -> None:
    """
    Test the challenge_a function in a given agent by mocking user inputs and checking the output file content.

    :param get_company_revenue_agent: The agent to test.
    :param monkeypatch: pytest's monkeypatch utility for modifying builtins.
    """
    run_interaction_loop(monkeypatch, get_company_revenue_agent, CYCLE_COUNT)


    file_path = str(get_company_revenue_agent.workspace.get_path("output.txt"))
    content = read_file(file_path)
    assert "81" in content, "Expected the file to contain 81"
