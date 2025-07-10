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

from config import get_config


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
        self.monitoring = False
    
    def start_monitoring(self):
        """Iniciar monitoramento"""
        self.monitoring = True
        self.snapshots = []
        print("📊 Monitoramento de recursos iniciado")
    
    def stop_monitoring(self):
        """Parar monitoramento"""
        self.monitoring = False
        print("📊 Monitoramento de recursos parado")
    
    def take_snapshot(self) -> ResourceSnapshot:
        """Tirar snapshot dos recursos atuais"""
        # Recursos do sistema
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Contar pods Kubernetes ativos
        pod_count = self._count_active_pods()
        
        snapshot = ResourceSnapshot(
            timestamp=time.time(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_available=memory.available,
            swap_percent=swap.percent,
            pod_count=pod_count
        )
        
        if self.monitoring:
            self.snapshots.append(snapshot)
        
        return snapshot
    
    def _count_active_pods(self) -> int:
        """Contar pods ativos no namespace"""
        try:
            result = subprocess.run([
                "sudo", "kubectl", "get", "pods", 
                f"--namespace={self.config.K8S_NAMESPACE}",
                "--no-headers"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                return len([line for line in lines if line.strip()])
            else:
                return 0
        except Exception:
            return 0
    
    def get_resource_recommendations(self) -> Dict[str, str]:
        """Obter recomendações de recursos baseado no monitoramento"""
        if not self.snapshots:
            return {"error": "Nenhum dado de monitoramento disponível"}
        
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
    
    def save_monitoring_report(self):
        """Salvar relatório de monitoramento"""
        if not self.snapshots:
            print("⚠️  Nenhum dado para salvar")
            return
        
        report_file = self.config.RESULTS_DIR / "resource_monitoring.json"
        
        import json
        report_data = {
            "total_snapshots": len(self.snapshots),
            "monitoring_duration": self.snapshots[-1].timestamp - self.snapshots[0].timestamp,
            "recommendations": self.get_resource_recommendations(),
            "snapshots": [
                {
                    "timestamp": s.timestamp,
                    "cpu_percent": s.cpu_percent,
                    "memory_percent": s.memory_percent,
                    "memory_available_gb": s.memory_available / (1024**3),
                    "swap_percent": s.swap_percent,
                    "pod_count": s.pod_count
                }
                for s in self.snapshots
            ]
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"📊 Relatório salvo em {report_file}")


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
