```
# Servidor C - Implementação de Alto Performance

Servidor HTTP implementado em C puro para máxima performance e eficiência de recursos.

## 📋 Características

- **Linguagem**: C (C99/C11)
- **Compilador**: GCC
- **Biblioteca JSON**: libcjson
- **Concorrência**: Sockets não-bloqueantes + select/epoll
- **Protocolo**: HTTP/1.1 básico
- **Footprint**: Mínimo uso de memória

## 🏗️ Arquivos

```
servidor-c/
├── app_configurable.c      # Implementação principal (recomendada)
├── app.c                   # Versão básica
├── app_simple.c           # Versão simplificada
├── app_cjson.c            # Versão com cJSON
├── server.c               # Core do servidor
├── Dockerfile             # Imagem Docker
├── Makefile               # Build configuration
└── obj/                   # Arquivos objeto (gerados)
```

## 🔧 Compilação

### Dependências

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install build-essential gcc libcjson-dev

# CentOS/RHEL
sudo yum install gcc cjson-devel

# Arch Linux
sudo pacman -S gcc cjson

# Alpine Linux (Docker)
apk add --no-cache gcc musl-dev cjson-dev
```

### Build com Makefile

```bash
# Compilar versão otimizada
make

# Compilar versão debug
make debug

# Limpar build
make clean

# Compilar tudo
make all
```

### Build Manual

```bash
# Versão otimizada
gcc -o servidor_c_configurable app_configurable.c \
    -lcjson -O3 -DNDEBUG -std=c99

# Versão debug
gcc -o servidor_c_debug app_configurable.c \
    -lcjson -g -DDEBUG -Wall -Wextra -std=c99

# Versão com sanitizers
gcc -o servidor_c_sanitized app_configurable.c \
    -lcjson -g -fsanitize=address -fsanitize=undefined
```

## 🚀 Execução

### Linha de Comando

```bash
# Porta padrão (8000)
./servidor_c_configurable

# Porta customizada
./servidor_c_configurable 9000

# Com logs de debug
DEBUG=1 ./servidor_c_configurable 8000

# Com configurações específicas
MAX_CONNECTIONS=1000 BUFFER_SIZE=8192 ./servidor_c_configurable 8000
```

### Variáveis de Ambiente

```bash
export SERVER_PORT=8000
export SERVER_HOST=0.0.0.0
export MAX_CONNECTIONS=500
export BUFFER_SIZE=4096
export LOG_LEVEL=INFO

./servidor_c_configurable
```

## 🐳 Docker

### Build da Imagem

```bash
# Build padrão
docker build -t guimsk/servidor-c:latest .

# Build com Alpine (menor)
docker build -f Dockerfile.alpine -t guimsk/servidor-c:alpine .

# Build multi-stage
docker build --target production -t guimsk/servidor-c:prod .
```

### Execução

```bash
# Porta padrão
docker run -p 8000:8000 guimsk/servidor-c:latest

# Porta customizada
docker run -p 9000:9000 guimsk/servidor-c:latest 9000

# Com limites de recursos
docker run -p 8000:8000 \
  --memory=64m \
  --cpus=0.5 \
  guimsk/servidor-c:latest
```

## 📊 Especificações Técnicas

### Performance
- **Conexões simultâneas**: ~2000
- **Requests/segundo**: ~12000-15000
- **Latência média**: 1-3ms
- **Uso de memória**: ~10-20MB
- **CPU overhead**: Mínimo

### Arquitetura
- **I/O Model**: Non-blocking sockets
- **Event Loop**: select() ou epoll() (Linux)
- **Memory Management**: Pool de buffers reutilizáveis
- **Connection Handling**: Keep-alive opcional

### Protocolo HTTP

#### Request Handling
```c
// Estrutura de request
typedef struct {
    char method[16];
    char path[256];
    char version[16];
    char headers[4096];
    char body[8192];
    size_t content_length;
} http_request_t;
```

