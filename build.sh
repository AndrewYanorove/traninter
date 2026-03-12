#!/bin/bash

# Установка зависимостей
pip install -r requirements.txt

# Сборка exe
python build_exe.py

echo "Готово! Файл находится в папке dist/"
