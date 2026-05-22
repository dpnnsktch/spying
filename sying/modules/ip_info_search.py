"""
Модуль поиска по IP адресу
Пример модуля для работы с IP адресами
"""

from typing import Dict, List, Optional, Any
from sying.core.base_module import BaseModule, SearchResult


class IPInfoSearch(BaseModule):
    """
    Модуль получения информации об IP адресе
    
    Поддерживает поиск по:
    - ip
    
    API документация: https://ipinfo.io/developers
    Требуется API ключ для расширенных лимитов (опционально)
    """
    
    # ===== НАСТРОЙКИ МОДУЛЯ =====
    name = "ip_info_search"
    description = "Получение информации об IP адресе"
    version = "1.0.0"
    supported_queries = ['ip']
    required_api_keys = []  # Работает без ключа с базовыми лимитами
    
    # ===== КОНФИГУРАЦИЯ API =====
    # Получите API ключ для увеличения лимитов: https://ipinfo.io/
    API_KEY = ""  # <-- ВСТАВЬТЕ IPINFO API KEY (опционально)
    BASE_URL = "https://ipinfo.io"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
    
    def _search(self, query: str, query_type: str) -> List[SearchResult]:
        """
        Получение информации об IP адресе
        
        Args:
            query: IP адрес для проверки
            query_type: Тип запроса (должен быть 'ip')
        
        Returns:
            Список результатов поиска
        """
        results = []
        
        if query_type != 'ip':
            return results
        
        # Формирование URL
        if self.API_KEY:
            url = f"{self.BASE_URL}/{query}/json?token={self.API_KEY}"
        else:
            url = f"{self.BASE_URL}/{query}/json"
        
        response = self._make_request(url)
        
        if response:
            result = self._parse_ip_data(response, query)
            results.append(result)
        else:
            # Создание пустого результата при ошибке
            data = {
                'full_name': '',
                'age': None,
                'country': '',
                'address': '',
                'email': '',
                'phone': '',
                'usernames': [],
                'social_profiles': [],
                'additional_info': {
                    'ip': query,
                    'status': 'error'
                }
            }
            
            result = SearchResult(
                source=self.name,
                data=data,
                confidence=0.0,
                raw_data={'error': 'Failed to get IP info'}
            )
            results.append(result)
        
        return results
    
    def _parse_ip_data(self, ip_data: Dict, query: str) -> SearchResult:
        """
        Парсинг данных об IP адресе
        
        Args:
            ip_data: Сырые данные от API
            query: Запрошенный IP адрес
        
        Returns:
            SearchResult с нормализованными данными
        """
        # Извлечение данных
        ip = ip_data.get('ip', query)
        city = ip_data.get('city', '')
        region = ip_data.get('region', '')
        country = ip_data.get('country', '')
        postal = ip_data.get('postal', '')
        latitude = ip_data.get('loc', '').split(',')[0] if ip_data.get('loc') else ''
        longitude = ip_data.get('loc', '').split(',')[1] if ip_data.get('loc') else ''
        org = ip_data.get('org', '')
        isp = ip_data.get('isp', '')
        timezone = ip_data.get('timezone', '')
        asn = ip_data.get('asn', '')
        
        # Формирование адреса
        address_parts = []
        if city:
            address_parts.append(city)
        if region:
            address_parts.append(region)
        if postal:
            address_parts.append(postal)
        address = ', '.join(address_parts) if address_parts else ''
        
        # Расшифровка названия страны
        country_names = {
            'US': 'United States',
            'RU': 'Russia',
            'DE': 'Germany',
            'GB': 'United Kingdom',
            'FR': 'France',
            'CN': 'China',
            'JP': 'Japan',
            'BR': 'Brazil',
            'IN': 'India',
            'CA': 'Canada',
            'AU': 'Australia',
            'UA': 'Ukraine',
            'BY': 'Belarus',
            'KZ': 'Kazakhstan'
        }
        country_full = country_names.get(country, country)
        
        # Формирование результата
        data = {
            'full_name': '',
            'age': None,
            'country': country_full,
            'address': address,
            'email': '',
            'phone': '',
            'usernames': [],
            'social_profiles': [],
            'additional_info': {
                'ip': ip,
                'city': city,
                'region': region,
                'postal': postal,
                'coordinates': {
                    'latitude': latitude,
                    'longitude': longitude
                },
                'org': org,
                'isp': isp,
                'timezone': timezone,
                'asn': asn,
                'hostname': ip_data.get('hostname', ''),
                'company': ip_data.get('company', {}).get('name', '') if ip_data.get('company') else ''
            }
        }
        
        # Расчет достоверности
        confidence = 0.5
        if city and country:
            confidence += 0.3
        if org or isp:
            confidence += 0.2
        
        return SearchResult(
            source=self.name,
            data=data,
            confidence=min(confidence, 1.0),
            raw_data=ip_data
        )
