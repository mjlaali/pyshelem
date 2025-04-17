from __future__ import annotations
from dataclasses import dataclass, field

from pyshelem.engine.card import Deck, Card
from pyshelem.engine.game import Shelem, ShelemPlayer, TurnState
from pyshelem.engine.trick import Trick


class Visualizer:
    def init(self, cards: list[Card], player_idx: int) -> None:
        pass

    def bid(
        self, cards: list[Card], bids: list[int], bid: int, player_idx: int
    ) -> None:
        pass

    def discard(
        self,
        cards: list[Card],
        left_over_cards: list[Card],
        discarded: list[Card],
        player_idx: int,
    ) -> None:
        pass

    def play(self, state: TurnState, card: Card, player_idx: int) -> None:
        pass


@dataclass
class StrVisualizer(Visualizer):
    player_cards: list[str] = field(default_factory=lambda: [[] for i in range(4)])
    bids: list[int] = field(default_factory=list)
    discarded: str = ""
    current_round: list[Card] = field(default_factory=lambda: [None for _ in range(4)])
    plays: list[str] = field(default_factory=list)

    def init(self, cards: list[Card], player_idx: int) -> None:
        self.player_cards[player_idx] = "".join(card.str_value for card in cards)
        print(f"player {player_idx} cards: {self.player_cards[player_idx]}")

    def bid(
        self, cards: list[Card], bids: list[int], bid: int, player_idx: int
    ) -> None:
        print(f"player {player_idx} bids as {bid}")
        self.bids = self.bids + [bid]

    def discard(
        self,
        cards: list[Card],
        left_over_cards: list[Card],
        discarded: list[Card],
        player_idx: int,
    ) -> None:
        if discarded:
            self.discarded = chr(len(discarded) + ord("A")) + "".join(
                card.str_value for card in discarded
            )
            print(f"player {player_idx} discards {self.discarded}")

    def play(self, state: TurnState, card: Card, player_idx: int) -> None:
        print(f"player {player_idx} plays {card.str_value}")
        self.current_round[player_idx] = card

        last_round = all(card is not None for card in self.current_round)
        if last_round:
            self.plays.append("".join(card.str_value for card in self.current_round))
            self.current_round = [None for _ in range(4)]

    @property
    def str_game(self) -> str:
        player_cards = "\n".join(self.player_cards)
        print(self.bids)
        bids = (
            "".join(
                ("*" + chr((bid - 95) // 5 + ord("A")) if bid is not None else "*")
                for bid in self.bids
            )
            + "******"
        )
        discarded = self.discarded
        plays = "\n".join(f"{i}: {play}" for i, play in enumerate(self.plays))

        return f"cards:\n{player_cards}\n{bids}\n{discarded}\n{plays}"


@dataclass
class VisualizerAdaptor(ShelemPlayer):
    player_idx: int
    player: ShelemPlayer
    visualizer: Visualizer

    def init(self, cards: list[Card]) -> None:
        self.player.init(cards)
        self.visualizer.init(cards, self.player_idx)

    def bid(self, cards: list[Card], bids: list[int]) -> int | None:
        bid = self.player.bid(cards, bids)
        self.visualizer.bid(cards, bids, bid, self.player_idx)
        return bid

    def discard(self, cards: list[Card], left_over_cards: list[Card]) -> list[Card]:
        discarded = self.player.discard(cards, left_over_cards)
        self.visualizer.discard(cards, left_over_cards, discarded, self.player_idx)
        return discarded

    def play(self, state: TurnState) -> Card:
        card = self.player.play(state)
        self.visualizer.play(state, card, self.player_idx)
        return card


@dataclass
class SimulatedPlayer(ShelemPlayer):
    bets: list[int]
    plays: list[Card]
    discard_cards: list[Card]

    def __post_init__(self):
        self.idx = 0
        if len(self.plays) != 12:
            raise ValueError(f"{len(self.plays)} != 12")

    def init(self, cards: list[Card]) -> None:
        difference_when_no_discard = len(self.discard_cards) == 0 and (
            set(self.plays) != set(cards)
        )
        difference_with_discard = len(self.discard_cards) > 0 and (
            len(set(self.plays) - set(cards) - set(self.discard_cards)) == 0
        )
        if difference_with_discard or difference_when_no_discard:
            raise ValueError(
                f"Player and game is out of sync!\nw/o discard: {difference_when_no_discard}\n"
                f"w/ discard: {difference_with_discard}\nplays = {self.plays}\n"
                f"sorted plays = {sorted(self.plays)}\ncards = {sorted(cards)}\n"
                f"diff = {set(self.plays) - set(cards)}\n"
                f"discard = {self.discard_cards}"
            )

    def bid(self, cards: list[Card], bids: list[int]) -> int:
        if len(self.bets):
            return self.bets.pop(0)
        return None

    def discard(self, cards: list[Card], left_over_cards: list[Card]) -> list[Card]:
        return self.discard_cards

    def play(self, state: TurnState) -> Card:
        self.idx += 1
        return self.plays.pop(0)


@dataclass
class Parser:
    deck: Deck | None = field(default=None, init=False)
    player_cards: list[list[Card]] | None = field(default=None, init=False)
    left_over_cards: list[Card] | None = field(default=None, init=False)
    starting_player_idx: int = field(default=-1, init=False)
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
            list(deck_cards[i * 12 : (i + 1) * 12]) for i in range(4)
        )
        self.left_over_cards = list(deck_cards[4 * 12 :])
        return self

    def set_betting(self, betting: str, starting_player_idx: int) -> Parser:
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
        self.starting_player_idx = starting_player_idx
        cur_player = starting_player_idx

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
        plays = self.deck.parse_cards(other_events[last_discard_card_pos:])
        return self.set_discard_cards(
            discard_cards, self.deck, self.bidding_winner
        ).set_plays(plays, self.bidding_winner, plays[0].suit)

    def set_discard_cards(
        self, discard_cards: str, deck: Deck, bedding_winner: int
    ) -> Parser:
        self.discard_cards[bedding_winner] = deck.parse_cards(discard_cards)
        return self

    def set_plays(
        self, cards: list[Card], bidding_winner: int, trump_suit: int
    ) -> Parser:

        cur_player_idx = bidding_winner
        for cur_card_idx in range(0, len(cards), 4):
            for i in range(4):
                self.player_plays[(cur_player_idx + i) % 4].append(
                    cards[cur_card_idx + i]
                )
            cur_player_idx = Trick(
                trump_suit=trump_suit,
                cards=[self.player_plays[i][-1] for i in range(4)],
                first_player=cur_player_idx,
            ).winner
        return self


@dataclass
class Simulator:
    str_game: str
    visualizer: Visualizer

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
            players=tuple(
                VisualizerAdaptor(
                    player_idx=i,
                    player=SimulatedPlayer(
                        bets=parser.player_bids[i],
                        plays=parser.player_plays[i],
                        discard_cards=parser.discard_cards[i],
                    ),
                    visualizer=self.visualizer,
                )
                for i in range(4)
            ),
            starting_player=parser.starting_player_idx,
        )


if __name__ == "__main__":
    str_game = (
        "259,0,233,253,266,264,"
        "3S5S4S7D6H4H7SKCAS4C6C9C"
        "2D5D3DJDJS8H4DJC2HKD8CQS"
        "XDQC9SXS9HAH6SXH7CKSAC5C"
        "7H5H6D2S8D3HQDJH9D8SADQH"
        "2CKH3CXC,"
        "*D*E*F*G******_"
        "E2C3CXC2S"
        "JH4H2H9H"  # 3
        "QH6H8HAH"  # 2
        "6S8SASJS"  # 0
        "7DKDXD6D"  # 1
        "2D5CQD4C"  # 3
        "KH3S8CXH"  # 3
        "7H4S5D9S"  # 3
        "5H6C4D7C"  # 3
        "AD7S3DQC"  # 3
        "9D9CJDXS"  # 1
        "QSKS3H5S"  # 3
        "8DKCJCAC"  # 3
    )
    visualizer = StrVisualizer()
    simulator = Simulator(str_game, visualizer)
    simulator.shelem.play()

    print(visualizer.str_game)
