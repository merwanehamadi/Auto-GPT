import os

import openai
import pytest

from tests.conftest import PROXY
from tests.vcr.vcr_filter import before_record_request, before_record_response


@pytest.fixture(scope="session")
def vcr_config():
    # this fixture is called by the pytest-recording vcr decorator.
    return {
        "record_mode": "new_episodes",
        "before_record_request": before_record_request,
        "before_record_response": before_record_response,
        "filter_headers": [
            "Authorization",
            "X-OpenAI-Client-User-Agent",
            "User-Agent",
        ],
        "match_on": ["method", "body"],
    }

@pytest.fixture
def patched_api_requestor(mocker):
    original_init = openai.api_requestor.APIRequestor.__init__
    original_validate_headers = openai.api_requestor.APIRequestor._validate_headers

    def patched_init(requestor, *args, **kwargs):
        original_init(requestor, *args, **kwargs)
        patch_api_base(requestor)

    def patched_validate_headers(self, supplied_headers):
        headers = original_validate_headers(self, supplied_headers)
        headers["new_header_1"] = "header_value_1"
        headers["new_header_2"] = "header_value_2"
        return headers

    if PROXY:
        mocker.patch("openai.api_requestor.APIRequestor.__init__", new=patched_init)
        mocker.patch.object(openai.api_requestor.APIRequestor, "_validate_headers", new=patched_validate_headers)

    return mocker
