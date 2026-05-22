"""
Модули OSINT фреймворка Sying
Все модули должны находиться в этой директории
"""

# Автоматическая загрузка всех модулей
__all__ = []

import pkgutil
from pathlib import Path

# Получаем список всех модулей в пакете
module_dir = Path(__file__).parent
for importer, mod_name, ispkg in pkgutil.iter_modules([str(module_dir)]):
    if not mod_name.startswith('_'):
        __all__.append(mod_name)