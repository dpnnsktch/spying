"""
Генератор отчетов - создание визуальных схем результатов поиска
Формирует файлы result_{ID}.py с графическим представлением данных
"""

import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from sying.core.base_module import SearchResult


class ReportGenerator:
    """
    Генератор отчетов в виде визуальных схем
    
    Создает файлы с уникальным ID в формате result_{ID}.py
    Данные представляются в виде схемы со стрелками --> и ->>
    """
    
    def __init__(self, output_dir: str = "reports"):
        """
        Инициализация генератора отчетов
        
        Args:
            output_dir: Директория для сохранения отчетов
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.report_id = str(uuid.uuid4())[:8]  # Короткий уникальный ID
    
    def generate(self, results: List[SearchResult], query: str, query_type: str) -> str:
        """
        Генерация отчета по результатам поиска
        
        Args:
            results: Список результатов поиска
            query: Исходный запрос
            query_type: Тип запроса
        
        Returns:
            Путь к созданному файлу отчета
        """
        # Обновляем ID для каждого отчета
        self.report_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Агрегация данных из всех результатов
        aggregated_data = self._aggregate_results(results)
        
        # Формирование содержимого отчета
        content = self._build_report_content(
            aggregated_data=aggregated_data,
            query=query,
            query_type=query_type,
            timestamp=timestamp,
            report_id=self.report_id,
            modules_count=len(results),
            results=results
        )
        
        # Сохранение файла
        filename = f"result_{self.report_id}.py"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(filepath)
    
    def _aggregate_results(self, results: List[SearchResult]) -> Dict[str, Any]:
        """
        Агрегация данных из всех результатов в единую структуру
        
        Args:
            results: Список результатов поиска
        
        Returns:
            Словарь с агрегированными данными
        """
        aggregated = {
            'full_name': '',
            'age': None,
            'country': '',
            'address': '',
            'email': '',
            'phone': '',
            'usernames': set(),
            'social_profiles': [],
            'additional_info': {},
            'sources': []
        }
        
        for result in results:
            data = result.data
            
            # Объединение данных с приоритетом непустых значений
            if data.get('full_name') and not aggregated['full_name']:
                aggregated['full_name'] = data['full_name']
            
            if data.get('age') and not aggregated['age']:
                aggregated['age'] = data['age']
            
            if data.get('country') and not aggregated['country']:
                aggregated['country'] = data['country']
            
            if data.get('address') and not aggregated['address']:
                aggregated['address'] = data['address']
            
            if data.get('email') and not aggregated['email']:
                aggregated['email'] = data['email']
            
            if data.get('phone') and not aggregated['phone']:
                aggregated['phone'] = data['phone']
            
            # Добавление usernames
            if data.get('usernames'):
                aggregated['usernames'].update(data['usernames'])
            
            # Добавление социальных профилей
            if data.get('social_profiles'):
                for profile in data['social_profiles']:
                    if profile not in aggregated['social_profiles']:
                        aggregated['social_profiles'].append(profile)
            
            # Добавление источников
            aggregated['sources'].append({
                'module': result.source,
                'confidence': result.confidence,
                'timestamp': result.timestamp
            })
            
            # Объединение дополнительной информации
            if data.get('additional_info'):
                for key, value in data['additional_info'].items():
                    if key not in aggregated['additional_info']:
                        aggregated['additional_info'][key] = value
        
        # Конвертация set в list для JSON-сериализуемости
        aggregated['usernames'] = list(aggregated['usernames'])
        
        return aggregated
    
    def _build_report_content(
        self,
        aggregated_data: Dict[str, Any],
        query: str,
        query_type: str,
        timestamp: str,
        report_id: str,
        modules_count: int,
        results: List[SearchResult]
    ) -> str:
        """
        Построение содержимого отчета в виде визуальной схемы
        
        Args:
            aggregated_data: Агрегированные данные
            query: Исходный запрос
            query_type: Тип запроса
            timestamp: Время создания отчета
            report_id: Уникальный ID отчета
            modules_count: Количество модулей, которые нашли данные
            results: Исходные результаты для детального вывода
        
        Returns:
            Строка с содержимым отчета
        """
        # Шапка отчета
        content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OSINT Отчет - Sying Framework
=============================

ID отчета: {report_id}
Дата создания: {timestamp}
Запрос: {query}
Тип запроса: {query_type}
Модулей использовано: {modules_count}

Визуальная схема связей
-----------------------
"""

# ============================================================================
# ВИЗУАЛЬНАЯ СХЕМА ДАННЫХ
# ============================================================================

