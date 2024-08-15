# Використовуємо офіційний образ Python
FROM python:3.11

# Встановлюємо Poetry
RUN pip install poetry

# Встановлюємо робочу директорію
WORKDIR /app

# Копіюємо файли проекту в контейнер
COPY pyproject.toml poetry.lock ./

# Встановлюємо залежності з Poetry
RUN poetry install --no-root

# Копіюємо решту файлів проекту
COPY . .

# Відкриваємо порт для Django
EXPOSE 8000

# Команда для запуску сервера
CMD ["poetry", "run", "gunicorn", "quotes_scraper.wsgi:application", "--bind", "0.0.0.0:8000"]
