# Sying OSINT Framework

**Модульная OSINT платформа для поиска информации**

## 📋 Описание

Sying — это масштабируемый фреймворк для OSINT-расследований, спроектированный для поддержки 200+ модулей. Утилита позволяет искать информацию по:

- **Имени и фамилии** (`--name`)
- **Номеру телефона** (`--phone`)
- **Email адресу** (`--email`)
- **Никнейму** (`--username`)
- **IP адресу** (`--ip`)
- **Автоматическое определение типа** (`--auto`)

## 🏗️ Архитектура

```
sying/
├── __init__.py              # Инициализация пакета
├── main.py                  # Главный CLI интерфейс
├── core/                    # Ядро фреймворка
│   ├── __init__.py
│   ├── base_module.py       # Базовый класс BaseModule
│   ├── module_manager.py    # Менеджер загрузки модулей
│   └── report_generator.py  # Генератор отчетов
├── modules/                 # OSINT модули
│   ├── __init__.py
│   ├── github_search.py     # Пример: поиск на GitHub
│   ├── hibp_search.py       # Пример: проверка email в утечках
│   └── ip_info_search.py    # Пример: информация об IP
├── utils/                   # Вспомогательные утилиты
│   ├── __init__.py
│   └── helpers.py           # Хелпер функции
└── reports/                 # Директория для отчетов
```

## 🚀 Быстрый старт

### Установка зависимостей

```bash
pip install requests rich
```

### Запуск

```bash
# Поиск по никнейму
python sying/main.py --username torvalds

# Поиск по email
python sying/main.py --email test@example.com

# Поиск по IP
python sying/main.py --ip 8.8.8.8

# Поиск по имени
python sying/main.py --name "John Doe"

# Поиск по телефону
python sying/main.py --phone +79991234567

# Автоопределение типа запроса
python sying/main.py --auto "query"

# Показать все модули
python sying/main.py --list-modules
```

## 📝 Создание собственного модуля

Все модули наследуются от `BaseModule`:

```python
from sying.core.base_module import BaseModule, SearchResult
from typing import Dict, List, Optional, Any


class MyCustomSearch(BaseModule):
    # Настройки модуля
    name = "my_custom_search"
    description = "Поиск в моей базе данных"
    version = "1.0.0"
    supported_queries = ['username', 'email']  # Типы запросов
    required_api_keys = ['API_KEY']  # Требуемые API ключи
    
    # Конфигурация API
    API_KEY = ""  # <-- ВСТАВЬТЕ API КЛЮЧ
    BASE_URL = "https://api.example.com"
    
    def _search(self, query: str, query_type: str) -> List[SearchResult]:
        """Основной метод поиска"""
        results = []
        
        # Ваш код поиска здесь
        # ...
        
        # Формирование результата
        data = {
            'full_name': 'Имя Фамилия',
            'age': 30,
            'country': 'Россия',
            'address': 'Москва, ул. Примерная 1',
            'email': 'email@example.com',
            'phone': '+79991234567',
            'usernames': ['username'],
            'social_profiles': [
                {
                    'platform': 'Platform',
                    'username': 'user',
                    'url': 'https://...'
                }
            ],
            'additional_info': {...}
        }
        
        result = SearchResult(
            source=self.name,
            data=data,
            confidence=0.8,  # 0.0 - 1.0
            raw_data=raw_response
        )
        
        results.append(result)
        return results
```

## 📊 Формат отчетов

После поиска автоматически создается файл `result_{ID}.py` с визуальной схемой:

```
[ ФИО ] --> Имя Фамилия
        --> Возраст: 30

[ Местоположение ] --> Россия --> Адрес: Москва, ул. Примерная 1

[ Контакты ] --> Email: email@example.com --> Номер: +79991234567

[ Никнеймы ] --> username1 --> username2

[ Социальные профили ]
    ->> GitHub: username
        --> https://github.com/username

[ Дополнительная информация ]
    ->> key: value
```

## 🔧 Конфигурация API

Для работы некоторых модулей требуются API ключи. Откройте соответствующий файл модуля и вставьте ключи:

```python
# modules/github_search.py
API_KEY = "your_github_token"  # <-- ВСТАВЬТЕ GITHUB TOKEN

# modules/hibp_search.py
API_KEY = "your_hibp_api_key"  # <-- ВСТАВЬТЕ HIBP API KEY

# modules/ip_info_search.py
API_KEY = "your_ipinfo_token"  # <-- ВСТАВЬТЕ IPINFO TOKEN (опционально)
```

## 🎯 Возможности расширения

Фреймворк рассчитан на 200+ модулей. Вы можете добавить модули для:

- Социальных сетей (VK, Facebook, Twitter, Instagram, LinkedIn)
- Мессенджеров (Telegram, WhatsApp)
- Поисковых систем (Google, Yandex, Bing)
- Баз данных утечек
- Публичных реестров
- WHOIS сервисов
- Геолокации
- Анализа изображений
- И многих других источников

## 📄 Лицензия

MIT License

## ⚠️ Отказ от ответственности

Данный инструмент предназначен только для образовательных и исследовательских целей. Используйте его ответственно и в соответствии с законодательством вашей страны.
