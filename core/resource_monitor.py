#!/usr/bin/env python3
"""
MONITOR DE RECURSOS V6
Sistema para monitorar utilização de recursos durante testes
"""

import time
import psutil
import subprocess
from typing import Dict, List
from dataclasses import dataclass
from pathlib import Path

from core.config import get_config


@dataclass
class ResourceSnapshot:
    """Snapshot de recursos em um momento específico"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_available: int
    swap_percent: float
    pod_count: int
    
    
class ResourceMonitor:
    """Monitor de recursos do sistema"""
    
    def __init__(self):
        self.config = get_config()
        self.snapshots: List[ResourceSnapshot] = []
        self.errors = []
        self.monitoring = False
        self.start_time = None
    
    def start_monitoring(self):
        """Iniciar monitoramento"""
        try:
            self.monitoring = True
            self.start_time = time.time()
            self._collect_snapshot()  # snapshot inicial
            print("📊 Monitoramento de recursos iniciado")
        except Exception as e:
            self.errors.append(f"Erro ao iniciar monitoramento: {e}")
            self.monitoring = False
    
    def stop_monitoring(self):
        """Parar monitoramento"""
        try:
            self.monitoring = False
            self._collect_snapshot()  # snapshot final
            print("📊 Monitoramento de recursos parado")
        except Exception as e:
            self.errors.append(f"Erro ao parar monitoramento: {e}")

    def save_monitoring_report(self):
        """Salvar relatório de monitoramento"""
        try:
            # Salva snapshots em arquivo para análise posterior
            import json
            with open("resource_monitor_report.json", "w") as f:
                json.dump(self.snapshots, f, indent=2)
        except Exception as e:
            self.errors.append(f"Erro ao salvar relatório: {e}")

    def _collect_snapshot(self):
        """Coletar snapshot dos recursos atuais"""
        try:
            snapshot = {
                "timestamp": time.time(),
                "cpu_percent": psutil.cpu_percent(interval=0.5),
                "memory": psutil.virtual_memory()._asdict(),
                "swap": psutil.swap_memory()._asdict(),
                "disk": psutil.disk_usage("/")._asdict(),
                "net": psutil.net_io_counters()._asdict(),
                "process_count": len(psutil.pids()),
            }
            self.snapshots.append(snapshot)
        except Exception as e:
            self.errors.append(f"Erro ao coletar snapshot: {e}")

    def take_snapshot(self):
        """Coleta e retorna um snapshot de recursos no formato ResourceSnapshot"""
        try:
            cpu = psutil.cpu_percent(interval=0.2)
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            # Se houver monitoramento de pods, pode ser ajustado aqui
            pod_count = 0
            snapshot = ResourceSnapshot(
                timestamp=time.time(),
                cpu_percent=cpu,
                memory_percent=mem.percent,
                memory_available=mem.available,
                swap_percent=swap.percent,
                pod_count=pod_count
            )
            return snapshot
        except Exception as e:
            self.errors.append(f"Erro ao coletar snapshot: {e}")
            return ResourceSnapshot(time.time(), 0, 0, 0, 0, 0)

    def print_current_status(self):
        """Imprimir status atual dos recursos"""
        snapshot = self.take_snapshot()
        
        print("\n📊 STATUS ATUAL DOS RECURSOS")
        print("=" * 40)
        print(f"💻 CPU: {snapshot.cpu_percent:.1f}%")
        print(f"🧠 Memória: {snapshot.memory_percent:.1f}% ({snapshot.memory_available/(1024**3):.1f}GB livre)")
        print(f"💾 Swap: {snapshot.swap_percent:.1f}%")
        print(f"🚀 Pods ativos: {snapshot.pod_count}")
        print("=" * 40)
    
    def get_resource_recommendations(self) -> Dict[str, str]:
        """Obter recomendações de recursos baseado no monitoramento"""
        try:
            if not self.snapshots:
                return {"info": "Sem dados de monitoramento."}
            
            # Calcular estatísticas
            avg_cpu = sum(s.cpu_percent for s in self.snapshots) / len(self.snapshots)
            max_cpu = max(s.cpu_percent for s in self.snapshots)
            avg_memory = sum(s.memory_percent for s in self.snapshots) / len(self.snapshots)
            max_memory = max(s.memory_percent for s in self.snapshots)
            max_pods = max(s.pod_count for s in self.snapshots)
            
            recommendations = {}
            
            # Recomendações CPU
            if avg_cpu < 30:
                recommendations["cpu"] = "CPU subutilizada - pode aumentar limites dos pods"
            elif avg_cpu > 80:
                recommendations["cpu"] = "CPU sobregregada - reduzir limites ou paralelismo"
            else:
                recommendations["cpu"] = "Utilização CPU adequada"
            
            # Recomendações Memória
            if avg_memory < 40:
                recommendations["memory"] = "Memória subutilizada - pode aumentar limites dos pods"
            elif avg_memory > 85:
                recommendations["memory"] = "Memória sobregarregada - reduzir limites ou paralelismo"
            else:
                recommendations["memory"] = "Utilização memória adequada"
            
            # Recomendações Pods
            if max_pods > 10:
                recommendations["pods"] = "Muitos pods simultâneos - considere reduzir paralelismo"
            elif max_pods < 4:
                recommendations["pods"] = "Poucos pods - pode aumentar paralelismo"
            else:
                recommendations["pods"] = "Número de pods adequado"
            
            recommendations["stats"] = {
                "avg_cpu": round(avg_cpu, 1),
                "max_cpu": round(max_cpu, 1),
                "avg_memory": round(avg_memory, 1),
                "max_memory": round(max_memory, 1),
                "max_pods": max_pods
            }
            
            return recommendations
        except Exception as e:
            self.errors.append(f"Erro ao gerar recomendações: {e}")
            return {"error": str(e)}
    
    def get_system_metrics(self):
        """Retorna métricas básicas do sistema (CPU, RAM, disco)."""
        import psutil
        try:
            return {
                'cpu_percent': psutil.cpu_percent(interval=0.1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent
            }
        except Exception as e:
            return {'cpu_percent': None, 'memory_percent': None, 'disk_percent': None, 'error': str(e)}

    def collect_metrics(self):
        """Coleta e retorna snapshot de métricas do sistema."""
        try:
            return self.get_system_metrics()
        except Exception as e:
            return {'error': str(e)}

    def start_continuous_monitoring(self, interval=1.0, duration=10):
        """Inicia monitoramento contínuo de métricas por um tempo determinado (em segundos)."""
        import threading, time
        self._monitoring = True
        self._snapshots = []
        def monitor():
            start = time.time()
            while self._monitoring and (time.time() - start < duration):
                try:
                    self._snapshots.append(self.get_system_metrics())
                except Exception as e:
                    self._snapshots.append({'error': str(e)})
                time.sleep(interval)
        t = threading.Thread(target=monitor)
        t.daemon = True
        t.start()
        return t

    def stop_continuous_monitoring(self):
        """Para o monitoramento contínuo."""
        self._monitoring = False
        return getattr(self, '_snapshots', [])
    
def get_resource_monitor() -> ResourceMonitor:
    """Obter monitor de recursos"""
    return ResourceMonitor()


if __name__ == "__main__":
    monitor = get_resource_monitor()
    monitor.print_current_status()
    
    # Mostrar recomendações se houver dados de monitoramento
    if monitor.snapshots:
        recommendations = monitor.get_resource_recommendations()
        print("\n🔍 RECOMENDAÇÕES:")
        for key, value in recommendations.items():
            if key != "stats":
                print(f"• {key}: {value}")
