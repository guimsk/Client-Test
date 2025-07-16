# Monitoramento de recursos e concorrência
from resource_monitor import *
from concurrency_manager import *
import shutil

class SystemMonitor:
    def __init__(self):
        self.snapshots = []
        self.errors = []
        self.monitoring = False

    def start_monitoring(self):
        try:
            self.monitoring = True
            self._collect_snapshot()
        except Exception as e:
            self.errors.append(f"Erro ao iniciar monitoramento: {e}")
            self.monitoring = False

    def stop_monitoring(self):
        try:
            self.monitoring = False
            self._collect_snapshot()
        except Exception as e:
            self.errors.append(f"Erro ao parar monitoramento: {e}")

    def _collect_snapshot(self):
        try:
            cpu = shutil.which('lscpu')
            mem = shutil.which('free')
            snap = {"cpu": cpu, "mem": mem}
            self.snapshots.append(snap)
        except Exception as e:
            self.errors.append(f"Erro ao coletar snapshot: {e}")

    def get_resource_recommendations(self):
        try:
            if not self.snapshots:
                return {"info": "Sem dados de monitoramento."}
            return {"snapshots": self.snapshots}
        except Exception as e:
            self.errors.append(f"Erro ao gerar recomendações: {e}")
            return {"error": str(e)}
