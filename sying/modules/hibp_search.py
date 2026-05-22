"""
Модуль поиска по Email через HaveIBeenPwned API
Пример модуля с использованием API ключа
"""

from typing import Dict, List, Optional, Any
from sying.core.base_module import BaseModule, SearchResult


class HaveIBeenPwnedSearch(BaseModule):
    """
    Модуль проверки утечек данных через HaveIBeenPwned API
    
    Поддерживает поиск по:
    - email
    
    API документация: https://haveibeenpwned.com/API/v3
    Требуется API ключ: https://haveibeenpwned.com/API/Key
    """
    
    # ===== НАСТРОЙКИ МОДУЛЯ =====
    name = "hibp_search"
    description = "Проверка email в базе утечек HaveIBeenPwned"
    version = "1.0.0"
    supported_queries = ['email']
    required_api_keys = ['API_KEY']  # Требуется API ключ
    
    # ===== КОНФИГУРАЦИЯ API =====
    # Получите API ключ: https://haveibeenpwned.com/API/Key
    API_KEY = ""  # <-- ВСТАВЬТЕ HIBP API KEY
    BASE_URL = "https://haveibeenpwned.com/api/v3"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.headers = {
            'hibp-api-key': self.API_KEY,
            'User-Agent': 'Sying-OSINT-Framework'
        }
    
    def _search(self, query: str, query_type: str) -> List[SearchResult]:
        """
        Проверка email в базе утечек
        
        Args:
            query: Email адрес для проверки
            query_type: Тип запроса (должен быть 'email')
        
        Returns:
            Список результатов поиска
        """
        results = []
        
        if query_type != 'email':
            return results
        
        # Запрос к API
        url = f"{self.BASE_URL}/breachedaccount/{query}"
        params = {'truncateResponse': 'false'}
        
        response = self._make_request(url, params=params, headers=self.headers)
        
        if response is None:
            # API вернул ошибку или email не найден
            # Создаем результат с информацией об отсутствии утечек
            data = {
                'full_name': '',
                'age': None,
                'country': '',
                'address': '',
                'email': query,
                'phone': '',
                'usernames': [],
                'social_profiles': [],
                'additional_info': {
                    'breaches_found': False,
                    'breach_count': 0,
                    'breaches': [],
                    'status': 'not_found_or_error'
                }
            }
            
            result = SearchResult(
                source=self.name,
                data=data,
                confidence=0.0,
                raw_data={'error': 'No breaches found or API error'}
            )
            results.append(result)
        
        elif isinstance(response, list):
            # Найдены утечки
            breaches = []
            usernames = set()
            
            for breach in response:
                breach_info = {
                    'name': breach.get('Name', ''),
                    'title': breach.get('Title', ''),
                    'domain': breach.get('Domain', ''),
                    'date': breach.get('BreachDate', ''),
                    'description': breach.get('Description', ''),
                    'data_classes': breach.get('DataClasses', [])
                }
                breaches.append(breach_info)
                
                # Попытка извлечь usernames из данных утечки
                if 'Username' in breach.get('DataClasses', []):
                    # В реальной ситуации здесь был бы парсинг конкретных данных
                    pass
            
            # Формирование результата
            data = {
                'full_name': '',
                'age': None,
                'country': '',
                'address': '',
                'email': query,
                'phone': '',
                'usernames': list(usernames),
                'social_profiles': [],
                'additional_info': {
                    'breaches_found': True,
                    'breach_count': len(breaches),
                    'breaches': breaches,
                    'status': 'found'
                }
            }
            
            # Расчет достоверности на основе количества утечек
            confidence = min(0.5 + (len(breaches) * 0.1), 1.0)
            
            result = SearchResult(
                source=self.name,
                data=data,
                confidence=confidence,
                raw_data=response
            )
            results.append(result)
        
        return results
    
    def _check_api_keys(self) -> bool:
        """Переопределенная проверка API ключа"""
        if not self.API_KEY or self.API_KEY == "":
            return False
        # Проверка формата ключа (опционально)
        if len(self.API_KEY) < 32:
            print(f"[!] Модуль {self.name}: API ключ слишком короткий")
            return False
        return True