#### Response Format
```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 156
Connection: keep-alive

{
  "status": "success",
  "message": "Message processed",
  "server_time": "2024-01-01T12:00:00.123Z",
  "processing_time_ms": 0.85,
  "server_id": "c_server_001"
}
```

## 🔧 Configuração

### Arquivo de Configuração (server.conf)

```ini
[server]
host = 0.0.0.0
port = 8000
backlog = 128
max_connections = 1000

[performance]
buffer_size = 8192
keep_alive = true
tcp_nodelay = true
timeout_seconds = 30

[logging]
level = INFO
file = server.log
max_size_mb = 50
rotate = true
```

### Definições de Compilação

```c
// Configurações via defines
#define MAX_CONNECTIONS 1000
#define BUFFER_SIZE 8192
#define KEEP_ALIVE_TIMEOUT 30
#define LOG_LEVEL LOG_INFO

// Features opcionais
#define ENABLE_EPOLL      // Linux epoll (mais eficiente)
#define ENABLE_KQUEUE     // BSD kqueue
#define ENABLE_STATS      // Coleta de estatísticas
#define ENABLE_JSON_PRETTY // JSON formatado
```

## 📈 Monitoramento

### Estatísticas Internas

```c
typedef struct {
    uint64_t requests_total;
    uint64_t requests_success;
    uint64_t requests_error;
    uint64_t bytes_sent;
    uint64_t bytes_received;
    uint32_t connections_active;
    uint32_t connections_total;
    double avg_response_time_ms;
    time_t start_time;
} server_stats_t;
```

### Endpoint de Status

```bash
curl http://localhost:8000/stats

{
  "server": {
    "version": "1.0.0",
    "uptime": 3600,
    "pid": 1234
  },
  "requests": {
    "total": 50000,
    "success": 49950,
    "errors": 50,
    "rate_per_sec": 138.5
  },
  "connections": {
    "active": 45,
    "total": 1250,
    "max_concurrent": 89
  },
  "memory": {
    "usage_mb": 12.3,
    "peak_mb": 15.7
  }
}
```

## 🔍 Debugging

### Compilação Debug

```bash
# Debug completo
gcc -o servidor_c_debug app_configurable.c \
    -lcjson -g -O0 -DDEBUG \
    -Wall -Wextra -Wpedantic \
    -fsanitize=address -fsanitize=undefined

# Memory debug
gcc -o servidor_c_memcheck app_configurable.c \
    -lcjson -g -DDEBUG_MEMORY
```

### Debug com GDB

```bash
gdb ./servidor_c_debug
(gdb) set args 8000
(gdb) run
(gdb) bt  # em caso de crash
(gdb) info locals
```

### Análise de Memória

```bash
# Valgrind
valgrind --leak-check=full \
         --show-leak-kinds=all \
         --track-origins=yes \
         ./servidor_c_configurable 8000

# Address Sanitizer
ASAN_OPTIONS=verbosity=1:halt_on_error=1 ./servidor_c_debug 8000
```

### Profiling

```bash
# CPU profiling com gprof
gcc -pg -o servidor_c_prof app_configurable.c -lcjson
./servidor_c_prof 8000
gprof servidor_c_prof gmon.out > profile.txt

# System calls tracing
strace -c ./servidor_c_configurable 8000
```

## 🔧 Otimizações

### Compilação Otimizada

```bash
# Máxima otimização
gcc -o servidor_c_optimized app_configurable.c \
    -lcjson -O3 -march=native -mtune=native \
    -flto -ffast-math -DNDEBUG \
    -funroll-loops -finline-functions

# Profile-guided optimization
gcc -fprofile-generate -o servidor_c_pgo app_configurable.c -lcjson
./servidor_c_pgo 8000  # executar workload típico
gcc -fprofile-use -O3 -o servidor_c_final app_configurable.c -lcjson
```

### Sistema Operacional

```bash
# Aumentar limites de file descriptors
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# Otimizar TCP stack
echo 'net.core.somaxconn = 65536' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_max_syn_backlog = 65536' >> /etc/sysctl.conf
echo 'net.core.netdev_max_backlog = 5000' >> /etc/sysctl.conf
sysctl -p
```

