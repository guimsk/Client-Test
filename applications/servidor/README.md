# Servidor C++ - Aplicação de Alto Performance

Servidor HTTP implementado em C++ para testes de escalabilidade e performance.

## 📋 Características

- **Linguagem**: C++17
- **Concorrência**: Thread pool para múltiplas conexões
- **Parsing JSON**: nlohmann/json library
- **Protocolo**: HTTP/1.1
- **Porta configurável**: Via argumento ou variável de ambiente

## 🏗️ Arquivos

```
servidor/
├── app_configurable.cpp    # Implementação principal (recomendada)
├── app.cpp                 # Versão básica
├── app_old.cpp            # Versão legada
├── app_new.cpp            # Versão experimental
├── app_simple.cpp         # Versão simplificada
├── app_json.cpp           # Versão focada em JSON
├── Dockerfile             # Imagem Docker
└── README.txt             # Instruções antigas (removido)
```

## 🔧 Compilação

### Dependências

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install build-essential g++ libnlohmann-json3-dev

# CentOS/RHEL
sudo yum install gcc-c++ nlohmann-json-devel

# Arch Linux
sudo pacman -S gcc nlohmann-json
```

### Build Local

```bash
# Compilar versão configurável (recomendada)
g++ -o servidor_cpp_configurable app_configurable.cpp \
    -std=c++17 -pthread -O3 -DNDEBUG

# Compilar versão básica
g++ -o servidor_cpp app.cpp -std=c++17 -pthread

# Compilar com debug
g++ -o servidor_cpp_debug app_configurable.cpp \
    -std=c++17 -pthread -g -DDEBUG
```

### Makefile (Opcional)

```makefile
CXX = g++
CXXFLAGS = -std=c++17 -pthread -O3 -DNDEBUG
TARGET = servidor_cpp_configurable
SOURCE = app_configurable.cpp

$(TARGET): $(SOURCE)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SOURCE)

debug: CXXFLAGS = -std=c++17 -pthread -g -DDEBUG
debug: $(TARGET)

clean:
	rm -f $(TARGET) servidor_cpp_debug

.PHONY: clean debug
```

## 🚀 Execução

### Linha de Comando

```bash
# Porta padrão (8000)
./servidor_cpp_configurable

# Porta customizada
./servidor_cpp_configurable 9000

# Com logs de debug
DEBUG=1 ./servidor_cpp_configurable 8000
```

### Variáveis de Ambiente

```bash
export SERVER_PORT=8000
export SERVER_HOST=0.0.0.0
export THREAD_POOL_SIZE=10
export LOG_LEVEL=INFO

./servidor_cpp_configurable
```

## 🐳 Docker

### Build da Imagem

```bash
# Build local
docker build -t guimsk/servidor-cpp:latest .

# Build com argumentos
docker build --build-arg PORT=9000 -t guimsk/servidor-cpp:custom .
```

### Execução

```bash
# Porta padrão
docker run -p 8000:8000 guimsk/servidor-cpp:latest

# Porta customizada
docker run -p 9000:9000 guimsk/servidor-cpp:latest 9000

# Com variáveis de ambiente
docker run -p 8000:8000 \
  -e THREAD_POOL_SIZE=20 \
  -e LOG_LEVEL=DEBUG \
  guimsk/servidor-cpp:latest
```

## 📊 Especificações Técnicas

### Thread Pool
- **Threads padrão**: 10
- **Máximo configurável**: 100
- **Queue size**: 1000 requests

### Limites de Performance
- **Conexões simultâneas**: ~1000
- **Requests/segundo**: ~8000-10000
- **Latência média**: 2-5ms
- **Uso de memória**: ~50MB base

### Protocolo HTTP

#### Request Format
```http
POST / HTTP/1.1
Host: localhost:8000
Content-Type: application/json
Content-Length: 123

{
  "message": "test message",
  "timestamp": "2024-01-01T12:00:00Z",
  "client_id": "client_001"
}
```

#### Response Format
```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 234

{
  "status": "success",
  "message": "Message received and processed",
  "server_time": "2024-01-01T12:00:00.123Z",
  "processing_time_ms": 1.23,
  "server_id": "cpp_server_001"
}
```

## 🔧 Configuração Avançada

### Arquivo de Configuração

Crie `server_config.json`:

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8000,
    "backlog": 128
  },
  "threading": {
    "pool_size": 20,
    "queue_size": 1000,
    "stack_size": 8192
  },
  "performance": {
    "keep_alive": true,
    "tcp_nodelay": true,
    "buffer_size": 8192,
    "timeout_ms": 30000
  },
  "logging": {
    "level": "INFO",
    "file": "server.log",
    "max_size_mb": 100
  }
}
```

### Compilação com Configuração

```cpp
#include "server_config.h"

// Usar configuração
ServerConfig config = loadConfig("server_config.json");
Server server(config);
server.start();
```

## 📈 Monitoramento

### Métricas Internas

O servidor coleta automaticamente:

```cpp
struct ServerMetrics {
    uint64_t requests_total;
    uint64_t requests_success;
    uint64_t requests_error;
    double avg_response_time_ms;
    uint32_t active_connections;
    uint64_t bytes_sent;
    uint64_t bytes_received;
};
```

### Endpoint de Status

