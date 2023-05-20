import os
from datetime import datetime

from github import Github

from tests.integration.agent_factory import get_pr_review_agent
from tests.integration.challenges.utils import run_interaction_loop
from collections import defaultdict
PR_TARGET_BRANCH = "hackathon-pr-target"
PR_TARGET_REPO_USER = "merwanehamadi"
REPO_NAME = "Auto-GPT"
PR_TARGET_REPO = f"https://github.com/{PR_TARGET_REPO_USER}/{REPO_NAME}"
GITHUB_TOKEN = os.environ.get("GITHUB_PAT")


def create_pr(
        source_branch_name,
        source_repo_user,
        title,
        body
    ):
    # First create a Github instance with your token:

    g = Github(GITHUB_TOKEN)

    # Then get your repository:
    repo = g.get_user(source_repo_user).get_repo(REPO_NAME)

    # Get the branch you want to copy

    base_branch = repo.get_branch(source_branch_name)

    # Create the name for the new branch
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    new_branch_name = f"{source_branch_name}-{timestamp}"

    # Create the new branch
    repo.create_git_ref(ref=f"refs/heads/{new_branch_name}", sha=base_branch.commit.sha)
    title = f"{os.environ.get('TEAM_MEMBER_NAME')} {title}"
    # Create a new pull request
    pr = repo.create_pull(
        title=title,
        body=body,
        head=new_branch_name,
        base=PR_TARGET_BRANCH,
    )

    return pr.number


def check_pr(pr_number, parameters):
    # First create a Github instance with your token:
    g = Github(GITHUB_TOKEN)

    # Get the repository
    repo = g.get_user(PR_TARGET_REPO_USER).get_repo(REPO_NAME)

    # Get the pull request
    pr = repo.get_pull(pr_number)

    # Count approvals
    approvals = 0

    # Get reviews for the pull request
    for review in pr.get_reviews():
        # Check if the review is an approval
        if review.state == "APPROVED":
            approvals += 1

    # Get file comments
    check_comments(parameters, pr, pr_number)

    print(
        f"The PR number {pr_number} in the repository {PR_TARGET_REPO} has {approvals} approvals."
    )
    if parameters.approved:
        assert approvals > 0
    else:
        assert approvals == 0

    return True  # All conditions were satisfied


def check_comments(parameters, pr, pr_number):
    file_comments = defaultdict(list)  # Store comments per file
    for comment in pr.get_comments():
        file_comments[comment.path].append(comment.body)
    # Verify if all required comments are present
    for file, required_comments in parameters.contains.items():
        for required_comment in required_comments:
            assert any(required_comment in comment for comment in file_comments[file]), \
                f"Missing required comment '{required_comment}' in file {file} for PR number {pr_number} in the repository {PR_TARGET_REPO}."


def run_tests(parameters, monkeypatch, workspace):
    pr_number = create_pr(
        parameters.source_branch_name,
        parameters.source_repo_user,
        parameters.title,
        parameters.body,
    )
    review_agent = get_pr_review_agent(pr_number, PR_TARGET_REPO, workspace)
    run_interaction_loop(monkeypatch, review_agent, parameters.cycle_count)
    check_pr(pr_number, parameters)
