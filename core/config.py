#!/usr/bin/env python3
"""
CONFIGURAÇÃO GLOBAL DO SISTEMA DE TESTES V6
Sistema totalmente automatizado com Docker Hub e Kubernetes
"""

import os
import psutil
import time
from pathlib import Path
from typing import List, Dict, Any
from core.utils import get_logger

logger = get_logger("core.config")


class SystemConfig:
    """Configuração otimizada do sistema"""
    
    def __init__(
        self,
        max_pods: int = None,
        pod_startup_delay: float = None,
        test_cleanup_delay: float = None,
        cpu_threshold: int = None,
        mem_threshold: int = None,
        min_pods: int = None,
        cpu_cores: int = None,
        min_memory_per_pod: int = None,
        min_cpu_per_pod: int = None
    ):
        # Diretório raiz do projeto (um nível acima de core)
        self.BASE_DIR = Path(__file__).parent.parent.resolve()
        self.APPLICATIONS_DIR = self.BASE_DIR / "applications"
        self.RESULTS_DIR = self.BASE_DIR / "resultados"
        self.GRAPHICS_DIR = self.RESULTS_DIR / "graficos"
        self.CONFIG_DIR = self.BASE_DIR / "config"
        
        # Criar diretórios se não existirem
        self.RESULTS_DIR.mkdir(exist_ok=True)
        self.GRAPHICS_DIR.mkdir(exist_ok=True)
        
        # Docker Hub configuração
        self.DOCKER_USERNAME = os.getenv("DOCKER_USERNAME", "guimsk")  # Parametrizado via env var
        self.DOCKER_REGISTRY = "docker.io"
        
        # Configurações de teste conforme requisitos do professor
        self.LANGUAGES = ["c", "cpp"]
        self.SERVERS = [2, 4, 6, 8, 10]  # Requisito: 2 a 10, incrementando de 2 em 2
        self.CLIENTS = list(range(10, 101, 10))  # Requisito: 10 a 100, incrementando de 10 em 10
        self.MESSAGES = [1, 10, 100, 500, 1000, 10000]  # Requisito: conforme especificação
        self.RUNS_PER_CONFIG = 10  # Requisito: 10 execuções por configuração
        
        # Configurações de rede
        self.BASE_PORT = 8000
        self.TIMEOUT = 60  # Aumentado para 60s
        self.RETRY_ATTEMPTS = 3
        
        # Configurações do Kubernetes
        self.K8S_NAMESPACE = "scalability-test"
        self.K8S_DEPLOYMENT_TIMEOUT = 600  # Aumentado para 10 minutos
        
        # Configurações de paralelismo OTIMIZADAS para máxima velocidade segura
        # Permite sobrescrever via argumentos ou variáveis de ambiente
        cpu_cores = cpu_cores or int(os.getenv("CPU_CORES", psutil.cpu_count(logical=True) or 4))
        available_memory_gb = psutil.virtual_memory().total / 1024**3
        max_pods_env = int(os.getenv("MAX_CONCURRENT_PODS", 0))
        safe_pods = max_pods or max_pods_env or cpu_cores  # Remove limite fixo de 24
        self.MAX_CONCURRENT_PODS = safe_pods
        self.POD_STARTUP_DELAY = pod_startup_delay or float(os.getenv("POD_STARTUP_DELAY", 0.1))
        self.PARALLEL_EXECUTION = True
        self.TEST_CLEANUP_DELAY = test_cleanup_delay or float(os.getenv("TEST_CLEANUP_DELAY", 0.2))
        min_memory_per_pod = min_memory_per_pod or int(os.getenv("MIN_MEMORY_PER_POD", 256))
        min_cpu_per_pod = min_cpu_per_pod or int(os.getenv("MIN_CPU_PER_POD", 100))
        memory_per_pod = max(min_memory_per_pod, int(available_memory_gb * 1024 * 0.7 / self.MAX_CONCURRENT_PODS))
        cpu_per_pod = max(min_cpu_per_pod, int(1000 * 0.7 / self.MAX_CONCURRENT_PODS))
        self.RESOURCE_LIMITS = {
            "cpu": f"{min(cpu_per_pod * 2, 1200)}m",
            "memory": f"{min(memory_per_pod * 2, 2048)}Mi"
        }
        self.RESOURCE_REQUESTS = {
            "cpu": f"{cpu_per_pod}m",
            "memory": f"{memory_per_pod}Mi"
        }
        self.BATCH_SIZE = self.MAX_CONCURRENT_PODS
        self.WORKER_THREADS = self.MAX_CONCURRENT_PODS
        self.ASYNC_OPERATIONS = True
        logger.info(f"Configuração do sistema inicializada para performance máxima segura: {self.MAX_CONCURRENT_PODS} pods.")
        # --- Monitoramento dinâmico de carga ---
        self._dynamic_adjustment_enabled = True
        self._cpu_threshold = cpu_threshold or int(os.getenv("CPU_THRESHOLD", 95))
        self._mem_threshold = mem_threshold or int(os.getenv("MEM_THRESHOLD", 95))
        self._min_pods = min_pods or max(4, cpu_cores // 4)
        self._max_pods = self.MAX_CONCURRENT_PODS
        self._last_adjust = time.time()

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

    def adjust_parallelism(self):
        """Ajusta dinamicamente o paralelismo conforme uso de CPU/RAM"""
        if not self._dynamic_adjustment_enabled:
            return
        import psutil
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory().percent
        now = time.time()
        # Ajuste a cada 5s
        if now - self._last_adjust < 5:
            return
        self._last_adjust = now
        if cpu > self._cpu_threshold or mem > self._mem_threshold:
            if self.MAX_CONCURRENT_PODS > self._min_pods:
                self.MAX_CONCURRENT_PODS = max(self._min_pods, self.MAX_CONCURRENT_PODS - 1)
                self.BATCH_SIZE = self.MAX_CONCURRENT_PODS
                self.WORKER_THREADS = self.MAX_CONCURRENT_PODS
                print(f"⚠️  Reduzindo paralelismo para {self.MAX_CONCURRENT_PODS} devido à carga (CPU={cpu:.1f}%, RAM={mem:.1f}%)")
        elif cpu < self._cpu_threshold - 10 and mem < self._mem_threshold - 10:
            if self.MAX_CONCURRENT_PODS < self._max_pods:
                self.MAX_CONCURRENT_PODS += 1
                self.BATCH_SIZE = self.MAX_CONCURRENT_PODS
                self.WORKER_THREADS = self.MAX_CONCURRENT_PODS
                print(f"🚀 Aumentando paralelismo para {self.MAX_CONCURRENT_PODS} (CPU={cpu:.1f}%, RAM={mem:.1f}%)")
        

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
    print("📊 CONFIGURAÇÃO DE TESTES OTIMIZADA")
    print(f"   Linguagens: {config.LANGUAGES}")
    print(f"   Servidores: {config.SERVERS}")
    print(f"   Clientes: {config.CLIENTS}")
    print(f"   Mensagens: {config.MESSAGES}")
    print(f"   Runs por config: {config.RUNS_PER_CONFIG}")
    print(f"   Total de testes: {config.get_total_tests() * len(config.LANGUAGES)}")
    print()
    print("⚙️  OTIMIZAÇÕES DE ESTABILIDADE")
    print(f"   Max pods simultâneos: {config.MAX_CONCURRENT_PODS}")
    print(f"   Worker threads: {config.WORKER_THREADS}")
    print(f"   Batch size: {config.BATCH_SIZE}")
    print(f"   Startup delay: {config.POD_STARTUP_DELAY}s")
    print(f"   Cleanup delay: {config.TEST_CLEANUP_DELAY}s")
    print(f"   Execução paralela: {config.PARALLEL_EXECUTION}")
    print(f"   Async operations: {config.ASYNC_OPERATIONS}")
    print()
    print("�🐳 CONFIGURAÇÃO DOCKER")
    print(f"   Registry: {config.DOCKER_REGISTRY}")
    print(f"   Username: {config.DOCKER_USERNAME}")
    print()
    print("☸️  CONFIGURAÇÃO KUBERNETES")
    print(f"   Namespace: {config.K8S_NAMESPACE}")
    print(f"   Timeout: {config.K8S_DEPLOYMENT_TIMEOUT}s")
    print(f"   CPU Request: {config.RESOURCE_REQUESTS['cpu']}")
    print(f"   CPU Limit: {config.RESOURCE_LIMITS['cpu']}")
    print(f"   Memory Request: {config.RESOURCE_REQUESTS['memory']}")
    print(f"   Memory Limit: {config.RESOURCE_LIMITS['memory']}")


if __name__ == "__main__":
    print_system_info()
