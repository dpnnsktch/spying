"""
Менеджер модулей - загрузка и управление всеми OSINT модулями
Автоматически обнаруживает и загружает все доступные модули
"""

import importlib
import pkgutil
from pathlib import Path
from typing import Dict, List, Type, Any, Optional
from sying.core.base_module import BaseModule


class ModuleManager:
    """
    Менеджер для загрузки и управления OSINT модулями
    
    Автоматически обнаруживает все модули в папке modules/
    и предоставляет удобный интерфейс для работы с ними
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Инициализация менеджера модулей
        
        Args:
            config: Глобальная конфигурация для всех модулей
        """
        self.config = config or {}
        self.modules: Dict[str, BaseModule] = {}
        self._load_all_modules()
    
    def _load_all_modules(self):
        """Автоматическая загрузка всех модулей из папки modules/"""
        # Получаем путь к папке modules
        modules_path = Path(__file__).parent.parent / 'modules'
        
        if not modules_path.exists():
            print(f"[!] Папка модулей не найдена: {modules_path}")
            return
        
        # Импорт всех модулей из папки
        for importer, mod_name, ispkg in pkgutil.iter_modules([str(modules_path)]):
            if mod_name.startswith('_'):
                continue  # Пропускаем служебные файлы
            
            try:
                # Динамический импорт модуля
                full_module_name = f"sying.modules.{mod_name}"
                module = importlib.import_module(full_module_name)
                
                # Поиск классов, наследующих BaseModule
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    
                    # Проверка: класс, наследник BaseModule, не сам BaseModule
                    if (isinstance(attr, type) and 
                        issubclass(attr, BaseModule) and 
                        attr is not BaseModule):
                        
                        # Создание экземпляра модуля
                        instance = attr(config=self.config)
                        self.modules[instance.name] = instance
                        
                        print(f"[+] Загружен модуль: {instance.name} ({instance.description})")
                    
            except Exception as e:
                print(f"[!] Ошибка загрузки модуля {mod_name}: {str(e)}")
    
    def get_module(self, name: str) -> Optional[BaseModule]:
        """
        Получение модуля по имени
        
        Args:
            name: Имя модуля
        
        Returns:
            Экземпляр модуля или None если не найден
        """
        return self.modules.get(name)
    
    def get_modules_by_query_type(self, query_type: str) -> List[BaseModule]:
        """
        Получение всех модулей, поддерживающих данный тип запроса
        
        Args:
            query_type: Тип запроса ('name', 'phone', 'email', 'username', 'ip')
        
        Returns:
            Список модулей, поддерживающих этот тип запроса
        """
        return [
            module for module in self.modules.values()
            if query_type in module.supported_queries
        ]
    
    def search_all(self, query: str, query_type: str) -> List[Any]:
        """
        Выполнение поиска во всех доступных модулях
        
        Args:
            query: Строка запроса
            query_type: Тип запроса
        
        Returns:
            Список всех результатов от всех модулей
        """
        all_results = []
        modules = self.get_modules_by_query_type(query_type)
        
        print(f"\n[*] Запуск поиска по {len(modules)} модулям...")
        
        for module in modules:
            print(f"  -> Модуль {module.name}...")
            results = module.search(query, query_type)
            all_results.extend(results)
            
            if results:
                print(f"     Найдено результатов: {len(results)}")
            else:
                print(f"     Нет результатов")
        
        return all_results
    
    def list_modules(self) -> List[Dict[str, Any]]:
        """
        Получение списка всех загруженных модулей с информацией
        
        Returns:
            Список словарей с информацией о каждом модуле
        """
        return [module.get_info() for module in self.modules.values()]
    
    def print_modules_table(self):
        """Вывод таблицы всех доступных модулей"""
        from rich.console import Console
        from rich.table import Table
        
        console = Console()
        table = Table(title="Доступные OSINT модули", show_header=True)
        
        table.add_column("Название", style="cyan")
        table.add_column("Описание", style="white")
        table.add_column("Типы запросов", style="green")
        table.add_column("API ключи", style="yellow")
        table.add_column("Статус", style="blue")
        
        for module in self.modules.values():
            info = module.get_info()
            queries = ', '.join(info['supported_queries']) if info['supported_queries'] else '-'
            api_status = "✓" if info['has_api_keys'] else "✗" if module.required_api_keys else "-"
            status = "Готов" if (not module.required_api_keys or info['has_api_keys']) else "Требует API"
            
            table.add_row(
                info['name'],
                info['description'],
                queries,
                api_status,
                status
            )
        
        console.print(table)
        console.print(f"\nВсего модулей: {len(self.modules)}")
