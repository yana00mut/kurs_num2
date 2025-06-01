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
        self._session.headers = {
            "User-Agent": "JobSearchApp/1.0 (api@example.com)"
        }

    def connect(self) -> bool:
        """
        Проверка подключения к API
        
        Returns:
            bool: Успешность подключения
        """
        try:
            response = self._session.get(f"{self.config.base_url}/ping")
            self._is_connected = response.status_code == 200
            return self._is_connected
        except requests.RequestException:
            self._is_connected = False
            return False

    def get_vacancies(
        self,
        keywords: str,
        location: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Получение списка вакансий с HeadHunter
        
        Args:
            keywords: Ключевые слова для поиска
            location: Местоположение (город, регион)
            limit: Максимальное количество вакансий
            
        Returns:
            List[Dict]: Список вакансий
        """
        params = {
            "text": keywords,
            "area": self._get_area_id(location) if location else None,
            "per_page": min(limit, 100),
            "page": 0
        }

        try:
            response = self._session.get(
                f"{self.config.base_url}/vacancies",
                params={k: v for k, v in params.items() if v is not None}
            )
            response.raise_for_status()
            self._last_request_time = datetime.now()
            
            data = response.json()
            return [self._parse_vacancy(item) for item in data.get("items", [])]
        except requests.RequestException as e:
            print(f"Ошибка при получении вакансий: {e}")
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