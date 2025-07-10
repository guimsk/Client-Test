# Usa imagem Python 3.10 slim para menor tamanho
FROM python:3.10-slim

# Define diretório de trabalho
WORKDIR /app

# Copia script Python do cliente
COPY app.py .

# Cria diretório para resultados
RUN mkdir -p /app/results

# Nenhuma lib extra é necessária aqui, pois usamos apenas bibliotecas padrão do Python
# (socket, time, os, csv são built-in)

# Comando padrão para executar o cliente
CMD ["python", "app.py"]
