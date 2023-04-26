import functools
import os
from contextlib import contextmanager

import pytest

from autogpt.config import Config


@contextmanager
def temporary_api_key(config, api_key):
    original_api_key = config.get_openai_api_key()
    config.set_openai_api_key(api_key)
    try:
        yield
    finally:
        config.set_openai_api_key(original_api_key)

def requires_api_key(env_var):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(request, *args, **kwargs):
            use_api_key = request.config.getoption("--use-api-key")
            config = Config()
            if use_api_key:
                return func(request, *args, **kwargs)
            ## Even when we use the cassettes we are forced to have a fake API key because open AI library needs it.
            with temporary_api_key(config, "sk-dummy"):
                return func(request, *args, **kwargs)

        return pytest.mark.xfail(strict=False)(wrapper)

    return decorator

def requires_api_key(env_var):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not os.environ.get(env_var):
                pytest.skip(
                    f"Environment variable '{env_var}' is not set, skipping the test."
                )
            else:
                return func(*args, **kwargs)

        return wrapper

    return decorator


def skip_in_ci(test_function):
    return pytest.mark.skipif(
        os.environ.get("CI") == "true",
        reason="This test doesn't work on GitHub Actions.",
    )(test_function)
