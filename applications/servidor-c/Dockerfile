# Dockerfile otimizado para build rápido - Servidor C
FROM gcc:13

# Instalar dependências otimizadas em uma camada
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libc6-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Define diretório de trabalho
WORKDIR /app

# Copia código fonte C
COPY app_configurable.c .

# Compilação otimizada para máxima performance
# -O3: Otimização máxima
# -march=native: Otimizar para CPU atual
# -flto: Link Time Optimization  
# -std=c99: C99 standard
# -pthread: POSIX threads
RUN gcc -std=c99 -pthread -O3 -march=native -flto \
    -ffast-math -funroll-loops \
    app_configurable.c -o servidor \
    && strip servidor

# Expõe porta 8000
EXPOSE 8000

# Comando otimizado
ENTRYPOINT ["./servidor"]
CMD ["8000"]