```bash
curl http://localhost:8000/status

{
  "status": "running",
  "uptime_seconds": 3600,
  "requests_total": 10000,
  "requests_per_second": 85.3,
  "memory_usage_mb": 45.2,
  "cpu_usage_percent": 15.8
}
```

### Logs

```bash
# Logs em tempo real
tail -f server.log

# Filtrar apenas erros
grep ERROR server.log

# Análise de performance
grep "response_time" server.log | awk '{print $5}' | sort -n
```

## 🔍 Debugging

### Compilação com Debug

```bash
g++ -o servidor_cpp_debug app_configurable.cpp \
    -std=c++17 -pthread -g -DDEBUG -fsanitize=address
```

### Debug com GDB

```bash
gdb ./servidor_cpp_debug
(gdb) run 8000
(gdb) bt  # backtrace em caso de crash
```

### Profiling com Valgrind

```bash
# Memory leaks
valgrind --leak-check=full ./servidor_cpp_configurable 8000

# Performance profiling
valgrind --tool=callgrind ./servidor_cpp_configurable 8000
```

### Análise de Performance

```bash
# CPU usage
top -p $(pgrep servidor_cpp)

# Network connections
netstat -tlnp | grep :8000

# File descriptors
lsof -p $(pgrep servidor_cpp)
```

## 🐛 Troubleshooting

### Problemas Comuns

1. **Porta já em uso**
   ```bash
   # Verificar processo usando a porta
   sudo netstat -tlnp | grep :8000
   sudo kill <PID>
   ```

2. **Segmentation fault**
   ```bash
   # Executar com debug
   gdb ./servidor_cpp_configurable
   (gdb) run 8000
   (gdb) bt
   ```

3. **Too many open files**
   ```bash
   # Aumentar limite
   ulimit -n 65536
   echo "* soft nofile 65536" >> /etc/security/limits.conf
   ```

4. **Memory leaks**
   ```bash
   # Verificar com valgrind
   valgrind --leak-check=full ./servidor_cpp_configurable 8000
   ```

### Otimizações de Performance

```bash
# Compilar com otimizações máximas
g++ -o servidor_cpp_optimized app_configurable.cpp \
    -std=c++17 -pthread -O3 -march=native -DNDEBUG \
    -flto -ffast-math

# Configurar sistema para alta performance
echo 'net.core.somaxconn = 65536' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_max_syn_backlog = 65536' >> /etc/sysctl.conf
sysctl -p
```

# Pasta applications/servidor/

Esta pasta contém as implementações do servidor utilizadas nos testes de benchmark, com versões em C++ e diferentes modos de operação para análise comparativa de desempenho.

## Arquivos e Funções

- **app.cpp**: Implementação principal do servidor em C++.
  - Funções: inicialização do servidor, escuta de conexões, processamento de requisições, resposta ao cliente.
  - Justificativa: Base para comparação de performance entre diferentes abordagens e linguagens.

- **app_configurable.cpp**: Versão configurável do servidor, permitindo ajuste dinâmico de parâmetros via variáveis de ambiente ou argumentos.
  - Funções: leitura de configurações, adaptação de comportamento conforme parâmetros.
  - Justificativa: Facilita experimentação e tuning de performance.

- **app_json.cpp**: Versão do servidor com suporte a requisições/respostas em JSON.
  - Funções: serialização/deserialização de dados, integração com clientes que usam JSON.

- **app_new.cpp**: Nova abordagem/versão do servidor, com otimizações ou mudanças estruturais.
  - Funções: pode incluir melhorias de paralelismo, uso de recursos, etc.

- **app_old.cpp**: Versão legada do servidor, mantida para comparação histórica.

- **app_simple.cpp**: Versão simplificada do servidor, útil para testes básicos e validação de infraestrutura.

- **servidor**: Binário compilado do servidor principal.
- **servidor_cpp_configurable**: Binário compilado da versão configurável.
- **test_compile**: Script ou binário para teste de compilação.

- **Dockerfile**: Define o ambiente de execução do servidor para containerização.
  - Compila o código-fonte, instala dependências e define o entrypoint.

- **README.md**: Este arquivo de documentação.

## Como compilar e executar

- Para compilar manualmente (exemplo):
  ```bash
  g++ app.cpp -o servidor -lpthread
  ```
- Para buildar e rodar via Docker:
  ```bash
  docker build -t servidor-cpp .
  docker run --rm -p 8000:8000 servidor-cpp
  ```
- Via Docker Compose ou Kubernetes, o build e execução são automáticos.

## Observações
- O servidor pode ser configurado via variáveis de ambiente (ex: número de threads, modo de operação).
- Cada versão do servidor permite avaliar diferentes estratégias de implementação e otimização.

---

**Resumo das Saídas do Terminal**

- **Servidor iniciado na porta X:** O servidor está rodando e pronto para receber conexões.
- **Conexão recebida de ...:** Nova conexão de cliente aceita.
- **Requisição processada:** O servidor processou uma requisição com sucesso.
- **Erro de binding/porta ocupada:** A porta especificada já está em uso ou não pôde ser alocada.
- **Finalizando servidor:** O servidor foi encerrado normalmente.

Essas mensagens ajudam a monitorar o funcionamento do servidor C++ durante os testes.
