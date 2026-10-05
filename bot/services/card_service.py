from pathlib import Path
import random
from config import CARDS_DIR

# ============================================================
# КАРТОЧКИ — ГЛАВНЫЙ БЛОК НАСТРОЕК
# ============================================================
# category: shooting / dribbling / speed / physical / general
# time: секунды на выполнение
# ============================================================

CARDS = {
    i: {
        "file": str(Path(CARDS_DIR) / f"{i:03}.png"),
        "category": "speed",
        "time": 30,
    }
    for i in range(1, 51)
}

# Пример настройки отдельной карточки:
# CARDS[1].update({"category": "shooting", "time": 20})
CARDS[1].update({"category": "speed", "time": 20})
CARDS[2].update({"category": "speed", "time": 10})
CARDS[3].update({"category": "speed", "time": 15})
CARDS[4].update({"category": "speed", "time": 25})
CARDS[5].update({"category": "speed", "time": 20})
CARDS[6].update({"category": "speed", "time": 10})
CARDS[7].update({"category": "speed", "time": 15})
CARDS[8].update({"category": "speed", "time": 15})
CARDS[9].update({"category": "speed", "time": 10})
CARDS[10].update({"category": "speed", "time": 15})
CARDS[11].update({"category": "speed", "time": 25})
CARDS[12].update({"category": "speed", "time": 15})
CARDS[13].update({"category": "speed", "time": 20})
CARDS[14].update({"category": "speed", "time": 30})
CARDS[15].update({"category": "speed", "time": 25})
CARDS[16].update({"category": "speed", "time": 25})

CARDS[17].update({"category": "shooting", "time": None})
CARDS[18].update({"category": "shooting", "time": None})
CARDS[19].update({"category": "shooting", "time": None})
CARDS[20].update({"category": "shooting", "time": None})
CARDS[21].update({"category": "shooting", "time": None})
CARDS[22].update({"category": "shooting", "time": None})
CARDS[23].update({"category": "shooting", "time": None})
CARDS[24].update({"category": "shooting", "time": None})
CARDS[25].update({"category": "shooting", "time": None})
CARDS[26].update({"category": "shooting", "time": None})
CARDS[27].update({"category": "shooting", "time": None})
CARDS[28].update({"category": "shooting", "time": None})
CARDS[29].update({"category": "shooting", "time": None})
CARDS[30].update({"category": "shooting", "time": None})
CARDS[31].update({"category": "shooting", "time": None})
CARDS[32].update({"category": "shooting", "time": None})

CARDS[33].update({"category": "physical", "time": None})
CARDS[34].update({"category": "physical", "time": None})
CARDS[35].update({"category": "physical", "time": None})
CARDS[36].update({"category": "physical", "time": None})
CARDS[37].update({"category": "physical", "time": None})
CARDS[38].update({"category": "physical", "time": None})
CARDS[39].update({"category": "physical", "time": None})
CARDS[40].update({"category": "physical", "time": None})
CARDS[41].update({"category": "physical", "time": None})
CARDS[42].update({"category": "physical", "time": None})
CARDS[43].update({"category": "physical", "time": None})
CARDS[44].update({"category": "physical", "time": None})
CARDS[45].update({"category": "physical", "time": None})
CARDS[46].update({"category": "physical", "time": None})
CARDS[47].update({"category": "physical", "time": None})
CARDS[48].update({"category": "physical", "time": None})

CARDS[49].update({"category": "general", "time": None})


def draw_card(pool, previous_card=None):
    if not pool:
        return None
    choices = [x for x in pool if x != previous_card] or pool
    return random.choice(choices)
