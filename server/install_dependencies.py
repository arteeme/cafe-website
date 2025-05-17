#!/usr/bin/env python
"""
Скрипт для установки зависимостей проекта Кафе "Аромат".
Этот скрипт поможет установить все необходимые зависимости даже
при наличии проблем с установкой некоторых пакетов.
"""

import subprocess
import sys
import time
import os

# Основные зависимости
CORE_DEPENDENCIES = [
    "Flask>=2.0.0",
    "Flask-Cors>=3.0.0",
    "Flask-JWT-Extended>=4.0.0",
    "Flask-SQLAlchemy>=2.0.0",
    "SQLAlchemy>=2.0.0",
    "bcrypt>=4.0.0",
    "email-validator>=1.0.0",
    "python-dotenv>=1.0.0",
    "Werkzeug>=2.0.0",
]

# Дополнительные зависимости
OPTIONAL_DEPENDENCIES = [
    "Pillow>=9.0.0",
    "alembic>=1.0.0",
]

def run_command(command):
    """Запускает команду и выводит результат"""
    print(f"Выполняется: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ Команда успешно выполнена")
        return True
    else:
        print(f"❌ Ошибка: {result.stderr}")
        return False

def install_package(package):
    """Устанавливает пакет с помощью pip"""
    print(f"\n📦 Установка {package}...")
    return run_command([sys.executable, "-m", "pip", "install", package])

def main():
    """Основная функция скрипта"""
    print("=" * 70)
    print("📌 Установка зависимостей для проекта Кафе 'Аромат'")
    print("=" * 70)
    
    # Обновляем pip до последней версии
    print("\n🔄 Обновление pip...")
    run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    
    # Устанавливаем основные зависимости
    print("\n🔧 Установка основных зависимостей...")
    for package in CORE_DEPENDENCIES:
        install_package(package)
    
    # Устанавливаем дополнительные зависимости с обработкой ошибок
    print("\n🔍 Установка дополнительных зависимостей...")
    for package in OPTIONAL_DEPENDENCIES:
        if not install_package(package):
            package_name = package.split(">=")[0]
            print(f"⚠️ Не удалось установить {package_name}. Это не критично для базовой работы приложения.")
    
    print("\n" + "=" * 70)
    print("✅ Установка зависимостей завершена!")
    print("""
🚀 Теперь вы можете запустить приложение командой:
    python app.py
    
📝 Если возникнут проблемы, обратитесь к README.md
""")
    print("=" * 70)

if __name__ == "__main__":
    main() 
