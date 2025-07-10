#!/usr/bin/env python3
"""
CLIENTE KUBERNETES V6 - TESTES DE ESCALABILIDADE
Cliente otimizado para execução em pods Kubernetes
"""

import socket
import time
import json
import os
import sys
import threading
import statistics
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed


@dataclass
class TestResult:
    """Resultado de teste individual"""
    success: bool
    duration: float
    latency_avg: float
    latency_min: float
    latency_max: float
    latency_median: float
    latency_stddev: float
    throughput: float
    messages_sent: int
    messages_received: int
    server_ports: List[int]
    container_ids: List[str]
    error_message: Optional[str] = None


class KubernetesClient:
    """Cliente otimizado para Kubernetes"""
    
    def __init__(self):
        self.servers = self._parse_servers()
        self.num_clients = int(os.getenv("CLIENTS", "10"))
        self.messages_per_client = int(os.getenv("MESSAGES", "10"))
        self.timeout = int(os.getenv("TIMEOUT", "30"))
        self.parallel_workers = int(os.getenv("PARALLEL_WORKERS", "10"))
        
        # Otimizar threads baseado nos recursos disponíveis
        self.max_workers = min(self.num_clients, self.parallel_workers)
    
    def _parse_servers(self) -> List[Tuple[str, int]]:
        """Parsear servidores do ambiente"""
        servers_env = os.getenv("SERVERS", "")
        servers = []
        
        for server_addr in servers_env.split(","):
            if ":" in server_addr:
                host, port = server_addr.strip().split(":")
                servers.append((host, int(port)))
        
        return servers
    
    def _test_single_client(self, client_id: int) -> Dict[str, Any]:
        """Executar teste de um cliente individual"""
        latencies = []
        messages_sent = 0
        messages_received = 0
        errors = 0
        
        start_time = time.time()
        
        try:
            for message_num in range(self.messages_per_client):
                # Selecionar servidor (round-robin)
                server_host, server_port = self.servers[message_num % len(self.servers)]
                
                # Testar conexão
                msg_start = time.time()
                
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        sock.settimeout(self.timeout)
                        sock.connect((server_host, server_port))
                        
                        # Enviar mensagem
                        message = f"PING_{client_id}_{message_num}"
                        sock.send(message.encode())
                        messages_sent += 1
                        
                        # Receber resposta
                        response = sock.recv(1024).decode()
                        if response.startswith("PONG"):
                            messages_received += 1
                            latency = time.time() - msg_start
                            latencies.append(latency)
                        else:
                            errors += 1
                            
                except Exception as e:
                    errors += 1
                    
        except Exception as e:
            errors += 1
        
        total_time = time.time() - start_time
        
        return {
            "client_id": client_id,
            "messages_sent": messages_sent,
            "messages_received": messages_received,
            "latencies": latencies,
            "errors": errors,
            "total_time": total_time
        }
    
    def run_test(self) -> TestResult:
        """Executar teste completo"""
        print(f"🧪 Iniciando teste: {self.num_clients} clientes, {self.messages_per_client} mensagens")
        print(f"📡 Servidores: {self.servers}")
        
        start_time = time.time()
        all_latencies = []
        total_sent = 0
        total_received = 0
        total_errors = 0
        
        # Executar clientes em paralelo com otimização de recursos
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [
                executor.submit(self._test_single_client, i) 
                for i in range(self.num_clients)
            ]
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    all_latencies.extend(result["latencies"])
                    total_sent += result["messages_sent"]
                    total_received += result["messages_received"]
                    total_errors += result["errors"]
                except Exception as e:
                    total_errors += 1
        
        total_time = time.time() - start_time
        
        # Calcular métricas
        if all_latencies:
            latency_avg = statistics.mean(all_latencies)
            latency_min = min(all_latencies)
            latency_max = max(all_latencies)
            latency_median = statistics.median(all_latencies)
            latency_stddev = statistics.stdev(all_latencies) if len(all_latencies) > 1 else 0.0
            throughput = total_received / total_time if total_time > 0 else 0.0
            success = total_errors == 0 and total_received > 0
        else:
            latency_avg = latency_min = latency_max = latency_median = latency_stddev = 0.0
            throughput = 0.0
            success = False
        
        # Extrair informações dos servidores
        server_ports = [port for _, port in self.servers]
        container_ids = [os.getenv("HOSTNAME", "unknown")]
        
        return TestResult(
            success=success,
            duration=total_time,
            latency_avg=latency_avg,
            latency_min=latency_min,
            latency_max=latency_max,
            latency_median=latency_median,
            latency_stddev=latency_stddev,
            throughput=throughput,
            messages_sent=total_sent,
            messages_received=total_received,
            server_ports=server_ports,
            container_ids=container_ids,
            error_message=None if success else f"Errors: {total_errors}"
        )


def main():
    """Função principal"""
    try:
        client = KubernetesClient()
        result = client.run_test()
        
        # Saída JSON estruturada
        output = asdict(result)
        print(json.dumps(output, indent=2))
        
        return 0 if result.success else 1
        
    except Exception as e:
        error_result = {
            "success": False,
            "error_message": str(e),
            "duration": 0.0,
            "latency_avg": 0.0,
            "latency_min": 0.0,
            "latency_max": 0.0,
            "latency_median": 0.0,
            "latency_stddev": 0.0,
            "throughput": 0.0,
            "messages_sent": 0,
            "messages_received": 0,
            "server_ports": [],
            "container_ids": []
        }
        
        print(json.dumps(error_result, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())
