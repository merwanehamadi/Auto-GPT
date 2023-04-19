import concurrent
import os
import unittest

import pytest
import vcr

from autogpt.agent import Agent
from autogpt.commands.file_operations import LOG_FILE, delete_file, read_file
from autogpt.config import AIConfig, Config, check_openai_api_key
from autogpt.memory import get_memory
from autogpt.prompt import Prompt
from autogpt.workspace import WORKSPACE_PATH
from tests.integration.goal_oriented.vcr_utils import replace_timestamp_in_request

current_file_dir = os.path.dirname(os.path.abspath(__file__))
# tests_directory = os.path.join(current_file_dir, 'tests')

my_vcr = vcr.VCR(
    cassette_library_dir=os.path.join(current_file_dir, "cassettes"),
    record_mode="once",
    before_record_request=replace_timestamp_in_request,
)

CFG = Config()


@pytest.mark.integration_test
def test_find_information_on_web() -> None:
    # if file exist
    file_name = "hello_world.txt"

    file_path_to_write_into = f"{WORKSPACE_PATH}/{file_name}"
    if os.path.exists(file_path_to_write_into):
        os.remove(file_path_to_write_into)
    file_logger_path = f"{WORKSPACE_PATH}/{LOG_FILE}"
    if os.path.exists(file_logger_path):
        os.remove(file_logger_path)

    delete_file(file_name)
    agent = create_writer_agent()
    try:
        with my_vcr.use_cassette(
            "write_file.yaml",
            filter_headers=[
                "authorization",
                "X-OpenAI-Client-User-Agent",
                "User-Agent",
            ],
        ):
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(agent.start_interaction_loop)
                try:
                    result = future.result(timeout=45)
                except concurrent.futures.TimeoutError:
                    assert False, "The process took longer than 45 seconds to complete."
    # catch system exit exceptions
    except SystemExit:  # the agent returns an exception when it shuts down
        content = ""
        content = read_file(file_name)
        os.remove(file_path_to_write_into)

        assert content == "Hello World", f"Expected 'Hello World', got {content}"


def create_writer_agent():
    ai_config = AIConfig(
        ai_name="information_retriever-GPT",
        ai_role="an AI designed to retrieve information an store it in a file.",
        ai_goals=[
            "Find the Auto-GPT github repository.",
            "Find the username of the Auto-GPT founder.",
            "Write this username in a file called auto_gpt_founder.txt.",
            "Complete the task.",
        ],
    )
    memory = get_memory(CFG, init=True)
    prompt = Prompt(ai_config=ai_config)
    agent = Agent(
        ai_name="",
        memory=memory,
        full_message_history=[],
        next_action_count=0,
        system_prompt=prompt.system_prompt,
        triggering_prompt=prompt.triggering_prompt,
    )
    CFG.set_continuous_mode(True)
    CFG.set_memory_backend("no_memory")
    CFG.set_temperature(0)
    os.environ["TIKTOKEN_CACHE_DIR"] = ""

    CFG.set_use_azure(False)
    return agent


if __name__ == "__main__":
    unittest.main()
