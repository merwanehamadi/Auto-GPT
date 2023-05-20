from __future__ import annotations

import requests

from autogpt.commands.command import command
from autogpt.llm import create_chat_completion
from autogpt.config import Config


@command(
    "review_pr",
    "Review PR",
    '"pr_link": "<link_to_pr>"',
)
def review_diff(pr_link: str) -> str:
    """
    A function that takes in code and suggestions and returns a response from create
      chat completion api call.

    to get diff add ".diff to the end of the PR" and then make an http request

    Make a review comment on a pull request

    Request change or approve PR with the github api

    Parameters:
        suggestions (list): A list of suggestions around what needs to be improved.
        code (str): Code to be improved.
    Returns:
        A result string from create chat completion. Improved code in response.
    """
    # use requests to get the pr diff
    diff_link = pr_link + '.diff'
    response = requests.get(diff_link)
    if response.status_code != 200:
        raise ValueError(f'Invalid response status: {response.status_code}. '
                         f'Response text is: {response.text} ')
    diff = response.text

    # now we need to make llm call to evaluate the reponse
    response = _process_diff(diff)


    return "Successfully reviewed PR."

def _process_diff(diff):
    """
    Given a diff
    """
    system_prompt = """
Instructions:
You are a github diff reviewer. Below is are the contribution guidelines for a project you are doing reviews for.

The user is going to provide you with a diff to review. Your job is to determine if the diff is acceptable or not. You have very high standards for accepting a diff.

If the diff is acceptable, respond with "Acceptable". If the diff is not acceptable, respond with "Request Changes" and explain the needed changes. 

Below are guidelines for acceptable PRs.

- Your pull request should be atomic and focus on a single change.
- Your pull request should include tests for your change. We automatically enforce this with [CodeCov](https://docs.codecov.com/docs/commit-status)
- You should have thoroughly tested your changes with multiple different prompts.
- You should have considered potential risks and mitigations for your changes.
- You should have documented your changes clearly and comprehensively.
- You should not include any unrelated or "extra" small tweaks or changes.
    """
    cfg = Config()
    model = cfg.smart_llm_model
    # parse args to comma separated string
    messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
        {"role": "user", "content": diff},
    ]

    response = create_chat_completion(model=model, messages=messages, temperature=0)
    return response
