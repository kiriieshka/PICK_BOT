import time
from dataclasses import dataclass, field
from bot.services.card_service import CARDS, draw_card

# Режимы игры:
# 5 / 15 — карточки возвращаются в колоду после выполнения или провала.
# 50 — каждая карточка удаляется после попытки; нужно набрать 50 успешных.

@dataclass
class Player:
    name: str
    score: int = 0
    attempts: int = 0
    completed: int = 0
    failed: int = 0
    categories: dict = field(default_factory=dict)
    completed_cards: list = field(default_factory=list)

    def to_dict(self):
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data):
        data = dict(data)
        data.setdefault("completed_cards", [])
        return cls(**data)

@dataclass
class Game:
    mode: int
    players: list
    pool: list
    current_player: int = 0
    current_card: int | None = None
    card_started_at: float | None = None
    previous_card: int | None = None

    @property
    def target_score(self):
        return self.mode

    @property
    def return_cards(self):
        return self.mode in (5, 15)

    def instant_winner(self):
        return self.mode == 50 and self.current_card == 49

    @property
    def player(self):
        return self.players[self.current_player]

    def next_player(self):
        self.current_player = (self.current_player + 1) % len(self.players)

    def draw(self):
        self.current_card = draw_card(self.pool, self.previous_card)
        return self.current_card

    def start_timer(self):
        if self.current_card is None:
            return
        if CARDS[self.current_card]["time"] is None:
            self.card_started_at = None
            return
        self.card_started_at = time.monotonic()

    def elapsed(self):
        return 0 if self.card_started_at is None else time.monotonic() - self.card_started_at

    def time_left(self):
        if self.current_card is None:
            return 0
        card_time = CARDS[self.current_card]["time"]
        if card_time is None:
            return None
        return max(0, card_time - self.elapsed())

    def _record_attempt(self, success: bool):
        cid = self.current_card
        p = self.player
        p.attempts += 1
        cat = CARDS[cid]["category"]
        stats = p.categories.setdefault(cat, {"completed": 0, "failed": 0})
        if success:
            p.completed += 1
            p.score += 1
            stats["completed"] += 1
            if cid not in p.completed_cards:
                p.completed_cards.append(cid)
        else:
            p.failed += 1
            stats["failed"] += 1

        # В режимах до 5/15 карта возвращается всегда.
        # В режиме до 50 карта после попытки удаляется независимо от результата.
        if not self.return_cards and cid in self.pool:
            self.pool.remove(cid)

        self._clear_card(cid)

    def success(self):
        self._record_attempt(True)

    def fail(self):
        self._record_attempt(False)

    def _clear_card(self, cid):
        self.previous_card = cid
        self.current_card = None
        self.card_started_at = None

    def is_finished(self):
        # В режимах 5/15 игра заканчивается по очкам.
        if any(p.score >= self.target_score for p in self.players):
            return True
        # В режиме 50 игра также заканчивается, если карточки закончились.
        return not self.pool

    def winner(self):
        winners = [p for p in self.players if p.score >= self.target_score]
        return winners[0] if winners else None

    def to_dict(self):
        return {
            "mode": self.mode,
            "players": [p.to_dict() for p in self.players],
            "pool": self.pool,
            "current_player": self.current_player,
            "current_card": self.current_card,
            "previous_card": self.previous_card,
            "card_started_at": None,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            int(d.get("mode", 50)),
            [Player.from_dict(x) for x in d["players"]],
            d["pool"],
            d.get("current_player", 0),
            d.get("current_card"),
            None,
            d.get("previous_card"),
        )

ACTIVE_GAMES = {}

def create_game(chat_id, mode, names):
    game = Game(int(mode), [Player(n) for n in names], list(CARDS.keys()))
    ACTIVE_GAMES[chat_id] = game
    return game

def get_game(chat_id):
    return ACTIVE_GAMES.get(chat_id)

def delete_game(chat_id):
    ACTIVE_GAMES.pop(chat_id, None)
