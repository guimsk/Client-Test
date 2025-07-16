#!/usr/bin/env python3
"""
GERENCIADOR DE CONCORRÊNCIA INTELIGENTE
Sistema avançado para controlar paralelismo e evitar sobrecarga de recursos
"""

import time
import psutil
import threading
from typing import Dict, Optional, List
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, Future
import subprocess
import json


@dataclass
class ConcurrencyResourceSnapshot:
    """Snapshot dos recursos do sistema para gerenciamento de concorrência"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    active_pods: int
    load_average: float
    disk_io_percent: float


class ConcurrencyManager:
    """Gerenciador inteligente de concorrência"""
    
    def __init__(self):
        from core.config import get_config
        config = get_config()
        # Limites de recursos sincronizados com config
        self.MAX_CPU_USAGE = 95.0
        self.MAX_MEMORY_USAGE = 95.0
        self.MAX_CONCURRENT_PODS = config.MAX_CONCURRENT_PODS
        self.MAX_CONCURRENT_TESTS = config.MAX_CONCURRENT_PODS
        
        # Controle de execução
        self.active_pods = 0
        self.active_tests = 0
        self.resource_lock = threading.Lock()
        self.resource_history: List[ConcurrencyResourceSnapshot] = []
        
        # Configurações dinâmicas
        self.pod_creation_delay = config.POD_STARTUP_DELAY
        self.test_execution_delay = config.TEST_CLEANUP_DELAY
        self.resource_check_interval = 0.1  # Intervalo de verificação de recursos
        
        # Controle de adaptação dinâmica
        self.consecutive_failures = 0
        self.consecutive_successes = 0
        self.adaptive_mode = True
        
        print("🧠 Gerenciador de Concorrência Inteligente inicializado (sincronizado com config)")
        print(f"   • CPU máximo: {self.MAX_CPU_USAGE}%")
        print(f"   • Memória máxima: {self.MAX_MEMORY_USAGE}%")
        print(f"   • Pods simultâneos: {self.MAX_CONCURRENT_PODS}")
        print(f"   • Testes simultâneos: {self.MAX_CONCURRENT_TESTS}")
    
    def acquire_pod_slot(self, timeout: int = 300) -> bool:
        """Adquirir slot para criação de pod"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            with self.resource_lock:
                # Verificar se há slot disponível
                if (self.active_pods < self.MAX_CONCURRENT_PODS and 
                    self._check_resource_availability()):
                    
                    self.active_pods += 1
                    print(f"🔒 Pod slot adquirido ({self.active_pods}/{self.MAX_CONCURRENT_PODS})")
                    return True
            
            # Aguardar antes de tentar novamente
            time.sleep(self.resource_check_interval)
        
        print(f"⏰ Timeout aguardando slot para pod")
        return False
    
    def release_pod_slot(self):
        """Liberar slot de pod"""
        with self.resource_lock:
            if self.active_pods > 0:
                self.active_pods -= 1
                print(f"🔓 Pod slot liberado ({self.active_pods}/{self.MAX_CONCURRENT_PODS})")
    
    def acquire_test_slot(self, timeout: int = 600) -> bool:
        """Adquirir slot para execução de teste"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            with self.resource_lock:
                if (self.active_tests < self.MAX_CONCURRENT_TESTS and
                    self._check_system_health()):
                    
                    self.active_tests += 1
                    print(f"🧪 Teste slot adquirido ({self.active_tests}/{self.MAX_CONCURRENT_TESTS})")
                    return True
            
            time.sleep(self.test_execution_delay)
        
        print(f"⏰ Timeout aguardando slot para teste")
        return False
    
    def release_test_slot(self):
        """Liberar slot de teste"""
        with self.resource_lock:
            if self.active_tests > 0:
                self.active_tests -= 1
                print(f"🧪 Teste slot liberado ({self.active_tests}/{self.MAX_CONCURRENT_TESTS})")
    
    def _check_resource_availability(self) -> bool:
        """Verificar disponibilidade de recursos"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            if cpu_percent > self.MAX_CPU_USAGE:
                print(f"⚠️  CPU alta: {cpu_percent:.1f}%")
                return False
            
            # Memory usage
            memory = psutil.virtual_memory()
            if memory.percent > self.MAX_MEMORY_USAGE:
                print(f"⚠️  Memória alta: {memory.percent:.1f}%")
                return False
            
            # Load average (Linux)
            try:
                load_avg = psutil.getloadavg()[0]  # 1-minute load average
                cpu_cores = psutil.cpu_count()
                if load_avg > cpu_cores * 1.5:  # Load > 150% dos cores
                    print(f"⚠️  Load average alto: {load_avg:.2f}")
                    return False
            except:
                pass  # getloadavg não disponível em Windows
            
            return True
            
        except Exception as e:
            print(f"⚠️  Erro verificando recursos: {e}")
            return False
    
    def _check_system_health(self) -> bool:
        """Verificar saúde geral do sistema"""
        try:
            # Verificar recursos básicos
            if not self._check_resource_availability():
                return False
            
            # Verificar pods do Kubernetes
            pod_count = self._get_active_k8s_pods()
            if pod_count > self.MAX_CONCURRENT_PODS * 1.5:
                print(f"⚠️  Muitos pods K8s ativos: {pod_count}")
                return False
            
            # Verificar conectividade Docker
            if not self._check_docker_health():
                print(f"⚠️  Docker não saudável")
                return False
            
            return True
            
        except Exception as e:
            print(f"⚠️  Erro verificando saúde do sistema: {e}")
            return False
    
    def _get_active_k8s_pods(self) -> int:
        """Contar pods ativos no Kubernetes"""
        try:
            result = subprocess.run(
                ["kubectl", "get", "pods", "-n", "scalability-test", "--output=json"],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return len(data.get("items", []))
            else:
                return 0
                
        except Exception:
            return 0
    
    def _check_docker_health(self) -> bool:
        """Verificar saúde do Docker"""
        try:
            result = subprocess.run(
                ["docker", "system", "df", "--format", "json"],
                capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
        except Exception:
            return True  # Assumir OK se não conseguir verificar
    
    def report_test_success(self):
        """Reportar sucesso de teste para adaptação"""
        self.consecutive_successes += 1
        self.consecutive_failures = 0
        
        if self.adaptive_mode and self.consecutive_successes >= 5:
            self._adapt_for_success()
    
    def report_test_failure(self):
        """Reportar falha de teste para adaptação"""
        self.consecutive_failures += 1
        self.consecutive_successes = 0
        
        if self.adaptive_mode and self.consecutive_failures >= 2:
            self._adapt_for_failure()
    
    def _adapt_for_success(self):
        """Adaptar configurações após sucessos consecutivos"""
        if self.MAX_CONCURRENT_TESTS < 4:
            self.MAX_CONCURRENT_TESTS += 1
            print(f"📈 Adaptação: Aumentando testes simultâneos para {self.MAX_CONCURRENT_TESTS}")
        
        if self.test_execution_delay > 2.0:
            self.test_execution_delay *= 0.9
            print(f"📈 Adaptação: Reduzindo delay para {self.test_execution_delay:.1f}s")
        
        self.consecutive_successes = 0
    
    def _adapt_for_failure(self):
        """Adaptar configurações após falhas consecutivas"""
        if self.MAX_CONCURRENT_TESTS > 1:
            self.MAX_CONCURRENT_TESTS -= 1
            print(f"📉 Adaptação: Reduzindo testes simultâneos para {self.MAX_CONCURRENT_TESTS}")
        
        if self.MAX_CONCURRENT_PODS > 6:
            self.MAX_CONCURRENT_PODS -= 2
            print(f"📉 Adaptação: Reduzindo pods simultâneos para {self.MAX_CONCURRENT_PODS}")
        
        self.test_execution_delay *= 1.5
        self.pod_creation_delay *= 1.2
        print(f"📉 Adaptação: Aumentando delays (teste: {self.test_execution_delay:.1f}s, pod: {self.pod_creation_delay:.1f}s)")
        
        self.consecutive_failures = 0
    
    def wait_for_resource_stabilization(self, duration: float = 5.0):
        """Aguardar estabilização dos recursos"""
        print(f"⏳ Aguardando estabilização dos recursos ({duration}s)...")
        time.sleep(duration)
    
    def get_recommended_delays(self) -> Dict[str, float]:
        """Obter delays recomendados com base no estado atual"""
        return {
            "pod_creation": self.pod_creation_delay,
            "test_execution": self.test_execution_delay,
            "resource_check": self.resource_check_interval
        }
    
    def get_resource_status(self) -> Dict:
        """Obter status atual dos recursos"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "active_pods": self.active_pods,
                "active_tests": self.active_tests,
                "max_pods": self.MAX_CONCURRENT_PODS,
                "max_tests": self.MAX_CONCURRENT_TESTS,
                "health_status": "healthy" if self._check_system_health() else "stressed"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def cleanup(self):
        """Limpeza final do gerenciador"""
        print("🧹 Limpando gerenciador de concorrência...")
        with self.resource_lock:
            self.active_pods = 0
            self.active_tests = 0


def get_concurrency_manager() -> ConcurrencyManager:
    """Obter instância do gerenciador de concorrência"""
    return ConcurrencyManager()


if __name__ == "__main__":
    # Teste do gerenciador
    manager = get_concurrency_manager()
    status = manager.get_resource_status()
    print("\n📊 Status dos recursos:")
    for key, value in status.items():
        print(f"   {key}: {value}")
