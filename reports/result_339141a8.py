#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OSINT Отчет - Sying Framework
=============================

ID отчета: 339141a8
Дата создания: 2026-05-22 06:04:58
Запрос: torvalds
Тип запроса: username
Модулей использовано: 1

Визуальная схема связей
-----------------------
"""

# ============================================================================
# ВИЗУАЛЬНАЯ СХЕМА ДАННЫХ
# ============================================================================

[ ФИО ] --> Linus Torvalds

[ Местоположение ] --> OR --> Адрес: Portland, OR

[ Контакты ] --> Не найдено

[ Никнеймы ] --> torvalds

[ Социальные профили ]
    ->> GitHub: torvalds
        --> https://github.com/torvalds

[ Дополнительная информация ]
    ->> company: Linux Foundation
    ->> followers: 304022
    ->> public_repos: 11
    ->> created_at: 2011-09-03T15:26:22Z
    ->> profile_url: https://github.com/torvalds

# ============================================================================
# ИСТОЧНИКИ ДАННЫХ
# ============================================================================

[ Источники ]
    ->> Модуль: github_search (достоверность: 80%)
        --> Время: 2026-05-22T06:04:58.261391

# ============================================================================
# ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ ПО МОДУЛЯМ
# ============================================================================

# --- Модуль: github_search ---
# Достоверность: 80%
# Время: 2026-05-22T06:04:58.261391
# Данные: {'full_name': 'Linus Torvalds', 'age': None, 'country': 'OR', 'address': 'Portland, OR', 'email': '', 'phone': '', 'usernames': ['torvalds'], 'social_profiles': [{'platform': 'GitHub', 'username': 'torvalds', 'url': 'https://github.com/torvalds', 'avatar': 'https://avatars.githubusercontent.com/u/1024025?v=4'}], 'additional_info': {'bio': '', 'company': 'Linux Foundation', 'blog': '', 'followers': 304022, 'public_repos': 11, 'created_at': '2011-09-03T15:26:22Z', 'profile_url': 'https://github.com/torvalds'}, 'repositories': [{'name': 'linux', 'url': 'https://github.com/torvalds/linux', 'description': 'Linux kernel source tree', 'language': 'C', 'stars': 234011}, {'name': 'AudioNoise', 'url': 'https://github.com/torvalds/AudioNoise', 'description': 'Random digital audio effects', 'language': 'C', 'stars': 4371}, {'name': 'GuitarPedal', 'url': 'https://github.com/torvalds/GuitarPedal', 'description': 'Linus learns analog circuits', 'language': 'C', 'stars': 1932}, {'name': 'uemacs', 'url': 'https://github.com/torvalds/uemacs', 'description': 'Random version of microemacs with my private modificatons', 'language': 'C', 'stars': 2028}, {'name': 'test-tlb', 'url': 'https://github.com/torvalds/test-tlb', 'description': 'Stupid memory latency and TLB tester', 'language': 'C', 'stars': 997}, {'name': 'subsurface-for-dirk', 'url': 'https://github.com/torvalds/subsurface-for-dirk', 'description': 'Do not use - the real upstream is  Subsurface-divelog/subsurface', 'language': 'C++', 'stars': 455}, {'name': 'HunspellColorize', 'url': 'https://github.com/torvalds/HunspellColorize', 'description': "Wrapper around 'less' to colorize spelling mistakes using Hunspell", 'language': 'C', 'stars': 344}, {'name': 'pesconvert', 'url': 'https://github.com/torvalds/pesconvert', 'description': 'Brother PES file converter', 'language': 'C', 'stars': 559}, {'name': 'libgit2', 'url': 'https://github.com/torvalds/libgit2', 'description': 'A cross-platform, linkable library implementation of Git that you can use in your application.', 'language': 'C', 'stars': 356}, {'name': 'libdc-for-dirk', 'url': 'https://github.com/torvalds/libdc-for-dirk', 'description': "Only use for syncing with Dirk, don't use for anything else", 'language': 'C', 'stars': 387}]}
#


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
