import json
import os
from abc import ABC, abstractmethod
from typing import Any, cast

from src.models.aeroplane import Aeroplane


class FileSaver(ABC):
    """
    Абстрактный класс, обязывающий реализовать методы для работы с хранилищем данных.
    Выступает основой для коннекторов (файлы, базы данных, облако).
    """

    @abstractmethod
    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Добавить информацию о самолете в хранилище."""
        pass

    @abstractmethod
    def get_aeroplanes(self, criterion: dict) -> list:
        """Получить данные из хранилища по указанным критериям."""
        pass

    @abstractmethod
    def delete_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Удалить информацию о самолете из хранилища."""
        pass


class JSONSaver(FileSaver):
    """Класс для сохранения, поиска и удаления информации о самолетах в JSON-файле."""

    def __init__(self, filename: str = "data/answers.json") -> None:
        # ИСПРАВЛЕНО: Вычисляем абсолютный путь к корню проекта (на 2 уровня вверх от file_saver.py)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.filename = os.path.join(base_dir, filename)

        # Автоматически создаем папку data в корне проекта, если её ещё нет
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        # Если сам JSON-файл не существует, создаем его с пустым списком внутри
        if not os.path.exists(self.filename):
            self._save_to_file([])

    def _read_file(self) -> list[Any]:
        """Внутренний метод для безопасного чтения данных из JSON-файла."""
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                return cast(list[Any], json.load(f))
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_to_file(self, data: list) -> None:
        """Внутренний метод для записи списка данных обратно в JSON-файл."""
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Метод используется для очистки и перезаписи файла новым списком."""
        # Для реализации Шага 3, если метод вызывается для одного самолета, мы можем либо копить,
        # либо перезаписывать. Но так как в main мы пишем пачкой, мы сделаем метод save_bulk ниже,
        # а этот метод адаптируем под чистую перезапись одиночным объектом, если нужно.
        self._save_to_file([aeroplane.to_dict()])

    def save_bulk_aeroplanes(self, aeroplanes: list[Aeroplane]) -> None:
        """
        Дополнительный удобный метод для полной перезаписи файла списком самолетов.
        Очищает файл и записывает туда только переданный ТОП.
        """
        data_to_save = [plane.to_dict() for plane in aeroplanes]
        self._save_to_file(data_to_save)

    def get_aeroplanes(self, criterion: dict) -> list:
        """Находит самолеты в файле по критериям."""
        data = self._read_file()
        filtered = []
        for item in data:
            if all(item.get(k) == v for k, v in criterion.items()):
                filtered.append(item)
        return filtered

    def delete_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Удаляет самолет из файла по совпадению позывного (callsign)."""
        data = self._read_file()
        data = [item for item in data if item["callsign"] != aeroplane.callsign]
        self._save_to_file(data)


class DatabaseSaverStub(FileSaver):
    """Класс-заглушка для будущей интеграции с базой данных."""

    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        pass

    def get_aeroplanes(self, criterion: dict) -> list:
        return []

    def delete_aeroplane(self, aeroplane: Aeroplane) -> None:
        pass
