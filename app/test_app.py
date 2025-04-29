# test_app.py
import pytest
from app import Card, Deck, Hand, Player, Game


@pytest.fixture
def deck():
    return Deck(1)


@pytest.fixture
def hand():
    return Hand()


@pytest.fixture
def player():
    return Player("Test", 100)

# ['♥️', '♦️', '♣️', '♠️']
def test_card_creation():
    card = Card("♥️", "10")
    assert card.suit == "♥️"
    assert card.value == "10"


def test_deck_creation(deck):
    assert len(deck.cards) == 52


def test_deal_card(deck):
    card = deck.deal_card()
    assert isinstance(card, Card)
    assert len(deck.cards) == 51


def test_hand_add_card(hand):
    card = Card("♥️", "10")
    hand.add_card(card)
    assert len(hand.cards) == 1


def test_hand_get_value(hand):
    card1 = Card("♥️", "10")
    card2 = Card("♦️", "5")
    hand.add_card(card1)
    hand.add_card(card2)
    assert hand.get_value() == 15


def test_player_hit(player, deck):
    player.hit(deck)
    assert len(player.hand.cards) == 1


def test_player_double_down(player, deck):
    card1 = Card("♥️", "10")
    card2 = Card("♦️", "5")
    player.hand.add_card(card1)
    player.hand.add_card(card2)
    assert player.double_down(deck)


def test_player_split(player, deck):
    card1 = Card("♥️", "10")
    card2 = Card("♦️", "10")
    player.hand.add_card(card1)
    player.hand.add_card(card2)
    assert player.split(deck)

# My own personal test (Jessie)
def test_player_split_invalid(player, deck):
    card1 = Card("♠️", "10")
    card2 = Card("♣️", "7")
    player.hand.add_card(card1)
    player.hand.add_card(card2)
    assert not player.split(deck)


def test_game_play_bot_non_interactive_one_round():
    # Non-interactive bot-only play should complete one round without error
    game = Game(1, 1, interactive=False)
    game.play(max_rounds=1)

def test_game_play_bot_non_interactive_multiple_rounds():
    # Non-interactive bot-only play for multiple rounds
    game = Game(1, 2, interactive=False)
    game.play(max_rounds=3)

def test_game_play_human_interactive(monkeypatch):
    # Human play with mocked inputs: name, bet, stand; deterministic deck
    # Replace Deck so cards are predictable
    from app import Card
    class DummyDeck:
        def __init__(self, num_decks):
            self.cards = []
        def deal_card(self):
            return Card('♠️', '2')
    monkeypatch.setattr('app.Deck', DummyDeck)
    # Actions: name, bet, action, press Enter
    actions = ['Tester', '5', 'stand', '']
    game = Game(1, 0, interactive=True, human_actions=actions)
    game.play(max_rounds=1)
    # After one round, balance should remain non-negative
    assert game.players[0].balance >= 0
