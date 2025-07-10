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

// Função para criar resposta JSON simples (sem biblioteca)
std::string create_json_response(const std::string& tipo, const std::string& data, 
                                long long timestamp, int message_id) {
    std::ostringstream json;
    json << "{";
    json << "\"tipo\":\"RESPONSE\",";
    json << "\"server_timestamp\":" << std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::system_clock::now().time_since_epoch()).count() << ",";
    json << "\"client_timestamp\":" << timestamp << ",";
    json << "\"message_id\":" << message_id << ",";
    json << "\"data\":\"" << data << "\",";
    json << "\"server_stats\":{";
    json << "\"active_connections\":" << clientes_conectados.load() << ",";
    json << "\"total_messages\":" << total_messages.load();
    json << "}";
    json << "}";
    return json.str();
}

// Função para parsear JSON simples (sem biblioteca)
std::string extract_json_value(const std::string& json, const std::string& key) {
    std::string search_key = "\"" + key + "\":";
    size_t pos = json.find(search_key);
    if (pos == std::string::npos) return "";
    
    pos += search_key.length();
    while (pos < json.length() && (json[pos] == ' ' || json[pos] == '\t')) pos++;
    
    if (pos >= json.length()) return "";
    
    if (json[pos] == '\"') {
        // String value
        pos++;
        size_t end_pos = json.find('\"', pos);
        if (end_pos == std::string::npos) return "";
        return json.substr(pos, end_pos - pos);
    } else {
        // Numeric value
        size_t end_pos = pos;
        while (end_pos < json.length() && json[end_pos] != ',' && json[end_pos] != '}') {
            end_pos++;
        }
        return json.substr(pos, end_pos - pos);
    }
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
            // Parse JSON simples
            std::string tipo = extract_json_value(message_json, "tipo");
            std::string data = extract_json_value(message_json, "data");
            std::string timestamp_str = extract_json_value(message_json, "timestamp");
            
            long long timestamp = 0;
            if (!timestamp_str.empty()) {
                timestamp = std::stoll(timestamp_str);
            }
            
            // Criar resposta baseada no tipo
            std::string response_data;
            if (tipo == "PING") {
                response_data = "PONG";
            } else if (tipo == "ECHO") {
                response_data = data;
            } else if (tipo == "STATS") {
                response_data = "SERVER_STATS";
            } else {
                response_data = "ACK";
            }
            
            // Criar resposta JSON
            std::string response_json = create_json_response(tipo, response_data, timestamp, messages_from_client);
            
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
