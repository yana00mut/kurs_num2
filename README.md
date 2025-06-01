# Job Search API

Проект для поиска вакансий с использованием API HeadHunter. Позволяет искать вакансии, фильтровать их по различным параметрам и сохранять результаты в JSON формате.

## Возможности

- Поиск вакансий на HeadHunter
- Фильтрация по ключевым словам
- Фильтрация по зарплате
- Фильтрация по опыту работы
- Фильтрация по региону
- Сохранение результатов в JSON

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/job-search-api.git
cd job-search-api
```

2. Установите зависимости с помощью Poetry:
```bash
poetry install
```

## Использование

```python
from src.api.hh_api import HeadHunterAPI
from src.api.storage import JSONVacancyStorage

# Создание экземпляра API
api = HeadHunterAPI()

# Поиск вакансий
vacancies = api.get_vacancies(
    "Python Developer",
    salary_from=150000,
    experience="between1And3",
    area=1  # Москва
)

# Сохранение результатов
storage = JSONVacancyStorage("data/vacancies")
storage.save_vacancies(vacancies)
```

## Тестирование

Для запуска тестов используйте:
```bash
poetry run pytest
```

## Структура проекта

```
job-search-api/
├── src/
│   └── api/
│       ├── __init__.py
│       ├── abstract_api.py
│       ├── hh_api.py
│       ├── vacancy.py
│       └── storage.py
├── tests/
│   ├── __init__.py
│   ├── test_hh_api.py
│   ├── test_vacancy.py
│   └── test_storage.py
├── data/
│   └── README.md
├── pyproject.toml
├── README.md
└── .gitignore
```

## Лицензия

MIT


