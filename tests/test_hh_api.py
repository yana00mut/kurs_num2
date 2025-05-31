import unittest
from unittest.mock import patch, MagicMock
from src.api.hh_api import HeadHunterAPI
from src.api.vacancy import Vacancy


class TestHeadHunterAPI(unittest.TestCase):
    """Тесты для класса HeadHunterAPI."""

    def setUp(self):
        """Подготовка тестовых данных."""
        self.api = HeadHunterAPI()
        self.test_vacancy_data = {
            "id": "12345",
            "name": "Python Developer",
            "salary": {
                "from": 100000,
                "to": 150000,
                "currency": "RUR",
                "gross": False
            },
            "snippet": {
                "requirement": "Python, Django, REST",
                "responsibility": "Разработка веб-приложений"
            },
            "employer": {
                "name": "IT Company"
            },
            "alternate_url": "https://hh.ru/vacancy/12345",
            "experience": {
                "name": "От 1 года до 3 лет"
            },
            "employment": {
                "name": "Полная занятость"
            },
            "published_at": "2024-02-20T10:00:00+0300"
        }

    @patch('requests.get')
    def test_get_vacancies(self, mock_get):
        """Тест получения вакансий."""
        # Подготовка мок-ответа
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [self.test_vacancy_data],
            "found": 1,
            "pages": 1,
            "per_page": 20,
            "page": 0
        }
        mock_get.return_value = mock_response

        # Вызов метода и проверка результатов
        vacancies = self.api.get_vacancies("Python Developer")
        
        self.assertEqual(len(vacancies), 1)
        self.assertIsInstance(vacancies[0], Vacancy)
        self.assertEqual(vacancies[0].id, "12345")
        self.assertEqual(vacancies[0].title, "Python Developer")

        # Проверка вызова API с правильными параметрами
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertEqual(kwargs['params']['text'], "Python Developer")
        self.assertEqual(kwargs['params']['per_page'], 100)

    @patch('requests.get')
    def test_get_vacancies_empty_response(self, mock_get):
        """Тест получения пустого списка вакансий."""
        # Подготовка мок-ответа без вакансий
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [],
            "found": 0,
            "pages": 0,
            "per_page": 20,
            "page": 0
        }
        mock_get.return_value = mock_response

        # Вызов метода и проверка результатов
        vacancies = self.api.get_vacancies("Несуществующая вакансия")
        self.assertEqual(len(vacancies), 0)

    @patch('requests.get')
    def test_get_vacancies_with_error(self, mock_get):
        """Тест обработки ошибки при получении вакансий."""
        # Имитация ошибки сети
        mock_get.side_effect = Exception("Network error")

        # Проверка, что метод возвращает пустой список при ошибке
        vacancies = self.api.get_vacancies("Python Developer")
        self.assertEqual(len(vacancies), 0)

    @patch('requests.get')
    def test_get_vacancies_invalid_response(self, mock_get):
        """Тест обработки некорректного ответа API."""
        # Подготовка некорректного ответа
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"invalid": "response"}
        mock_get.return_value = mock_response

        # Проверка обработки некорректного ответа
        vacancies = self.api.get_vacancies("Python Developer")
        self.assertEqual(len(vacancies), 0)

    @patch('requests.get')
    def test_get_vacancies_with_filters(self, mock_get):
        """Тест получения вакансий с дополнительными фильтрами."""
        # Подготовка мок-ответа
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [self.test_vacancy_data],
            "found": 1,
            "pages": 1,
            "per_page": 20,
            "page": 0
        }
        mock_get.return_value = mock_response

        # Вызов метода с дополнительными параметрами
        vacancies = self.api.get_vacancies(
            "Python Developer",
            area=1,  # Москва
            experience="noExperience",
            employment="full"
        )

        # Проверка параметров запроса
        args, kwargs = mock_get.call_args
        self.assertEqual(kwargs['params']['area'], 1)
        self.assertEqual(kwargs['params']['experience'], "noExperience")
        self.assertEqual(kwargs['params']['employment'], "full")


if __name__ == '__main__':
    unittest.main() 