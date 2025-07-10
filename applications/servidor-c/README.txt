DIRETÓRIO SERVIDOR-C - Servidor C
==================================

DESCRIÇÃO:
Implementação alternativa do servidor em linguagem C pura que recebe conexões 
de clientes e processa mensagens usando threads POSIX para comparação de 
performance com a versão C++.

ARQUIVOS:
---------

app.c
- Código fonte principal do servidor C
- Implementa servidor TCP socket em C puro
- Usa pthreads para cada cliente
- Processa protocolo ping-pong
- Implementação sem overhead de C++

server.c
- Implementação adicional/alternativa
- Pode conter variações do servidor
- Usado para testes específicos

Dockerfile
- Imagem Docker para servidor C
- Baseada em gcc para compilação C
- Compila código fonte durante build
- Configura ambiente de execução mínimo
- Expõe porta 5000

Makefile
- Script de compilação automatizada
- Define flags de compilação
- Gerencia dependências
- Facilita build reproduzível

README.md
- Documentação específica do servidor C
- Instruções de compilação
- Detalhes de implementação

servidor-c
- Executável compilado
- Resultado da compilação
- Pronto para execução

obj/
- Diretório de objetos compilados
- Arquivos .o intermediários
- Organização do build

RESPONSABILIDADES:
-----------------

app.c:
- Implementar servidor TCP em C puro
- Gerenciar threads POSIX
- Processar protocolo de comunicação
- Otimizar para performance em C

Dockerfile:
- Compilar código C otimizado
- Configurar runtime mínimo
- Expor serviços necessários

Makefile:
- Automatizar processo de build
- Definir flags de otimização
- Gerenciar dependências

FUNCIONALIDADES DO SERVIDOR C:
-----------------------------

1. SERVIDOR TCP POSIX:
   - socket(), bind(), listen() syscalls
   - accept() para novas conexões
   - Configuração de socket options
   - Tratamento de sinais

2. THREADING POSIX:
   - pthread_create() para cada cliente
   - pthread_detach() para cleanup
   - Sincronização com mutexes se necessário
   - Gerenciamento manual de threads

3. PROTOCOLO SIMPLES:
   - recv() para receber dados
   - send() para enviar echo
   - Buffers de tamanho fixo
   - Tratamento de erros de I/O

4. OTIMIZAÇÕES C:
   - Compilação com -O3
   - Uso direto de syscalls
   - Gerenciamento manual de memória
   - Overhead mínimo de runtime

5. ROBUSTEZ:
   - Tratamento de sinais (SIGPIPE, etc)
   - Validação de parâmetros
   - Cleanup de recursos
   - Logs de erro

CARACTERÍSTICAS TÉCNICAS:
------------------------

LINGUAGEM: C99/C11
COMPILADOR: gcc com otimizações (-O3)
THREADING: pthreads (POSIX)
SOCKETS: Berkeley sockets
PERFORMANCE: Máxima eficiência em C

VANTAGENS DO C:
- Controle total sobre recursos
- Overhead mínimo absoluto
- Compilação altamente otimizada
- Previsibilidade de performance
- Compatibilidade máxima

DIFERENÇAS vs C++:
- Sem overhead de classes/objetos
- Gerenciamento manual de memória
- Sem exceptions/RTTI
- Código mais verboso mas direto
- Performance potencialmente superior

COMPILAÇÃO:
----------

Flags principais:
- -std=c99: C99 standard
- -O3: Otimização máxima
- -pthread: Suporte POSIX threads
- -Wall: Todos os warnings
- -Wextra: Warnings extras

Via Makefile:
make clean && make

Via gcc direto:
gcc -std=c99 -O3 -pthread -Wall app.c -o servidor-c

CONFIGURAÇÃO:
------------

PORTA: 5000 (hardcoded)
MAX_CLIENTS: 100 (configurável)
BUFFER_SIZE: 1024 bytes
THREAD_STACK: Default do sistema

PROTOCOLO DE COMUNICAÇÃO:
------------------------

Idêntico ao servidor C++:
1. Accept de conexão TCP
2. Receive de mensagem
3. Send de echo
4. Repetir até desconexão

ESTRUTURAS DE DADOS:
-------------------

Estruturas C simples para:
- Informações do cliente
- Buffers de comunicação
- Configurações do servidor
- Estados de conexão

COMO EXECUTAR:
--------------

1. Compilação e execução local:
   make
   ./servidor-c

2. Execução Docker:
   docker run -p 5000:5000 servidor-c

3. Execução Kubernetes:
   kubectl apply -f k8s-servidor-c.yaml

DEBUGGING:
---------

Ferramentas recomendadas:
- gdb para debugging
- valgrind para memory leaks
- strace para syscalls
- tcpdump para rede

OBSERVAÇÕES:
-----------

- Implementação mais baixo nível que C++
- Potencial para maior performance
- Requer mais cuidado com gerenciamento de recursos
- Ideal para comparação de overhead de linguagens
- Código mais verboso mas mais controlável
- Excelente para benchmarks de performance pura
