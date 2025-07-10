DIRETÓRIO CLIENTE - Aplicação Cliente Python
============================================

DESCRIÇÃO:
Aplicação cliente Python que se conecta aos servidores (C++ ou C) e executa 
testes de performance com múltiplas threads simulando clientes concorrentes.

ARQUIVOS:
---------

app.py
- Aplicação principal do cliente
- Implementa protocolo de comunicação socket
- Gerencia múltiplas threads de clientes
- Coleta métricas de performance
- Salva resultados em CSV

RESPONSABILIDADES:
- Conectar aos servidores via socket TCP
- Simular múltiplos clientes concorrentes
- Enviar mensagens ping-pong configuráveis
- Medir latência e throughput
- Registrar resultados detalhados

Dockerfile
- Imagem Docker para o cliente
- Baseada em Python 3.9-slim
- Instala dependências necessárias
- Configura ambiente de execução
- Otimizada para execução em containers

RESPONSABILIDADES:
- Criar ambiente Python consistente
- Instalar bibliotecas necessárias
- Configurar ponto de entrada
- Otimizar tamanho da imagem

FUNCIONALIDADES DO CLIENTE:
--------------------------

1. CONEXÃO SOCKET:
   - Conecta via TCP ao servidor
   - Suporta configuração de host e porta
   - Trata erros de conexão
   - Implementa timeout de conexão

2. SIMULAÇÃO DE CLIENTES:
   - Cria múltiplas threads concorrentes
   - Cada thread simula um cliente
   - Configura número de clientes via variável
   - Sincronização entre threads

3. PROTOCOLO PING-PONG:
   - Envia mensagens para o servidor
   - Recebe respostas (echo)
   - Configura número de mensagens por cliente
   - Mede tempo de resposta

4. COLETA DE MÉTRICAS:
   - Latência por mensagem
   - Throughput total
   - Taxa de sucesso
   - Tempo total de execução

5. REGISTRO DE RESULTADOS:
   - Salva em arquivo CSV
   - Inclui timestamp de execução
   - Organiza por cenário e linguagem
   - Formato compatível com análise

VARIÁVEIS DE AMBIENTE:
---------------------

SERVER_HOST
- Endereço IP ou hostname do servidor
- Padrão: localhost
- Usado para conexão socket

SERVER_PORT
- Porta TCP do servidor
- Padrão: 5000
- Deve corresponder à porta do servidor

QTD_CLIENTES
- Número de clientes simulados
- Padrão: 10
- Cria esse número de threads

MENSAGENS_POR_CLIENTE
- Quantas mensagens cada cliente envia
- Padrão: 100
- Multiplica a carga de trabalho

SCENARIO_ID
- Identificador único do cenário
- Usado para organização dos resultados
- Facilita análise posterior

SERVER_LANGUAGE
- Linguagem do servidor (cpp ou c)
- Usado para separar resultados
- Permite comparação entre linguagens

RESULTS_DIR
- Diretório para salvar resultados
- Padrão: ./results
- Deve ser mapeado no container

COMO EXECUTAR:
--------------

1. Execução local:
   python app.py

2. Execução Docker:
   docker run -e SERVER_HOST=... -e QTD_CLIENTES=... cliente

3. Execução Kubernetes:
   kubectl apply -f job-cliente.yaml

FORMATO DE SAÍDA:
----------------

O cliente gera arquivos CSV com as seguintes colunas:
- timestamp: Data/hora da execução
- scenario_id: ID do cenário
- client_id: ID do cliente (thread)
- message_id: ID da mensagem
- latency_ms: Latência em milissegundos
- success: Se a mensagem foi bem-sucedida
- server_language: Linguagem do servidor

OBSERVAÇÕES:
-----------

- Implementa retry automático para conexões
- Trata exceções de rede graciosamente
- Otimizado para alta concorrência
- Compatível com Docker e Kubernetes
- Suporta configuração flexível via variáveis
- Gera logs detalhados para debugging
