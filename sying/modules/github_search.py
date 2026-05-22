"""
Модуль поиска по GitHub
Пример рабочего модуля для демонстрации архитектуры
"""

from typing import Dict, List, Optional, Any
from sying.core.base_module import BaseModule, SearchResult


class GitHubSearch(BaseModule):
    """
    Модуль поиска пользователей и репозиториев на GitHub
    
    Поддерживает поиск по:
    - username (никнейм)
    - name (имя)
    
    API документация: https://docs.github.com/en/rest
    """
    
    # ===== НАСТРОЙКИ МОДУЛЯ =====
    name = "github_search"
    description = "Поиск пользователей и репозиториев на GitHub"
    version = "1.0.0"
    supported_queries = ['username', 'name']
    required_api_keys = []  # GitHub API работает без ключа с лимитами
    
    # ===== КОНФИГУРАЦИЯ API =====
    # Для увеличения лимитов получите токен: https://github.com/settings/tokens
    API_KEY = ""  # <-- ВСТАВЬТЕ GITHUB TOKEN (опционально)
    BASE_URL = "https://api.github.com"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Sying-OSINT-Framework'
        }
        if self.API_KEY:
            self.headers['Authorization'] = f'token {self.API_KEY}'
    
    def _search(self, query: str, query_type: str) -> List[SearchResult]:
        """
        Поиск на GitHub
        
        Args:
            query: Строка запроса (никнейм или имя)
            query_type: Тип запроса ('username' или 'name')
        
        Returns:
            Список результатов поиска
        """
        results = []
        
        if query_type == 'username':
            # Поиск конкретного пользователя по никнейму
            user_data = self._get_user(query)
            if user_data:
                result = self._parse_user_data(user_data)
                results.append(result)
            
            # Поиск репозиториев пользователя
            repos_data = self._get_user_repos(query)
            if repos_data and result:
                result.data['repositories'] = [
                    {
                        'name': repo.get('name', ''),
                        'url': repo.get('html_url', ''),
                        'description': repo.get('description', ''),
                        'language': repo.get('language', ''),
                        'stars': repo.get('stargazers_count', 0)
                    }
                    for repo in repos_data[:10]  # Ограничим первыми 10
                ]
        
        elif query_type == 'name':
            # Поиск пользователей по имени
            users_data = self._search_users_by_name(query)
            for user_data in users_data[:5]:  # Ограничим первыми 5
                result = self._parse_user_data(user_data)
                results.append(result)
        
        return results
    
    def _get_user(self, username: str) -> Optional[Dict]:
        """Получение данных о пользователе по никнейму"""
        url = f"{self.BASE_URL}/users/{username}"
        return self._make_request(url, headers=self.headers)
    
    def _get_user_repos(self, username: str) -> Optional[List[Dict]]:
        """Получение списка репозиториев пользователя"""
        url = f"{self.BASE_URL}/users/{username}/repos"
        params = {'sort': 'updated', 'per_page': 10}
        response = self._make_request(url, params=params, headers=self.headers)
        return response if isinstance(response, list) else None
    
    def _search_users_by_name(self, name: str) -> List[Dict]:
        """Поиск пользователей по имени"""
        url = f"{self.BASE_URL}/search/users"
        params = {'q': name, 'sort': 'followers', 'order': 'desc'}
        response = self._make_request(url, params=params, headers=self.headers)
        
        if response and 'items' in response:
            return response['items']
        return []
    
    def _parse_user_data(self, user_data: Dict) -> SearchResult:
        """
        Парсинг данных пользователя в единый формат
        
        Args:
            user_data: Сырые данные от GitHub API
        
        Returns:
            SearchResult с нормализованными данными
        """
        # Извлечение данных
        full_name = user_data.get('name', '') or user_data.get('login', '')
        login = user_data.get('login', '')
        location = user_data.get('location', '')
        email = user_data.get('email', '')
        blog = user_data.get('blog', '')
        company = user_data.get('company', '')
        bio = user_data.get('bio', '')
        followers = user_data.get('followers', 0)
        public_repos = user_data.get('public_repos', 0)
        created_at = user_data.get('created_at', '')
        avatar_url = user_data.get('avatar_url', '')
        profile_url = user_data.get('html_url', '')
        
        # Определение страны из локации (упрощенно)
        country = ""
        address = ""
        if location:
            parts = location.split(', ')
            if len(parts) >= 2:
                country = parts[-1].strip()
                address = location
            else:
                country = location
                address = location
        
        # Формирование результата
        data = {
            'full_name': full_name,
            'age': None,  # GitHub не предоставляет возраст
            'country': country,
            'address': address,
            'email': email or '',
            'phone': '',  # GitHub не предоставляет телефоны
            'usernames': [login],
            'social_profiles': [
                {
                    'platform': 'GitHub',
                    'username': login,
                    'url': profile_url,
                    'avatar': avatar_url
                }
            ],
            'additional_info': {
                'bio': bio or '',
                'company': company or '',
                'blog': blog or '',
                'followers': followers,
                'public_repos': public_repos,
                'created_at': created_at,
                'profile_url': profile_url
            }
        }
        
        # Расчет уровня достоверности
        confidence = 0.5
        if email:
            confidence += 0.2
        if full_name and full_name != login:
            confidence += 0.2
        if followers > 100:
            confidence += 0.1
        
        return SearchResult(
            source=self.name,
            data=data,
            confidence=min(confidence, 1.0),
            raw_data=user_data
        )
