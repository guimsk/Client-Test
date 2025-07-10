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

// CONFIGURAÇÕES ULTRA-OTIMIZADAS V5
#define PORT 8000
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

// Função para extrair valor de JSON simples (sem biblioteca)
char* extract_json_value(const char* json, const char* key, char* buffer, size_t buffer_size) {
    char search_key[256];
    snprintf(search_key, sizeof(search_key), "\"%s\":", key);
    
    char* pos = strstr(json, search_key);
    if (!pos) return NULL;
    
    pos += strlen(search_key);
    while (*pos == ' ' || *pos == '\t') pos++;
    
    if (*pos == '\"') {
        // String value
        pos++;
        char* end_pos = strchr(pos, '\"');
        if (!end_pos) return NULL;
        
        size_t len = end_pos - pos;
        if (len >= buffer_size) len = buffer_size - 1;
        strncpy(buffer, pos, len);
        buffer[len] = '\0';
        return buffer;
    } else {
        // Numeric value
        char* end_pos = pos;
        while (*end_pos && *end_pos != ',' && *end_pos != '}') end_pos++;
        
        size_t len = end_pos - pos;
        if (len >= buffer_size) len = buffer_size - 1;
        strncpy(buffer, pos, len);
        buffer[len] = '\0';
        return buffer;
    }
}

// Função para criar resposta JSON simples (sem biblioteca)
int create_json_response(char* buffer, size_t buffer_size, const char* tipo, const char* data, 
                        long long timestamp, int message_id) {
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    long long server_timestamp = ts.tv_sec * 1000LL + ts.tv_nsec / 1000000LL;
    
    return snprintf(buffer, buffer_size,
        "{\"tipo\":\"RESPONSE\",\"server_timestamp\":%lld,\"client_timestamp\":%lld,"
        "\"message_id\":%d,\"data:\"%s\",\"server_stats\":{\"active_connections\":%d,"
        "\"total_messages\":%lld}}",
        server_timestamp, timestamp, message_id, data, clientes_conectados, server_stats.total_messages);
}

uint32_t receive_message_size(int socket) {
    uint32_t size;
    ssize_t bytes_received = recv(socket, &size, sizeof(size), MSG_WAITALL);
    if (bytes_received != sizeof(size)) {
        return 0;
    }
    return ntohl(size);
}

int receive_json_message(int socket, char* buffer, size_t buffer_size) {
    // Receber tamanho da mensagem
    uint32_t message_size = receive_message_size(socket);
    if (message_size == 0 || message_size >= buffer_size) {
        return -1;
    }
    
    // Receber mensagem
    ssize_t bytes_received = recv(socket, buffer, message_size, MSG_WAITALL);
    if (bytes_received != message_size) {
        return -1;
    }
    
    buffer[message_size] = '\0';
    return message_size;
}

int send_json_message(int socket, const char* message) {
    size_t message_len = strlen(message);
    
    // Enviar tamanho da mensagem
    uint32_t message_size = htonl(message_len);
    ssize_t bytes_sent = send(socket, &message_size, sizeof(message_size), 0);
    if (bytes_sent != sizeof(message_size)) {
        return -1;
    }
    
    // Enviar mensagem
    bytes_sent = send(socket, message, message_len, 0);
    return (bytes_sent == message_len) ? 0 : -1;
}

