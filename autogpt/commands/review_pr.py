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


@command(
    "close_github_PR",
    "Close GitHub PR",
    '"owner": "<owner>", "repo": "<repo>", "pull_number": "<pull_number>"',
    CFG.github_personal_access_token,
    "Configure GITHUB_PAT env variable pls",
)
@validate_url
def close_github_pr(owner, repo, pull_number) -> str:
    """Closes a pull request on GitHub.

    Args:
        owner: The owner of the GitHub repository.
        repo: The name of the GitHub repository.
        pull_number: The number of the pull request to close.
        github_token: A Personal Access Token with the `repo` scope.

    Returns:
        A response object from the GitHub API.
    """

    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}"
    headers = {
        "Authorization": f"token {github_token}",
        "Content-Type": "application/json",
    }
    data = {"state": "closed"}

    response = requests.patch(url, headers=headers, data=json.dumps(data))
    return response



@command(
    "comment_github_PR",
    "Comment on a GitHub PR",
    '"owner": "<owner>", "repo": "<repo>", "pull_number": "<pull_number>", "comment": "<comment>"',
    CFG.github_personal_access_token,
    "Configure GITHUB_PAT env variable pls",
)
@validate_url
def create_github_comment(owner, repo, issue_number, comment) -> str:
    """Comments on a pull request on GitHub.

    Args:
        owner: The owner of the GitHub repository.
        repo: The name of the GitHub repository.
        pull_number: The number of the pull request to close.
        github_token: A Personal Access Token with the `repo` scope.

    Returns:
        A response object from the GitHub API.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {CFG.github_personal_access_token}",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    data = {
        "body": comment
    }
    response = requests.post(url, headers=headers, json=data)
    return response