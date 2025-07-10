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

bool send_message_size(int socket, uint32_t size) {
    uint32_t network_size = htonl(size);
    ssize_t bytes_sent = send(socket, &network_size, sizeof(network_size), 0);
    return bytes_sent == sizeof(network_size);
}

std::string receive_json_message(int socket) {
    // Receber tamanho da mensagem
    uint32_t message_size = receive_message_size(socket);
    if (message_size == 0 || message_size > BUFFER_SIZE) {
        return "";
    }
    
    // Receber mensagem
    char buffer[BUFFER_SIZE];
    ssize_t bytes_received = recv(socket, buffer, message_size, MSG_WAITALL);
    if (bytes_received != message_size) {
        return "";
    }
    
    buffer[bytes_received] = '\0';
    return std::string(buffer);
}

bool send_json_response(int socket, const std::string& response) {
    uint32_t response_size = response.length();
    
    // Enviar tamanho
    if (!send_message_size(socket, response_size)) {
        return false;
    }
    
    // Enviar resposta
    ssize_t bytes_sent = send(socket, response.c_str(), response_size, 0);
    return bytes_sent == response_size;
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
            
            // Extrair dados
            int client_id = root.get("client_id", 0).asInt();
            std::string message = root.get("message", "").asString();
            double timestamp = root.get("timestamp", 0.0).asDouble();
            int sequence = root.get("sequence", 0).asInt();
            
            // Log otimizado (reduzido para performance)
            if (messages_from_client <= 5 || messages_from_client % 1000 == 0) {
                std::cout << "📨 " << ip << " (#" << messages_from_client << "): " 
                          << "client_" << client_id << " seq_" << sequence << std::endl;
            }
            
            // Criar resposta JSON
            Json::Value response;
            response["status"] = "ok";
            response["client_id"] = client_id;
            response["original_message"] = message;
            response["sequence"] = sequence;
            response["server_timestamp"] = std::chrono::duration_cast<std::chrono::milliseconds>(
                std::chrono::system_clock::now().time_since_epoch()
            ).count() / 1000.0;
            response["processed_by"] = "cpp_server";
            
            // Serializar resposta
            Json::StreamWriterBuilder builder;
            builder["indentation"] = "";
            std::string response_json = Json::writeString(builder, response);
            
            // Enviar resposta
            if (!send_json_response(socketCliente, response_json)) {
                std::cout << "⚠️  Erro enviando resposta para " << ip << std::endl;
                std::lock_guard<std::mutex> lock(stats_mutex);
                server_stats.errors++;
                break;
            }
            
            // Atualizar estatísticas
            {
                std::lock_guard<std::mutex> lock(stats_mutex);
                server_stats.total_messages++;
            }
            
        } catch (const std::exception& e) {
            std::cout << "❌ Erro processando mensagem de " << ip << ": " << e.what() << std::endl;
            std::lock_guard<std::mutex> lock(stats_mutex);
            server_stats.errors++;
            continue;
        }
    }
    
    // Cleanup
    close(socketCliente);
    
    auto connection_end = std::chrono::steady_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::seconds>(connection_end - connection_start);
    
    std::cout << "🔌 Cliente " << ip << " desconectado após " << duration.count() 
              << "s (" << messages_from_client << " mensagens)" << std::endl;
    
    // Atualizar estatísticas
    {
        std::lock_guard<std::mutex> lock(stats_mutex);
        server_stats.active_threads--;
        clientes_conectados--;
    }
}

