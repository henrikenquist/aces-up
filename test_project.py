import pytest
from project import check_strategy, game_option, play_game


def test_play_game():
    assert play_game()[0] <= 48


def test_check_strategy():
    assert check_strategy("1 100 1000") == [1, 100, 1000]
    with pytest.raises(ValueError):
        check_strategy("12 120 1200")
    with pytest.raises(ValueError):
        check_strategy("a")


def test_game_option(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "1")
    assert game_option() == 1