## 🐛 Troubleshooting

### Problemas Comuns

1. **Erro de compilação - cjson não encontrado**
   ```bash
   # Ubuntu/Debian
   sudo apt install libcjson-dev
   
   # Verificar localização
   pkg-config --cflags --libs libcjson
   ```

2. **Segmentation fault**
   ```bash
   # Executar com core dump
   ulimit -c unlimited
   ./servidor_c_configurable 8000
   gdb ./servidor_c_configurable core
   ```

3. **Too many open files**
   ```bash
   # Verificar limite atual
   ulimit -n
   
   # Aumentar temporariamente
   ulimit -n 65536
   ```

4. **Port already in use**
   ```bash
   # Encontrar processo
   sudo netstat -tlnp | grep :8000
   sudo kill -9 <PID>
   
   # Usar SO_REUSEADDR
   setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(yes));
   ```

### Debugging de Performance

```bash
# CPU usage em tempo real
top -p $(pgrep servidor_c)

# I/O statistics
iostat -x 1

# Network connections
ss -tuln | grep :8000

# Memory usage
pmap $(pgrep servidor_c)

# System calls frequency
strace -c -p $(pgrep servidor_c)
```

### Logs de Debug

```c
// Habilitar debug em tempo de compilação
#ifdef DEBUG
    #define DEBUG_LOG(fmt, ...) \
        fprintf(stderr, "[DEBUG] %s:%d " fmt "\n", __FILE__, __LINE__, ##__VA_ARGS__)
#else
    #define DEBUG_LOG(fmt, ...)
#endif

// Usar no código
DEBUG_LOG("Connection from %s:%d", client_ip, client_port);
```

# Pasta applications/servidor-c/

Esta pasta contém as implementações do servidor em linguagem C, utilizadas nos testes de benchmark para comparação de desempenho e análise de diferentes abordagens.

## Arquivos e Funções

- **app.c**: Implementação principal do servidor em C.
  - Funções: inicialização do servidor, escuta de conexões, processamento de requisições, resposta ao cliente.
  - Justificativa: Base para análise de performance e comparação com outras linguagens.

- **app_configurable.c**: Versão configurável do servidor em C, permitindo ajuste dinâmico de parâmetros via variáveis de ambiente ou argumentos.
  - Funções: leitura de configurações, adaptação de comportamento conforme parâmetros.
  - Justificativa: Facilita experimentação e tuning de performance.

- **app_cjson.c**: Versão do servidor com suporte a requisições/respostas em JSON.
  - Funções: serialização/deserialização de dados, integração com clientes que usam JSON.

- **app_simple.c**: Versão simplificada do servidor, útil para testes básicos e validação de infraestrutura.

- **server.c**: Implementação alternativa ou complementar do servidor, podendo conter abordagens específicas de performance ou arquitetura.

- **servidor-c**: Binário compilado do servidor principal.
- **servidor_c_configurable**: Binário compilado da versão configurável.
- **test_compile**: Script ou binário para teste de compilação.
- **obj/**: Diretório de objetos compilados intermediários.

- **Dockerfile**: Define o ambiente de execução do servidor para containerização.
  - Compila o código-fonte, instala dependências e define o entrypoint.

- **Makefile**: Automatiza o processo de compilação dos diferentes modos do servidor.
  - Comandos: `make`, `make clean`, `make configurable`, etc.

- **README.md**: Este arquivo de documentação.

## Como compilar e executar

- Para compilar manualmente (exemplo):
  ```bash
  gcc app.c -o servidor-c -lpthread
  ```
- Para buildar e rodar via Docker:
  ```bash
  docker build -t servidor-c .
  docker run --rm -p 8000:8000 servidor-c
  ```
- Via Docker Compose ou Kubernetes, o build e execução são automáticos.
- Para compilar versões específicas, utilize o Makefile:
  ```bash
  make configurable
  ```

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

Essas mensagens ajudam a monitorar o funcionamento do servidor C durante os testes.
