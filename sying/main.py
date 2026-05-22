#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sying - OSINT Framework
Главный исполняемый файл с CLI интерфейсом

Использование:
    python sying.py --username torvalds
    python sying.py --email test@example.com
    python sying.py --ip 8.8.8.8
    python sying.py --name "John Doe"
    python sying.py --phone +79991234567
"""

import argparse
import sys
from pathlib import Path

# Добавляем корень проекта в путь импорта
sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

from sying.core.module_manager import ModuleManager
from sying.core.report_generator import ReportGenerator
from sying.utils.helpers import detect_query_type


def print_banner(console: Console):
    """Вывод стильного баннера приложения"""
    banner = """
 ███████╗███╗   ██╗███████╗███╗   ██╗
 ╚══███╔╝████╗  ██║██╔════╝████╗  ██║
   ███╔╝ ██╔██╗ ██║█████╗  ██╔██╗ ██║
  ███╔╝  ██║╚██╗██║██╔══╝  ██║╚██╗██║
 ███████╗██║ ╚████║███████╗██║ ╚████║
 ╚══════╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═══╝
                                     
 OSINT Framework v1.0.0
    """
    
    console.print(Panel(
        banner,
        title="[bold cyan]SYING[/bold cyan]",
        subtitle="[dim]Модульная OSINT платформа[/dim]",
        box=box.DOUBLE_EDGE,
        border_style="cyan"
    ))
    console.print()


def create_parser() -> argparse.ArgumentParser:
    """Создание парсера аргументов командной строки"""
    parser = argparse.ArgumentParser(
        prog='sying',
        description='Sying - Модульный OSINT фреймворк для поиска информации',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  %(prog)s --username torvalds          Поиск по никнейму
  %(prog)s --email test@example.com     Поиск по email
  %(prog)s --ip 8.8.8.8                 Поиск по IP адресу
  %(prog)s --name "John Doe"            Поиск по имени
  %(prog)s --phone +79991234567         Поиск по телефону
  %(prog)s --list-modules               Показать все доступные модули
  %(prog)s --auto "query"               Автоматическое определение типа запроса
        """
    )
    
    # Группа для основных аргументов поиска
    search_group = parser.add_argument_group('Параметры поиска')
    search_group.add_argument(
        '--username', '-u',
        type=str,
        help='Никнейм для поиска'
    )
    search_group.add_argument(
        '--email', '-e',
        type=str,
        help='Email адрес для поиска'
    )
    search_group.add_argument(
        '--ip', '-i',
        type=str,
        help='IP адрес для поиска'
    )
    search_group.add_argument(
        '--name', '-n',
        type=str,
        help='Имя и фамилия для поиска'
    )
    search_group.add_argument(
        '--phone', '-p',
        type=str,
        help='Номер телефона для поиска'
    )
    search_group.add_argument(
        '--auto', '-a',
        type=str,
        help='Автоматическое определение типа запроса'
    )
    
    # Группа для настроек
    config_group = parser.add_argument_group('Настройки')
    config_group.add_argument(
        '--list-modules', '-l',
        action='store_true',
        help='Показать список всех доступных модулей'
    )
    config_group.add_argument(
        '--output-dir', '-o',
        type=str,
        default='reports',
        help='Директория для сохранения отчетов (по умолчанию: reports)'
    )
    config_group.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Подробный вывод'
    )
    config_group.add_argument(
        '--no-report',
        action='store_true',
        help='Не создавать файл отчета'
    )
    
    return parser