'''
        
        # Основная схема данных
        data = aggregated_data
        
        # ФИО
        if data['full_name']:
            content += f"[ ФИО ] --> {data['full_name']}\n"
            if data['age']:
                content += f"        --> Возраст: {data['age']}\n"
        else:
            content += "[ ФИО ] --> Не найдено\n"
        
        content += "\n"
        
        # Местоположение
        if data['country'] or data['address']:
            content += f"[ Местоположение ]"
            if data['country']:
                content += f" --> {data['country']}"
            if data['address']:
                content += f" --> Адрес: {data['address']}"
            content += "\n"
        else:
            content += "[ Местоположение ] --> Не найдено\n"
        
        content += "\n"
        
        # Контакты
        content += "[ Контакты ]"
        contacts_found = False
        
        if data['email']:
            content += f" --> Email: {data['email']}"
            contacts_found = True
        
        if data['phone']:
            content += f" --> Номер: {data['phone']}"
            contacts_found = True
        
        if not contacts_found:
            content += " --> Не найдено"
        
        content += "\n\n"
        
        # Никнеймы
        if data['usernames']:
            content += "[ Никнеймы ]"
            for username in data['usernames'][:10]:  # Ограничим первыми 10
                content += f" --> {username}"
            if len(data['usernames']) > 10:
                content += f" --> ... и ещё {len(data['usernames']) - 10}"
            content += "\n"
        else:
            content += "[ Никнеймы ] --> Не найдено\n"
        
        content += "\n"
        
        # Социальные профили
        if data['social_profiles']:
            content += "[ Социальные профили ]\n"
            for profile in data['social_profiles']:
                platform = profile.get('platform', 'Unknown')
                username = profile.get('username', '')
                url = profile.get('url', '')
                
                if platform and url:
                    content += f"    ->> {platform}: {username}\n"
                    content += f"        --> {url}\n"
        else:
            content += "[ Социальные профили ] --> Не найдено\n"
        
        content += "\n"
        
        # Дополнительная информация от модулей
        if data['additional_info']:
            content += "[ Дополнительная информация ]\n"
            for key, value in data['additional_info'].items():
                if isinstance(value, (dict, list)):
                    content += f"    ->> {key}: {str(value)[:100]}{'...' if len(str(value)) > 100 else ''}\n"
                elif value:
                    content += f"    ->> {key}: {value}\n"
        else:
            content += "[ Дополнительная информация ] --> Отсутствует\n"
        
        content += "\n"
        
        # Источники данных
        content += "# ============================================================================\n"
        content += "# ИСТОЧНИКИ ДАННЫХ\n"
        content += "# ============================================================================\n\n"
        
        content += "[ Источники ]\n"
        for source in data['sources']:
            module_name = source['module']
            confidence = source['confidence']
            conf_percent = int(confidence * 100)
            content += f"    ->> Модуль: {module_name} (достоверность: {conf_percent}%)\n"
            content += f"        --> Время: {source['timestamp']}\n"
        
        content += "\n"
        
        # Детальные данные от каждого модуля
        content += "# ============================================================================\n"
        content += "# ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ ПО МОДУЛЯМ\n"
        content += "# ============================================================================\n\n"
        
        for result in results:
            content += f"# --- Модуль: {result.source} ---\n"
            content += f"# Достоверность: {int(result.confidence * 100)}%\n"
            content += f"# Время: {result.timestamp}\n"
            content += f"# Данные: {result.data}\n"
            content += "#\n\n"
        
        # Подвал
        content += '''
# ============================================================================
# КОНЕЦ ОТЧЕТА
# ============================================================================
# 
# Для использования данных в коде:
#   from sying.core.report_generator import ReportGenerator
#   generator = ReportGenerator()
#   generator.generate(results, query, query_type)
#
# Sying OSINT Framework v1.0.0
# https://github.com/sying-osint
# ============================================================================
'''
        
        return content
    
    def generate_simple(self, data: Dict[str, Any], title: str = "Отчет") -> str:
        """
        Генерация простого отчета без агрегации
        
        Args:
            data: Данные для отчета
            title: Заголовок отчета
        
        Returns:
            Путь к созданному файлу
        """
        self.report_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{title}
ID: {self.report_id}
Дата: {timestamp}
"""

# Визуальная схема
'''
        
        for key, value in data.items():
            if isinstance(value, list):
                content += f"[ {key} ]"
                for item in value[:5]:
                    content += f" --> {item}"
                if len(value) > 5:
                    content += f" --> ... ({len(value)} всего)"
                content += "\n\n"
            elif isinstance(value, dict):
                content += f"[ {key} ]\n"
                for subkey, subvalue in value.items():
                    content += f"    ->> {subkey}: {subvalue}\n"
                content += "\n"
            else:
                content += f"[ {key} ] --> {value}\n\n"
        
        filepath = self.output_dir / f"result_{self.report_id}.py"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(filepath)
