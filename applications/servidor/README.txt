DIRETÓRIO SERVIDOR - Servidor C++
=================================

DESCRIÇÃO:
Implementação do servidor em C++ que recebe conexões de clientes e processa
mensagens de teste usando threads para suportar múltiplos clientes simultâneos.

ARQUIVOS:
---------

app.cpp
- Código fonte principal do servidor C++
- Implementa servidor TCP socket
- Usa threads para cada cliente
- Processa protocolo ping-pong
- Otimizado para performance

RESPONSABILIDADES:
- Aceitar conexões TCP de clientes
- Criar thread dedicada para cada cliente
- Processar mensagens ping-pong
- Retornar echo das mensagens recebidas
- Gerenciar recursos e cleanup

Dockerfile
- Imagem Docker para servidor C++
- Baseada em gcc para compilação
- Compila código fonte durante build
- Configura ambiente de execução
- Expõe porta 5000

RESPONSABILIDADES:
- Fornecer ambiente de compilação C++
- Compilar código fonte otimizado
- Configurar runtime mínimo
- Expor porta do servidor

FUNCIONALIDADES DO SERVIDOR C++:
-------------------------------

1. SERVIDOR TCP:
   - Bind na porta 5000
   - Listen para conexões
   - Accept múltiplas conexões
   - Configuração de socket

2. GERENCIAMENTO DE THREADS:
   - Thread principal para accept
   - Thread separada para cada cliente
   - Detach de threads para cleanup automático
   - Sincronização thread-safe

3. PROTOCOLO DE COMUNICAÇÃO:
   - Recebe mensagens dos clientes
   - Processa dados recebidos
   - Envia echo de volta
   - Trata desconexões graciosamente

4. OTIMIZAÇÕES DE PERFORMANCE:
   - Compilação com flags de otimização
   - Uso eficiente de memória
   - Operações I/O não-bloqueantes
   - Reutilização de recursos

5. TRATAMENTO DE ERROS:
   - Validação de dados recebidos
   - Tratamento de exceções
   - Logs de erro apropriados
   - Cleanup de recursos

CARACTERÍSTICAS TÉCNICAS:
------------------------

LINGUAGEM: C++17
COMPILADOR: g++ com otimizações (-O3)
THREADING: std::thread (C++11)
SOCKETS: Berkeley sockets (POSIX)
PERFORMANCE: Otimizado para baixa latência

VANTAGENS DO C++:
- Compilação nativa para máquina
- Gerenciamento manual de memória
- Overhead mínimo do runtime
- Otimizações avançadas do compilador
- Performance previsível

PROTOCOLO DE COMUNICAÇÃO:
------------------------

1. Cliente conecta via TCP
2. Cliente envia mensagem
3. Servidor recebe e processa
4. Servidor envia echo de volta
5. Repete até cliente desconectar

FORMATO DAS MENSAGENS:
- Texto simples via socket
- Sem protocolo complexo
- Echo exato do recebido
- Tratamento de buffers

CONFIGURAÇÃO:
------------

PORTA: 5000 (padrão)
BACKLOG: 128 conexões pendentes
BUFFER: 1024 bytes por mensagem
TIMEOUT: Configurável via socket options

COMPILAÇÃO:
----------

Flags de compilação usadas:
- -std=c++17: C++17 standard
- -O3: Otimização máxima
- -pthread: Suporte a threads
- -Wall: Avisos habilitados

Comando de compilação:
g++ -std=c++17 -O3 -pthread -Wall app.cpp -o servidor

COMO EXECUTAR:
--------------

1. Compilação local:
   g++ -o servidor app.cpp -pthread
   ./servidor

2. Execução Docker:
   docker run -p 5000:5000 servidor

3. Execução Kubernetes:
   kubectl apply -f k8s-servidor.yaml

LOGS E DEBUGGING:
----------------

O servidor produz logs para:
- Conexões aceitas
- Clientes conectados/desconectados
- Mensagens processadas
- Erros de comunicação

OBSERVAÇÕES:
-----------

- Otimizado para máxima performance
- Usa recursos mínimos do sistema
- Suporta alta concorrência
- Implementação robusta e estável
- Compatível com ambiente containerizado
- Adequado para benchmarks de performance
