FROM mcr.microsoft.com/playwright/python:v1.45.0-jammy

WORKDIR /app

# Cài đặt các thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn vào container
COPY . .

# Mở cổng 10000 (Cổng mặc định của Render Web Service)
EXPOSE 10000

CMD ["python", "main.py"]
