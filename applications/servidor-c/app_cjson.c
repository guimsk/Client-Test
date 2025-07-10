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
#include <cjson/cJSON.h>
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
    (void)signal;
    printf("\n🛑 Parando servidor C ultra-otimizado...\n");
    servidor_rodando = 0;
}

void print_stats() {
    pthread_mutex_lock(&stats_mutex);
    struct timespec current_time;
    clock_gettime(CLOCK_REALTIME, &current_time);
    double uptime = (current_time.tv_sec - server_stats.start_time.tv_sec) + 
                   (current_time.tv_nsec - server_stats.start_time.tv_nsec) / 1e9;
    
    printf("📊 [STATS] Conexões: %d | Mensagens: %lld | Threads: %d | Peak: %d | Erros: %d | Uptime: %.1fs\n", 
           server_stats.total_connections, 
           server_stats.total_messages, 
           server_stats.active_threads,
           server_stats.peak_connections,
           server_stats.errors,
           uptime);
    pthread_mutex_unlock(&stats_mutex);
}

uint32_t receive_message_size(int socket) {
    uint32_t size;
    ssize_t bytes_received = recv(socket, &size, sizeof(size), MSG_WAITALL);
    if (bytes_received != sizeof(size)) {
        return 0;
    }
    return ntohl(size);
}

int send_message_size(int socket, uint32_t size) {
    uint32_t network_size = htonl(size);
    ssize_t bytes_sent = send(socket, &network_size, sizeof(network_size), 0);
    return bytes_sent == sizeof(network_size);
}

char* receive_json_message(int socket) {
    // Receber tamanho da mensagem
    uint32_t message_size = receive_message_size(socket);
    if (message_size == 0 || message_size > BUFFER_SIZE - 1) {
        return NULL;
    }
    
    // Alocar buffer
    char* buffer = malloc(message_size + 1);
    if (!buffer) {
        return NULL;
    }
    
    // Receber mensagem
    ssize_t bytes_received = recv(socket, buffer, message_size, MSG_WAITALL);
    if (bytes_received != message_size) {
        free(buffer);
        return NULL;
    }
    
    buffer[bytes_received] = '\0';
    return buffer;
}

int send_json_response(int socket, const char* response) {
    uint32_t response_size = strlen(response);
    
    // Enviar tamanho
    if (!send_message_size(socket, response_size)) {
        return 0;
    }
    
    // Enviar resposta
    ssize_t bytes_sent = send(socket, response, response_size, 0);
    return bytes_sent == response_size;
}

