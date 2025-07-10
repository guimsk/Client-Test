#include <iostream>
#include <thread>
#include <vector>
#include <cstring>
#include <unistd.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <signal.h>
#include <chrono>
#include <atomic>
#include <mutex>
#include <json/json.h>
#include <string>
#include <sstream>
#include <algorithm>

// CONFIGURAÇÕES ULTRA-OTIMIZADAS V5
#define PORT 8000
#define BUFFER_SIZE 4096
#define MAX_CONNECTIONS 2000
#define MAX_THREADS 100

// Controle thread-safe
std::atomic<bool> servidor_rodando(true);
std::atomic<int> clientes_conectados(0);
std::atomic<int> total_messages(0);
std::mutex stats_mutex;

// Estatísticas do servidor
struct ServerStats {
    int total_connections = 0;
    int total_messages = 0;
    int active_threads = 0;
    int errors = 0;
} server_stats;

void signal_handler(int signal) {
    std::cout << "\n🛑 Parando servidor..." << std::endl;
    servidor_rodando = false;
}

void print_stats() {
    std::lock_guard<std::mutex> lock(stats_mutex);
    std::cout << "📊 [STATS] Conexões: " << server_stats.total_connections 
              << " | Mensagens: " << server_stats.total_messages 
              << " | Threads ativas: " << server_stats.active_threads 
              << " | Erros: " << server_stats.errors << std::endl;
}

uint32_t receive_message_size(int socket) {
    uint32_t size;
    ssize_t bytes_received = recv(socket, &size, sizeof(size), MSG_WAITALL);
    if (bytes_received != sizeof(size)) {
        return 0;
    }
    return ntohl(size);
}

std::string receive_json_message(int socket) {
    // Receber tamanho da mensagem
    uint32_t message_size = receive_message_size(socket);
    if (message_size == 0 || message_size > BUFFER_SIZE) {
        return "";
    }
    
    // Receber mensagem
    std::vector<char> buffer(message_size);
    ssize_t bytes_received = recv(socket, buffer.data(), message_size, MSG_WAITALL);
    
    if (bytes_received != message_size) {
        return "";
    }
    
    return std::string(buffer.data(), message_size);
}

bool send_json_message(int socket, const std::string& message) {
    // Enviar tamanho da mensagem
    uint32_t message_size = htonl(message.length());
    ssize_t bytes_sent = send(socket, &message_size, sizeof(message_size), 0);
    if (bytes_sent != sizeof(message_size)) {
        return false;
    }
    
    // Enviar mensagem
    bytes_sent = send(socket, message.c_str(), message.length(), 0);
    return bytes_sent == message.length();
}

