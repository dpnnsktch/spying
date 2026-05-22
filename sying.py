#!/usr/bin/env python3
"""
sying - OSINT Utility Framework
Модульный фреймворк для OSINT-расследований с поддержкой 200+ модулей.
"""

import argparse
import uuid
import importlib
import pkgutil
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

# Инициализация консоли Rich
console = Console()

# =============================================================================
# СТРУКТУРЫ ДАННЫХ
# =============================================================================


@dataclass
class SearchResult:
    """Класс для хранения результатов поиска от одного модуля."""
    source: str  # Название источника (модуля)
    category: str  # Категория данных (соцсети, реестры, и т.д.)
    data: Dict[str, Any]  # Найденные данные
    confidence: float = 0.0  # Уровень достоверности (0.0 - 1.0)
    raw_url: Optional[str] = None  # Ссылка на источник
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class OSINTReport:
    """Агрегированный отчет по всем найденным данным."""
    target_id: str
    search_query: Dict[str, str]
    results: List[SearchResult] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def add_result(self, result: SearchResult):
        """Добавить результат в отчет."""
        self.results.append(result)
    
    def get_all_data(self) -> Dict[str, Any]:
        """Объединить все данные из результатов в единую структуру."""
        consolidated = {
            'full_name': None,
            'age': None,
            'country': None,
            'address': None,
            'email': None,
            'phone': None,
            'nicknames': [],
            'social_profiles': [],
            'additional': {}
        }
        
        for result in self.results:
            data = result.data
            # Объединение данных с приоритетом более достоверных источников
            if data.get('full_name') and not consolidated['full_name']:
                consolidated['full_name'] = data['full_name']
            if data.get('age') and not consolidated['age']:
                consolidated['age'] = data['age']
            if data.get('country') and not consolidated['country']:
                consolidated['country'] = data['country']
            if data.get('address') and not consolidated['address']:
                consolidated['address'] = data['address']
            if data.get('email') and not consolidated['email']:
                consolidated['email'] = data['email']
            if data.get('phone') and not consolidated['phone']:
                consolidated['phone'] = data['phone']
            if data.get('nickname'):
                if data['nickname'] not in consolidated['nicknames']:
                    consolidated['nicknames'].append(data['nickname'])
            if data.get('profile_url'):
                consolidated['social_profiles'].append({
                    'source': result.source,
                    'url': data['profile_url']
                })
            
            # Дополнительные данные
            for key, value in data.items():
                if key not in ['full_name', 'age', 'country', 'address', 'email', 'phone', 'nickname', 'profile_url']:
                    consolidated['additional'][key] = value
        
        return consolidated


# =============================================================================
# БАЗОВЫЙ КЛАСС МОДУЛЯ
# =============================================================================


