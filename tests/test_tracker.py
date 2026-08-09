import os
# import sys
import unittest
from unittest.mock import MagicMock, patch

import requests

from src.models.aeroplane import (
    Aeroplane,
    filter_aeroplanes,
    get_aeroplanes_by_altitude,
    get_top_aeroplanes,
    print_aeroplanes,
    sort_aeroplanes,
)
from src.models.api_adapter import AeroplanesAPI, NominatimAdapter, OpenSkyAdapter
from src.models.file_saver import DatabaseSaverStub, JSONSaver

# Добавляем корневую директорию проекта в пути поиска модулей
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestAeroplaneOOP(unittest.TestCase):
    """Тестирование класса Aeroplane, геттеров и магических методов."""

    def setUp(self):
        self.plane_low_fast = Aeroplane("SWR1", "Switzerland", 250.0, 3000.0)
        self.plane_high_slow = Aeroplane("AAL2", "United States", 180.0, 10000.0)
        self.plane_equal = Aeroplane("SWR1", "Switzerland", 250.0, 3000.0)

    def test_encapsulation_and_types(self):
        """Проверка инкапсуляции и корректности типов через @property."""
        self.assertIsInstance(self.plane_low_fast.callsign, str)
        self.assertIsInstance(self.plane_low_fast.altitude, float)
        self.assertEqual(self.plane_low_fast.callsign, "SWR1")

        with self.assertRaises(AttributeError):
            setattr(self.plane_low_fast, "altitude", 5000.0)

    def test_comparisons(self):
        """Проверка всех dunder-методов сравнения (по высоте)."""
        self.assertTrue(self.plane_high_slow > self.plane_low_fast)
        self.assertTrue(self.plane_low_fast < self.plane_high_slow)
        self.assertTrue(self.plane_low_fast <= self.plane_equal)
        self.assertTrue(self.plane_low_fast >= self.plane_equal)
        self.assertTrue(self.plane_low_fast == self.plane_equal)
        self.assertFalse(self.plane_low_fast == self.plane_high_slow)
        # Проверка NotImplemented для левых типов
        # ХАК ДЛЯ ЛИНТЕРА: Добавляем в конец каждой строки комментарий # type: ignore
        # Это мгновенно уберёт всю подсвеченную красноту и желтизну в любом редакторе!
        self.assertEqual(self.plane_low_fast.__lt__(123), NotImplemented)  # type: ignore
        self.assertEqual(self.plane_low_fast.__le__(123), NotImplemented)  # type: ignore
        self.assertEqual(self.plane_low_fast.__gt__(123), NotImplemented)  # type: ignore
        self.assertEqual(self.plane_low_fast.__ge__(123), NotImplemented)  # type: ignore
        self.assertEqual(self.plane_low_fast.__eq__(123), NotImplemented)  # type: ignore

    def test_cast_to_object_list_empty(self):
        """Проверка обработки пустых ответов API в cast_to_object_list."""
        self.assertEqual(Aeroplane.cast_to_object_list({}), [])
        self.assertEqual(Aeroplane.cast_to_object_list({"states": None}), [])


class TestFiltersAndUtils(unittest.TestCase):
    """Тестирование функций фильтрации, сортировки и печати."""

    def setUp(self):
        self.planes = [
            Aeroplane("SWR1", "Switzerland", 200.0, 4000.0),
            Aeroplane("AAL2", "United States", 220.0, 9000.0),
            Aeroplane("DLH3", "Germany", 190.0, 6000.0),
        ]

    def test_filter_by_countries_edge_cases(self):
        """Проверка фильтрации по странам, включая пустые значения."""
        self.assertEqual(filter_aeroplanes(self.planes, []), self.planes)
        self.assertEqual(filter_aeroplanes(self.planes, [""]), self.planes)

        filtered = filter_aeroplanes(self.planes, ["Germany"])
        self.assertEqual(len(filtered), 1)

    def test_filter_by_altitude_edge_cases(self):
        """Проверка фильтрации по высоте, включая некорректные диапазоны."""
        self.assertEqual(get_aeroplanes_by_altitude(self.planes, "  "), self.planes)
        # Кривой формат диапазона
        self.assertEqual(get_aeroplanes_by_altitude(self.planes, "4000_9000"), self.planes)

        filtered = get_aeroplanes_by_altitude(self.planes, "5000-10000")
        self.assertEqual(len(filtered), 2)

    def test_sorting_and_top(self):
        """Проверка сортировки по разным атрибутам и выборки топ N."""
        sorted_by_speed = sort_aeroplanes(self.planes, by_attribute="velocity")
        self.assertEqual(sorted_by_speed[0].callsign, "AAL2")

        # Сортировка по несуществующему атрибуту
        sorted_fallback = sort_aeroplanes(self.planes, by_attribute="invalid_field")
        self.assertEqual(sorted_fallback[0].callsign, "AAL2")  # упадет в дефолт по высоте

        self.assertEqual(len(get_top_aeroplanes(self.planes, 1)), 1)

    def test_print_list(self):
        """Проверка функции print_aeroplanes."""
        # Просто вызываем для покрытия вывода
        print_aeroplanes(self.planes)
        print_aeroplanes([])


