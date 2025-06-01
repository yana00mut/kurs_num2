from dataclasses import dataclass
from typing import Optional, Union, List, Dict
from datetime import datetime


@dataclass
class Salary:
    """Класс для представления зарплаты"""
    min_value: Optional[int] = None
    max_value: Optional[int] = None
    currency: str = "RUR"
    gross: bool = False

    def __post_init__(self):
        """Валидация данных после инициализации"""
        if self.min_value is None and self.max_value is None:
            self.min_value = 0
            self.max_value = 0
            self.currency = "RUR"

    def __lt__(self, other: 'Salary') -> bool:
        """Сравнение зарплат по минимальному значению"""
        return self.min_value < other.min_value if self.min_value and other.min_value else False

    def __str__(self) -> str:
        """Строковое представление зарплаты"""
        if self.min_value == 0 and self.max_value == 0:
            return "Зарплата не указана"
        if self.min_value and self.max_value:
            return f"от {self.min_value} до {self.max_value} {self.currency}"
        if self.min_value:
            return f"от {self.min_value} {self.currency}"
        return f"до {self.max_value} {self.currency}"

    def in_range(self, min_salary: int, max_salary: int) -> bool:
        """Проверка, попадает ли зарплата в указанный диапазон"""
        if self.min_value == 0 and self.max_value == 0:
            return False
        if self.min_value and self.max_value:
            return min_salary <= self.min_value <= max_salary or min_salary <= self.max_value <= max_salary
        if self.min_value:
            return min_salary <= self.min_value <= max_salary
        return min_salary <= self.max_value <= max_salary


class Vacancy:
    """Класс для работы с вакансиями"""

    def __init__(
        self,
        vacancy_id: str,
        title: str,
        salary: Optional[Union[dict, Salary]] = None,
        description: str = "",
        company_name: str = "",
        url: str = "",
        requirements: str = "",
        experience: str = "",
        employment: str = "",
        created_at: Optional[datetime] = None
    ):
        """
        Инициализация вакансии
        
        Args:
            vacancy_id: Идентификатор вакансии
            title: Название вакансии
            salary: Зарплата (словарь или объект Salary)
            description: Описание вакансии
            company_name: Название компании
            url: Ссылка на вакансию
            requirements: Требования
            experience: Требуемый опыт
            employment: Тип занятости
            created_at: Дата создания вакансии
        """
        self._id = vacancy_id
        self._title = title
        self._salary = self._validate_salary(salary)
        self._description = description
        self._company_name = company_name
        self._url = url
        self._requirements = requirements
        self._experience = experience
        self._employment = employment
        self._created_at = created_at or datetime.now()

    def _validate_salary(self, salary: Optional[Union[dict, Salary]]) -> Salary:
        """Валидация данных о зарплате"""
        if isinstance(salary, Salary):
            return salary
        if isinstance(salary, dict):
            return Salary(
                min_value=salary.get('from'),
                max_value=salary.get('to'),
                currency=salary.get('currency', 'RUR'),
                gross=salary.get('gross', False)
            )
        return Salary()

    @staticmethod
    def cast_to_object_list(vacancies_data: List[Dict]) -> List['Vacancy']:
        """
        Преобразование списка словарей в список объектов Vacancy
        
        Args:
            vacancies_data: Список вакансий в формате словарей
            
        Returns:
            List[Vacancy]: Список объектов Vacancy
        """
        return [
            Vacancy(
                vacancy_id=data.get('id', ''),
                title=data.get('name', ''),
                salary=data.get('salary'),
                description=data.get('description', ''),
                company_name=data.get('employer', {}).get('name', ''),
                url=data.get('alternate_url', ''),
                requirements=data.get('snippet', {}).get('requirement', ''),
                experience=data.get('experience', {}).get('name', ''),
                employment=data.get('employment', {}).get('name', ''),
                created_at=datetime.fromisoformat(
                    data.get('created_at', datetime.now().isoformat()).replace("Z", "+00:00")
                )
            )
            for data in vacancies_data
        ]

    def contains_keywords(self, keywords: List[str]) -> bool:
        """
        Проверка наличия ключевых слов в описании вакансии
        
        Args:
            keywords: Список ключевых слов
            
        Returns:
            bool: True если все ключевые слова найдены
        """
        description_lower = self.description.lower()
        requirements_lower = self.requirements.lower()
        title_lower = self.title.lower()
        
        return all(
            keyword.lower() in description_lower or
            keyword.lower() in requirements_lower or
            keyword.lower() in title_lower
            for keyword in keywords
        )

    def salary_in_range(self, salary_range: str) -> bool:
        """
        Проверка, попадает ли зарплата в указанный диапазон
        
        Args:
            salary_range: Строка с диапазоном зарплат (например, "100000-150000")
            
        Returns:
            bool: True если зарплата попадает в диапазон
        """
        try:
            min_salary, max_salary = map(int, salary_range.replace(" ", "").split("-"))
            return self.salary.in_range(min_salary, max_salary)
        except (ValueError, AttributeError):
            return False

    @property
    def id(self) -> str:
        return self._id

    @property
    def title(self) -> str:
        return self._title

    @property
    def salary(self) -> Salary:
        return self._salary

    @property
    def description(self) -> str:
        return self._description

    @property
    def company_name(self) -> str:
        return self._company_name

    @property
    def url(self) -> str:
        return self._url

    @property
    def requirements(self) -> str:
        return self._requirements

    @property
    def experience(self) -> str:
        return self._experience

    @property
    def employment(self) -> str:
        return self._employment

    @property
    def created_at(self) -> datetime:
        return self._created_at

    def __lt__(self, other: 'Vacancy') -> bool:
        """Сравнение вакансий по зарплате"""
        return self.salary < other.salary

    def __str__(self) -> str:
        """Строковое представление вакансии"""
        return (
            f"Вакансия: {self.title}\n"
            f"Компания: {self.company_name}\n"
            f"Зарплата: {self.salary}\n"
            f"Опыт: {self.experience}\n"
            f"Тип занятости: {self.employment}\n"
            f"URL: {self.url}"
        ) 