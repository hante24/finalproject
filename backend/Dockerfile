FROM python:3.11-slim


COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/


WORKDIR /app


COPY pyproject.toml .


RUN uv pip install --system --no-cache \
    fastapi \
    uvicorn \
    sqlalchemy \
    asyncpg \
    alembic \
    "python-jose[cryptography]" \
    "passlib[bcrypt]" \
    pydantic-settings \
    "pydantic[email]" \
    python-multipart \
    bcrypt



COPY . .


CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]