# Usa imagem oficial do GCC 13 como base
FROM gcc:13

# Instala dependências: netcat para health checks
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

# Define diretório de trabalho dentro do container
WORKDIR /app

# Copia código fonte C++ para o container
COPY app_configurable.cpp .

# Compila aplicação C++ com flags de otimização
# -std=c++17: Usa padrão C++17
# -pthread: Habilita suporte a threads POSIX
RUN g++ -std=c++17 -pthread app_configurable.cpp -o servidor

# Expõe porta 8000 para comunicação externa
EXPOSE 8000

# Comando padrão para executar o servidor
# A porta será passada como argumento pelo Kubernetes
ENTRYPOINT ["./servidor"]
CMD ["8000"]
