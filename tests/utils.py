import functools
import os

import pytest


import pytest
import functools
import os

def requires_api_key(env_var):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not os.environ.get(env_var):
                reason = f"Environment variable '{env_var}' is not set, marking the test as xfail."
                xfail_marker = pytest.mark.xfail(reason=reason, strict=False)
                return xfail_marker(func)(*args, **kwargs)
            else:
                return func(*args, **kwargs)

        return wrapper

    return decorator


def skip_in_ci(test_function):
    return pytest.mark.skipif(
        os.environ.get("CI") == "true",
        reason="This test doesn't work on GitHub Actions.",
    )(test_function)
