from operator import attrgetter


class Aeroplane:
    """Класс, описывающий конкретное воздушное судно в парадигме ООП с полной инкапсуляцией."""

    def __init__(self, callsign: str, country: str, velocity: float, altitude: float) -> None:
        # ИНКАПСУЛЯЦИЯ: Делаем атрибуты защищенными (с нижним подчеркиванием)
        self._callsign = callsign.strip() if callsign else "UNKNOWN"
        self._country = country if country else "Unknown"
        self._velocity = float(velocity) if velocity is not None else 0.0
        self._altitude = float(altitude) if altitude is not None else 0.0

    # ГЕТТЕРЫ (Properties) для безопасного доступа к данным извне (только для чтения)
    @property
    def callsign(self) -> str:
        return self._callsign

    @property
    def country(self) -> str:
        return self._country

    @property
    def velocity(self) -> float:
        return self._velocity

    @property
    def altitude(self) -> float:
        return self._altitude

    # =================================================================
    # МЕТОДЫ СРАВНЕНИЯ (По умолчанию по ВЫСОТЕ, как требуется в ТОП N)
    # =================================================================
    def __lt__(self, other: "Aeroplane") -> bool:
        """Сравнение: 'меньше' (<) по высоте полета."""
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self._altitude < other._altitude

    def __le__(self, other: "Aeroplane") -> bool:
        """Сравнение: 'меньше или равно' (<=) по высоте полета."""
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self._altitude <= other._altitude

    def __gt__(self, other: "Aeroplane") -> bool:
        """Сравнение: 'больше' (>) по высоте полета."""
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self._altitude > other._altitude

    def __ge__(self, other: "Aeroplane") -> bool:
        """Сравнение: 'больше или равно' (>=) по высоте полета."""
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self._altitude >= other._altitude

    def __eq__(self, other: object) -> bool:
        """Сравнение: 'равно' (==) по высоте полета."""
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self._altitude == other._altitude

    # ==========================================
    # ФАБРИЧНЫЙ МЕТОД ПРЕОБРАЗОВАНИЯ ДАННЫХ API
    # ==========================================
    @classmethod
    def cast_to_object_list(cls, api_response: dict) -> list["Aeroplane"]:
        """Преобразует сырой JSON-ответ API или Mock-данные в список объектов Aeroplane."""
        if not api_response or "states" not in api_response or api_response["states"] is None:
            return []

        aeroplanes_list = []
        for state in api_response["states"]:
            # Извлекаем данные по строгим индексам OpenSky:
            # 1 - позывной, 2 - страна, 7 - высота, 9 - скорость
            obj = cls(callsign=state[1], country=state[2], altitude=state[7], velocity=state[9])
            aeroplanes_list.append(obj)
        return aeroplanes_list

    def to_dict(self) -> dict:
        """Конвертирует объект класса в словарь для сохранения в JSON."""
        return {
            "callsign": self.callsign,
            "country": self.country,
            "velocity": self.velocity,
            "altitude": self.altitude,
        }

    def __repr__(self) -> str:
        """Красивое текстовое отображение объекта в консоли."""
        return f"[{self.callsign}] Страна: {self.country} | Скорость: {self.velocity} м/с | Высота: {self.altitude} м"


# =================================================================
# ВЫНЕСЕННЫЕ ФУНКЦИИ ДЛЯ РАБОТЫ СО СПИСКАМИ САМОЛЕТОВ
# =================================================================


def filter_aeroplanes(aeroplanes: list[Aeroplane], countries: list[str]) -> list[Aeroplane]:
    """Фильтрует самолеты по списку стран их регистрации."""
    if not countries or countries == [""] or countries == []:
        return aeroplanes
    return [a for a in aeroplanes if any(c.lower() in a.country.lower() for c in countries)]


def get_aeroplanes_by_altitude(aeroplanes: list[Aeroplane], altitude_range: str) -> list[Aeroplane]:
    """Фильтрует самолеты по диапазону высот (принимает строку формата '1000-5000')."""
    if not altitude_range.strip():
        return aeroplanes
    try:
        start, end = map(float, altitude_range.split("-"))
        return [a for a in aeroplanes if start <= a.altitude <= end]
    except ValueError:
        print("⚠️ Некорректный формат диапазона высот. Фильтрация пропущена.")
        return aeroplanes


def sort_aeroplanes(aeroplanes: list[Aeroplane], by_attribute: str = "altitude") -> list[Aeroplane]:
    """
    Универсальная сортировка списка самолетов от большего к меньшему.
    По умолчанию сортирует по 'altitude' (высоте), но может сортировать и по 'velocity' (скорости).
    """
    try:
        # attrgetter безопасно читает свойства через геттеры @property, не нарушая инкапсуляцию
        return sorted(aeroplanes, key=attrgetter(by_attribute), reverse=True)
    except AttributeError:
        print(f"⚠️ У самолета нет свойства '{by_attribute}' для сортировки. Сортируем по высоте.")
        return sorted(aeroplanes, reverse=True)


def get_top_aeroplanes(aeroplanes: list[Aeroplane], top_n: int) -> list[Aeroplane]:
    """Возвращает первые N самолетов из списка."""
    return aeroplanes[:top_n]


def print_aeroplanes(aeroplanes: list[Aeroplane]) -> None:
    """Выводит список самолетов в консоль с порядковыми номерами."""
    if not aeroplanes:
        print("Самолеты по заданным критериям не найдены.")
        return
    for idx, plane in enumerate(aeroplanes, 1):
        print(f"{idx}. {plane}")
