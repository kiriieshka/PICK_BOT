import json

from pathlib import Path

import asyncpg

from config import (
    DB_ENABLED,
    DATABASE_URL,
    HISTORY_FILE,
    EXCLUDED_FILE,
)

from bot.services.game_service import Game


POOL = None


# ============================================================
# ИНИЦИАЛИЗАЦИЯ БАЗЫ
# ============================================================

async def init_db():
    global POOL

    if not DB_ENABLED:
        Path(HISTORY_FILE).parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not Path(HISTORY_FILE).exists():
            Path(HISTORY_FILE).write_text(
                "[]",
                encoding="utf-8",
            )

        if not Path(EXCLUDED_FILE).exists():
            Path(EXCLUDED_FILE).write_text(
                "[]",
                encoding="utf-8",
            )

        return

    if not DATABASE_URL:
        raise RuntimeError(
            "DB_ENABLED=true, но переменная DATABASE_URL не задана"
        )

    POOL = await asyncpg.create_pool(
        dsn=DATABASE_URL,
        min_size=1,
        max_size=5,
    )

    async with POOL.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS active_games (
                chat_id BIGINT PRIMARY KEY,
                state_json TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS game_history (
                id BIGSERIAL PRIMARY KEY,
                chat_id BIGINT NOT NULL,
                mode INT NOT NULL DEFAULT 50,
                players_count INT NOT NULL,
                result_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Миграция старой v1.0 таблицы
        await conn.execute("""
            ALTER TABLE game_history
            ADD COLUMN IF NOT EXISTS mode INT NOT NULL DEFAULT 50
        """)

        # Игроки, исключённые из турнирной таблицы.
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS excluded_players (
                name_key VARCHAR(100) PRIMARY KEY,
                display_name VARCHAR(100) NOT NULL,
                excluded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


# ============================================================
# ЗАКРЫТИЕ БАЗЫ
# ============================================================

async def close_db():
    global POOL

    if POOL:
        await POOL.close()
        POOL = None


# ============================================================
# СОХРАНЕНИЕ ИГРЫ
# ============================================================

async def save_game(chat_id, game):
    if not POOL:
        return

    state = json.dumps(
        game.to_dict(),
        ensure_ascii=False,
    )

    async with POOL.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO active_games(chat_id, state_json, updated_at)
            VALUES($1, $2, CURRENT_TIMESTAMP)
            ON CONFLICT (chat_id) DO UPDATE SET
                state_json = EXCLUDED.state_json,
                updated_at = CURRENT_TIMESTAMP
            """,
            chat_id,
            state,
        )


# ============================================================
# УДАЛЕНИЕ СОХРАНЁННОЙ ИГРЫ
# ============================================================

async def delete_saved_game(chat_id):
    if not POOL:
        return

    async with POOL.acquire() as conn:
        await conn.execute(
            "DELETE FROM active_games WHERE chat_id=$1",
            chat_id,
        )


# ============================================================
# СОХРАНЕНИЕ ИСТОРИИ
# ============================================================

async def save_history(chat_id, game):
    result = {
        "players": [
            p.to_dict()
            for p in game.players
        ],
        "pool_left": len(game.pool),
        "winner": (
            game.winner().name
            if game.winner()
            else None
        ),
        "mode": game.mode,
    }

    if not POOL:
        path = Path(HISTORY_FILE)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        try:
            history = json.loads(
                path.read_text(
                    encoding="utf-8"
                )
            )

            if not isinstance(history, list):
                history = []

        except Exception:
            history = []

        history.append(result)

        path.write_text(
            json.dumps(
                history,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        return

    async with POOL.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO game_history(
                chat_id,
                mode,
                players_count,
                result_json
            )
            VALUES($1, $2, $3, $4)
            """,
            chat_id,
            game.mode,
            len(game.players),
            json.dumps(
                result,
                ensure_ascii=False,
            ),
        )


# ============================================================
# НОРМАЛИЗАЦИЯ ИМЕНИ
# ============================================================

def normalize_player_name(name):
    return str(name).strip().casefold()


# ============================================================
# ПОЛУЧИТЬ ИСКЛЮЧЁННЫХ ИГРОКОВ
# ============================================================

async def get_excluded_players():
    if POOL:

        async with POOL.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT name_key, display_name
                FROM excluded_players
                ORDER BY display_name
                """
            )

        return [
            {
                "name_key": row["name_key"],
                "name": row["display_name"],
            }
            for row in rows
        ]

    path = Path(EXCLUDED_FILE)

    if not path.exists():
        return []

    try:
        data = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

        if not isinstance(data, list):
            return []

        return [
            {
                "name_key": normalize_player_name(name),
                "name": str(name),
            }
            for name in data
        ]

    except Exception:
        return []


# ============================================================
# ИСКЛЮЧИТЬ ИГРОКА
# ============================================================

async def exclude_player(name):
    name = str(name).strip()[:30]
    name_key = normalize_player_name(name)

    if not name_key:
        return

    if POOL:

        async with POOL.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO excluded_players(
                    name_key,
                    display_name
                )
                VALUES($1, $2)
                ON CONFLICT (name_key) DO UPDATE SET
                    display_name = EXCLUDED.display_name
                """,
                name_key,
                name,
            )

        return

    path = Path(EXCLUDED_FILE)
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    try:
        data = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

        if not isinstance(data, list):
            data = []

    except Exception:
        data = []

    existing = {
        normalize_player_name(x)
        for x in data
    }

    if name_key not in existing:
        data.append(name)

    path.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


# ============================================================
# ВЕРНУТЬ ИГРОКА В ТУРНИР
# ============================================================

async def include_player(name):
    name_key = normalize_player_name(name)

    if not name_key:
        return

    if POOL:

        async with POOL.acquire() as conn:
            await conn.execute(
                """
                DELETE FROM excluded_players
                WHERE name_key=$1
                """,
                name_key,
            )

        return

    path = Path(EXCLUDED_FILE)

    if not path.exists():
        return

    try:
        data = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

        if not isinstance(data, list):
            return

    except Exception:
        return

    data = [
        x
        for x in data
        if normalize_player_name(x) != name_key
    ]

    path.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


# ============================================================
# ПРОВЕРКА ИСКЛЮЧЕНИЯ
# ============================================================

async def is_player_excluded(name):
    name_key = normalize_player_name(name)

    excluded = await get_excluded_players()

    return any(
        item["name_key"] == name_key
        for item in excluded
    )


# ============================================================
# ОБЩАЯ СТАТИСТИКА
# ============================================================

async def get_overall_statistics():
    records = []

    excluded = await get_excluded_players()

    excluded_keys = {
        item["name_key"]
        for item in excluded
    }

    if POOL:

        async with POOL.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT result_json
                FROM game_history
                ORDER BY created_at ASC, id ASC
                """
            )

        for row in rows:
            try:
                records.append(
                    json.loads(row["result_json"])
                )
            except Exception:
                pass

    else:

        path = Path(HISTORY_FILE)

        if path.exists():
            try:
                records = json.loads(
                    path.read_text(
                        encoding="utf-8"
                    )
                )
            except Exception:
                records = []

    aggregate = {}

    for record in records:

        players = record.get(
            "players",
            [],
        )

        winner = record.get("winner")

        for player in players:

            name = str(
                player.get(
                    "name",
                    "Игрок",
                )
            )[:30]

            key = normalize_player_name(name)

            if not key:
                continue

            # ИСКЛЮЧЁННЫЕ ИГРОКИ НЕ ПОПАДАЮТ В РЕЙТИНГ.
            if key in excluded_keys:
                continue

            if key not in aggregate:
                aggregate[key] = {
                    "name": name,
                    "games": 0,
                    "wins": 0,
                    "completed": 0,
                    "failed": 0,
                    "attempts": 0,
                }

            item = aggregate[key]

            item["games"] += 1

            item["completed"] += int(
                player.get(
                    "completed",
                    0,
                )
            )

            item["failed"] += int(
                player.get(
                    "failed",
                    0,
                )
            )

            item["attempts"] += int(
                player.get(
                    "attempts",
                    0,
                )
            )

            if (
                winner
                and key == normalize_player_name(winner)
            ):
                item["wins"] += 1

    result = list(
        aggregate.values()
    )

    for item in result:

        item["success_percent"] = (
            round(
                item["completed"]
                / item["attempts"]
                * 100
            )
            if item["attempts"]
            else 0
        )

    return result


# ============================================================
# ВОССТАНОВЛЕНИЕ АКТИВНЫХ ИГР
# ============================================================

async def restore_games(active_games):
    if not POOL:
        return

    async with POOL.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT chat_id, state_json
            FROM active_games
            """
        )

    for row in rows:
        chat_id = row["chat_id"]
        state = row["state_json"]

        try:
            active_games[int(chat_id)] = Game.from_dict(
                json.loads(state)
            )

        except Exception:
            continue
