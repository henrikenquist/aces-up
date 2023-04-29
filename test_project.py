import pytest
from project import check_strategy, play_game, user_input


def test_play_game():
    assert play_game() <= 48


def test_check_strategy():
    assert check_strategy("1 100 1000") == [1, 100, 1000]
    with pytest.raises(ValueError):
        check_strategy("12 120 1200")


def test_user_input(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "1")
    assert user_input() == 1
    # monkeypatch.setattr("builtins.input", lambda _: "a")
    # with pytest.raises(ValueError):
    #     user_input()