void* tratar_cliente(void* arg) {
    ClientData* client_data = (ClientData*)arg;
    int socket_cliente = client_data->socket_cliente;
    struct sockaddr_in endereco_cliente = client_data->endereco_cliente;
    int client_id = client_data->client_id;
    
    char* ip = inet_ntoa(endereco_cliente.sin_addr);
    int porta = ntohs(endereco_cliente.sin_port);
    
    // Otimizações de socket para máxima performance
    int flag = 1;
    setsockopt(socket_cliente, IPPROTO_TCP, TCP_NODELAY, &flag, sizeof(flag));
    
    // Buffer size otimizado
    int buffer_size = BUFFER_SIZE;
    setsockopt(socket_cliente, SOL_SOCKET, SO_RCVBUF, &buffer_size, sizeof(buffer_size));
    setsockopt(socket_cliente, SOL_SOCKET, SO_SNDBUF, &buffer_size, sizeof(buffer_size));
    
    // Timeout para evitar clientes ociosos
    struct timeval timeout;
    timeout.tv_sec = SOCKET_TIMEOUT_SEC;
    timeout.tv_usec = 0;
    setsockopt(socket_cliente, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));
    setsockopt(socket_cliente, SOL_SOCKET, SO_SNDTIMEO, &timeout, sizeof(timeout));
    
    // Atualizar estatísticas
    pthread_mutex_lock(&stats_mutex);
    server_stats.total_connections++;
    server_stats.active_threads++;
    if (clientes_conectados > server_stats.peak_connections) {
        server_stats.peak_connections = clientes_conectados;
    }
    pthread_mutex_unlock(&stats_mutex);
    
    printf("🔌 Cliente %d conectado: %s:%d (Total: %d)\n", client_id, ip, porta, clientes_conectados);
    
    int messages_from_client = 0;
    char buffer[BUFFER_SIZE];
    char response_buffer[BUFFER_SIZE];
    char tipo_buffer[256], data_buffer[256], timestamp_buffer[64];
    
    struct timespec connection_start;
    clock_gettime(CLOCK_MONOTONIC, &connection_start);
    
    while (servidor_rodando) {
        // Receber mensagem JSON
        int message_len = receive_json_message(socket_cliente, buffer, BUFFER_SIZE);
        
        if (message_len <= 0) {
            // Erro ou desconexão
            break;
        }
        
        messages_from_client++;
        __sync_add_and_fetch(&server_stats.total_messages, 1);
        
        // Parse JSON simples
        char* tipo = extract_json_value(buffer, "tipo", tipo_buffer, sizeof(tipo_buffer));
        char* data = extract_json_value(buffer, "data", data_buffer, sizeof(data_buffer));
        char* timestamp_str = extract_json_value(buffer, "timestamp", timestamp_buffer, sizeof(timestamp_buffer));
        
        long long timestamp = 0;
        if (timestamp_str) {
            timestamp = strtoll(timestamp_str, NULL, 10);
        }
        
        // Criar resposta baseada no tipo
        const char* response_data;
        if (tipo && strcmp(tipo, "PING") == 0) {
            response_data = "PONG";
        } else if (tipo && strcmp(tipo, "ECHO") == 0) {
            response_data = data ? data : "ECHO";
        } else if (tipo && strcmp(tipo, "STATS") == 0) {
            response_data = "SERVER_STATS";
        } else {
            response_data = "ACK";
        }
        
        // Criar resposta JSON
        create_json_response(response_buffer, BUFFER_SIZE, tipo ? tipo : "UNKNOWN", 
                           response_data, timestamp, messages_from_client);
        
        // Enviar resposta
        if (send_json_message(socket_cliente, response_buffer) < 0) {
            break;
        }
        
        // Simulação de processamento adaptativo baseado na carga
        struct timespec current_time;
        clock_gettime(CLOCK_MONOTONIC, &current_time);
        long connection_duration = current_time.tv_sec - connection_start.tv_sec;
        
        if (messages_from_client > 1000 || connection_duration > 60) {
            // Alta carga - processamento mínimo
            usleep(5);
        } else if (messages_from_client > 100) {
            // Carga média
            usleep(10);
        } else if (messages_from_client > 10) {
            // Carga baixa
            usleep(20);
        }
    }
    
    close(socket_cliente);
    
    // Atualizar estatísticas na saída
    pthread_mutex_lock(&connection_mutex);
    clientes_conectados--;
    pthread_mutex_unlock(&connection_mutex);
    
    pthread_mutex_lock(&stats_mutex);
    server_stats.active_threads--;
    pthread_mutex_unlock(&stats_mutex);
    
    printf("[-] Cliente %d %s desconectado (%d mensagens processadas)\n", 
           client_id, ip, messages_from_client);
    
    free(client_data);
    return NULL;
}

void* thread_stats(void* arg) {
    while (servidor_rodando) {
        sleep(10);
        if (servidor_rodando) {
            print_stats();
        }
    }
    return NULL;
}

int main() {
    printf("SERVIDOR DE ESCALABILIDADE C - VERSÃO COMPLETA\n");
    printf("Porta: %d\n", PORT);
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
    endereco_servidor.sin_port = htons(PORT);
    
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
    
    printf("🚀 Servidor iniciado na porta %d\n", PORT);
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
