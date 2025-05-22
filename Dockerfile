# Use a imagem base do Python 3.12
FROM python:3.13.3

# Defina variáveis de ambiente para o Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Configure o diretório de trabalho dentro do contêiner
WORKDIR /usr/src/app

# Atualize o sistema e instale dependências necessárias
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Crie o diretório de logs para evitar problemas de ausência de diretórios
RUN mkdir -p /usr/src/app/logs && \
    chmod -R 755 /usr/src/app/logs

# Copie o arquivo requirements.txt primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instale as dependências Python especificadas no requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copie o restante do código da aplicação para o diretório de trabalho do contêiner
COPY . .

# Execute o collectstatic para coletar arquivos estáticos (se aplicável)
RUN python manage.py collectstatic --noinput || echo "Static collection skipped"
