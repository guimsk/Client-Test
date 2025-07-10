# Dockerfile para Servidor C
FROM gcc:latest

# Instala dependências necessárias
RUN apt-get update && apt-get install -y \
    build-essential \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# Define diretório de trabalho
WORKDIR /app

# Copia código fonte
COPY app_configurable.c .

# Compila o servidor
RUN gcc -std=c99 -pthread -O2 app_configurable.c -o servidor

# Expõe a porta
EXPOSE 8000

# Define o comando para executar o servidor
CMD ["./servidor", "8000"]
