"""Lab 6 branching exercise; independent from Lab 2–4 and the application design."""

import sys


def greeting(name: str = "") -> str:
    cleaned_name = name.strip()
    prefix = f"Сайн уу, {cleaned_name}! " if cleaned_name else ""
    return prefix + (
        "Нийтийн дугуй түрээсийн системд тавтай морил! "
        "Аюулгүй аяллыг хамтдаа эхлүүлье!"
    )


def safety_note() -> str:
    return "Дуулгаа өмсөж, дугуйн тоормосоо шалгаарай."


if __name__ == "__main__":
    print(greeting(" ".join(sys.argv[1:])))
    print(safety_note())