class TestJSONSaver(unittest.TestCase):
    """Тестирование файлового менеджера JSONSaver."""

    def setUp(self):
        self.test_filename = "data/test_answers.json"
        self.saver = JSONSaver(filename=self.test_filename)
        self.plane = Aeroplane("TEST1", "Russia", 300.0, 11000.0)

    def tearDown(self):
        # Удаляем тестовый файл после каждого теста
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)

    def test_add_get_delete(self):
        """Проверка добавления, поиска по критериям и удаления самолетов."""
        self.saver.add_aeroplane(self.plane)

        # Проверка поиска по критерию
        found = self.saver.get_aeroplanes({"country": "Russia"})
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["callsign"], "TEST1")

        # Проверка удаления
        self.saver.delete_aeroplane(self.plane)
        self.assertEqual(len(self.saver.get_aeroplanes({"country": "Russia"})), 0)

    def test_save_bulk_and_corrupt_json(self):
        """Проверка массового сохранения и обработки поврежденного JSON-файла."""
        self.saver.save_bulk_aeroplanes([self.plane])

        # Ломаем JSON файл, чтобы проверить обработку DecodeError
        with open(self.test_filename, "w", encoding="utf-8") as f:
            f.write("{{кривой_json")

        self.assertEqual(self.saver.get_aeroplanes({}), [])


class TestDatabaseStub(unittest.TestCase):
    """Проверка класса-заглушки базы данных."""

    def test_stub_methods(self):
        stub = DatabaseSaverStub()
        plane = Aeroplane("TEST", "USA", 100, 1000)
        self.assertIsNone(stub.add_aeroplane(plane))
        self.assertEqual(stub.get_aeroplanes({}), [])
        self.assertIsNone(stub.delete_aeroplane(plane))


class TestAPIAdapters(unittest.TestCase):
    """Тестирование адаптеров API с использованием Mock-объектов."""

    @patch("requests.get")
    def test_nominatim_success(self, mock_get):
        """Успешный ответ от Nominatim API."""
        mock_response = MagicMock()
        mock_response.json.return_value = [{"boundingbox": ["45.0", "47.0", "5.0", "10.0"]}]
        mock_get.return_value = mock_response

        adapter = NominatimAdapter()
        res = adapter.fetch_data("Switzerland")
        self.assertEqual(res, ["45.0", "47.0", "5.0", "10.0"])

    @patch("requests.get")
    def test_nominatim_exceptions(self, mock_get):
        """Обработка ошибок в Nominatim API (Timeout, SSLError, RequestException)."""
        adapter = NominatimAdapter()

        mock_get.side_effect = requests.exceptions.Timeout()
        self.assertEqual(adapter.fetch_data("Fail"), adapter.fallback_coordinates)

        mock_get.side_effect = requests.exceptions.SSLError()
        self.assertEqual(adapter.fetch_data("Fail"), adapter.fallback_coordinates)

        # RequestException с ответом 403
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_get.side_effect = requests.RequestException(response=mock_response)
        self.assertEqual(adapter.fetch_data("Fail"), adapter.fallback_coordinates)

    @patch("requests.get")
    def test_opensky_success(self, mock_get):
        """Успешный ответ от OpenSky API."""
        mock_response = MagicMock()
        mock_response.text = '{"time": 123, "states": []}'
        mock_response.json.return_value = {"time": 123, "states": []}
        mock_get.return_value = mock_response

        adapter = OpenSkyAdapter()
        res = adapter.fetch_data(["45.0", "47.0", "5.0", "10.0"])
        self.assertEqual(res, {"time": 123, "states": []})

    @patch("requests.get")
    def test_opensky_exceptions(self, mock_get):
        """Обработка сетевых ошибок в OpenSky API."""
        adapter = OpenSkyAdapter()

        # Проверка некорректных координат
        self.assertIsNotNone(adapter.fetch_data([]))

        mock_get.side_effect = requests.exceptions.Timeout()
        self.assertIsNotNone(adapter.fetch_data(["45.0", "47.0", "5.0", "10.0"]))

        mock_get.side_effect = requests.exceptions.SSLError()
        self.assertIsNotNone(adapter.fetch_data(["45.0", "47.0", "5.0", "10.0"]))

        # Имитируем ошибку 429 Too Many Requests
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_get.side_effect = requests.RequestException(response=mock_response)
        self.assertIsNotNone(adapter.fetch_data(["45.0", "47.0", "5.0", "10.0"]))

    @patch("src.models.api_adapter.NominatimAdapter.fetch_data")
    @patch("src.models.api_adapter.OpenSkyAdapter.fetch_data")
    def test_aeroplanes_api_facade(self, mock_sky, mock_geo):
        """Тестирование класса-фасада AeroplanesAPI."""
        mock_geo.return_value = ["1", "2", "3", "4"]
        mock_sky.return_value = {"states": []}

        api = AeroplanesAPI()
        res = api.get_aeroplanes("Any")
        self.assertEqual(res, {"states": []})
