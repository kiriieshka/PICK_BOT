def percent(p):
    return round(p.completed / p.attempts * 100) if p.attempts else 0


def ranking(players):
    ordered = sorted(players, key=lambda p: (p.score, percent(p)), reverse=True)
    medals = ["🥇", "🥈", "🥉"]
    lines = []
    for i, p in enumerate(ordered):
        place = medals[i] if i < 3 else f"{i + 1}."
        lines.append(f"{place} {p.name} — {p.score} очк. • {p.completed} выполнено • {percent(p)}%")
    return "\n".join(lines)


def details(players):
    out = []
    cat_names = {
        "shooting": "Броски",
        "dribbling": "Дриблинг",
        "speed": "Скорость",
        "physical": "Физика",
        "general": "Общее",
    }
    for p in players:
        cats = []
        for cat, value in p.categories.items():
            attempts = value["completed"] + value["failed"]
            cat_percent = round(value["completed"] / attempts * 100) if attempts else 0
            cats.append(f"{cat_names.get(cat, cat)}: {cat_percent}%")
        block = (
            f"🏀 {p.name}\n"
            f"🏆 Очки: {p.score}\n"
            f"😎 Выполнено: {p.completed}\n"
            f"💀 Провалено: {p.failed}\n"
            f"🎯 Успешность: {percent(p)}%"
        )
        if cats:
            block += "\n📚 " + ", ".join(cats)
        out.append(block)
    return "\n\n".join(out)


def overall_ranking(players):
    if not players:
        return "Пока нет завершённых игр.\nСыграйте первую игру, и здесь появится турнирная таблица."

    ordered = sorted(players, key=lambda x: (x["wins"], x["completed"], x["success_percent"]), reverse=True)
    medals = ["🥇", "🥈", "🥉"]
    lines = ["🏆 ТУРНИРНАЯ ТАБЛИЦА", ""]
    for i, p in enumerate(ordered):
        place = medals[i] if i < 3 else f"{i + 1}."
        lines.append(
            f"{place} {p['name']}\n"
            f"   🏆 {p['completed']} выполнено • {p['wins']} побед • "
            f"🎯 {p['success_percent']}% успеха • 🎮 {p['games']} игр"
        )
    return "\n".join(lines)