void* tratarCliente(void* arg) {
    ClientData* client_data = (ClientData*)arg;
    int socket_cliente = client_data->socket_cliente;
    struct sockaddr_in endereco_cliente = client_data->endereco_cliente;
    int client_id = client_data->client_id;
    
    char* ip = inet_ntoa(endereco_cliente.sin_addr);
    int porta = ntohs(endereco_cliente.sin_port);
    
    // Configurar timeout do socket
    struct timeval timeout;
    timeout.tv_sec = SOCKET_TIMEOUT_SEC;
    timeout.tv_usec = 0;
    setsockopt(socket_cliente, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));
    setsockopt(socket_cliente, SOL_SOCKET, SO_SNDTIMEO, &timeout, sizeof(timeout));
    
    // Otimizações avançadas de socket
    int nodelay = 1;
    setsockopt(socket_cliente, IPPROTO_TCP, TCP_NODELAY, &nodelay, sizeof(nodelay));
    
    int buffer_size = BUFFER_SIZE;
    setsockopt(socket_cliente, SOL_SOCKET, SO_RCVBUF, &buffer_size, sizeof(buffer_size));
    setsockopt(socket_cliente, SOL_SOCKET, SO_SNDBUF, &buffer_size, sizeof(buffer_size));
    
    // Atualizar estatísticas
    pthread_mutex_lock(&stats_mutex);
    server_stats.total_connections++;
    server_stats.active_threads++;
    pthread_mutex_unlock(&stats_mutex);
    
    pthread_mutex_lock(&connection_mutex);
    clientes_conectados++;
    if (clientes_conectados > server_stats.peak_connections) {
        server_stats.peak_connections = clientes_conectados;
    }
    pthread_mutex_unlock(&connection_mutex);
    
    printf("🔌 Cliente conectado: %s:%d (ID: %d, Total: %d)\n", 
           ip, porta, client_id, clientes_conectados);
    
    int messages_from_client = 0;
    struct timespec connection_start;
    clock_gettime(CLOCK_REALTIME, &connection_start);
    
    while (servidor_rodando) {
        // Receber mensagem JSON
        char* message_json = receive_json_message(socket_cliente);
        
        if (!message_json) {
            // Erro ou desconexão
            break;
        }
        
        messages_from_client++;
        
        // Parse JSON
        cJSON *json = cJSON_Parse(message_json);
        if (!json) {
            pthread_mutex_lock(&stats_mutex);
            server_stats.errors++;
            pthread_mutex_unlock(&stats_mutex);
            free(message_json);
            continue;
        }
        
        // Extrair dados
        cJSON *client_id_json = cJSON_GetObjectItem(json, "client_id");
        cJSON *message_json_obj = cJSON_GetObjectItem(json, "message");
        cJSON *timestamp_json = cJSON_GetObjectItem(json, "timestamp");
        cJSON *sequence_json = cJSON_GetObjectItem(json, "sequence");
        
        int msg_client_id = cJSON_IsNumber(client_id_json) ? client_id_json->valueint : 0;
        char *message_text = cJSON_IsString(message_json_obj) ? message_json_obj->valuestring : "";
        double timestamp = cJSON_IsNumber(timestamp_json) ? timestamp_json->valuedouble : 0.0;
        int sequence = cJSON_IsNumber(sequence_json) ? sequence_json->valueint : 0;
        
        // Log otimizado (reduzido para performance)
        if (messages_from_client <= 5 || messages_from_client % 1000 == 0) {
            printf("📨 %s (#%d): client_%d seq_%d\n", 
                   ip, messages_from_client, msg_client_id, sequence);
        }
        
        // Criar resposta JSON
        cJSON *response = cJSON_CreateObject();
        cJSON *status = cJSON_CreateString("ok");
        cJSON *resp_client_id = cJSON_CreateNumber(msg_client_id);
        cJSON *original_msg = cJSON_CreateString(message_text);
        cJSON *resp_sequence = cJSON_CreateNumber(sequence);
        
        // Timestamp do servidor
        struct timespec current_time;
        clock_gettime(CLOCK_REALTIME, &current_time);
        double server_timestamp = current_time.tv_sec + current_time.tv_nsec / 1e9;
        cJSON *server_ts = cJSON_CreateNumber(server_timestamp);
        
        cJSON *processed_by = cJSON_CreateString("c_server");
        
        cJSON_AddItemToObject(response, "status", status);
        cJSON_AddItemToObject(response, "client_id", resp_client_id);
        cJSON_AddItemToObject(response, "original_message", original_msg);
        cJSON_AddItemToObject(response, "sequence", resp_sequence);
        cJSON_AddItemToObject(response, "server_timestamp", server_ts);
        cJSON_AddItemToObject(response, "processed_by", processed_by);
        
        // Serializar resposta
        char *response_string = cJSON_Print(response);
        
        // Enviar resposta
        if (!send_json_response(socket_cliente, response_string)) {
            printf("⚠️  Erro enviando resposta para %s\n", ip);
            pthread_mutex_lock(&stats_mutex);
            server_stats.errors++;
            pthread_mutex_unlock(&stats_mutex);
            
            free(response_string);
            cJSON_Delete(response);
            cJSON_Delete(json);
            free(message_json);
            break;
        }
        
        // Atualizar estatísticas
        pthread_mutex_lock(&stats_mutex);
        server_stats.total_messages++;
        pthread_mutex_unlock(&stats_mutex);
        
        // Cleanup
        free(response_string);
        cJSON_Delete(response);
        cJSON_Delete(json);
        free(message_json);
    }
    
    // Cleanup da conexão
    close(socket_cliente);
    
    struct timespec connection_end;
    clock_gettime(CLOCK_REALTIME, &connection_end);
    double duration = (connection_end.tv_sec - connection_start.tv_sec) + 
                     (connection_end.tv_nsec - connection_start.tv_nsec) / 1e9;
    
    printf("🔌 Cliente %s desconectado após %.1fs (%d mensagens)\n", 
           ip, duration, messages_from_client);
    
    // Atualizar estatísticas finais
    pthread_mutex_lock(&stats_mutex);
    server_stats.active_threads--;
    pthread_mutex_unlock(&stats_mutex);
    
    pthread_mutex_lock(&connection_mutex);
    clientes_conectados--;
    pthread_mutex_unlock(&connection_mutex);
    
    free(client_data);
    return NULL;
}

void* stats_thread(void* arg) {
    (void)arg;
    while (servidor_rodando) {
        sleep(10);
        if (servidor_rodando) {
            print_stats();
        }
    }
    return NULL;
}

