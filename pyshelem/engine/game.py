from __future__ import annotations

from dataclasses import dataclass, replace

from pyshelem.engine.card import Card, Deck
from pyshelem.engine.trick import Trick


@dataclass
class TurnState:
    # These need to change for every play
    players_cards: list[set[Card]]
    trick: Trick
    player_valid_cards: set[Card]
    player_idx: int

    validator: Validator

    def played(self, card: Card) -> int:
        # Get the player card
        self.players_cards[self.player_idx].remove(card)

        # Go to the next player
        next_player = (self.player_idx + 1) % len(self.trick)

        pad_card = self.trick.cards[self.player_idx]

        # Add to the trick
        trick_cards = list(self.trick.cards)
        trick_cards[self.player_idx] = card

        # This is required even for the last player, otherwise the winner is incorrect
        self.trick = replace(self.trick, cards=tuple(trick_cards))

        if next_player == self.trick.first_player:
            trick_cards = (pad_card, pad_card, pad_card, pad_card)
            next_player = self.trick.winner
            point = self.trick.point
            self.trick = replace(
                self.trick, cards=trick_cards, first_player=next_player
            )
        else:
            point = 0

        self.player_idx = next_player
        self.player_valid_cards = self.validator(self)
        return point


@dataclass(frozen=True)
class Validator:
    pad_card: Card

    def __call__(self, game_state: TurnState) -> tuple[Card]:
        hand = game_state.players_cards[game_state.player_idx]
        first_card = game_state.trick.first_card
        if first_card == self.pad_card:
            return hand

        valid_cards = set(card for card in hand if card.suit == first_card.suit)
        if valid_cards:
            return valid_cards
        return hand


class ShelemPlayer:
    def play(self, state: TurnState) -> Card:
        pass


@dataclass
class Shelem:
    deck: Deck
    validator: Validator
    # These need to change after a trick get completed
    tricks: tuple[Trick]

    # These will not change during the game
    player_bets: tuple[int]
    bet_winner: int
    trump_suit: int | None

    players: tuple[ShelemPlayer, ShelemPlayer, ShelemPlayer, ShelemPlayer]

    def play_card(self, state: TurnState, current_player_action: Card) -> TurnState:
        valid_card = self.validator(state)
        if current_player_action in valid_card:
            point = state.played(current_player_action)
        else:
            point = -1

        return state

    def bet(self):
        pass

    def pick_trump(self, state: TurnState) -> TurnState:
        pass

    def report_results(self):
        pass

    def play(self):
        num_player = len(self.players)
        state = TurnState(
            players_cards=[set() for _ in range(num_player)],
            trick=Trick(
                trump_suit=-1,
                cards=(self.deck["PAD"] for _ in range(num_player)),
                first_player=-1,
            ),
            player_valid_cards=set(),
            player_idx=-1,
            validator=self.validator,
        )

        deck_cards = self.deck.deck_cards

        card_idx = 0
        for player_idx in range(num_player):
            for i in range(12):
                state.players_cards[i].add(deck_cards[card_idx])
                card_idx += 1

        three_passes = False
        while not three_passes:
            self.bet()

        state = self.pick_trump(state)

        while len(self.tricks) != 12:
            card = self.players[state.player_idx].play(state)
            self.play_card(state, card)

        self.report_results()
