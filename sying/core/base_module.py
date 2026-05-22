"""
BaseModule - Базовый класс для всех OSINT модулей
Все модули должны наследоваться от этого класса
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SearchResult:
    """Структура результата поиска"""
    source: str  # Название источника (модуля)
    data: Dict[str, Any]  # Найденные данные
    confidence: float = 0.0  # Уровень достоверности (0.0 - 1.0)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    raw_data: Optional[Any] = None  # Сырые данные для дальнейшей обработки


class BaseModule(ABC):
    """
    Базовый класс для всех OSINT модулей
    
    Каждый модуль должен реализовать:
    - name: название модуля
    - description: описание модуля
    - supported_queries: типы поддерживаемых запросов
    - _search(): метод поиска
    """
    
    # ===== НАСТРОЙКИ МОДУЛЯ =====
    # Переопределите эти параметры в дочерних классах
    
    name: str = "base_module"
    description: str = "Базовый модуль OSINT"
    version: str = "1.0.0"
    
    # Типы запросов, которые поддерживает модуль
    # Возможные значения: 'name', 'phone', 'email', 'username', 'ip'
    supported_queries: List[str] = []
    
    # Требуемые API ключи (если нужны)
    required_api_keys: List[str] = []
    
    # Лимиты и настройки
    rate_limit: int = 60  # Запросов в минуту
    timeout: int = 30  # Таймаут запроса в секундах
    
    # ===== КОНФИГУРАЦИЯ API =====
    # Вставьте свои API ключи здесь или через переменные окружения
    API_KEY: str = ""  # <-- ВСТАВЬТЕ API КЛЮЧ
    API_SECRET: str = ""  # <-- ВСТАВЬТЕ API СЕКРЕТ
    BASE_URL: str = ""  # <-- ВСТАВЬТЕ БАЗОВЫЙ URL API
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Инициализация модуля
        
        Args:
            config: Словарь с конфигурацией (API ключи, настройки и т.д.)
        """
        self.config = config or {}
        self._apply_config()
    
    def _apply_config(self):
        """Применение конфигурации из словаря"""
        if 'api_key' in self.config:
            self.API_KEY = self.config['api_key']
        if 'api_secret' in self.config:
            self.API_SECRET = self.config['api_secret']
        if 'base_url' in self.config:
            self.BASE_URL = self.config['base_url']
        if 'timeout' in self.config:
            self.timeout = self.config['timeout']
    
    @abstractmethod
    def _search(self, query: str, query_type: str) -> List[SearchResult]:
        """
        Основной метод поиска (должен быть реализован в дочернем классе)
        
        Args:
            query: Строка запроса (имя, телефон, email и т.д.)
            query_type: Тип запроса ('name', 'phone', 'email', 'username', 'ip')
        
        Returns:
            Список результатов поиска
        """
        pass
    
    def search(self, query: str, query_type: str) -> List[SearchResult]:
        """
        Публичный метод поиска с проверками
        
        Args:
            query: Строка запроса
            query_type: Тип запроса
        
        Returns:
            Список результатов поиска
        """
        # Проверка поддержки типа запроса
        if query_type not in self.supported_queries:
            return []
        
        # Проверка наличия API ключей (если требуются)
        if not self._check_api_keys():
            print(f"[!] Модуль {self.name}: отсутствуют необходимые API ключи")
            return []
        
        # Выполнение поиска
        try:
            results = self._search(query, query_type)
            return results
        except Exception as e:
            print(f"[!] Модуль {self.name}: ошибка при поиске - {str(e)}")
            return []
    
    def _check_api_keys(self) -> bool:
        """Проверка наличия всех требуемых API ключей"""
        for key in self.required_api_keys:
            if not getattr(self, key, ""):
                return False
        return True
    
    def get_info(self) -> Dict[str, Any]:
        """Получение информации о модуле"""
        return {
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'supported_queries': self.supported_queries,
            'has_api_keys': self._check_api_keys()
        }
    
    def _make_request(self, url: str, params: Optional[Dict] = None, 
                     headers: Optional[Dict] = None) -> Optional[Dict]:
        """
        Вспомогательный метод для HTTP запросов
        
        Args:
            url: URL запроса
            params: Параметры запроса
            headers: Заголовки запроса
        
        Returns:
            Ответ сервера в виде словаря или None при ошибке
        """
        import requests
        
        try:
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[!] HTTP ошибка в модуле {self.name}: {str(e)}")
            return None
    
    def _normalize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Нормализация данных к единому формату
        
        Переопределите этот метод для специфичной обработки данных
        """
        normalized = {
            'full_name': data.get('full_name', ''),
            'age': data.get('age'),
            'country': data.get('country', ''),
            'address': data.get('address', ''),
            'email': data.get('email', ''),
            'phone': data.get('phone', ''),
            'usernames': data.get('usernames', []),
            'social_profiles': data.get('social_profiles', []),
            'additional_info': data.get('additional_info', {})
        }
        return normalized
