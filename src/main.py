# import os
# import sys

from src.models.aeroplane import (
    Aeroplane,
    filter_aeroplanes,
    get_aeroplanes_by_altitude,
    get_top_aeroplanes,
    print_aeroplanes,
    sort_aeroplanes,
)
from src.models.api_adapter import AeroplanesAPI
from src.models.file_saver import JSONSaver

# Добавляем корневую директорию в пути поиска модулей для корректной работы Poetry
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def user_interaction() -> None:
    """Интерактивный диалог с пользователем для определения параметров и вывода конечного результата"""
    print("=== СИСТЕМНЫЙ ТРЕКЕР ВОЗДУШНОГО ПРОСТРАНСТВА ===")
    api = AeroplanesAPI()
    json_saver = JSONSaver()

    # 1. Запрос страны и получение данных
    country = input("Введите название страны для запроса (например, Spain): ").strip()
    if not country:
        country = "Switzerland"
        print(f"Применено дефолтное воздушное пространство: {country}")

    print(f"Получение данных из API для региона '{country}'...")
    raw_data = api.get_aeroplanes(country)

    if raw_data is None:
        print("❌ Не удалось получить данные о самолетах для этого региона (API вернул пустоту).")
        return

    aeroplanes = Aeroplane.cast_to_object_list(raw_data)

    if not aeroplanes:
        print("❌ Не удалось получить данные о самолетах для этого региона.")
        return

    print(f"✈️ Всего самолетов обнаружено в небе: {len(aeroplanes)}")

    # 2. Запрос параметров у пользователя
    try:
        top_n_input = input("Введите количество самолетов для вывода в ТОП N по высоте (по умолчанию 5): ").strip()
        top_n = int(top_n_input) if top_n_input else 5
    except ValueError:
        print("⚠️ Некорректный ввод. Выведено 5 самолетов по умолчанию.")
        top_n = 5

    filter_words = input(
        "Введите страны регистрации через пробел или Enter (например, Germany France): "
    ).split()
    altitude_range = input("Введите диапазон высот полета через дефис (например: 4000-12000) или Enter: ")

    # 3. Обработка данных (вызов функций из модуля aeroplane)
    filtered_aeroplanes = filter_aeroplanes(aeroplanes, filter_words)
    ranged_aeroplanes = get_aeroplanes_by_altitude(filtered_aeroplanes, altitude_range)
    sorted_aeroplanes = sort_aeroplanes(ranged_aeroplanes)
    top_aeroplanes = get_top_aeroplanes(sorted_aeroplanes, top_n)

    # 4. Вывод результата
    print("\n--- РЕЗУЛЬТАТ ОБРАБОТКИ ДАННЫХ ---")
    print_aeroplanes(top_aeroplanes)

    # 5. Сохранение данных в файл answers.json (с полной перезаписью)
    if top_aeroplanes:
        save_choice = input("\nХотите сохранить найденный ТОП самолетов в файл? (y/n): ").strip().lower()
        if save_choice in ["y", "yes", "да"]:
            print("[Система]: Полная перезапись файла актуальными данными...")
            json_saver.save_bulk_aeroplanes(top_aeroplanes)
            print(f"✅ Успешно сохранено {len(top_aeroplanes)} самолетов в корень проекта (data/answers.json).")


if __name__ == "__main__":
    user_interaction()
