# Dockerfile otimizado para build rápido - Servidor C++
FROM gcc:13

# Instalar dependências em uma única camada para aproveitar cache
RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Define diretório de trabalho
WORKDIR /app

# Copia código fonte C++ (usar .dockerignore para otimizar)
COPY app_configurable.cpp .

# Compilação otimizada para performance máxima
# -O3: Otimização máxima
# -march=native: Otimizar para CPU atual  
# -flto: Link Time Optimization
# -std=c++17: C++17 standard
# -pthread: POSIX threads
RUN g++ -std=c++17 -pthread -O3 -march=native -flto \
    -ffast-math -funroll-loops \
    app_configurable.cpp -o servidor \
    && strip servidor

# Expõe porta 8000 (padrão compatível com configuração)
EXPOSE 8000

# Comando otimizado
ENTRYPOINT ["./servidor"]
CMD ["8000"]
