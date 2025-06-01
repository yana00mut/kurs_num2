from abc import ABC, abstractmethod
from typing import List, Optional
import json
from pathlib import Path

from src.vacancy import Vacancy


class VacancyStorage(ABC):
    """Абстрактный класс для работы с хранилищем вакансий"""

    @abstractmethod
    def add_vacancy(self, vacancy: Vacancy) -> None:
        """Добавление вакансии в хранилище"""
        pass

    @abstractmethod
    def get_vacancies(self, keyword: Optional[str] = None) -> List[Vacancy]:
        """Получение списка вакансий по ключевому слову"""
        pass

    @abstractmethod
    def remove_vacancy(self, vacancy_id: str) -> None:
        """Удаление вакансии из хранилища"""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Очистка хранилища"""
        pass


class JSONVacancyStorage(VacancyStorage):
    """Реализация хранилища вакансий в JSON файле"""

    def __init__(self, file_path: str):
        """
        Инициализация хранилища
        
        Args:
            file_path: Путь к JSON файлу
        """
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self.file_path.write_text('[]')

    def add_vacancy(self, vacancy: Vacancy) -> None:
        """
        Добавление вакансии в JSON файл
        
        Args:
            vacancy: Объект вакансии
        """
        vacancies = self._read_file()
        vacancy_dict = {
            'id': vacancy.id,
            'title': vacancy.title,
            'salary': {
                'min_value': vacancy.salary.min_value,
                'max_value': vacancy.salary.max_value,
                'currency': vacancy.salary.currency,
                'gross': vacancy.salary.gross
            },
            'description': vacancy.description,
            'company_name': vacancy.company_name,
            'url': vacancy.url,
            'requirements': vacancy.requirements,
            'experience': vacancy.experience,
            'employment': vacancy.employment,
            'created_at': vacancy.created_at.isoformat()
        }
        
        # Проверяем, нет ли уже такой вакансии
        if not any(v['id'] == vacancy.id for v in vacancies):
            vacancies.append(vacancy_dict)
            self._write_file(vacancies)

    def get_vacancies(self, keyword: Optional[str] = None) -> List[Vacancy]:
        """
        Получение списка вакансий по ключевому слову
        
        Args:
            keyword: Ключевое слово для поиска
            
        Returns:
            List[Vacancy]: Список вакансий
        """
        vacancies = self._read_file()
        result = []

        for vacancy_dict in vacancies:
            if keyword is None or keyword.lower() in vacancy_dict['description'].lower():
                result.append(self._dict_to_vacancy(vacancy_dict))

        return result

    def remove_vacancy(self, vacancy_id: str) -> None:
        """
        Удаление вакансии из JSON файла
        
        Args:
            vacancy_id: Идентификатор вакансии
        """
        vacancies = self._read_file()
        vacancies = [v for v in vacancies if v['id'] != vacancy_id]
        self._write_file(vacancies)

    def clear(self) -> None:
        """Очистка JSON файла"""
        self._write_file([])

    def _read_file(self) -> List[dict]:
        """Чтение данных из JSON файла"""
        with self.file_path.open('r', encoding='utf-8') as f:
            return json.load(f)

    def _write_file(self, data: List[dict]) -> None:
        """Запись данных в JSON файл"""
        with self.file_path.open('w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _dict_to_vacancy(self, vacancy_dict: dict) -> Vacancy:
        """Преобразование словаря в объект Vacancy"""
        from datetime import datetime
        return Vacancy(
            vacancy_id=vacancy_dict['id'],
            title=vacancy_dict['title'],
            salary=vacancy_dict['salary'],
            description=vacancy_dict['description'],
            company_name=vacancy_dict['company_name'],
            url=vacancy_dict['url'],
            requirements=vacancy_dict['requirements'],
            experience=vacancy_dict['experience'],
            employment=vacancy_dict['employment'],
            created_at=datetime.fromisoformat(vacancy_dict['created_at'])
        ) 