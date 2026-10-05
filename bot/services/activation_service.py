import json
import secrets
from pathlib import Path

from config import DATA_DIR, DATABASE_URL, DB_ENABLED


CODES_FILE = Path(DATA_DIR) / "activation_codes.json"
USERS_FILE = Path(DATA_DIR) / "activated_users.json"

CODE_LENGTH = 10
CODES_COUNT = 100


def _ensure_data_dir():
    Path(DATA_DIR).mkdir(parents=True, exist_ok=True)


def _load_json(path: Path, default):
    _ensure_data_dir()

    if not path.exists():
        path.write_text(
            json.dumps(default, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return default

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def _save_json(path: Path, data):
    _ensure_data_dir()
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _db_connect():
    if not DB_ENABLED or not DATABASE_URL:
        return None

    import psycopg
    return psycopg.connect(DATABASE_URL)


def generate_codes(count=CODES_COUNT):
    """Создаёт нужное количество кодов."""
    if DB_ENABLED:
        with _db_connect() as conn:
            with conn.cursor() as cur:
                while True:
                    cur.execute(
                        "SELECT COUNT(*) FROM activation_codes"
                    )
                    current = cur.fetchone()[0]
                    if current >= count:
                        break

                    code = "".join(
                        str(secrets.randbelow(10))
                        for _ in range(CODE_LENGTH)
                    )

                    try:
                        cur.execute(
                            """
                            INSERT INTO activation_codes(code, status)
                            VALUES (%s, 'available')
                            ON CONFLICT (code) DO NOTHING
                            """,
                            (code,),
                        )
                    except Exception:
                        conn.rollback()
        return

    codes = _load_json(CODES_FILE, {})

    while len(codes) < count:
        code = "".join(
            str(secrets.randbelow(10))
            for _ in range(CODE_LENGTH)
        )

        if code not in codes:
            codes[code] = False

    _save_json(CODES_FILE, codes)
    return codes


def is_activated(user_id: int) -> bool:
    if DB_ENABLED:
        with _db_connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 1
                    FROM activated_users
                    WHERE telegram_id=%s
                    """,
                    (user_id,),
                )
                return cur.fetchone() is not None

    users = _load_json(USERS_FILE, {})
    return str(user_id) in users


def activate_code(user_id: int, code: str) -> str:
    """
    Returns:
    - activated
    - already_activated
    - invalid
    - used
    - not_for_user
    """
    if DB_ENABLED:
        with _db_connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 1
                    FROM activated_users
                    WHERE telegram_id=%s
                    """,
                    (user_id,),
                )
                if cur.fetchone():
                    return "already_activated"

                cur.execute(
                    """
                    SELECT status, buyer_telegram_id
                    FROM activation_codes
                    WHERE code=%s
                    FOR UPDATE
                    """,
                    (code,),
                )
                row = cur.fetchone()

                if not row:
                    return "invalid"

                status, buyer_telegram_id = row

                if status == "activated":
                    return "used"

                # Shop-issued keys belong to the Telegram account that paid.
                # Pre-generated "available" admin keys remain usable by anyone.
                if (
                    status == "issued"
                    and buyer_telegram_id is not None
                    and int(buyer_telegram_id) != int(user_id)
                ):
                    return "not_for_user"

                if status not in ("available", "issued"):
                    return "used"

                cur.execute(
                    """
                    UPDATE activation_codes
                    SET status='activated',
                        activated_at=CURRENT_TIMESTAMP
                    WHERE code=%s
                    """,
                    (code,),
                )

                cur.execute(
                    """
                    INSERT INTO activated_users(telegram_id)
                    VALUES (%s)
                    ON CONFLICT (telegram_id) DO NOTHING
                    """,
                    (user_id,),
                )

                return "activated"

    user_id = str(user_id)
    code = code.strip()

    users = _load_json(USERS_FILE, {})
    codes = _load_json(CODES_FILE, {})

    if user_id in users:
        return "already_activated"

    if code not in codes:
        return "invalid"

    if codes[code]:
        return "used"

    codes[code] = True
    users[user_id] = True

    _save_json(CODES_FILE, codes)
    _save_json(USERS_FILE, users)

    return "activated"


def get_unused_codes():
    if DB_ENABLED:
        with _db_connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT code
                    FROM activation_codes
                    WHERE status='available'
                    ORDER BY id
                    """
                )
                return [row[0] for row in cur.fetchall()]

    codes = _load_json(CODES_FILE, {})
    return [code for code, used in codes.items() if not used]


def get_used_codes():
    if DB_ENABLED:
        with _db_connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT code
                    FROM activation_codes
                    WHERE status='activated'
                    ORDER BY id
                    """
                )
                return [row[0] for row in cur.fetchall()]

    codes = _load_json(CODES_FILE, {})
    return [code for code, used in codes.items() if used]
