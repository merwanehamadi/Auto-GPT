from types import SimpleNamespace
import pytest
from autogpt.workspace import Workspace
from tests.integration.challenges.pr_review.base import run_tests
from tests.utils import requires_api_key
PR_LINK = "https://github.com/merwanehamadi/Auto-GPT/pull/116"
PARAMETERS = SimpleNamespace(
    source_branch_name="imports-challenge-test",
    source_repo_user="merwanehamadi",

    # PR information
    title="imports-challenge-test",
    body="imports-challenge-test",
    # time allowed to run
    cycle_count=3,
    # PR success criteria
    approved=False,
    # contains={"bad_variable_name.py": ["variable"]},
)
@pytest.skip("skip")
@requires_api_key("OPENAI_API_KEY")
def test_kube_challenge_2(
    monkeypatch: pytest.MonkeyPatch, workspace: Workspace
) -> None:
    run_tests(PARAMETERS, monkeypatch, workspace)
