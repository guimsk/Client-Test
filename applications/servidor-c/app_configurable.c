#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>
#include <signal.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>
#include <time.h>
#include <errno.h>
#include <sys/time.h>
#include <stdint.h>

// CONFIGURAÇÕES ULTRA-OTIMIZADAS V5 - COM PORTA CONFIGURÁVEL
#define DEFAULT_PORT 8000
#define BUFFER_SIZE 4096
#define MAX_CONNECTIONS 2000
#define MAX_THREADS 100
#define SOCKET_TIMEOUT_SEC 30

// Controle thread-safe ultra-otimizado
volatile int servidor_rodando = 1;
volatile int clientes_conectados = 0;
pthread_mutex_t stats_mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t connection_mutex = PTHREAD_MUTEX_INITIALIZER;

// Estatísticas avançadas do servidor
typedef struct {
    volatile int total_connections;
    volatile long long total_messages;
    volatile int active_threads;
    volatile int peak_connections;
    volatile int errors;
    struct timespec start_time;
} ServerStats;

ServerStats server_stats = {0, 0, 0, 0, 0, {0, 0}};

// Estrutura para dados do cliente
typedef struct {
    int socket_cliente;
    struct sockaddr_in endereco_cliente;
    int client_id;
} ClientData;

void signal_handler(int signal) {
    printf("\n🛑 Parando servidor...\n");
    servidor_rodando = 0;
}

void print_stats() {
    pthread_mutex_lock(&stats_mutex);
    printf("📊 [STATS] Conexões: %d | Mensagens: %lld | Threads ativas: %d | Pico: %d | Erros: %d\n",
           server_stats.total_connections, server_stats.total_messages,
           server_stats.active_threads, server_stats.peak_connections, server_stats.errors);
    pthread_mutex_unlock(&stats_mutex);
}

void update_peak_connections() {
    pthread_mutex_lock(&stats_mutex);
    if (clientes_conectados > server_stats.peak_connections) {
        server_stats.peak_connections = clientes_conectados;
    }
    pthread_mutex_unlock(&stats_mutex);
}

void* thread_stats(void* arg) {
    while (servidor_rodando) {
        sleep(5);
        print_stats();
    }
    return NULL;
}

void* tratar_cliente(void* arg) {
    ClientData* client_data = (ClientData*)arg;
    int socket_cliente = client_data->socket_cliente;
    int client_id = client_data->client_id;
    
    char buffer[BUFFER_SIZE];
    
    // Atualizar estatísticas
    pthread_mutex_lock(&stats_mutex);
    server_stats.total_connections++;
    server_stats.active_threads++;
    pthread_mutex_unlock(&stats_mutex);
    
    update_peak_connections();
    
    printf("🔗 Cliente %d conectado de %s:%d\n", 
           client_id, inet_ntoa(client_data->endereco_cliente.sin_addr), 
           ntohs(client_data->endereco_cliente.sin_port));
    
    // Configurar timeout para o socket
    struct timeval timeout;
    timeout.tv_sec = SOCKET_TIMEOUT_SEC;
    timeout.tv_usec = 0;
    setsockopt(socket_cliente, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));
    setsockopt(socket_cliente, SOL_SOCKET, SO_SNDTIMEO, &timeout, sizeof(timeout));
    
    // Configurar TCP_NODELAY para reduzir latência
    int flag = 1;
    setsockopt(socket_cliente, IPPROTO_TCP, TCP_NODELAY, &flag, sizeof(flag));
    
    // Loop de comunicação
    while (servidor_rodando) {
        memset(buffer, 0, BUFFER_SIZE);
        
        // Receber mensagem
        ssize_t bytes_received = recv(socket_cliente, buffer, BUFFER_SIZE - 1, 0);
        
        if (bytes_received <= 0) {
            if (bytes_received == 0) {
                printf("🔌 Cliente %d desconectado\n", client_id);
            } else {
                if (errno != EAGAIN && errno != EWOULDBLOCK) {
                    printf("❌ Erro ao receber dados do cliente %d: %s\n", client_id, strerror(errno));
                    pthread_mutex_lock(&stats_mutex);
                    server_stats.errors++;
                    pthread_mutex_unlock(&stats_mutex);
                }
            }
            break;
        }
        
        // Processar mensagem
        buffer[bytes_received] = '\0';
        
        // Atualizar contador de mensagens
        pthread_mutex_lock(&stats_mutex);
        server_stats.total_messages++;
        pthread_mutex_unlock(&stats_mutex);
        
        // Enviar resposta (echo simples)
        char response[BUFFER_SIZE];
        snprintf(response, sizeof(response), "Echo: %s", buffer);
        
        ssize_t bytes_sent = send(socket_cliente, response, strlen(response), 0);
        if (bytes_sent <= 0) {
            printf("❌ Erro ao enviar resposta para cliente %d: %s\n", client_id, strerror(errno));
            pthread_mutex_lock(&stats_mutex);
            server_stats.errors++;
            pthread_mutex_unlock(&stats_mutex);
            break;
        }
    }
    
    // Cleanup
    close(socket_cliente);
    
    // Atualizar contadores
    pthread_mutex_lock(&connection_mutex);
    clientes_conectados--;
    pthread_mutex_unlock(&connection_mutex);
    
    pthread_mutex_lock(&stats_mutex);
    server_stats.active_threads--;
    pthread_mutex_unlock(&stats_mutex);
    
    free(client_data);
    
    printf("🔌 Thread do cliente %d finalizada\n", client_id);
    
    return NULL;
}

