from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class APIConfig:
    """Конфигурация для подключения к API"""
    base_url: str
    api_key: Optional[str] = None
    timeout: int = 30


class JobAPIBase(ABC):
    """
    Базовый абстрактный класс для работы с API сервисов поиска работы.
    Определяет общий интерфейс для всех классов-потомков.
    """

    def __init__(self, config: APIConfig):
        """
        Инициализация базового класса API.
        
        Args:
            config: Конфигурация для подключения к API
        """
        self.config = config
        self._last_request_time: Optional[datetime] = None
        self._is_connected: bool = False

    @abstractmethod
    def connect(self) -> bool:
        """
        Установка соединения с API сервиса.
        
        Returns:
            bool: Успешность подключения
        """
        pass

    @abstractmethod
    def get_vacancies(
        self,
        keywords: str,
        location: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Получение списка вакансий по заданным критериям.
        
        Args:
            keywords: Ключевые слова для поиска
            location: Местоположение (город, регион)
            limit: Максимальное количество вакансий
            
        Returns:
            List[Dict]: Список вакансий в виде словарей
        """
        pass

    @abstractmethod
    def get_vacancy_details(self, vacancy_id: str) -> Dict:
        """
        Получение детальной информации о конкретной вакансии.
        
        Args:
            vacancy_id: Идентификатор вакансии
            
        Returns:
            Dict: Детальная информация о вакансии
        """
        pass

    def is_connected(self) -> bool:
        """
        Проверка статуса подключения к API.
        
        Returns:
            bool: Статус подключения
        """
        return self._is_connected

    def get_last_request_time(self) -> Optional[datetime]:
        """
        Получение времени последнего запроса к API.
        
        Returns:
            Optional[datetime]: Время последнего запроса
        """
        return self._last_request_time 