int main() {
    printf("🚀 SERVIDOR C ULTRA-OTIMIZADO V5\n");
    printf("📡 Porta: %d\n", PORT);
    printf("📊 Buffer: %d bytes\n", BUFFER_SIZE);
    printf("🔗 Max conexões: %d\n", MAX_CONNECTIONS);
    printf("🧵 Max threads: %d\n", MAX_THREADS);
    printf("%s\n", "==================================================");
    
    // Configurar signal handlers
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    signal(SIGPIPE, SIG_IGN); // Ignorar SIGPIPE
    
    // Inicializar tempo de início
    clock_gettime(CLOCK_REALTIME, &server_stats.start_time);
    
    // Criar socket
    int socket_servidor = socket(AF_INET, SOCK_STREAM, 0);
    if (socket_servidor == -1) {
        perror("❌ Erro criando socket");
        return 1;
    }
    
    // Otimizações de socket
    int opt = 1;
    setsockopt(socket_servidor, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
    setsockopt(socket_servidor, SOL_SOCKET, SO_REUSEPORT, &opt, sizeof(opt));
    
    // Configurar endereço
    struct sockaddr_in endereco_servidor;
    endereco_servidor.sin_family = AF_INET;
    endereco_servidor.sin_addr.s_addr = INADDR_ANY;
    endereco_servidor.sin_port = htons(PORT);
    
    // Bind
    if (bind(socket_servidor, (struct sockaddr*)&endereco_servidor, sizeof(endereco_servidor)) == -1) {
        perror("❌ Erro no bind");
        close(socket_servidor);
        return 1;
    }
    
    // Listen
    if (listen(socket_servidor, MAX_CONNECTIONS) == -1) {
        perror("❌ Erro no listen");
        close(socket_servidor);
        return 1;
    }
    
    printf("✅ Servidor C iniciado e aguardando conexões...\n");
    
    // Thread para estatísticas
    pthread_t stats_tid;
    pthread_create(&stats_tid, NULL, stats_thread, NULL);
    
    int client_counter = 0;
    
    while (servidor_rodando) {
        struct sockaddr_in endereco_cliente;
        socklen_t tamanho_endereco = sizeof(endereco_cliente);
        
        int socket_cliente = accept(socket_servidor, (struct sockaddr*)&endereco_cliente, &tamanho_endereco);
        
        if (socket_cliente == -1) {
            if (servidor_rodando) {
                perror("⚠️  Erro no accept");
            }
            continue;
        }
        
        // Verificar limite de threads
        if (server_stats.active_threads >= MAX_THREADS) {
            printf("⚠️  Limite de threads atingido, rejeitando conexão\n");
            close(socket_cliente);
            continue;
        }
        
        // Criar dados do cliente
        ClientData* client_data = malloc(sizeof(ClientData));
        if (!client_data) {
            printf("❌ Erro alocando memória para cliente\n");
            close(socket_cliente);
            continue;
        }
        
        client_data->socket_cliente = socket_cliente;
        client_data->endereco_cliente = endereco_cliente;
        client_data->client_id = ++client_counter;
        
        // Criar thread para cliente
        pthread_t thread_id;
        if (pthread_create(&thread_id, NULL, tratarCliente, client_data) != 0) {
            printf("❌ Erro criando thread para cliente\n");
            free(client_data);
            close(socket_cliente);
            continue;
        }
        
        // Detach thread para cleanup automático
        pthread_detach(thread_id);
    }
    
    printf("🛑 Finalizando servidor C...\n");
    
    // Aguardar thread de estatísticas
    pthread_join(stats_tid, NULL);
    
    close(socket_servidor);
    
    // Estatísticas finais
    print_stats();
    printf("✅ Servidor C finalizado\n");
    
    return 0;
}
    pthread_mutex_unlock(&connection_mutex);
    
    printf("[+] Cliente conectado: %s:%d (ID: %d, Total: %d)\n", 
           ip, porta, client_id, clientes_conectados);
    
    int messages_from_client = 0;
    
    while (servidor_rodando) {
        memset(buffer, 0, BUFFER_SIZE);
        ssize_t bytes_recebidos = recv(socket_cliente, buffer, BUFFER_SIZE - 1, 0);
        
        if (bytes_recebidos <= 0) {
            if (bytes_recebidos == 0) {
                printf("[INFO] Cliente %s (ID: %d) desconectou normalmente\n", ip, client_id);
            } else if (errno == EWOULDBLOCK || errno == EAGAIN) {
                printf("[TIMEOUT] Cliente %s (ID: %d) timeout\n", ip, client_id);
            } else {
                printf("[ERRO] Erro recebendo dados do cliente %s (ID: %d): %s\n", 
                       ip, client_id, strerror(errno));
            }
            break;
        }
        
        buffer[bytes_recebidos] = '\0';
        messages_from_client++;
        
        // Log apenas para primeiras mensagens (evita spam)
        if (messages_from_client <= 5 || messages_from_client % 1000 == 0) {
            printf("[MSG] %s (ID: %d, #%d): %s\n", ip, client_id, messages_from_client, buffer);
        }
        
        // Protocolo PING-PONG otimizado conforme especificação
        char resposta[BUFFER_SIZE];
        if (strstr(buffer, "PING-") == buffer) {
            // Extrai componentes da mensagem PING-{client_id}-{message_id}-{timestamp}
            char* ping_data = buffer + 5; // Remove "PING-"
            snprintf(resposta, BUFFER_SIZE, "PONG-%s", ping_data);
            
            // Processamento adaptativo baseado na carga
            if (clientes_conectados > 50) {
                // Alta carga: processamento mínimo
                if (messages_from_client % 100 == 0) {
                    usleep(1); // 1 microsegundo ocasional
                }
            } else if (messages_from_client > 1000) {
                // Muitas mensagens: simula processamento
                usleep(5); // 5 microsegundos
            } else if (messages_from_client > 100) {
                usleep(2); // 2 microsegundos
            }
            
        } else if (strstr(buffer, "PING") == buffer) {
            // Compatibilidade com protocolo básico
            struct timespec ts;
            clock_gettime(CLOCK_REALTIME, &ts);
            long timestamp = ts.tv_sec * 1000 + ts.tv_nsec / 1000000;
            snprintf(resposta, BUFFER_SIZE, "PONG-%s-%ld", buffer, timestamp);
        } else {
            // Resposta genérica para mensagens que não são PING
            snprintf(resposta, BUFFER_SIZE, "ACK-%s", buffer);
        }
        
        ssize_t bytes_enviados = send(socket_cliente, resposta, strlen(resposta), 0);
        if (bytes_enviados < 0) {
            printf("[ERRO] Erro enviando resposta para cliente %s (ID: %d): %s\n", 
                   ip, client_id, strerror(errno));
            break;
        }
        
        // Atualiza contador de mensagens de forma otimizada
        if (messages_from_client % 100 == 0) {
            pthread_mutex_lock(&stats_mutex);
            server_stats.total_messages += 100;
            pthread_mutex_unlock(&stats_mutex);
        } else if (messages_from_client == 1) {
            pthread_mutex_lock(&stats_mutex);
            server_stats.total_messages++;
            pthread_mutex_unlock(&stats_mutex);
        }
    }
    
    close(socket_cliente);
    
    // Atualiza estatísticas na saída de forma otimizada
    pthread_mutex_lock(&stats_mutex);
    server_stats.active_threads--;
    // Ajusta contador final de mensagens
    if (messages_from_client % 100 != 0) {
        server_stats.total_messages += (messages_from_client % 100) - 1;
    }
    pthread_mutex_unlock(&stats_mutex);
    
    pthread_mutex_lock(&connection_mutex);
    clientes_conectados--;
    pthread_mutex_unlock(&connection_mutex);
    
    printf("[-] Cliente %s (ID: %d) desconectado (%d mensagens processadas)\n", 
           ip, client_id, messages_from_client);
    
    free(client_data);
    return NULL;
}