int main(int argc, char* argv[]) {
    int port = DEFAULT_PORT;
    
    // Verificar se a porta foi passada como argumento
    if (argc > 1) {
        port = atoi(argv[1]);
        if (port <= 0 || port > 65535) {
            fprintf(stderr, "❌ Porta inválida: %d. Usando porta padrão %d\n", port, DEFAULT_PORT);
            port = DEFAULT_PORT;
        }
    }
    
    printf("SERVIDOR DE ESCALABILIDADE C - VERSÃO COMPLETA (CONFIGURÁVEL)\n");
    printf("Porta: %d\n", port);
    printf("Max conexões simultâneas: %d\n", MAX_CONNECTIONS);
    printf("Suporte completo a threads: 1 thread por cliente\n");
    printf("Protocolo: Socket ping-pong para testes de escalabilidade\n");
    printf("============================================================\n");
    
    // Inicializar timestamp de início
    clock_gettime(CLOCK_REALTIME, &server_stats.start_time);
    
    // Configurar handlers de sinal
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    signal(SIGPIPE, SIG_IGN); // Ignorar SIGPIPE
    
    // Criar socket servidor
    int socket_servidor = socket(AF_INET, SOCK_STREAM, 0);
    if (socket_servidor < 0) {
        fprintf(stderr, "❌ Erro ao criar socket: %s\n", strerror(errno));
        return 1;
    }
    
    // Configurar reutilização de endereço
    int flag = 1;
    setsockopt(socket_servidor, SOL_SOCKET, SO_REUSEADDR, &flag, sizeof(flag));
    
    // Configurar endereço do servidor
    struct sockaddr_in endereco_servidor;
    memset(&endereco_servidor, 0, sizeof(endereco_servidor));
    endereco_servidor.sin_family = AF_INET;
    endereco_servidor.sin_addr.s_addr = INADDR_ANY;
    endereco_servidor.sin_port = htons(port);
    
    // Bind do socket
    if (bind(socket_servidor, (struct sockaddr*)&endereco_servidor, sizeof(endereco_servidor)) < 0) {
        fprintf(stderr, "❌ Erro no bind: %s\n", strerror(errno));
        close(socket_servidor);
        return 1;
    }
    
    // Começar a escutar
    if (listen(socket_servidor, MAX_CONNECTIONS) < 0) {
        fprintf(stderr, "❌ Erro no listen: %s\n", strerror(errno));
        close(socket_servidor);
        return 1;
    }
    
    printf("🚀 Servidor iniciado na porta %d\n", port);
    printf("⏳ Aguardando conexões...\n");
    
    // Thread para estatísticas
    pthread_t stats_thread;
    pthread_create(&stats_thread, NULL, thread_stats, NULL);
    
    int client_counter = 0;
    
    // Loop principal do servidor
    while (servidor_rodando) {
        struct sockaddr_in endereco_cliente;
        socklen_t tamanho_endereco = sizeof(endereco_cliente);
        
        int socket_cliente = accept(socket_servidor, (struct sockaddr*)&endereco_cliente, &tamanho_endereco);
        
        if (socket_cliente < 0) {
            if (servidor_rodando) {
                fprintf(stderr, "❌ Erro no accept: %s\n", strerror(errno));
                pthread_mutex_lock(&stats_mutex);
                server_stats.errors++;
                pthread_mutex_unlock(&stats_mutex);
            }
            continue;
        }
        
        // Verificar limite de conexões
        if (clientes_conectados >= MAX_CONNECTIONS) {
            printf("⚠️ Limite de conexões atingido. Rejeitando cliente.\n");
            close(socket_cliente);
            continue;
        }
        
        // Atualizar contador de clientes
        pthread_mutex_lock(&connection_mutex);
        clientes_conectados++;
        client_counter++;
        pthread_mutex_unlock(&connection_mutex);
        
        // Criar dados do cliente
        ClientData* client_data = malloc(sizeof(ClientData));
        if (!client_data) {
            fprintf(stderr, "❌ Erro ao alocar memória para cliente\n");
            close(socket_cliente);
            pthread_mutex_lock(&connection_mutex);
            clientes_conectados--;
            pthread_mutex_unlock(&connection_mutex);
            continue;
        }
        
        client_data->socket_cliente = socket_cliente;
        client_data->endereco_cliente = endereco_cliente;
        client_data->client_id = client_counter;
        
        // Criar thread para cliente
        pthread_t thread_cliente;
        if (pthread_create(&thread_cliente, NULL, tratar_cliente, client_data) != 0) {
            fprintf(stderr, "❌ Erro ao criar thread para cliente\n");
            close(socket_cliente);
            free(client_data);
            pthread_mutex_lock(&connection_mutex);
            clientes_conectados--;
            pthread_mutex_unlock(&connection_mutex);
            continue;
        }
        
        // Desanexar thread (ela se limpará automaticamente)
        pthread_detach(thread_cliente);
    }
    
    printf("🛑 Finalizando servidor...\n");
    
    // Aguardar um pouco para threads finalizarem
    sleep(2);
    
    // Finalizar thread de estatísticas
    pthread_join(stats_thread, NULL);
    
    close(socket_servidor);
    
    // Estatísticas finais
    print_stats();
    printf("✅ Servidor finalizado\n");
    
    return 0;
}
