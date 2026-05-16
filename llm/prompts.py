SYSTEM_PROMPT = """
Ты — полезный ассистент.
Ответь кратко, ясно и по делу.
Если пользователь просит суммаризацию, выдели главную мысль.
""".strip()


def build_prompt(message: str) -> list[dict]:
    return [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": message,
        },
    ]