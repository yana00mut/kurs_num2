import unittest
import json
import os
import tempfile
from src.api.storage import JSONVacancyStorage
from src.api.vacancy import Vacancy


class TestJSONVacancyStorage(unittest.TestCase):
    """Тесты для класса JSONVacancyStorage."""

    def setUp(self):
        """Создание временного файла для тестов."""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, "test_vacancies.json")
        self.storage = JSONVacancyStorage(self.test_file)
        
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
        self.vacancy = Vacancy(self.test_vacancy_data)

    def tearDown(self):
        """Удаление временных файлов после тестов."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        os.rmdir(self.test_dir)

    def test_save_and_load_vacancies(self):
        """Тест сохранения и загрузки вакансий."""
        # Сохранение вакансии
        self.storage.save_vacancies([self.vacancy])
        
        # Проверка существования файла
        self.assertTrue(os.path.exists(self.test_file))
        
        # Загрузка и проверка данных
        loaded_vacancies = self.storage.load_vacancies()
        self.assertEqual(len(loaded_vacancies), 1)
        
        loaded_vacancy = loaded_vacancies[0]
        self.assertEqual(loaded_vacancy.id, self.vacancy.id)
        self.assertEqual(loaded_vacancy.title, self.vacancy.title)
        self.assertEqual(loaded_vacancy.company_name, self.vacancy.company_name)

    def test_save_empty_list(self):
        """Тест сохранения пустого списка вакансий."""
        self.storage.save_vacancies([])
        self.assertTrue(os.path.exists(self.test_file))
        
        with open(self.test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.assertEqual(data, [])

    def test_load_non_existent_file(self):
        """Тест загрузки из несуществующего файла."""
        non_existent_file = os.path.join(self.test_dir, "non_existent.json")
        storage = JSONVacancyStorage(non_existent_file)
        vacancies = storage.load_vacancies()
        self.assertEqual(vacancies, [])

    def test_add_vacancies(self):
        """Тест добавления вакансий."""
        # Сохранение первой вакансии
        self.storage.save_vacancies([self.vacancy])
        
        # Создание второй вакансии
        second_vacancy_data = self.test_vacancy_data.copy()
        second_vacancy_data["id"] = "67890"
        second_vacancy_data["name"] = "Senior Python Developer"
        second_vacancy = Vacancy(second_vacancy_data)
        
        # Добавление второй вакансии
        self.storage.add_vacancies([second_vacancy])
        
        # Проверка загрузки обеих вакансий
        loaded_vacancies = self.storage.load_vacancies()
        self.assertEqual(len(loaded_vacancies), 2)
        
        # Проверка, что вакансии разные
        vacancy_ids = {v.id for v in loaded_vacancies}
        self.assertEqual(vacancy_ids, {"12345", "67890"})

    def test_add_duplicate_vacancy(self):
        """Тест добавления дубликата вакансии."""
        # Сохранение вакансии
        self.storage.save_vacancies([self.vacancy])
        
        # Попытка добавить ту же вакансию
        self.storage.add_vacancies([self.vacancy])
        
        # Проверка, что дубликат не добавился
        loaded_vacancies = self.storage.load_vacancies()
        self.assertEqual(len(loaded_vacancies), 1)
        self.assertEqual(loaded_vacancies[0].id, self.vacancy.id)


if __name__ == '__main__':
    unittest.main() 