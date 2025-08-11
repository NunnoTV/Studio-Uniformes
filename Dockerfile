# Use uma imagem base do Python
FROM python:3.11-slim

# Defina o diretÃ³rio de trabalho no contÃªiner
WORKDIR /app

# Copie o arquivo de dependÃªncias e instale as dependÃªncias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie o resto do cÃ³digo da aplicaÃ§Ã£o
COPY . .

# A porta que o Gunicorn irÃ¡ expor
EXPOSE 80
