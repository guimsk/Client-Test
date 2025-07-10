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
#include <cstdlib>

// CONFIGURAÇÕES ULTRA-OTIMIZADAS V6 - COM PORTA CONFIGURÁVEL
#define DEFAULT_PORT 8000
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

// Função para processar mensagens do cliente
void processar_cliente(int cliente_socket, sockaddr_in cliente_addr) {
    {
        std::lock_guard<std::mutex> lock(stats_mutex);
        server_stats.total_connections++;
        server_stats.active_threads++;
        clientes_conectados++;
    }
    
    char buffer[BUFFER_SIZE];
    std::string cliente_ip = inet_ntoa(cliente_addr.sin_addr);
    
    std::cout << "✅ Cliente conectado: " << cliente_ip << ":" << ntohs(cliente_addr.sin_port) << std::endl;
    
    try {
        while (servidor_rodando) {
            // Ler tamanho da mensagem (4 bytes)
            uint32_t message_size = 0;
            ssize_t bytes_read = recv(cliente_socket, &message_size, sizeof(message_size), MSG_WAITALL);
            
            if (bytes_read != sizeof(message_size)) {
                break; // Cliente desconectou
            }
            
            message_size = ntohl(message_size); // Converter de network byte order
            
            if (message_size == 0 || message_size > BUFFER_SIZE - 1) {
                break; // Mensagem inválida
            }
            
            // Ler mensagem
            bytes_read = recv(cliente_socket, buffer, message_size, MSG_WAITALL);
            if (bytes_read != static_cast<ssize_t>(message_size)) {
                break;
            }
            
            buffer[message_size] = '\0';
            
            // Processar mensagem (ping-pong)
            std::string response = "pong_" + std::string(buffer);
            uint32_t response_size = htonl(response.length());
            
            // Enviar tamanho da resposta
            if (send(cliente_socket, &response_size, sizeof(response_size), 0) != sizeof(response_size)) {
                break;
            }
            
            // Enviar resposta
            if (send(cliente_socket, response.c_str(), response.length(), 0) != static_cast<ssize_t>(response.length())) {
                break;
            }
            
            {
                std::lock_guard<std::mutex> lock(stats_mutex);
                server_stats.total_messages++;
                total_messages++;
            }
        }
    } catch (const std::exception& e) {
        std::lock_guard<std::mutex> lock(stats_mutex);
        server_stats.errors++;
    }
    
    close(cliente_socket);
    
    {
        std::lock_guard<std::mutex> lock(stats_mutex);
        server_stats.active_threads--;
        clientes_conectados--;
    }
    
    std::cout << "🔌 Cliente desconectado: " << cliente_ip << std::endl;
}

int main(int argc, char* argv[]) {
    int PORT = DEFAULT_PORT;
    
    // Verificar se porta foi fornecida como argumento
    if (argc > 1) {
        PORT = std::atoi(argv[1]);
        if (PORT <= 0 || PORT > 65535) {
            std::cerr << "❌ Porta inválida: " << argv[1] << std::endl;
            return 1;
        }
    }
    
    std::cout << "🚀 SERVIDOR DE ESCALABILIDADE C++ - VERSÃO COMPLETA" << std::endl;
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
    sockaddr_in endereco_servidor;
    memset(&endereco_servidor, 0, sizeof(endereco_servidor));
    endereco_servidor.sin_family = AF_INET;
    endereco_servidor.sin_addr.s_addr = INADDR_ANY;
    endereco_servidor.sin_port = htons(PORT);
    
    // Bind do socket
    if (bind(socketServidor, (sockaddr*)&endereco_servidor, sizeof(endereco_servidor)) < 0) {
        std::cerr << "❌ Erro no bind: " << strerror(errno) << std::endl;
        close(socketServidor);
        return 1;
    }
    
    // Listen
    if (listen(socketServidor, MAX_CONNECTIONS) < 0) {
        std::cerr << "❌ Erro no listen: " << strerror(errno) << std::endl;
        close(socketServidor);
        return 1;
    }
    
    std::cout << "🎯 Servidor escutando na porta " << PORT << "..." << std::endl;
    
    // Thread para estatísticas
    std::thread stats_thread([&]() {
        while (servidor_rodando) {
            std::this_thread::sleep_for(std::chrono::seconds(10));
            if (servidor_rodando) print_stats();
        }
    });
    
    // Loop principal para aceitar conexões
    std::vector<std::thread> client_threads;
    
    while (servidor_rodando) {
        sockaddr_in cliente_addr;
        socklen_t cliente_len = sizeof(cliente_addr);
        
        int cliente_socket = accept(socketServidor, (sockaddr*)&cliente_addr, &cliente_len);
        
        if (cliente_socket < 0) {
            if (servidor_rodando) {
                std::lock_guard<std::mutex> lock(stats_mutex);
                server_stats.errors++;
            }
            continue;
        }
        
        // Configurar socket do cliente para otimização
        int tcp_nodelay = 1;
        setsockopt(cliente_socket, IPPROTO_TCP, TCP_NODELAY, &tcp_nodelay, sizeof(tcp_nodelay));
        
        // Criar thread para processar cliente
        try {
            client_threads.emplace_back(processar_cliente, cliente_socket, cliente_addr);
            
            // Limpar threads finalizadas (detach para evitar acúmulo)
            for (auto it = client_threads.begin(); it != client_threads.end();) {
                if (it->joinable()) {
                    it->detach();
                    it = client_threads.erase(it);
                } else {
                    ++it;
                }
            }
            
        } catch (const std::exception& e) {
            std::cerr << "❌ Erro ao criar thread: " << e.what() << std::endl;
            close(cliente_socket);
            std::lock_guard<std::mutex> lock(stats_mutex);
            server_stats.errors++;
        }
    }
    
    // Cleanup
    close(socketServidor);
    
    // Aguardar threads finalizarem
    for (auto& t : client_threads) {
        if (t.joinable()) {
            t.join();
        }
    }
    
    if (stats_thread.joinable()) {
        stats_thread.join();
    }
    
    std::cout << "\n📊 ESTATÍSTICAS FINAIS:" << std::endl;
    std::cout << "Total de conexões: " << server_stats.total_connections << std::endl;
    std::cout << "Total de mensagens: " << server_stats.total_messages << std::endl;
    std::cout << "Total de erros: " << server_stats.errors << std::endl;
    std::cout << "🏁 Servidor finalizado." << std::endl;
    
    return 0;
}
