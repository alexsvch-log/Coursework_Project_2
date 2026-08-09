from abc import ABC, abstractmethod
from typing import Any, cast

import requests


class BaseAPIAdapter(ABC):
    """Абстрактный базовый класс для всех API адаптеров."""

    @abstractmethod
    def fetch_data(self, *args: Any, **kwargs: Any) -> Any:
        pass


class NominatimAdapter(BaseAPIAdapter):
    """Адаптер для работы с OpenStreetMap Nominatim API (получение координат)."""

    def __init__(self) -> None:
        self.url = "https://openstreetmap.org"

        # Маскируемся под реальный браузер Chrome, чтобы избежать ошибки 406!
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
            " Chrome/120.0.0.0 Safari/537.36"
        }
        # Идеальный резервный квадрат Швейцарии
        self.fallback_coordinates = ["45.81792", "47.80838", "5.95587", "10.49203"]

    def fetch_data(self, country: str) -> list:
        params: dict[str, str | int] = {"country": country, "format": "json", "limit": 1}
        try:
            response = requests.get(url=self.url, params=params, headers=self.headers, timeout=5)
            response.raise_for_status()
            data = response.json()

            if data and isinstance(data, list) and len(data) > 0:
                bbox = data[0].get("boundingbox")
                if bbox and len(bbox) == 4:
                    return cast(list[str], bbox)

            print(f"⚠️ Страна '{country}' не найдена в базе данных Nominatim. Используем резервный квадрат Швейцарии.")
            return self.fallback_coordinates

        except requests.exceptions.Timeout:
            print("⚠️ Превышено время ожидания ответа от Nominatim API (Timeout). Сервер координат перегружен.")
            print("💡 Переключаемся на резервный квадрат Швейцарии.")
            return self.fallback_coordinates

        except requests.exceptions.SSLError:
            print(
                "⚠️ Ошибка SSL-сертификата при подключении к Nominatim API."
                " Возможно, требуется отключить/включить VPN."
            )
            print("💡 Переключаемся на резервный квадрат Швейцарии.")
            return self.fallback_coordinates

        except requests.RequestException as e:
            print(f"⚠️ Сетевая ошибка при обращении к Nominatim API. {e}")

            # Расшифровываем код ответа сервера, если он есть
            if e.response is not None:
                status_code = e.response.status_code
                print(f"   Код ответа сервера: {status_code}")
                if status_code == 403:
                    print(
                        "   💡 Причина: Доступ заблокирован сервером OpenStreetMap (Forbidden). Проверьте User-Agent."
                    )
                elif status_code == 429:
                    print(
                        "   💡 Причина: Слишком много запросов (Too Many Requests). Вы заблокированы за спам-запросы."
                    )
            else:
                print("   💡 Причина: Нет связи с сервером координат. Проверьте подключение к интернету.")

            print("💡 Переключаемся на резервный квадрат Швейцарии.")
            return self.fallback_coordinates

        except (ValueError, IndexError, KeyError, TypeError):
            print("⚠️ Ошибка: Сервер Nominatim ответил некорректной структурой данных (ошибка парсинга).")
            print("💡 Переключаемся на резервный квадрат Швейцарии.")
            return self.fallback_coordinates


