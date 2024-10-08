from __future__ import annotations

from dataclasses import dataclass, replace, field

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

    def bet(self, cards: set[Card]) -> int:
        pass

    def discard(self, cards: set[Card], left_over_cards: set[Card]) -> set[Card]:
        pass


@dataclass
class Shelem:
    pad_card: Card
    player_cards: list[set[Card]]
    left_over_cards: set[Card]
    players: tuple[ShelemPlayer, ShelemPlayer, ShelemPlayer, ShelemPlayer]
    starting_player: int

    max_bet_value: int = -1
    tricks: list[Trick] = field(default_factory=list)
    discarded_card: set[Card] = field(default_factory=set)
    validator: Validator | None = None

    def __post_init__(self):
        if self.validator is None:
            self.validator = Validator(self.pad_card)

    def play(self):
        # betting rounds
        first_player = self.betting_round()

        # discarding
        self.discarding_round(first_player)

        state = self.set_trump(first_player)

        while len(self.tricks) != 12:
            card = self.players[state.player_idx].play(state)
            point, state = self.play_card(state, card)

        self.report_results()

    def play_card(
        self, state: TurnState, current_player_action: Card
    ) -> tuple[int, TurnState]:
        valid_card = self.validator(state)
        if current_player_action in valid_card:
            point = state.played(current_player_action)
        else:
            point = -1

        return point, state

    def report_results(self):
        pass

    def set_trump(self, first_player: int) -> TurnState:
        state = TurnState(
            players_cards=self.player_cards,
            trick=Trick(
                trump_suit=-1,
                cards=[self.pad_card, self.pad_card, self.pad_card, self.pad_card],
                first_player=first_player,
            ),
            player_valid_cards=self.player_cards[first_player],
            player_idx=first_player,
            validator=self.validator,
        )
        # set the trump
        card = self.players[state.player_idx].play(state)
        point, state = self.play_card(state, card)
        state = replace(state, trick=replace(state.trick, trump_suit=card.suit))
        return state

    def discarding_round(self, first_player: int) -> None:
        self.discarded_card = self.players[first_player].discard(
            self.player_cards[first_player], self.left_over_cards
        )
        assert len(self.discarded_card) == len(self.left_over_cards)
        self.player_cards[first_player] = (
            self.player_cards[first_player].union(self.left_over_cards)
            - self.discarded_card
        )

    def betting_round(self) -> int:
        num_player = len(self.players)
        left_players = list(range(num_player))
        idx = self.starting_player
        max_bet_value = 0
        while len(left_players) > 1:
            player_idx = left_players[idx]
            bet_value = self.players[player_idx].bet(self.player_cards[player_idx])
            if bet_value > max_bet_value:
                max_bet_value = bet_value
                idx += 1
            else:
                left_players.remove(player_idx)

            idx = idx % len(left_players)
        self.max_bet_value = max_bet_value
        first_player = left_players[0]
        return first_player