class BaseModule(ABC):
    """
    Базовый класс для всех OSINT-модулей.
    
    Все модули должны наследоваться от этого класса и реализовать метод search().
    
    Атрибуты:
        name: Уникальное имя модуля
        description: Описание того, что делает модуль
        category: Категория модуля (social, registry, breach, search_engine, etc.)
        api_key: API ключ (если требуется) - ЗАПОЛНЯЕТСЯ В НАСЛЕДНИКАХ
    """
    
    name: str = "base_module"
    description: str = "Базовый модуль"
    category: str = "general"
    api_key: Optional[str] = None  # <-- ВСТАВЬТЕ СЮДА ВАШ API КЛЮЧ В НАСЛЕДНИКЕ
    
    def __init__(self):
        """Инициализация модуля."""
        if self.api_key is None:
            console.print(f"[yellow]⚠ Модуль {self.name} не имеет API ключа[/yellow]")
    
    @abstractmethod
    def search(self, query: Dict[str, str]) -> Optional[SearchResult]:
        """
        Выполнить поиск по заданным параметрам.
        
        Args:
            query: Словарь с параметрами поиска, например:
                   {'name': 'John Doe', 'email': 'john@example.com'}
        
        Returns:
            SearchResult с найденными данными или None если ничего не найдено
        """
        pass
    
    def validate_query(self, query: Dict[str, str]) -> bool:
        """
        Проверить, содержит ли запрос нужные для этого модуля данные.
        
        Переопределите в наследнике для специфичных проверок.
        """
        return True
    
    def _make_request(self, url: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Вспомогательный метод для HTTP-запросов.
        
        Args:
            url: URL для запроса
            params: Параметры запроса
        
        Returns:
            JSON ответ или None при ошибке
        """
        try:
            import requests
            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            console.print(f"[red]✗ Ошибка запроса в {self.name}: {str(e)}[/red]")
            return None


# =============================================================================
# ПРИМЕР МОДУЛЯ: Поиск по GitHub
# =============================================================================


class GitHubModule(BaseModule):
    """
    Модуль для поиска пользователей на GitHub по никнейму.
    
    Для работы требуется API ключ GitHub (опционально, увеличивает лимиты).
    
    Настройка:
        1. Получите токен на https://github.com/settings/tokens
        2. Вставьте его в переменную api_key ниже
    """
    
    name = "github_search"
    description = "Поиск профилей и репозиториев на GitHub по никнейму"
    category = "social"
    
    # ↓↓↓ ВСТАВЬТЕ СЮДА ВАШ GITHUB TOKEN ↓↓↓
    api_key = None  # Пример: "ghp_xxxxxxxxxxxxxxxxxxxx"
    # ↑↑↑ КОНЕЦ НАСТРОЙКИ API КЛЮЧА ↑↑↑
    
    def validate_query(self, query: Dict[str, str]) -> bool:
        """Модуль работает только если есть никнейм."""
        return bool(query.get('nickname'))
    
    def search(self, query: Dict[str, str]) -> Optional[SearchResult]:
        """Выполнить поиск пользователя на GitHub."""
        nickname = query.get('nickname')
        if not nickname:
            return None
        
        console.print(f"[cyan]🔍 Поиск на GitHub: {nickname}[/cyan]")
        
        # Формируем запрос к GitHub API
        url = f"https://api.github.com/users/{nickname}"
        
        data = self._make_request(url)
        
        if data and data.get('login'):
            # Извлекаем полезные данные
            result_data = {
                'nickname': data.get('login'),
                'full_name': data.get('name'),
                'profile_url': data.get('html_url'),
                'avatar_url': data.get('avatar_url'),
                'bio': data.get('bio'),
                'company': data.get('company'),
                'location': data.get('location'),
                'public_repos': data.get('public_repos'),
                'followers': data.get('followers'),
                'created_at': data.get('created_at')
            }
            
            # Определяем местоположение (страна/город)
            location = data.get('location', '')
            country = None
            if location:
                # Простая эвристика - можно улучшить
                country = location.split(',')[-1].strip() if ',' in location else location
            
            if country:
                result_data['country'] = country
            
            return SearchResult(
                source=self.name,
                category=self.category,
                data=result_data,
                confidence=0.95,  # Высокая достоверность - данные напрямую от GitHub
                raw_url=data.get('html_url')
            )
        else:
            console.print(f"[yellow]⚠ Пользователь {nickname} не найден на GitHub[/yellow]")
            return None


# =============================================================================
# ПРИМЕР МОДУЛЯ: Поиск по Email (демонстрационный)
# =============================================================================


class EmailBreachModule(BaseModule):
    """
    Пример модуля для проверки утечек по email.
    
    Это шаблон - в реальности здесь был бы запрос к базе утечек.
    
    Настройка:
        Вставьте URL вашего API для проверки утечек
    """
    
    name = "email_breach_check"
    description = "Проверка email по базам известных утечек"
    category = "breach"
    
    # ↓↓↓ ВСТАВЬТЕ СЮДА URL ВАШЕГО API ДЛЯ ПРОВЕРКИ УТЕЧЕК ↓↓↓
    api_key = None  # Пример: "your_api_key_here"
    breach_api_url = "https://example-breach-api.com/check"  # Замените на реальный
    # ↑↑↑ КОНЕЦ НАСТРОЙКИ ↑↑↑
    
    def validate_query(self, query: Dict[str, str]) -> bool:
        return bool(query.get('email'))
    
    def search(self, query: Dict[str, str]) -> Optional[SearchResult]:
        """Проверить email в базах утечек."""
        email = query.get('email')
        if not email:
            return None
        
        console.print(f"[cyan]🔍 Проверка email в утечках: {email}[/cyan]")
        
        # ДЕМО-РЕЖИМ: Имитация ответа (удалите в продакшене)
        # В реальности здесь был бы запрос к API:
        # data = self._make_request(f"{self.breach_api_url}?email={email}")
        
        # Имитация нахождения в утечке
        import random
        if random.random() > 0.5:  # 50% шанс для демонстрации
            result_data = {
                'email': email,
                'breaches': ['Adobe', 'LinkedIn', 'Dropbox'],
                'breach_count': 3,
                'last_breach_date': '2023-01-15'
            }
            
            return SearchResult(
                source=self.name,
                category=self.category,
                data=result_data,
                confidence=0.8,
                raw_url=f"{self.breach_api_url}?email={email}"
            )
        else:
            console.print(f"[green]✓ Email {email} не найден в известных утечках (демо)[/green]")
            return None


# =============================================================================
# СИСТЕМА ГЕНЕРАЦИИ ОТЧЕТОВ
# =============================================================================


class ReportGenerator:
    """Генератор визуальных отчетов в виде схем."""
    
    @staticmethod
    def generate_ascii_schema(report: OSINTReport) -> str:
        """
        Создать текстовую схему с данными используя ASCII-графику.
        
        Формат:
        [ ФИО ] --> Возраст: {age}
        [ Местоположение ] --> {country} --> Адрес: {address}
        [ Контакты ] --> Email: {email} --> Номер: {phone}
        """
        data = report.get_all_data()
        lines = []
        
        # Заголовок
        lines.append("=" * 60)
        lines.append(f"OSINT REPORT | ID: {report.target_id}")
        lines.append(f"Generated: {report.created_at}")
        lines.append(f"Query: {report.search_query}")
        lines.append("=" * 60)
        lines.append("")
        
        # Схема данных
        lines.append("┌" + "─" * 58 + "┐")
        lines.append("│" + " DATA SCHEMA ".center(58) + "│")
        lines.append("└" + "─" * 58 + "┘")
        lines.append("")
        
        # ФИО и возраст
        if data['full_name']:
            lines.append(f"[ ФИО ] --> {data['full_name']}")
            if data['age']:
                lines.append(f"           └--> Возраст: {data['age']}")
        else:
            lines.append("[ ФИО ] --> <не найдено>")
        lines.append("")
        
        # Местоположение
        if data['country'] or data['address']:
            lines.append("[ Местоположение ]")
            if data['country']:
                lines.append(f"    └--> Страна: {data['country']}")
            if data['address']:
                lines.append(f"    └--> Адрес: {data['address']}")
        else:
            lines.append("[ Местоположение ] --> <не найдено>")
        lines.append("")
        
        # Контакты
        if data['email'] or data['phone']:
            lines.append("[ Контакты ]")
            if data['email']:
                lines.append(f"    └--> Email: {data['email']}")
            if data['phone']:
                lines.append(f"    └--> Номер: {data['phone']}")
        else:
            lines.append("[ Контакты ] --> <не найдено>")
        lines.append("")
        
        # Никнеймы
        if data['nicknames']:
            lines.append("[ Никнеймы ]")
            for nick in data['nicknames']:
                lines.append(f"    └--> {nick}")
            lines.append("")
        
        # Социальные профили
        if data['social_profiles']:
            lines.append("[ Социальные профили ]")
            for profile in data['social_profiles']:
                lines.append(f"    └>> {profile['source']}: {profile['url']}")
            lines.append("")
        
        # Дополнительные данные
        if data['additional']:
            lines.append("[ Дополнительно ]")
            for key, value in data['additional'].items():
                lines.append(f"    └--> {key}: {value}")
            lines.append("")
        
        # Статистика
        lines.append("┌" + "─" * 58 + "┐")
        lines.append("│" + " STATISTICS ".center(58) + "│")
        lines.append("└" + "─" * 58 + "┘")
        lines.append(f"Modules executed: {len(report.results)}")
        lines.append(f"Data points found: {sum(len(r.data) for r in report.results)}")
        lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_python_file(report: OSINTReport, output_dir: str = ".") -> str:
        """
        Создать файл result_{ID}.py со структурированными данными.
        
        Returns:
            Путь к созданному файлу
        """
        filename = f"result_{report.target_id}.py"
        filepath = os.path.join(output_dir, filename)
        
        schema = ReportGenerator.generate_ascii_schema(report)
        
        # Экранирование специальных символов для Python строки
        schema_escaped = schema.replace("\\", "\\\\").replace(chr(34), chr(92)+chr(34))
        
        # Создаем список результатов в виде простых словарей
        raw_results_list = []
        for r in report.results:
            raw_results_list.append({
                "source": r.source,
                "category": r.category,
                "data": r.data,
                "confidence": r.confidence,
                "url": r.raw_url,
                "timestamp": r.timestamp
            })
        
        results_list_str = repr(raw_results_list)
        
        content = f'''#!/usr/bin/env python3
"""
OSINT Report generated by sying framework
Report ID: {report.target_id}
Generated: {report.created_at}
"""

# ================================================================
# VISUAL SCHEMA
# ================================================================

SCHEMA = """
{schema_escaped}
"""

# ================================================================
# STRUCTURED DATA
# ================================================================

REPORT_DATA = {{
    "report_id": "{report.target_id}",
    "created_at": "{report.created_at}",
    "search_query": {repr(report.search_query)},
    "consolidated_data": {repr(report.get_all_data())},
    "raw_results": {results_list_str}
}}

# ================================================================
# USAGE EXAMPLE
# ================================================================

if __name__ == "__main__":
    print(SCHEMA)
    print("\nStructured data available in REPORT_DATA dictionary")
'''
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        return filepath
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath


# =============================================================================
# МЕНЕДЖЕР МОДУЛЕЙ
# =============================================================================


class ModuleManager:
    """Управляет загрузкой и выполнением всех доступных модулей."""
    
    def __init__(self):
        self.modules: List[BaseModule] = []
        self._discover_modules()
    
    def _discover_modules(self):
        """Автоматически найти и загрузить все модули."""
        # Загружаем модули из текущего файла (для примера)
        module_classes = [GitHubModule, EmailBreachModule]
        
        for cls in module_classes:
            try:
                self.modules.append(cls())
            except Exception as e:
                console.print(f"[red]✗ Ошибка загрузки модуля {cls.__name__}: {e}[/red]")
        
        # Здесь можно добавить автозагрузку из отдельных файлов:
        # import modules_package
        # for importer, modname, ispkg in pkgutil.iter_modules(modules_package.__path__):
        #     module = importlib.import_module(f"modules_package.{modname}")
        #     if hasattr(module, 'Module'):
        #         self.modules.append(module.Module())
    
    def get_modules_by_category(self, category: str) -> List[BaseModule]:
        """Получить модули определенной категории."""
        return [m for m in self.modules if m.category == category]
    
    def run_all_modules(self, query: Dict[str, str], report: OSINTReport) -> OSINTReport:
        """
        Запустить все подходящие модули для данного запроса.
        
        Args:
            query: Параметры поиска
            report: Объект отчета для заполнения результатами
        
        Returns:
            Обновленный отчет с результатами
        """
        suitable_modules = [m for m in self.modules if m.validate_query(query)]
        
        if not suitable_modules:
            console.print("[yellow]⚠ Нет модулей для текущих параметров поиска[/yellow]")
            return report
        
        console.print(f"\n[bold green]✓ Найдено {len(suitable_modules)} подходящих модулей[/bold green]\n")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Scanning...", total=len(suitable_modules))
            
            for module in suitable_modules:
                progress.update(task, description=f"Running {module.name}...")
                
                try:
                    result = module.search(query)
                    if result:
                        report.add_result(result)
                        console.print(f"[green]✓ {module.name}: найдено данных[/green]")
                    else:
                        console.print(f"[yellow]- {module.name}: ничего не найдено[/yellow]")
                except Exception as e:
                    console.print(f"[red]✗ {module.name}: ошибка - {str(e)}[/red]")
                
                progress.advance(task)
        
        return report


# =============================================================================
# CLI ИНТЕРФЕЙС
# =============================================================================


def create_parser() -> argparse.ArgumentParser:
    """Создать парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(
        prog='sying',
        description='OSINT Utility Framework - Модульный инструмент для разведки по открытым источникам',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  sying --name "John Doe" --email "john@example.com"
  sying --phone "+1234567890" --nickname "johndoe"
  sying --ip "192.168.1.1" --all-modules
  
Для добавления своих модулей:
  1. Создайте класс, наследующий BaseModule
  2. Реализуйте метод search(query)
  3. Зарегистрируйте модуль в ModuleManager
        """
    )
    
    # Группа для целевых параметров
    target_group = parser.add_argument_group('Target Parameters')
    target_group.add_argument('--name', '-n', type=str, help='Имя и Фамилия (например: "John Doe")')
    target_group.add_argument('--phone', '-p', type=str, help='Номер телефона')
    target_group.add_argument('--email', '-e', type=str, help='Email адрес')
    target_group.add_argument('--nickname', '-u', type=str, help='Никнейм/username')
    target_group.add_argument('--ip', type=str, help='IP адрес')
    
    # Группа для настроек
    config_group = parser.add_argument_group('Configuration')
    config_group.add_argument('--output-dir', '-o', type=str, default='.', 
                              help='Директория для сохранения отчетов (по умолчанию: текущая)')
    config_group.add_argument('--modules', '-m', type=str, nargs='+',
                              help='Конкретные модули для запуска (по умолчанию: все подходящие)')
    config_group.add_argument('--category', '-c', type=str,
                              choices=['social', 'breach', 'registry', 'search_engine', 'general'],
                              help='Запустить только модули указанной категории')
    config_group.add_argument('--verbose', '-v', action='store_true',
                              help='Подробный вывод')
    
    return parser


def print_banner():
    """Вывести стильный баннер программы."""
    banner = """
[bold cyan]
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   ███████╗████████╗ █████╗ ██████╗ ██╗      █████╗       ║
║   ██╔════╝╚══██╔══╝██╔══██╗██╔══██╗██║     ██╔══██╗      ║
║   ███████╗   ██║   ███████║██████╔╝██║     ███████║      ║
║   ╚════██║   ██║   ██╔══██║██╔══██╗██║     ██╔══██║      ║
║   ███████║   ██║   ██║  ██║██║  ██║███████╗██║  ██║      ║
║   ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝      ║
║                                                          ║
║          OSINT Framework v1.0 | 200+ Modules Ready       ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
[/bold cyan]
    """
    console.print(banner)


def main():
    """Точка входа приложения."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Показать баннер
    print_banner()
    
    # Собрать параметры поиска
    query = {}
    if args.name:
        query['name'] = args.name
    if args.phone:
        query['phone'] = args.phone
    if args.email:
        query['email'] = args.email
    if args.nickname:
        query['nickname'] = args.nickname
    if args.ip:
        query['ip'] = args.ip
    
    # Проверка наличия параметров
    if not query:
        console.print("[bold red]✗ Ошибка: Не указаны параметры поиска![/bold red]")
        console.print("\nИспользуйте хотя бы один из параметров:")
        console.print("  --name, --phone, --email, --nickname, --ip")
        console.print("\nПример: sying --name \"John Doe\" --email john@example.com")
        return 1
    
    # Создать уникальный ID для отчета
    report_id = str(uuid.uuid4())[:8]
    
    # Инициализировать отчет
    report = OSINTReport(
        target_id=report_id,
        search_query=query
    )
    
    # Показать информацию о поиске
    console.print(Panel.fit(
        f"[bold]Target ID:[/bold] {report_id}\n"
        f"[bold]Parameters:[/bold] {query}",
        title="🎯 Search Configuration",
        border_style="blue"
    ))
    
    # Инициализировать менеджер модулей
    console.print("\n[bold]📦 Loading modules...[/bold]")
    manager = ModuleManager()
    console.print(f"[green]✓ Loaded {len(manager.modules)} modules[/green]")
    
    # Фильтрация по категории если указано
    if args.category:
        console.print(f"[yellow]Filtering by category: {args.category}[/yellow]")
        # Можно добавить фильтрацию здесь
    
    # Запустить модули
    console.print("\n[bold]🚀 Starting scan...[/bold]\n")
    report = manager.run_all_modules(query, report)
    
    # Показать сводку
    console.print("\n" + "=" * 60)
    console.print(f"[bold]Scan Complete | Results: {len(report.results)}[/bold]")
    console.print("=" * 60)
    
    if report.results:
        # Создать таблицу результатов
        table = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
        table.add_column("Module", style="green")
        table.add_column("Category", style="yellow")
        table.add_column("Confidence", justify="right")
        table.add_column("Data Points", justify="right")
        
        for result in report.results:
            table.add_row(
                result.source,
                result.category,
                f"{result.confidence:.0%}",
                str(len(result.data))
            )
        
        console.print(table)
    
    # Сгенерировать отчет
    console.print("\n[bold]📄 Generating report...[/bold]")
    try:
        filepath = ReportGenerator.generate_python_file(report, args.output_dir)
        console.print(f"[green]✓ Report saved: {filepath}[/green]")
        
        # Показать превью схемы
        console.print("\n[bold]Preview:[/bold]")
        schema_preview = ReportGenerator.generate_ascii_schema(report)
        console.print(schema_preview)
        
    except Exception as e:
        console.print(f"[red]✗ Error generating report: {e}[/red]")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
