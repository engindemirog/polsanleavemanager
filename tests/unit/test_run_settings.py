from app.__main__ import settings_from_env


def test_default_host_is_loopback() -> None:
    """AC-1: without configuration the app listens on loopback only."""
    settings = settings_from_env({})

    assert settings.host == "127.0.0.1"
    assert settings.port == 8000


def test_empty_host_falls_back_to_loopback() -> None:
    """AC-1: an empty PLM_HOST must not open the app to the network."""
    assert settings_from_env({"PLM_HOST": ""}).host == "127.0.0.1"


def test_port_and_host_can_be_overridden_by_environment() -> None:
    settings = settings_from_env({"PLM_HOST": "127.0.0.2", "PLM_PORT": "8123"})

    assert settings.host == "127.0.0.2"
    assert settings.port == 8123
