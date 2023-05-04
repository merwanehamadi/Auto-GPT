import os

import pytest

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
            'Accept-Encoding',
            'Connection'
        ],
        "match_on": ["method", "uri", "body"],
    }

    filter_headers=['User-Agent', 'Accept-Encoding', 'Accept', 'Connection'],
