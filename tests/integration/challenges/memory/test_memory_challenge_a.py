import pytest

from autogpt.agent import Agent
from autogpt.commands.file_operations import read_file, write_to_file
from tests.integration.agent_utils import run_interaction_loop
from tests.integration.challenges.utils import get_level_to_run, record_test_result
from tests.utils import requires_api_key

LEVEL_CURRENTLY_BEATEN = 3  # real level beaten 30 and maybe more, but we can't record it, the cassette is too big
MAX_LEVEL = 7

from functools import wraps

def run_until_failure(func):
    @wraps(func)
    def wrapper(memory_management_agent, user_selected_level, patched_api_requestor):
        # Set a default value for user_selected_level if it's None
        user_selected_level = user_selected_level if user_selected_level is not None else 1
        for level in range(user_selected_level, MAX_LEVEL + 1):
            try:
                func(memory_management_agent, level, patched_api_requestor)
            except AssertionError as e:
                print(f"Test failed at level {level}")
                break
    return wrapper


@pytest.mark.vcr
@requires_api_key("OPENAI_API_KEY")
@record_test_result
@run_until_failure  # Add this decorator
def test_memory_challenge_a(
    memory_management_agent: Agent, user_selected_level: int, patched_api_requestor
) -> None:
    """
    The agent reads a file containing a task_id. Then, it reads a series of other files.
    After reading 'n' files, the agent must write the task_id into a new file.

    Args:
        memory_management_agent (Agent)
        user_selected_level (int)
    """

    num_files = get_level_to_run(user_selected_level, LEVEL_CURRENTLY_BEATEN, MAX_LEVEL)

    task_id = "2314"
    create_instructions_files(memory_management_agent, num_files, task_id)

    try:
        run_interaction_loop(memory_management_agent, 400)
    # catch system exit exceptions
    except SystemExit:
        file_path = str(memory_management_agent.workspace.get_path("output.txt"))
        content = read_file(file_path)
        assert task_id in content, f"Expected the file to contain {task_id}"


def create_instructions_files(
    memory_management_agent: Agent,
    num_files: int,
    task_id: str,
    base_filename: str = "instructions_",
) -> None:
    """
    Creates a series of instructions files for the memory challenge.
    Args:
        memory_management_agent (Agent)
        num_files (int)
        task_id (str)
        base_filename (str, optional)
    """
    for i in range(1, num_files + 1):
        content = generate_content(i, task_id, base_filename, num_files)
        file_name = f"{base_filename}{i}.txt"
        file_path = str(memory_management_agent.workspace.get_path(file_name))
        write_to_file(file_path, content)


def generate_content(
    index: int, task_id: str, base_filename: str, num_files: int
) -> str:
    """
    Args:
        index: int
        task_id: str
        base_filename: str
        num_files: int

    Returns: str
    """
    if index == 1:
        return (
            f"This task_id is {task_id}\nRead the file {base_filename}{index + 1}.txt"
        )
    if index != num_files:
        return f"Read the file {base_filename}{index + 1}.txt"
    return "Write the task_id into the file output.txt\nShutdown"
