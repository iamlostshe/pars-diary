"""Модуль для парсинга."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .consts import (
    COLOR_MARKERS,
    MARK_STR_TO_FLOAT,
    MINIFY_LESSON_TITLE,
    NO_I_MARKS_DATA,
)

if TYPE_CHECKING:
    from bars_api import BarsAPI


def _get_space_len(parent: dict) -> int:
    """Возвращает кол-во симовлов, для отступов."""
    try:
        return (
            max(
                len(
                    MINIFY_LESSON_TITLE.get(
                        s.discipline,
                        s.discipline,
                    ),
                )
                for s in parent
            )
            + 1
        )
    except ValueError:
        return 0


async def me(parser: BarsAPI) -> str:
    """Информация о пользователе."""
    data = await parser.get_person_data()

    # Авторизован родитель
    if data.children_persons:
        childrens = "\n\n".join(
            [
                (
                    f"{n + 1} ребенок:\n\n"
                    f"ФИО - {' '.join(i.fullname.split()[:-1])}\n"
                    f"Дата рождения - {i.fullname.split()[-1]}\n"
                    f"Школа - {i.school}\n"
                    f"Класс - {i.classyear}"
                )
                for n, i in enumerate(data.children_persons)
            ],
        )

        return (
            f"ФИО (родителя) - {data.user.fullname}\n"
            f"Номер телефона - {data.user.phone}\n\n"
        ) + childrens

    # Авторизован ребёнок
    return (
        f"ФИО - {data.user.fullname}\n"
        f"Пол - {'Мужской' if data.user.is_male else 'Женский'}\n"
        f"Школа - {data.selected_pupil.school}\n"
        f"Класс - {data.selected_pupil.classyear}"
    )


async def events(parser: BarsAPI) -> str:
    """Информация о ивентах."""
    data = await parser.get_events()

    if not data:
        return "Кажется, ивентов не намечается)"

    return f"{data}"


async def birthdays(parser: BarsAPI) -> str:
    """Информация о днях рождения."""
    data = await parser.get_birthdays()

    if not data:
        return "Кажется, дней рождений не намечается)"

    return "\n\n".join(
        f"{data.date.replace('-', ' ')}\n{data.short_name}" for i in data
    )


async def marks(parser: BarsAPI) -> str:
    """Информация об оценках."""
    data = await parser.get_summary_marks()

    if not data.discipline_marks:
        return (
            "Информация об оценках отсутствует\n\n"
            "Кажется, вам пока не поставили ни одной("
        )

    marks_list = []
    for_midle_marks = []

    space_len = _get_space_len(data.discipline_marks)

    for subject in data.discipline_marks:
        # Получаем название предмета
        g = MINIFY_LESSON_TITLE.get(
            subject.discipline,
            subject.discipline,
        ).ljust(space_len)

        # Получаем список оценок по предмету
        marks = []
        str_marks = []

        for m in subject.marks:
            mm = m.mark
            str_marks.append(mm)
            try:
                marks.append(float(mm))
            except ValueError:
                marks.append(MARK_STR_TO_FLOAT[mm])

        # Получаем правильные (рассчитанные) средние быллы по предметам,
        # потому что сервер иногда возвращает нули.
        len_marks = len(marks)
        average_mark = f"{sum(marks) / len_marks:.2f}" if len_marks else "0.00"
        float_average_mark = float(average_mark)

        # Добавляем средний балл по предмету в список
        # для рассчёта общего среднего балла
        for_midle_marks.append(float_average_mark)

        # Определяем цвет маркера, в зависимости от балла
        color_mark = COLOR_MARKERS[round(float_average_mark)]

        # Формируем сообщение
        marks_list.append(f"{color_mark} {g}│ {average_mark} │ {' '.join(str_marks)}")

    return (
        "Оценки:\n\n<pre>"
        f"{"\n".join(sorted(marks_list, key=lambda x: float(x.split(' │ ', 2)[1])))}\n"
        "\nОбщий средний балл (рассичитан): "
        f"{sum(for_midle_marks) / len(for_midle_marks):.2f}"
        "</pre>"
    )


async def i_marks(parser: BarsAPI) -> str:
    """Информация об итоговых оценках."""
    data = await parser.get_total_marks()

    discipline_marks_data = data.discipline_marks

    if not discipline_marks_data:
        return NO_I_MARKS_DATA

    subperiods = {i.code: i.name for i in data.subperiod}

    subperiods_names = list(subperiods.values())
    len_subperiods_names = len(subperiods_names)

    subperiods_names_first_letter = [i[0] for i in subperiods_names]

    explanation = [
        f"{subperiods_names_first_letter[i]} - {subperiods_names[i]}"
        for i, _ in enumerate(subperiods_names)
    ]

    space_len = _get_space_len(discipline_marks_data)

    msg_text = (
        f"Итоговые оценки:\n\n{'\n'.join(explanation)}\n\n<pre>\n"
        f"{'Предмет'.ljust(space_len)}│ "
        f"{' | '.join(subperiods_names_first_letter)} |\n"
        f"{space_len * '─'}┼{('───┼' * len_subperiods_names)[:-1]}┤\n"
    )

    subperiod_index = list(subperiods.keys())

    for discipline in discipline_marks_data:
        stroka = list("-" * len_subperiods_names)
        g = MINIFY_LESSON_TITLE.get(
            discipline.discipline,
            discipline.discipline,
        ).ljust(space_len)

        msg_text += f"{g}│ "

        for period_mark in discipline.period_marks:
            # Получаем индекс и присваиваем значение
            if period_mark.subperiod_code in subperiod_index:
                stroka[subperiod_index.index(period_mark.subperiod_code)] = (
                    period_mark.mark
                )

        msg_text += f"{' │ '.join(stroka)}"

        msg_text += " │\n"

    return f"{msg_text}</pre>"
