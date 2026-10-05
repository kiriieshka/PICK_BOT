import json
import secrets
from pathlib import Path

from config import DATA_DIR


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


def generate_codes(count=CODES_COUNT):
    """
    Создаёт нужное количество уникальных 10-значных кодов.
    Уже существующие коды не удаляются.
    """
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
    users = _load_json(USERS_FILE, {})
    return str(user_id) in users


def activate_code(user_id: int, code: str) -> str:
    """
    Возвращает:
    - 'activated' — успешно активирован
    - 'already_activated' — пользователь уже активирован
    - 'invalid' — код неправильный
    - 'used' — код уже использован
    """
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
    codes = _load_json(CODES_FILE, {})
    return [code for code, used in codes.items() if not used]


def get_used_codes():
    codes = _load_json(CODES_FILE, {})
    return [code for code, used in codes.items() if used]


# При первом запуске автоматически создаём 100 кодов.
generate_codes()