void tratarCliente(int socketCliente, sockaddr_in enderecoCliente) {
    std::string ip = inet_ntoa(enderecoCliente.sin_addr);
    int porta = ntohs(enderecoCliente.sin_port);
    
    // Otimizações de socket para máxima performance
    int flag = 1;
    setsockopt(socketCliente, IPPROTO_TCP, TCP_NODELAY, &flag, sizeof(flag));
    
    // Buffer size otimizado
    int buffer_size = BUFFER_SIZE;
    setsockopt(socketCliente, SOL_SOCKET, SO_RCVBUF, &buffer_size, sizeof(buffer_size));
    setsockopt(socketCliente, SOL_SOCKET, SO_SNDBUF, &buffer_size, sizeof(buffer_size));
    
    // Timeout para evitar clientes ociosos
    struct timeval timeout;
    timeout.tv_sec = 30;
    timeout.tv_usec = 0;
    setsockopt(socketCliente, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));
    setsockopt(socketCliente, SOL_SOCKET, SO_SNDTIMEO, &timeout, sizeof(timeout));
    
    // Atualizar estatísticas
    {
        std::lock_guard<std::mutex> lock(stats_mutex);
        server_stats.total_connections++;
        server_stats.active_threads++;
        clientes_conectados++;
    }
    
    std::cout << "🔌 Cliente conectado: " << ip << ":" << porta 
              << " (Total: " << clientes_conectados.load() << ")" << std::endl;
    
    int messages_from_client = 0;
    auto connection_start = std::chrono::steady_clock::now();
    
    while (servidor_rodando) {
        // Receber mensagem JSON
        std::string message_json = receive_json_message(socketCliente);
        
        if (message_json.empty()) {
            // Erro ou desconexão
            break;
        }
        
        messages_from_client++;
        total_messages++;
        
        try {
            // Parse JSON
            Json::Value root;
            Json::Reader reader;
            
            if (!reader.parse(message_json, root)) {
                // Erro de parsing
                std::lock_guard<std::mutex> lock(stats_mutex);
                server_stats.errors++;
                continue;
            }
            
            // Extrair dados da mensagem
            std::string tipo = root.get("tipo", "UNKNOWN").asString();
            std::string data = root.get("data", "").asString();
            long long timestamp = root.get("timestamp", 0).asInt64();
            
            // Criar resposta JSON
            Json::Value response;
            response["tipo"] = "RESPONSE";
            response["server_timestamp"] = std::chrono::duration_cast<std::chrono::milliseconds>(
                std::chrono::system_clock::now().time_since_epoch()).count();
            response["client_timestamp"] = timestamp;
            response["message_id"] = messages_from_client;
            response["server_stats"]["active_connections"] = clientes_conectados.load();
            response["server_stats"]["total_messages"] = total_messages.load();
            
            // Processamento específico por tipo de mensagem
            if (tipo == "PING") {
                response["data"] = "PONG";
                response["ping_data"] = data;
            } else if (tipo == "ECHO") {
                response["data"] = data;
            } else if (tipo == "STATS") {
                response["data"] = "SERVER_STATS";
                response["server_stats"]["total_connections"] = server_stats.total_connections;
                response["server_stats"]["errors"] = server_stats.errors;
            } else {
                response["data"] = "ACK";
                response["original_data"] = data;
            }
            
            // Converter resposta para string JSON
            Json::StreamWriterBuilder builder;
            builder["indentation"] = "";
            std::string response_json = Json::writeString(builder, response);
            
            // Enviar resposta
            if (!send_json_message(socketCliente, response_json)) {
                break;
            }
            
            // Simulação de processamento adaptativo baseado na carga
            auto current_time = std::chrono::steady_clock::now();
            auto connection_duration = std::chrono::duration_cast<std::chrono::seconds>(
                current_time - connection_start).count();
            
            if (messages_from_client > 1000 || connection_duration > 60) {
                // Alta carga - processamento mínimo
                std::this_thread::sleep_for(std::chrono::microseconds(5));
            } else if (messages_from_client > 100) {
                // Carga média
                std::this_thread::sleep_for(std::chrono::microseconds(10));
            } else if (messages_from_client > 10) {
                // Carga baixa
                std::this_thread::sleep_for(std::chrono::microseconds(20));
            }
            
        } catch (const std::exception& e) {
            // Erro de processamento
            std::lock_guard<std::mutex> lock(stats_mutex);
            server_stats.errors++;
            break;
        }
        
        // Atualizar estatísticas
        {
            std::lock_guard<std::mutex> lock(stats_mutex);
            server_stats.total_messages++;
        }
    }
    
    close(socketCliente);
    
    // Atualizar estatísticas na saída
    {
        std::lock_guard<std::mutex> lock(stats_mutex);
        server_stats.active_threads--;
        clientes_conectados--;
    }
    
    std::cout << "[-] Cliente " << ip << " desconectado (" << messages_from_client 
              << " mensagens processadas)" << std::endl;
}