class OpenSkyAdapter(BaseAPIAdapter):
    """Адаптер для работы с OpenSky Network API."""

    def __init__(self, username: str | None = None, password: str | None = None) -> None:
        self.url = "https://opensky-network.org"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
            " Chrome/120.0.0.0 Safari/537.36"
        }
        self.auth = (username, password) if username and password else None

    @staticmethod  # <-- Добавили декоратор, чтобы убрать предупреждение IDE
    def _get_mock_data() -> dict:
        """Возвращает 10 фейковых самолетов в точном формате OpenSky API для симуляции."""
        print("🤖 [Режим симуляции]: Генерируем расширенный набор из 10 самолетов для продолжения работы программы.")
        return {
            "time": 1766142246,
            "states": [
                [
                    "4b1812",
                    "SWR438A ",
                    "Switzerland",
                    1766166618,
                    1766166618,
                    -0.0168,
                    51.0888,
                    4267.2,
                    False,
                    189.7,
                    129.39,
                    14.63,
                    None,
                    4282.44,
                    "2061",
                    False,
                    0,
                ],
                [
                    "a10b3c",
                    "AAL123  ",
                    "United States",
                    1766166618,
                    1766166618,
                    8.5432,
                    47.3769,
                    10200.5,
                    False,
                    250.3,
                    90.0,
                    0.0,
                    None,
                    10300.0,
                    "1200",
                    False,
                    0,
                ],
                [
                    "3c4b12",
                    "DLH9x   ",
                    "Germany",
                    1766166618,
                    1766166618,
                    7.4474,
                    46.9480,
                    8500.0,
                    False,
                    210.5,
                    180.0,
                    -5.2,
                    None,
                    8600.0,
                    "3401",
                    False,
                    0,
                ],
                [
                    "4b1855",
                    "SWR11k  ",
                    "Switzerland",
                    1766166618,
                    1766166618,
                    6.1432,
                    46.2044,
                    1200.0,
                    False,
                    95.2,
                    270.0,
                    3.1,
                    None,
                    1250.0,
                    "7000",
                    False,
                    0,
                ],
                [
                    "39b1ca",
                    "AFR012  ",
                    "France",
                    1766166618,
                    1766166618,
                    2.3522,
                    48.8566,
                    11800.0,
                    False,
                    265.4,
                    45.0,
                    0.0,
                    None,
                    11950.0,
                    "2241",
                    False,
                    0,
                ],
                [
                    "34a211",
                    "IBE3102 ",
                    "Spain",
                    1766166618,
                    1766166618,
                    -3.7037,
                    40.4167,
                    5400.0,
                    False,
                    195.0,
                    220.0,
                    8.5,
                    None,
                    5500.0,
                    "1000",
                    False,
                    0,
                ],
                [
                    "c011b2",
                    "ACA850  ",
                    "Canada",
                    1766166618,
                    1766166618,
                    -73.5673,
                    45.5017,
                    9800.0,
                    False,
                    242.1,
                    85.5,
                    -1.2,
                    None,
                    9900.0,
                    "5521",
                    False,
                    0,
                ],
                [
                    "3c221a",
                    "DLH44   ",
                    "Germany",
                    1766166618,
                    1766166618,
                    9.9936,
                    53.5511,
                    3100.0,
                    False,
                    140.8,
                    15.0,
                    4.0,
                    None,
                    3150.0,
                    "4402",
                    False,
                    0,
                ],
                [
                    "a55b11",
                    "UAL901  ",
                    "United States",
                    1766166618,
                    1766166618,
                    -122.4194,
                    37.7749,
                    7200.0,
                    False,
                    220.1,
                    280.0,
                    0.0,
                    None,
                    7350.0,
                    "1200",
                    False,
                    0,
                ],
                [
                    "39c555",
                    "AFR88k  ",
                    "France",
                    1766166618,
                    1766166618,
                    5.3211,
                    43.2965,
                    6100.0,
                    False,
                    205.6,
                    110.0,
                    -2.5,
                    None,
                    6200.0,
                    "2245",
                    False,
                    0,
                ],
            ],
        }

    def fetch_data(self, geo_coordinates: list) -> dict | None:
        if not geo_coordinates or len(geo_coordinates) < 4:
            print("⚠️ Переданы некорректные координаты для сканирования.")
            return self._get_mock_data()

        params = {
            "lamin": float(geo_coordinates[0]),
            "lamax": float(geo_coordinates[1]),
            "lomin": float(geo_coordinates[2]),
            "lomax": float(geo_coordinates[3]),
        }
        try:
            response = requests.get(url=self.url, params=params, headers=self.headers, auth=self.auth, timeout=10)
            response.raise_for_status()

            if not response.text.strip():
                print("⚠️ Сервер OpenSky прислал пустой ответ.")
                return self._get_mock_data()

            return cast(dict[str, Any], response.json())

        except requests.exceptions.Timeout:
            print("⚠️ Превышено время ожидания ответа от OpenSky API (Timeout). Сервер перегружен.")
            return self._get_mock_data()

        except requests.exceptions.SSLError:
            print(
                "⚠️ Ошибка SSL-сертификата при подключении к OpenSky API. Возможно, требуется включить/выключить VPN."
            )
            return self._get_mock_data()

        except requests.RequestException as e:
            print(f"⚠️ Сетевая ошибка при обращении к OpenSky API. {e}")

            # Если сервер успел вернуть код ответа, расшифровываем его
            if e.response is not None:
                status_code = e.response.status_code
                print(f"   Код ответа сервера: {status_code}")
                if status_code == 429:
                    print("   💡 Причина: Вы исчерпали лимиты анонимных запросов (Too Many Requests).")
                elif status_code == 403:
                    print(
                        "   💡 Причина: Доступ заблокирован сервером (Forbidden)."
                        " Требуется авторизация или правильный User-Agent."
                    )
                elif status_code == 400:
                    print(
                        "   💡 Причина: Неверный формат параметров (Bad Request)."
                        " Возможно, выбран слишком большой квадрат территории."
                    )
            else:
                print("   💡 Причина: Нет связи с сервером. Проверьте подключение к интернету.")

            return self._get_mock_data()

        except ValueError:
            print("⚠️ Ошибка: Сервер OpenSky ответил не в формате JSON (ошибка парсинга).")
            return self._get_mock_data()


class AeroplanesAPI:
    """Фасад для управления обоими адаптерами."""

    def __init__(self, username: str | None = None, password: str | None = None) -> None:
        self.geo_api = NominatimAdapter()
        self.sky_api = OpenSkyAdapter(username, password)

    def get_aeroplanes(self, country: str) -> dict | None:
        coordinates = self.geo_api.fetch_data(country)
        return self.sky_api.fetch_data(coordinates)
