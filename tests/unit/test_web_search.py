import pytest

from autogpt.agent.agent import Agent
from autogpt.commands.web_search import safe_web_search_results, web_search


@pytest.mark.parametrize(
    "query, expected_output",
    [("test", "test"), (["test1", "test2"], '["test1", "test2"]')],
)
def test_safe_web_search_results(query, expected_output):
    result = safe_web_search_results(query)
    assert isinstance(result, str)
    assert result == expected_output


def test_safe_web_search_results_invalid_input():
    with pytest.raises(AttributeError):
        safe_web_search_results(123)


@pytest.mark.parametrize(
    "query, num_results, expected_output, return_value",
    [
        (
            "test",
            1,
            '[\n    {\n        "title": "Result 1",\n        "link": "https://example.com/result1"\n    }\n]',
            [{"title": "Result 1", "link": "https://example.com/result1"}],
        ),
        ("", 1, "[]", []),
        ("no results", 1, "[]", []),
    ],
)
def test_web_search(
    query, num_results, expected_output, return_value, mocker, agent: Agent
):
    mock_ddg = mocker.Mock()
    mock_ddg.return_value = return_value

    mocker.patch("autogpt.commands.web_search.DDGS.text", mock_ddg)
    actual_output = web_search(query, agent=agent, num_results=num_results)
    expected_output = safe_web_search_results(expected_output)
    assert actual_output == expected_output


@pytest.fixture
def mock_web_search_api_client(mocker):
    mock_build = mocker.patch("web_search_api_client.discovery.build")
    mock_service = mocker.Mock()
    mock_build.return_value = mock_service
    return mock_service.cse().list().execute().get
