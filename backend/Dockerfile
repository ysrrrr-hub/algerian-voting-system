# backend/Dockerfile
FROM python:3.11-slim

LABEL maintainer="Voting System Team"
LABEL description="Algerian Electronic Voting System — Flask Backend"

# متغيرات البيئة
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# تثبيت اعتماديات النظام
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# تثبيت متطلبات Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# نسخ الكود
COPY . .

# مجلد المفاتيح (يُوصَل عبر volume)
RUN mkdir -p /app/secure

# المستخدم غير الجذر للأمان
RUN addgroup --system voting && adduser --system --group voting
RUN chown -R voting:voting /app
USER voting

EXPOSE 5000

# Healthcheck
HEALTHCHECK --interval=15s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

CMD ["python", "run.py"]
