import unittest
from datetime import datetime
from src.api.vacancy import Vacancy, Salary


class TestSalary(unittest.TestCase):
    """Тесты для класса Salary."""

    def setUp(self):
        """Создание тестовых данных."""
        self.salary_data = {
            "from": 100000,
            "to": 150000,
            "currency": "RUR",
            "gross": False
        }
        self.salary = Salary(self.salary_data)

    def test_salary_creation(self):
        """Тест создания объекта Salary."""
        self.assertEqual(self.salary.min_value, 100000)
        self.assertEqual(self.salary.max_value, 150000)
        self.assertEqual(self.salary.currency, "RUR")
        self.assertEqual(self.salary.gross, False)

    def test_salary_str(self):
        """Тест строкового представления зарплаты."""
        expected = "100000-150000 RUR (на руки)"
        self.assertEqual(str(self.salary), expected)

    def test_salary_without_min(self):
        """Тест создания зарплаты без минимального значения."""
        data = self.salary_data.copy()
        data["from"] = None
        salary = Salary(data)
        self.assertIsNone(salary.min_value)
        self.assertEqual(str(salary), "до 150000 RUR (на руки)")

    def test_salary_without_max(self):
        """Тест создания зарплаты без максимального значения."""
        data = self.salary_data.copy()
        data["to"] = None
        salary = Salary(data)
        self.assertIsNone(salary.max_value)
        self.assertEqual(str(salary), "от 100000 RUR (на руки)")


class TestVacancy(unittest.TestCase):
    """Тесты для класса Vacancy."""

    def setUp(self):
        """Создание тестовых данных."""
        self.vacancy_data = {
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
        self.vacancy = Vacancy(self.vacancy_data)

    def test_vacancy_creation(self):
        """Тест создания объекта Vacancy."""
        self.assertEqual(self.vacancy.id, "12345")
        self.assertEqual(self.vacancy.title, "Python Developer")
        self.assertIsInstance(self.vacancy.salary, Salary)
        self.assertEqual(self.vacancy.company_name, "IT Company")
        self.assertEqual(self.vacancy.url, "https://hh.ru/vacancy/12345")
        self.assertEqual(self.vacancy.experience, "От 1 года до 3 лет")
        self.assertEqual(self.vacancy.employment, "Полная занятость")
        self.assertIsInstance(self.vacancy.created_at, datetime)

    def test_vacancy_str(self):
        """Тест строкового представления вакансии."""
        expected = "Python Developer (IT Company) - 100000-150000 RUR (на руки)"
        self.assertEqual(str(self.vacancy), expected)

    def test_vacancy_without_salary(self):
        """Тест создания вакансии без зарплаты."""
        data = self.vacancy_data.copy()
        data["salary"] = None
        vacancy = Vacancy(data)
        self.assertIsNone(vacancy.salary)
        self.assertEqual(str(vacancy), "Python Developer (IT Company) - З/п не указана")

    def test_vacancy_to_dict(self):
        """Тест преобразования вакансии в словарь."""
        vacancy_dict = self.vacancy.to_dict()
        self.assertEqual(vacancy_dict["id"], "12345")
        self.assertEqual(vacancy_dict["title"], "Python Developer")
        self.assertEqual(vacancy_dict["company_name"], "IT Company")
        self.assertEqual(vacancy_dict["url"], "https://hh.ru/vacancy/12345")
        self.assertEqual(vacancy_dict["requirements"], "Python, Django, REST")
        self.assertEqual(vacancy_dict["experience"], "От 1 года до 3 лет")
        self.assertEqual(vacancy_dict["employment"], "Полная занятость")


if __name__ == '__main__':
    unittest.main() 