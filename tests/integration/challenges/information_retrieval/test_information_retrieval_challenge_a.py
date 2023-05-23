import pytest
from pytest_mock import MockerFixture

from autogpt.commands.file_operations import read_file
from tests.integration.challenges.challenge_decorator.challenge_decorator import (
    challenge,
)
from tests.integration.challenges.utils import run_interaction_loop, run_multiple_times
from tests.utils import requires_api_key

CYCLE_COUNT = 3
from autogpt.agent import Agent


@pytest.mark.vcr
@requires_api_key("OPENAI_API_KEY")
@run_multiple_times(3)
@challenge
def test_information_retrieval_challenge_a(
    get_company_revenue_agent: Agent,
    monkeypatch: pytest.MonkeyPatch,
    patched_api_requestor: MockerFixture,
) -> None:
    """
    Test the challenge_a function in a given agent by mocking user inputs and checking the output file content.

    Args:
        get_company_revenue_agent (Agent)
        monkeypatch (pytest.MonkeyPatch)
        patched_api_requestor (MockerFixture)
    """
    run_interaction_loop(monkeypatch, get_company_revenue_agent, CYCLE_COUNT)

    file_path = str(get_company_revenue_agent.workspace.get_path("output.txt"))
    content = read_file(file_path)
    assert "81" in content, "Expected the file to contain 81"
