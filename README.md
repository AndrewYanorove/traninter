# ЭлектроКвест

Интерактивный симулятор электрических цепей для изучения физики и электротехники.

## Возможности

- Реалистичная физика (закон Ома)
- Система квестов и прогрессии
- Различные компоненты: батареи, резисторы, лампы, измерительные приборы
- Визуализация тока, напряжения и мощности
- Реалистичные эффекты (перегорание, свечение)

## Запуск локально

```bash
pip install -r requirements.txt
python app.py
```

Откройте http://localhost:5000

## Деплой на Render

1. Создайте репозиторий на GitHub
2. Залейте код
3. На Render: New → Web Service
4. Подключите репозиторий
5. Build Command: `pip install -r requirements.txt`
6. Start Command: `gunicorn app:app`

## Структура проекта

```
.
├── app.py                          # Flask приложение
├── requirements.txt                # Зависимости
├── Procfile                        # Для Render
├── templates/
│   └── index.html                  # Главная страница
├── static/
│   ├── css/
│   │   └── style.css              # Стили
│   └── js/
│       └── script.js              # JavaScript
└── dist/
    └── ЭлектроКвест.exe           # Собранное приложение (добавить после сборки)
```

## Сборка exe

На Windows:

```bash
pip install pygame pyinstaller
python build_exe.py
```

Файл появится в `dist/ЭлектроКвест.exe`

## Лицензия

MIT
