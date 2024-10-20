from __future__ import annotations
from dataclasses import dataclass, field

from pyshelem.engine.card import Deck, Card
from pyshelem.engine.game import Shelem, ShelemPlayer, TurnState


@dataclass
class SimulatedPlayer(ShelemPlayer):
    bets: list[int]
    plays: list[Card]
    discard: set[Card]

    def bet(self, cards: set[Card]) -> int:
        return self.bets.pop(0)

    def discard(self, cards: set[Card], left_over_cards: set[Card]) -> set[Card]:
        return self.discard

    def play(self, state: TurnState) -> Card:
        return self.plays.pop(0)


@dataclass
class Parser:
    deck: Deck | None = field(default=None, init=False)
    player_cards: list[set[Card]] | None = field(default=None, init=False)
    left_over_cards: set[Card] | None = field(default=None, init=False)
    bidding_winner: int = field(default=-1, init=False)
    player_bids: list[list[int]] = field(
        default_factory=lambda: [[] for _ in range(4)], init=False
    )

    discard_cards: list[list[Card]] = field(
        default_factory=lambda: [[] for _ in range(4)], init=False
    )
    player_plays: list[list[Card]] = field(
        default_factory=lambda: [[] for _ in range(4)], init=False
    )

    def set_player_cards(self, cards: str) -> Parser:
        with_joker = len(cards) == 54 * 2
        self.deck = Deck(with_joker=with_joker)
        deck_cards = self.deck.parse_cards(cards)
        self.player_cards = list(
            set(deck_cards[i * 12 : (i + 1) * 12]) for i in range(4)
        )
        self.left_over_cards = set(deck_cards[4 * 12 :])
        return self

    def set_betting(self, betting: str, first_player_idx: int) -> Parser:
        # *B -> A + 1 = 100
        # *C -> A + 2 = 105
        # *D -> A + 3 = 110
        # *E -> A + 4 = 115
        # *F -> A + 5 = 120
        # *G -> A + 6 = 125
        # *H -> A + 7 = 130
        # *I -> A + 8 = 135
        # *J -> A + 9 = 140
        # *K -> A + 10 = 145
        # ** -> Pass
        players = list(range(4))

        cur_player = first_player_idx

        for i in range(1, len(betting), 2):
            if betting[i] == "*":
                players.pop(cur_player)
                cur_player = cur_player % len(players)
            else:
                bid_value = (ord(betting[i]) - ord("A")) * 5 + 95
                player_idx = players[cur_player]
                self.player_bids[player_idx].append(bid_value)
                cur_player = (cur_player + 1) % len(players)
        assert len(players) == 1
        self.bidding_winner = players[0]
        return self

    def set_other_events(self, other_events: str) -> Parser:
        num_cards = ord(other_events[0]) - ord("A")

        last_discard_card_pos = num_cards * 2 + 1
        discard_cards = other_events[1:last_discard_card_pos]
        plays = other_events[last_discard_card_pos:]

        return self.set_discard_cards(
            discard_cards, self.deck, self.bidding_winner
        ).set_plays(plays, self.deck)

    def set_discard_cards(
        self, discard_cards: str, deck: Deck, bedding_winner: int
    ) -> Parser:
        self.discard_cards[bedding_winner] = deck.parse_cards(discard_cards)
        return self

    def set_plays(self, plays: str, deck: Deck) -> Parser:
        cards = deck.parse_cards(plays)
        for player in range(4):
            self.player_plays[player] = [cards[i] for i in range(player, len(cards), 4)]
        return self


@dataclass
class Simulator:
    str_game: str

    parser: Parser = field(default_factory=Parser)

    def __post_init__(self) -> None:
        (
            game_id,
            first_player_idx,
            p0_id,
            p1_id,
            p2_id,
            p3_id,
            cards,
            events,
        ) = self.str_game.split(",")

        betting, other_events = events.split("_")
        self.parser.set_player_cards(cards).set_betting(
            betting, int(first_player_idx)
        ).set_other_events(other_events)

    @property
    def shelem(self) -> Shelem:
        parser = self.parser
        return Shelem(
            pad_card=parser.deck.pad_card,
            player_cards=parser.player_cards,
            left_over_cards=parser.left_over_cards,
            players=(
                SimulatedPlayer(
                    bets=parser.player_bids[i],
                    plays=parser.player_plays[i],
                    discard=parser.discard_cards[i],
                )
                for i in range(4)
            ),
            starting_player=parser.bidding_winner,
        )
