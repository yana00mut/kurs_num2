import requests
from typing import List, Dict, Optional
from datetime import datetime

from src.abstract_api import JobAPIBase, APIConfig
from src.vacancy import Vacancy, Salary


class HeadHunterAPI(JobAPIBase):
    """Класс для работы с API HeadHunter"""

    def __init__(self):
        """Инициализация клиента API HeadHunter"""
        super().__init__(APIConfig(
            base_url="https://api.hh.ru",
            timeout=10
        ))
        self._session = requests.Session()

    def connect(self) -> bool:
        """
        Проверка подключения к API
        
        Returns:
            bool: Успешность подключения
        """
        try:
            response = self._session.get(f"{self.config.base_url}/vacancies")
            self._is_connected = response.status_code == 200
            return self._is_connected
        except requests.RequestException:
            self._is_connected = False
            return False

    def get_vacancies(
        self,
        text: str,
        location: Optional[str] = None,
        salary_from: Optional[int] = None,
        salary_to: Optional[int] = None,
        experience: Optional[str] = None,
        area: Optional[int] = None,
        per_page: int = 100,
        page: int = 0
    ) -> List[Dict]:
        """
        Получение списка вакансий с HeadHunter
        
        Args:
            text: Текст поискового запроса
            location: Местоположение (город, регион)
            salary_from: Минимальная зарплата
            salary_to: Максимальная зарплата
            experience: Требуемый опыт работы
            area: ID региона
            per_page: Количество вакансий на страницу
            page: Номер страницы
            
        Returns:
            List[Dict]: Список вакансий в формате словарей
        """
        params = {
            "text": text.strip(),
            "area": area if area is not None else self._get_area_id(location) if location else None,
            "salary": salary_from if salary_from else None,
            "only_with_salary": "true" if salary_from or salary_to else None,
            "experience": experience,
            "per_page": min(per_page, 100),
            "page": page,
            "search_field": ["name", "description"]  # Поиск в названии и описании
        }

        try:
            response = self._session.get(
                f"{self.config.base_url}/vacancies",
                params={k: v for k, v in params.items() if v is not None},
                timeout=self.config.timeout
            )
            response.raise_for_status()
            self._last_request_time = datetime.now()
            
            data = response.json()
            vacancies = data.get("items", [])
            
            # Дополнительная фильтрация результатов
            filtered_vacancies = []
            text_lower = text.lower()
            
            for vacancy in vacancies:
                # Проверка на наличие текста в названии или описании
                name = (vacancy.get("name") or "").lower()
                description = (vacancy.get("description") or "").lower()
                snippet = vacancy.get("snippet") or {}
                requirement = (snippet.get("requirement") or "").lower()
                responsibility = (snippet.get("responsibility") or "").lower()
                
                if text_lower not in name and text_lower not in description and \
                   text_lower not in requirement and text_lower not in responsibility:
                    continue
                
                # Проверка зарплаты
                salary_data = vacancy.get("salary")
                if salary_from and salary_data:
                    if not salary_data.get("from") or salary_data["from"] < salary_from:
                        continue
                if salary_to and salary_data:
                    if not salary_data.get("to") or salary_data["to"] > salary_to:
                        continue
                
                # Проверка опыта
                if experience:
                    vacancy_experience = vacancy.get("experience", {}).get("id")
                    if vacancy_experience != experience:
                        continue
                
                filtered_vacancies.append(vacancy)
            
            return filtered_vacancies[:per_page]
        except requests.RequestException as e:
            print(f"Ошибка при получении вакансий: {e}")
            if hasattr(e.response, 'text'):
                print(f"Ответ сервера: {e.response.text}")
            return []

    def get_vacancy_details(self, vacancy_id: str) -> Dict:
        """
        Получение детальной информации о вакансии
        
        Args:
            vacancy_id: Идентификатор вакансии
            
        Returns:
            Dict: Детальная информация о вакансии
        """
        try:
            response = self._session.get(f"{self.config.base_url}/vacancies/{vacancy_id}")
            response.raise_for_status()
            self._last_request_time = datetime.now()
            return response.json()
        except requests.RequestException as e:
            print(f"Ошибка при получении информации о вакансии: {e}")
            return {}

    def _get_area_id(self, location: str) -> Optional[int]:
        """Получение ID региона по названию"""
        try:
            response = self._session.get(
                f"{self.config.base_url}/areas",
                params={"text": location}
            )
            response.raise_for_status()
            areas = response.json()
            
            # Поиск по всем регионам и городам
            for area in areas:
                if location.lower() in area["name"].lower():
                    return area["id"]
                for city in area.get("areas", []):
                    if location.lower() in city["name"].lower():
                        return city["id"]
            return None
        except requests.RequestException:
            return None

    def _parse_vacancy(self, vacancy_data: Dict) -> Vacancy:
        """Преобразование данных API в объект Vacancy"""
        salary_data = vacancy_data.get("salary", {})
        if salary_data:
            salary = Salary(
                min_value=salary_data.get("from"),
                max_value=salary_data.get("to"),
                currency=salary_data.get("currency", "RUR"),
                gross=salary_data.get("gross", False)
            )
        else:
            salary = Salary()

        return Vacancy(
            vacancy_id=vacancy_data["id"],
            title=vacancy_data["name"],
            salary=salary,
            description=vacancy_data.get("description", ""),
            company_name=vacancy_data.get("employer", {}).get("name", ""),
            url=vacancy_data.get("alternate_url", ""),
            requirements=vacancy_data.get("snippet", {}).get("requirement", ""),
            experience=vacancy_data.get("experience", {}).get("name", ""),
            employment=vacancy_data.get("employment", {}).get("name", ""),
            created_at=datetime.fromisoformat(
                vacancy_data["created_at"].replace("Z", "+00:00")
            )
        ) 