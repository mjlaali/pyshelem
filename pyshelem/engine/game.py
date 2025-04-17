from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, replace, field

from pyshelem.engine.card import Card, Deck
from pyshelem.engine.trick import Trick


@dataclass
class TurnState:
    # These need to change for every play
    players_cards: list[set[Card]]
    current_trick: Trick
    game_tricks: list[Trick]
    player_valid_cards: set[Card]
    player_idx: int

    validator: Validator

    def play(self, card: Card) -> int | None:
        if card not in self.player_valid_cards:
            raise RuntimeError(
                f"This is not a valid card for this player, played: {str(card)}, valid cards: {str(self.player_valid_cards)} "
            )
        # Get the player card
        self.players_cards[self.player_idx].remove(card)

        # Go to the next player
        next_player = (self.player_idx + 1) % len(self.current_trick)

        pad_card = self.current_trick.cards[self.player_idx]

        # Add to the trick
        trick_cards = list(self.current_trick.cards)
        trick_cards[self.player_idx] = card

        # This is required even for the last player, otherwise the winner is incorrect
        self.current_trick = replace(self.current_trick, cards=tuple(trick_cards))

        if next_player == self.current_trick.first_player:
            trick_cards = (pad_card, pad_card, pad_card, pad_card)
            next_player = self.current_trick.winner
            point = self.current_trick.point
            self.game_tricks.append(self.current_trick)

            self.current_trick = replace(
                self.current_trick, cards=trick_cards, first_player=next_player
            )
        else:
            point = None

        self.player_idx = next_player
        self.player_valid_cards = self.validator(self)
        return point


@dataclass(frozen=True)
class Validator:
    pad_card: Card

    def __call__(self, game_state: TurnState) -> tuple[Card]:
        hand = game_state.players_cards[game_state.player_idx]
        first_card = game_state.current_trick.first_card
        if first_card == self.pad_card:
            return hand

        valid_cards = set(card for card in hand if card.suit == first_card.suit)
        if valid_cards:
            return valid_cards
        return hand


class ShelemPlayer(ABC):
    def init(self, cards: list[Card]) -> None:
        pass

    def play(self, state: TurnState) -> Card:
        pass

    def bid(self, cards: set[Card], last_bids: list[int]) -> int | None:
        pass

    def discard(self, cards: set[Card], left_over_cards: set[Card]) -> set[Card]:
        pass


@dataclass
class Shelem:
    pad_card: Card
    player_cards: list[list[Card]]
    left_over_cards: list[Card]
    players: tuple[ShelemPlayer, ShelemPlayer, ShelemPlayer, ShelemPlayer]
    starting_player: int

    max_bid_value: int = -1
    tricks: list[Trick] = field(default_factory=list)
    discarded_card: list[Card] = field(default_factory=set)
    validator: Validator | None = None

    def __post_init__(self):
        if self.validator is None:
            self.validator = Validator(self.pad_card)

    def play(self):
        for i in range(4):
            self.players[i].init(self.player_cards[i])

        # betting rounds
        first_player = self.betting_round()

        # discarding
        self.discarding_round(first_player)

        print(f"Trick 1")
        state = self.set_trump(first_player)

        num_cards = sum((len(player_card) for player_card in self.player_cards))
        for i in range(num_cards):
            card = self.players[state.player_idx].play(state)
            point, state = self.play_card(state, card)

        self.report_results()

    def play_card(
        self, state: TurnState, current_player_action: Card
    ) -> tuple[int | None, TurnState]:
        valid_card = self.validator(state)
        if current_player_action in valid_card:
            point = state.play(current_player_action)
        else:
            point = -1

        return point, state

    def report_results(self):
        pass

    def set_trump(self, first_player: int) -> TurnState:
        state = TurnState(
            players_cards=self.player_cards,
            current_trick=Trick(
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
        state = replace(state, trick=replace(state.current_trick, trump_suit=card.suit))
        return state

    def discarding_round(self, first_player: int) -> None:
        self.discarded_card = self.players[first_player].discard(
            self.player_cards[first_player], self.left_over_cards
        )
        assert len(self.discarded_card) == len(self.left_over_cards)
        self.player_cards[first_player] += self.left_over_cards
        to_remove = set(self.discarded_card)
        self.player_cards[first_player] = [
            card for card in self.player_cards[first_player] if card not in to_remove
        ]

    def betting_round(self) -> int:
        num_player = len(self.players)
        left_players = list(range(num_player))
        idx = self.starting_player
        max_bid_value = 0
        bid_values = []
        while len(left_players) > 1:
            player_idx = left_players[idx]
            bid_value = self.players[player_idx].bid(
                self.player_cards[player_idx], bid_values
            )
            if bid_value and bid_value > max_bid_value:
                max_bid_value = bid_value
                idx += 1
                bid_values.append(bid_value)
            else:
                left_players.remove(player_idx)
                bid_values.append(-1)

            idx = idx % len(left_players)
        self.max_bid_value = max_bid_value
        first_player = left_players[0]
        return first_player
