import unittest
from abc import ABC
from src.api.abstract_api import JobAPIBase
from src.api.vacancy import Vacancy


class TestJobAPI(JobAPIBase):
    """Тестовая реализация абстрактного класса JobAPIBase."""
    
    def __init__(self):
        """Инициализация тестового API."""
        self.test_vacancies = []

    def get_vacancies(self, search_query: str, **kwargs) -> list[Vacancy]:
        """Тестовая реализация получения вакансий."""
        return self.test_vacancies


class TestJobAPIBase(unittest.TestCase):
    """Тесты для абстрактного класса JobAPIBase."""

    def test_is_abstract(self):
        """Тест, что класс является абстрактным."""
        self.assertTrue(issubclass(JobAPIBase, ABC))
        
        # Проверка, что нельзя создать экземпляр абстрактного класса
        with self.assertRaises(TypeError):
            JobAPIBase()

    def test_concrete_implementation(self):
        """Тест создания конкретной реализации."""
        # Проверка, что можно создать экземпляр класса с реализацией
        api = TestJobAPI()
        self.assertIsInstance(api, JobAPIBase)

    def test_get_vacancies_implementation(self):
        """Тест реализации метода get_vacancies."""
        api = TestJobAPI()
        
        # Проверка возвращаемого значения
        vacancies = api.get_vacancies("test")
        self.assertIsInstance(vacancies, list)
        self.assertEqual(len(vacancies), 0)

        # Проверка типа аннотации возвращаемого значения
        return_type = api.get_vacancies.__annotations__['return']
        self.assertEqual(return_type, list[Vacancy])

    def test_get_vacancies_with_kwargs(self):
        """Тест передачи дополнительных параметров в get_vacancies."""
        api = TestJobAPI()
        
        # Проверка, что метод принимает дополнительные параметры
        vacancies = api.get_vacancies(
            "test",
            area=1,
            experience="noExperience",
            employment="full"
        )
        self.assertIsInstance(vacancies, list)


if __name__ == '__main__':
    unittest.main() 