void* stats_thread(void* arg) {
    (void)arg; // Suppress unused parameter warning
    while (servidor_rodando) {
        sleep(30);
        if (servidor_rodando) {
            print_stats();
        }
    }
    return NULL;
}

int main() {
    printf("SERVIDOR DE ESCALABILIDADE C - VERSÃO OTIMIZADA\n");
    printf("Porta: %d\n", PORT);
    printf("Max conexões simultâneas: %d\n", MAX_CONNECTIONS);
    printf("Max threads: %d\n", MAX_THREADS);
    printf("Timeout de socket: %ds\n", SOCKET_TIMEOUT_SEC);
    printf("Suporte completo a threads POSIX: 1 thread por cliente\n");
    printf("Protocolo: Socket ping-pong otimizado para testes de escalabilidade\n");
    printf("Linguagem: C (POSIX threads) com otimizações de performance\n");
    printf("============================================================\n");
    
    // Inicializa tempo de início
    clock_gettime(CLOCK_REALTIME, &server_stats.start_time);
    
    // Configura handlers de sinal
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    signal(SIGPIPE, SIG_IGN); // Ignora SIGPIPE
    
    // Cria socket
    int socket_servidor = socket(AF_INET, SOCK_STREAM, 0);
    if (socket_servidor == -1) {
        perror("Erro criando socket");
        return 1;
    }
    
    // Permite reutilizar endereço e otimizações
    int opt = 1;
    if (setsockopt(socket_servidor, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
        perror("Erro configurando SO_REUSEADDR");
        close(socket_servidor);
        return 1;
    }
    
    // Otimizações adicionais do socket
    int keepalive = 1;
    if (setsockopt(socket_servidor, SOL_SOCKET, SO_KEEPALIVE, &keepalive, sizeof(keepalive)) < 0) {
        perror("Aviso: Erro configurando SO_KEEPALIVE");
    }
    
    int backlog_size = MAX_CONNECTIONS;
    if (setsockopt(socket_servidor, SOL_SOCKET, SO_REUSEPORT, &opt, sizeof(opt)) < 0) {
        // SO_REUSEPORT pode não estar disponível em todos os sistemas
        printf("Aviso: SO_REUSEPORT não disponível\n");
    }
    
    // Configura endereço
    struct sockaddr_in endereco_servidor;
    memset(&endereco_servidor, 0, sizeof(endereco_servidor));
    endereco_servidor.sin_family = AF_INET;
    endereco_servidor.sin_addr.s_addr = INADDR_ANY;
    endereco_servidor.sin_port = htons(PORT);
    
    // Bind
    if (bind(socket_servidor, (struct sockaddr*)&endereco_servidor, sizeof(endereco_servidor)) == -1) {
        perror("Erro no bind");
        close(socket_servidor);
        return 1;
    }
    
    // Listen
    if (listen(socket_servidor, MAX_CONNECTIONS) == -1) {
        perror("Erro no listen");
        close(socket_servidor);
        return 1;
    }
    
    printf("✓ Servidor C iniciado na porta %d\n", PORT);
    printf("Aguardando conexões... (Ctrl+C para parar)\n");
    
    // Thread para imprimir estatísticas periodicamente
    pthread_t stats_tid;
    if (pthread_create(&stats_tid, NULL, stats_thread, NULL) != 0) {
        perror("Erro criando thread de estatísticas");
    }
    
    // Array para armazenar threads dos clientes
    pthread_t threads[MAX_THREADS];
    int thread_count = 0;
    int client_counter = 0;
    
    // Loop principal
    while (servidor_rodando) {
        struct sockaddr_in endereco_cliente;
        socklen_t tamanho_endereco = sizeof(endereco_cliente);
        
        int socket_cliente = accept(socket_servidor, (struct sockaddr*)&endereco_cliente, &tamanho_endereco);
        
        if (socket_cliente == -1) {
            if (servidor_rodando) {
                perror("Erro no accept");
            }
            continue;
        }
        
        // Verifica limite de conexões de forma thread-safe
        pthread_mutex_lock(&connection_mutex);
        int current_connections = clientes_conectados;
        pthread_mutex_unlock(&connection_mutex);
        
        if (current_connections >= MAX_CONNECTIONS) {
            printf("[WARN] Limite de conexões atingido (%d), rejeitando cliente\n", current_connections);
            close(socket_cliente);
            continue;
        }
        
        // Verifica limite de threads
        if (thread_count >= MAX_THREADS) {
            printf("[WARN] Limite de threads atingido, rejeitando cliente\n");
            close(socket_cliente);
            continue;
        }
        
        // Prepara dados do cliente
        ClientData* client_data = malloc(sizeof(ClientData));
        if (client_data == NULL) {
            printf("[ERRO] Erro alocando memória para cliente\n");
            close(socket_cliente);
            continue;
        }
        
        client_data->socket_cliente = socket_cliente;
        client_data->endereco_cliente = endereco_cliente;
        client_data->client_id = ++client_counter;
        
        // Cria thread para tratar cliente
        if (pthread_create(&threads[thread_count], NULL, tratarCliente, client_data) != 0) {
            perror("Erro criando thread para cliente");
            free(client_data);
            close(socket_cliente);
            continue;
        }
        
        // Detach da thread para limpeza automática
        pthread_detach(threads[thread_count]);
        thread_count++;
        
        // Limpa threads finalizadas (reset periódico)
        if (thread_count >= MAX_THREADS - 10) {
            printf("[INFO] Resetando contador de threads\n");
            thread_count = 0;
        }
    }
    
    printf("Finalizando servidor C...\n");
    
    // Para thread de estatísticas
    pthread_cancel(stats_tid);
    pthread_join(stats_tid, NULL);
    
    // Aguarda um pouco para threads terminarem
    sleep(2);
    
    // Estatísticas finais
    print_stats();
    
    close(socket_servidor);
    printf("Servidor C finalizado\n");
    
    return 0;
}
