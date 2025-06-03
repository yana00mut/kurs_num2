from abc import ABC, abstractmethod
from typing import List, Optional
import json
from pathlib import Path

from src.vacancy import Vacancy, Salary


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
        if not self.file_path.suffix:
            self.file_path = self.file_path / "vacancies.json"
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self._write_file([])

    def add_vacancy(self, vacancy: Vacancy) -> None:
        """
        Добавление вакансии в JSON файл
        
        Args:
            vacancy: Объект вакансии
        """
        vacancies = self._read_file()
        
        # Преобразуем вакансию в словарь
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
            'created_at': vacancy.created_at.isoformat() if vacancy.created_at else None
        }
        
        # Обновляем существующую вакансию или добавляем новую
        for i, v in enumerate(vacancies):
            if v['id'] == vacancy.id:
                vacancies[i] = vacancy_dict
                break
        else:
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
            if keyword is None or (
                keyword.lower() in vacancy_dict['title'].lower() or
                keyword.lower() in vacancy_dict['description'].lower()
            ):
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
        try:
            if not self.file_path.exists():
                return []
            with self.file_path.open('r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"Ошибка при чтении файла: {e}")
            return []

    def _write_file(self, data: List[dict]) -> None:
        """Запись данных в JSON файл"""
        try:
            with self.file_path.open('w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except OSError as e:
            print(f"Ошибка при записи в файл: {e}")

    def _dict_to_vacancy(self, vacancy_dict: dict) -> Vacancy:
        """Преобразование словаря в объект Vacancy"""
        from datetime import datetime
        
        # Создаем объект Salary
        salary_data = vacancy_dict.get('salary', {})
        salary = Salary(
            min_value=salary_data.get('min_value'),
            max_value=salary_data.get('max_value'),
            currency=salary_data.get('currency', 'RUR'),
            gross=salary_data.get('gross', False)
        )
        
        # Создаем объект Vacancy
        return Vacancy(
            vacancy_id=vacancy_dict['id'],
            title=vacancy_dict['title'],
            salary=salary,
            description=vacancy_dict.get('description', ''),
            company_name=vacancy_dict.get('company_name', ''),
            url=vacancy_dict.get('url', ''),
            requirements=vacancy_dict.get('requirements', ''),
            experience=vacancy_dict.get('experience', ''),
            employment=vacancy_dict.get('employment', ''),
            created_at=datetime.fromisoformat(vacancy_dict['created_at']) if vacancy_dict.get('created_at') else None
        ) 