# ============================
# 🐍 Base image
# ============================
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# ============================
# 📦 Install Poetry
# ============================
RUN pip install --no-cache-dir poetry

# ============================
# 📄 Copy dependency files
# ============================
COPY pyproject.toml poetry.lock* /app/

# Disable virtualenv creation inside containers
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# ============================
# 📂 Copy application files
# ============================
COPY . /app

# ============================
# 🧩 Ensure script permissions
# ============================
RUN chmod +x /app

# ============================
# 🚀 Start the service
# ============================
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]
