#!/usr/bin/env python3
"""
CONFIGURAÇÃO GLOBAL DO SISTEMA DE TESTES V6
Sistema totalmente automatizado com Docker Hub e Kubernetes
"""

import os
import psutil
from pathlib import Path
from typing import List, Dict, Any


class SystemConfig:
    """Configuração otimizada do sistema"""
    
    def __init__(self):
        # Diretórios base
        self.BASE_DIR = Path(__file__).parent
        self.APPLICATIONS_DIR = self.BASE_DIR / "applications"
        self.RESULTS_DIR = self.BASE_DIR / "resultados"
        self.GRAPHICS_DIR = self.RESULTS_DIR / "graficos"
        self.CONFIG_DIR = self.BASE_DIR / "config"
        
        # Criar diretórios se não existirem
        self.RESULTS_DIR.mkdir(exist_ok=True)
        self.GRAPHICS_DIR.mkdir(exist_ok=True)
        
        # Docker Hub configuração
        self.DOCKER_USERNAME = "guimsk"  # Seu username real do Docker Hub
        self.DOCKER_REGISTRY = "docker.io"
        
        # Configurações de teste conforme requisitos do professor
        self.LANGUAGES = ["c", "cpp"]
        self.SERVERS = [2, 4, 6, 8, 10]  # Requisito: 2 a 10, incrementando de 2 em 2
        self.CLIENTS = list(range(10, 101, 10))  # Requisito: 10 a 100, incrementando de 10 em 10
        self.MESSAGES = [1, 10, 100, 500, 1000, 10000]  # Requisito: conforme especificação
        self.RUNS_PER_CONFIG = 10  # Requisito: 10 execuções por configuração
        
        # Configurações de rede
        self.BASE_PORT = 8000
        self.TIMEOUT = 30
        self.RETRY_ATTEMPTS = 3
        
        # Configurações do Kubernetes
        self.K8S_NAMESPACE = "scalability-test"
        self.K8S_DEPLOYMENT_TIMEOUT = 300  # 5 minutos
        
        # Configurações de paralelismo otimizadas
        self.MAX_CONCURRENT_PODS = 8  # Máximo de pods simultâneos
        self.POD_STARTUP_DELAY = 2    # Delay entre startups (segundos)
        self.PARALLEL_EXECUTION = True  # Execução paralela de testes
        self.TEST_CLEANUP_DELAY = 5   # Delay para limpeza entre testes
        
        # Configurações de recursos otimizadas para máquina com 12 cores / 11GB RAM
        self.RESOURCE_LIMITS = {
            "cpu": "1000m",      # 1 core por pod (máximo)
            "memory": "512Mi"    # 512MB por pod
        }
        
        self.RESOURCE_REQUESTS = {
            "cpu": "200m",       # 0.2 cores por pod (mínimo)
            "memory": "256Mi"    # 256MB por pod
        }
    
    def get_test_combinations(self) -> List[Dict[str, Any]]:
        """Gerar combinações de teste"""
        combinations = []
        for servers in self.SERVERS:
            for clients in self.CLIENTS:
                for messages in self.MESSAGES:
                    combinations.append({
                        "servers": servers,
                        "clients": clients,
                        "messages": messages
                    })
        return combinations
    
    def get_total_tests(self) -> int:
        """Calcular total de testes"""
        return len(self.get_test_combinations()) * self.RUNS_PER_CONFIG
    
    def get_docker_image_name(self, component: str, language: str = None) -> str:
        """Gerar nome da imagem Docker"""
        if component == "cliente":
            return f"{self.DOCKER_USERNAME}/cliente:latest"
        elif component == "servidor":
            if language == "c":
                return f"{self.DOCKER_USERNAME}/servidor-c:latest"
            elif language == "cpp":
                return f"{self.DOCKER_USERNAME}/servidor-cpp:latest"
            else:
                return f"{self.DOCKER_USERNAME}/servidor-c:latest"
        else:
            # Fallback para componentes não conhecidos
            if language:
                return f"{self.DOCKER_USERNAME}/{component}-{language}:latest"
            return f"{self.DOCKER_USERNAME}/{component}:latest"


def get_config() -> SystemConfig:
    """Obter configuração do sistema"""
    return SystemConfig()


def print_system_info():
    """Imprimir informações do sistema"""
    config = get_config()
    
    print("🖥️  INFORMAÇÕES DO SISTEMA")
    print(f"   CPU: {psutil.cpu_count()} cores")
    print(f"   RAM: {psutil.virtual_memory().total / 1024**3:.1f} GB")
    print(f"   Disco: {psutil.disk_usage('/').total / 1024**3:.1f} GB")
    print()
    print("📊 CONFIGURAÇÃO DE TESTES")
    print(f"   Linguagens: {config.LANGUAGES}")
    print(f"   Servidores: {config.SERVERS}")
    print(f"   Clientes: {config.CLIENTS}")
    print(f"   Mensagens: {config.MESSAGES}")
    print(f"   Runs por config: {config.RUNS_PER_CONFIG}")
    print(f"   Total de testes: {config.get_total_tests() * len(config.LANGUAGES)}")
    print()
    print("🐳 CONFIGURAÇÃO DOCKER")
    print(f"   Registry: {config.DOCKER_REGISTRY}")
    print(f"   Username: {config.DOCKER_USERNAME}")
    print()
    print("☸️  CONFIGURAÇÃO KUBERNETES")
    print(f"   Namespace: {config.K8S_NAMESPACE}")
    print(f"   Timeout: {config.K8S_DEPLOYMENT_TIMEOUT}s")
    print(f"   CPU Limit: {config.RESOURCE_LIMITS['cpu']}")
    print(f"   Memory Limit: {config.RESOURCE_LIMITS['memory']}")


if __name__ == "__main__":
    print_system_info()