int main() {
    std::cout << "🚀 SERVIDOR C++ ULTRA-OTIMIZADO V5" << std::endl;
    std::cout << "📡 Porta: " << PORT << std::endl;
    std::cout << "📊 Buffer: " << BUFFER_SIZE << " bytes" << std::endl;
    std::cout << "🔗 Max conexões: " << MAX_CONNECTIONS << std::endl;
    std::cout << "🧵 Max threads: " << MAX_THREADS << std::endl;
    std::cout << "=" << std::string(50, '=') << std::endl;
    
    // Configurar signal handler
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    
    // Criar socket
    int socketServidor = socket(AF_INET, SOCK_STREAM, 0);
    if (socketServidor == -1) {
        std::cerr << "❌ Erro criando socket" << std::endl;
        return 1;
    }
    
    // Otimizações de socket
    int opt = 1;
    setsockopt(socketServidor, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
    setsockopt(socketServidor, SOL_SOCKET, SO_REUSEPORT, &opt, sizeof(opt));
    
    // Configurar endereço
    sockaddr_in enderecoServidor;
    enderecoServidor.sin_family = AF_INET;
    enderecoServidor.sin_addr.s_addr = INADDR_ANY;
    enderecoServidor.sin_port = htons(PORT);
    
    // Bind
    if (bind(socketServidor, (sockaddr*)&enderecoServidor, sizeof(enderecoServidor)) == -1) {
        std::cerr << "❌ Erro no bind" << std::endl;
        close(socketServidor);
        return 1;
    }
    
    // Listen
    if (listen(socketServidor, MAX_CONNECTIONS) == -1) {
        std::cerr << "❌ Erro no listen" << std::endl;
        close(socketServidor);
        return 1;
    }
    
    std::cout << "✅ Servidor iniciado e aguardando conexões..." << std::endl;
    
    // Thread para estatísticas
    std::thread stats_thread([]() {
        while (servidor_rodando) {
            std::this_thread::sleep_for(std::chrono::seconds(10));
            if (servidor_rodando) {
                print_stats();
            }
        }
    });
    
    // Pool de threads para clientes
    std::vector<std::thread> client_threads;
    
    while (servidor_rodando) {
        sockaddr_in enderecoCliente;
        socklen_t tamanhoEndereco = sizeof(enderecoCliente);
        
        int socketCliente = accept(socketServidor, (sockaddr*)&enderecoCliente, &tamanhoEndereco);
        
        if (socketCliente == -1) {
            if (servidor_rodando) {
                std::cerr << "⚠️  Erro no accept" << std::endl;
            }
            continue;
        }
        
        // Verificar limite de threads
        if (server_stats.active_threads >= MAX_THREADS) {
            std::cout << "⚠️  Limite de threads atingido, rejeitando conexão" << std::endl;
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
            
            // Simula processamento adaptativo baseado na carga
            auto current_time = std::chrono::steady_clock::now();
            auto connection_duration = std::chrono::duration_cast<std::chrono::seconds>(
                current_time - connection_start).count();
            
            // Processamento adaptativo baseado na duração da conexão e número de mensagens
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
            
        } else if (mensagem_recebida.find("PING") == 0) {
            // Compatibilidade com protocolo básico
            auto now = std::chrono::system_clock::now();
            auto timestamp = std::chrono::duration_cast<std::chrono::milliseconds>(
                now.time_since_epoch()).count();
            resposta = "PONG-" + mensagem_recebida + "-" + std::to_string(timestamp);
        } else {
            // Resposta genérica para mensagens que não são PING
            resposta = "ACK-" + mensagem_recebida;
        }
        
        send(socketCliente, resposta.c_str(), resposta.length(), 0);
        
        // Atualiza contador de mensagens
        {
            std::lock_guard<std::mutex> lock(stats_mutex);
            server_stats.total_messages++;
        }
    }
    
    close(socketCliente);
    
    // Atualiza estatísticas na saída
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
    
    // Cria socket
    int socketServidor = socket(AF_INET, SOCK_STREAM, 0);
    if (socketServidor == -1) {
        std::cerr << "Erro criando socket" << std::endl;
        return 1;
    }
    
    // Permite reutilizar endereço
    int opt = 1;
    setsockopt(socketServidor, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
    
    // Configura endereço
    sockaddr_in enderecoServidor;
    enderecoServidor.sin_family = AF_INET;
    enderecoServidor.sin_addr.s_addr = INADDR_ANY;
    enderecoServidor.sin_port = htons(PORT);
    
    // Bind
    if (bind(socketServidor, (sockaddr*)&enderecoServidor, sizeof(enderecoServidor)) == -1) {
        std::cerr << "Erro no bind" << std::endl;
        close(socketServidor);
        return 1;
    }
    
    // Listen
    if (listen(socketServidor, MAX_CONNECTIONS) == -1) {
        std::cerr << "Erro no listen" << std::endl;
        close(socketServidor);
        return 1;
    }
    
    std::cout << "✓ Servidor iniciado na porta " << PORT << std::endl;
    std::cout << "Aguardando conexões... (Ctrl+C para parar)" << std::endl;
    
    // Vector para armazenar threads dos clientes
    std::vector<std::thread> threads;
    
    // Thread para imprimir estatísticas periodicamente
    std::thread stats_thread([&]() {
        while (servidor_rodando) {
            std::this_thread::sleep_for(std::chrono::seconds(30));
            if (servidor_rodando) {
                print_stats();
            }
        }
    });
    
    // Loop principal
    while (servidor_rodando) {
        sockaddr_in enderecoCliente;
        socklen_t tamanhoEndereco = sizeof(enderecoCliente);
        
        int socketCliente = accept(socketServidor, (sockaddr*)&enderecoCliente, &tamanhoEndereco);
        
        if (socketCliente == -1) {
            if (servidor_rodando) {
                std::cerr << "Erro no accept" << std::endl;
            }
            continue;
        }
        
        // Verifica limite de conexões
        if (clientes_conectados >= MAX_CONNECTIONS) {
            std::cout << "[WARN] Limite de conexões atingido, rejeitando cliente" << std::endl;
            close(socketCliente);
            continue;
        }
        
        // Cria thread para tratar cliente
        threads.emplace_back(tratarCliente, socketCliente, enderecoCliente);
        
        // Limpa threads finalizadas (cleanup periódico)
        if (threads.size() > 100) {
            auto it = threads.begin();
            while (it != threads.end()) {
                if (it->joinable()) {
                    ++it;
                } else {
                    it = threads.erase(it);
                }
            }
        }
    }
    
    std::cout << "Finalizando servidor..." << std::endl;
    
    // Para thread de estatísticas
    if (stats_thread.joinable()) {
        stats_thread.join();
    }
    
    // Aguarda todas as threads terminarem
    for (auto& t : threads) {
        if (t.joinable()) {
            t.join();
        }
    }
    
    // Estatísticas finais
    print_stats();
    
    close(socketServidor);
    std::cout << "Servidor finalizado" << std::endl;
    
    return 0;
}