int main() {
    std::cout << "SERVIDOR DE ESCALABILIDADE C++ - VERSÃO COMPLETA" << std::endl;
    std::cout << "Porta: " << PORT << std::endl;
    std::cout << "Max conexões simultâneas: " << MAX_CONNECTIONS << std::endl;
    std::cout << "Suporte completo a threads: 1 thread por cliente" << std::endl;
    std::cout << "Protocolo: Socket ping-pong para testes de escalabilidade" << std::endl;
    std::cout << "=" << std::string(60, '=') << std::endl;
    
    // Configura handlers de sinal
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    
    // Criar socket servidor
    int socketServidor = socket(AF_INET, SOCK_STREAM, 0);
    if (socketServidor < 0) {
        std::cerr << "❌ Erro ao criar socket: " << strerror(errno) << std::endl;
        return 1;
    }
    
    // Configurar reutilização de endereço
    int flag = 1;
    setsockopt(socketServidor, SOL_SOCKET, SO_REUSEADDR, &flag, sizeof(flag));
    
    // Configurar endereço do servidor
    sockaddr_in enderecoServidor;
    memset(&enderecoServidor, 0, sizeof(enderecoServidor));
    enderecoServidor.sin_family = AF_INET;
    enderecoServidor.sin_addr.s_addr = INADDR_ANY;
    enderecoServidor.sin_port = htons(PORT);
    
    // Bind do socket
    if (bind(socketServidor, (sockaddr*)&enderecoServidor, sizeof(enderecoServidor)) < 0) {
        std::cerr << "❌ Erro no bind: " << strerror(errno) << std::endl;
        close(socketServidor);
        return 1;
    }
    
    // Começar a escutar
    if (listen(socketServidor, MAX_CONNECTIONS) < 0) {
        std::cerr << "❌ Erro no listen: " << strerror(errno) << std::endl;
        close(socketServidor);
        return 1;
    }
    
    std::cout << "🚀 Servidor iniciado na porta " << PORT << std::endl;
    std::cout << "⏳ Aguardando conexões..." << std::endl;
    
    // Thread para estatísticas
    std::thread stats_thread([&]() {
        while (servidor_rodando) {
            std::this_thread::sleep_for(std::chrono::seconds(10));
            if (servidor_rodando) {
                print_stats();
            }
        }
    });
    
    // Vetor para armazenar threads dos clientes
    std::vector<std::thread> client_threads;
    
    // Loop principal do servidor
    while (servidor_rodando) {
        sockaddr_in enderecoCliente;
        socklen_t tamanhoEndereco = sizeof(enderecoCliente);
        
        int socketCliente = accept(socketServidor, (sockaddr*)&enderecoCliente, &tamanhoEndereco);
        
        if (socketCliente < 0) {
            if (servidor_rodando) {
                std::cerr << "❌ Erro no accept: " << strerror(errno) << std::endl;
                std::lock_guard<std::mutex> lock(stats_mutex);
                server_stats.errors++;
            }
            continue;
        }
        
        // Verificar limite de conexões
        if (clientes_conectados >= MAX_CONNECTIONS) {
            std::cout << "⚠️ Limite de conexões atingido. Rejeitando cliente." << std::endl;
            close(socketCliente);
            continue;
        }
        
        // Criar thread para cliente
        client_threads.emplace_back(tratarCliente, socketCliente, enderecoCliente);
        
        // Cleanup de threads finalizadas
        client_threads.erase(
            std::remove_if(client_threads.begin(), client_threads.end(),
                          [](std::thread& t) {
                              if (t.joinable()) {
                                  return false;
                              }
                              return true;
                          }),
            client_threads.end()
        );
    }
    
    std::cout << "🛑 Finalizando servidor..." << std::endl;
    
    // Aguardar threads finalizarem
    for (auto& t : client_threads) {
        if (t.joinable()) {
            t.join();
        }
    }
    
    if (stats_thread.joinable()) {
        stats_thread.join();
    }
    
    close(socketServidor);
    
    // Estatísticas finais
    print_stats();
    std::cout << "✅ Servidor finalizado" << std::endl;
    
    return 0;
}
