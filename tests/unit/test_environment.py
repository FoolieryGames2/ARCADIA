from arcadia.environment import inspect_environment


def test_host_environment_passes() -> None:
    checks = inspect_environment()
    assert checks
    assert all(check.passed for check in checks), checks
