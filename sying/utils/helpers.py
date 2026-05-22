"""
Утилиты для Sying Framework
Вспомогательные функции и классы
"""

import re
from typing import Optional, Tuple


def detect_query_type(query: str) -> Optional[str]:
    """
    Автоматическое определение типа запроса
    
    Args:
        query: Строка запроса
    
    Returns:
        Тип запроса ('name', 'phone', 'email', 'username', 'ip') или None
    """
    query = query.strip()
    
    # Проверка на email
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(email_pattern, query):
        return 'email'
    
    # Проверка на IP адрес (IPv4)
    ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if re.match(ip_pattern, query):
        # Дополнительная проверка на валидность октетов
        parts = query.split('.')
        if all(0 <= int(part) <= 255 for part in parts):
            return 'ip'
    
    # Проверка на номер телефона (различные форматы)
    phone_patterns = [
        r'^\+?\d{7,15}$',  # +1234567890 или 1234567890
        r'^\+?\d[\s\-]?\(?\d{2,3}\)?[\s\-]?\d{3,4}[\s\-]?\d{4}$',  # +7 (999) 123-45-67
    ]
    for pattern in phone_patterns:
        if re.match(pattern, query.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')):
            return 'phone'
    
    # Проверка на никнейм (начинается с @ или содержит только допустимые символы)
    if query.startswith('@'):
        return 'username'
    
    username_pattern = r'^[a-zA-Z0-9_]{3,30}$'
    if re.match(username_pattern, query):
        return 'username'
    
    # Если ничего не подошло, считаем что это имя
    # Имя должно содержать хотя бы две части (имя и фамилия)
    name_parts = query.split()
    if len(name_parts) >= 2 and all(part.isalpha() or '-' in part for part in name_parts):
        return 'name'
    
    # По умолчанию считаем никнеймом
    return 'username'


def validate_email(email: str) -> bool:
    """
    Валидация email адреса
    
    Args:
        email: Email для проверки
    
    Returns:
        True если email валиден
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """
    Валидация номера телефона
    
    Args:
        phone: Телефон для проверки
    
    Returns:
        True если телефон валиден
    """
    cleaned = re.sub(r'[^\d+]', '', phone)
    return 7 <= len(cleaned) <= 15


def validate_ip(ip: str) -> bool:
    """
    Валидация IP адреса
    
    Args:
        ip: IP адрес для проверки
    
    Returns:
        True если IP валиден
    """
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip):
        return False
    
    parts = ip.split('.')
    return all(0 <= int(part) <= 255 for part in parts)


def normalize_phone(phone: str) -> str:
    """
    Нормализация номера телефона к международному формату
    
    Args:
        phone: Телефон для нормализации
    
    Returns:
        Нормализованный номер телефона
    """
    # Удаляем все кроме цифр и +
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # Если начинается с 8, заменяем на +7 (для России)
    if cleaned.startswith('8') and len(cleaned) == 11:
        cleaned = '+7' + cleaned[1:]
    elif cleaned.startswith('7') and len(cleaned) == 11:
        cleaned = '+7' + cleaned[1:]
    
    # Добавляем + если нет
    if not cleaned.startswith('+') and len(cleaned) == 11:
        # Предполагаем российский номер
        cleaned = '+7' + cleaned
    
    return cleaned


def split_name(full_name: str) -> Tuple[str, str]:
    """
    Разделение полного имени на имя и фамилию
    
    Args:
        full_name: Полное имя
    
    Returns:
        Кортеж (first_name, last_name)
    """
    parts = full_name.strip().split()
    
    if len(parts) == 0:
        return ('', '')
    elif len(parts) == 1:
        return (parts[0], '')
    else:
        return (parts[0], ' '.join(parts[1:]))


def sanitize_input(text: str) -> str:
    """
    Очистка входных данных от потенциально опасных символов
    
    Args:
        text: Входная строка
    
    Returns:
        Очищенная строка
    """
    # Удаляем управляющие символы
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # Экранируем специальные символы для безопасности
    dangerous_chars = ['<', '>', '&', '"', "'", '\\']
    for char in dangerous_chars:
        text = text.replace(char, f'\\{char}')
    
    return text.strip()