def main():
    """Основная функция приложения"""
    console = Console()
    
    # Вывод баннера
    print_banner(console)
    
    # Парсинг аргументов
    parser = create_parser()
    args = parser.parse_args()
    
    # Проверка наличия аргументов
    if not any([
        args.username, args.email, args.ip, 
        args.name, args.phone, args.auto, 
        args.list_modules
    ]):
        console.print("[yellow][!] Не указаны параметры поиска[/yellow]")
        console.print("Используйте --help для получения справки")
        sys.exit(1)
    
    # Инициализация менеджера модулей
    with console.status("[bold green]Загрузка модулей...", spinner="dots"):
        module_manager = ModuleManager()
    
    console.print(f"[green][+][/green] Загружено [bold]{len(module_manager.modules)}[/bold] модулей\n")
    
    # Показ списка модулей если запрошено
    if args.list_modules:
        module_manager.print_modules_table()
        sys.exit(0)
    
    # Определение типа запроса и значения
    query = None
    query_type = None
    
    if args.username:
        query = args.username
        query_type = 'username'
    elif args.email:
        query = args.email
        query_type = 'email'
    elif args.ip:
        query = args.ip
        query_type = 'ip'
    elif args.name:
        query = args.name
        query_type = 'name'
    elif args.phone:
        query = args.phone
        query_type = 'phone'
    elif args.auto:
        query = args.auto
        query_type = detect_query_type(query)
        if query_type:
            console.print(f"[cyan][*] Автоопределение: тип запроса = [bold]{query_type}[/bold][/cyan]\n")
        else:
            console.print("[red][!] Не удалось определить тип запроса[/red]")
            sys.exit(1)
    
    # Выполнение поиска
    console.print(Panel(
        f"[bold]Запрос:[/bold] {query}\n"
        f"[bold]Тип:[/bold] {query_type}",
        title="🔍 Параметры поиска",
        border_style="blue"
    ))
    console.print()
    
    # Поиск с индикатором прогресса
    all_results = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Поиск...", total=None)
        
        modules = module_manager.get_modules_by_query_type(query_type)
        
        if not modules:
            console.print(f"[yellow][!] Нет модулей для типа запроса '{query_type}'[/yellow]")
            sys.exit(1)
        
        for module in modules:
            progress.update(task, description=f"[cyan]Модуль: {module.name}")
            results = module.search(query, query_type)
            all_results.extend(results)
    
    # Вывод результатов
    console.print()
    console.print(Panel(
        f"[bold green]✓[/bold green] Найдено [bold]{len(all_results)}[/bold] результатов",
        border_style="green"
    ))
    
    if all_results:
        # Краткий вывод результатов
        for result in all_results:
            data = result.data
            confidence = int(result.confidence * 100)
            
            console.print()
            console.print(f"[bold cyan]Источник:[/bold cyan] {result.source}")
            console.print(f"[dim]Достоверность: {confidence}%[/dim]")
            
            if data.get('full_name'):
                console.print(f"  [green]•[/green] ФИО: {data['full_name']}")
            if data.get('email'):
                console.print(f"  [green]•[/green] Email: {data['email']}")
            if data.get('country'):
                console.print(f"  [green]•[/green] Страна: {data['country']}")
            if data.get('usernames'):
                usernames = ', '.join(data['usernames'][:5])
                console.print(f"  [green]•[/green] Никнеймы: {usernames}")
            if data.get('social_profiles'):
                for profile in data['social_profiles']:
                    platform = profile.get('platform', '')
                    url = profile.get('url', '')
                    if platform and url:
                        console.print(f"  [green]•[/green] {platform}: [link={url}]{url}[/link]")
    
    # Генерация отчета
    if not args.no_report and all_results:
        console.print()
        
        with console.status("[bold green]Генерация отчета...", spinner="dots"):
            generator = ReportGenerator(output_dir=args.output_dir)
            report_path = generator.generate(all_results, query, query_type)
        
        console.print(Panel(
            f"[bold]Отчет сохранен:[/bold]\n[dim]{report_path}[/dim]",
            title="📄 Файл отчета",
            border_style="yellow"
        ))
        
        # Подсказка как открыть отчет
        console.print(f"\n[dim]Для просмотра: cat {report_path}[/dim]")
    
    console.print()
    console.print("[dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim]")
    console.print("[dim]Sying OSINT Framework v1.0.0[/dim]")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Прервано пользователем")
        sys.exit(130)
    except Exception as e:
        print(f"\n[!] Произошла ошибка: {str(e)}")
        if '--verbose' in sys.argv or '-v' in sys.argv:
            import traceback
            traceback.print_exc()
        sys.exit(1)
