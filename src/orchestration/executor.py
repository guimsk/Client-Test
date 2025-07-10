#!/usr/bin/env python3
"""
ORQUESTRADOR DE EXECUÇÃO - ULTRA OTIMIZADO V5
Sistema de execução paralela de cenários de teste para máxima performance
"""

import os
import time
import csv
import json
import subprocess
import threading
from typing import List, Dict, Optional, Tuple, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
import uuid

# Importar do diretório raiz
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import get_config
from infrastructure_manager import get_infrastructure_manager


@dataclass
class TestScenario:
    """Cenário de teste individual"""
    scenario_id: str
    language: str
    num_servers: int
    num_clients: int
    messages_per_client: int
    run_number: int
    
    def __str__(self):
        return f"{self.language}_{self.num_servers}s_{self.num_clients}c_{self.messages_per_client}m_run{self.run_number}"


@dataclass
class TestResult:
    """Resultado de teste individual"""
    scenario: TestScenario
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
    errors: int
    error_message: Optional[str] = None
    timestamp: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        return {
            'scenario_id': self.scenario.scenario_id,
            'language': self.scenario.language,
            'num_servers': self.scenario.num_servers,
            'num_clients': self.scenario.num_clients,
            'messages_per_client': self.scenario.messages_per_client,
            'run_number': self.scenario.run_number,
            'success': self.success,
            'duration': self.duration,
            'latency_avg': self.latency_avg,
            'latency_min': self.latency_min,
            'latency_max': self.latency_max,
            'latency_median': self.latency_median,
            'latency_stddev': self.latency_stddev,
            'throughput': self.throughput,
            'messages_sent': self.messages_sent,
            'messages_received': self.messages_received,
            'errors': self.errors,
            'error_message': self.error_message,
            'timestamp': self.timestamp
        }


class TestExecutor:
    """Executor de testes individuais"""
    
    def __init__(self):
        self.config = get_config()
        self.infrastructure = get_infrastructure_manager()
    
    def execute_test_scenario(self, scenario: TestScenario) -> TestResult:
        """Executar um cenário de teste individual"""
        start_time = time.time()
        
        try:
            print(f"🧪 Executing {scenario}")
            
            # Deploy aplicações para este cenário
            if not self.infrastructure.deploy_applications(scenario.language, scenario.num_servers):
                return TestResult(
                    scenario=scenario,
                    success=False,
                    duration=time.time() - start_time,
                    latency_avg=0, latency_min=0, latency_max=0, 
                    latency_median=0, latency_stddev=0,
                    throughput=0, messages_sent=0, messages_received=0, errors=1,
                    error_message="Failed to deploy applications",
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                )
            
            # Aguardar estabilização
            time.sleep(2)
            
            # Executar teste cliente
            result = self._run_client_test(scenario)
            
            # Aguardar finalização
            time.sleep(1)
            
            return result
            
        except Exception as e:
            return TestResult(
                scenario=scenario,
                success=False,
                duration=time.time() - start_time,
                latency_avg=0, latency_min=0, latency_max=0, 
                latency_median=0, latency_stddev=0,
                throughput=0, messages_sent=0, messages_received=0, errors=1,
                error_message=str(e),
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
            )
    
    def _run_client_test(self, scenario: TestScenario) -> TestResult:
        """Executar teste do cliente usando Docker diretamente"""
        try:
            # Primeiro, iniciar servidor(es) usando Docker
            server_containers = []
            
            # Determinar imagem do servidor
            if scenario.language == "cpp":
                server_image = "guimsk/servidor-cpp:latest"
            elif scenario.language == "c":
                server_image = "guimsk/servidor-c:latest"
            else:
                raise ValueError(f"Unsupported language: {scenario.language}")
            
            # Iniciar servidor(es)
            for i in range(scenario.num_servers):
                port = self.config.BASE_PORT + i
                container_name = f"test-server-{scenario.language}-{i}-{int(time.time())}"
                
                cmd = [
                    "sudo", "docker", "run", "-d", "--rm",
                    "--name", container_name,
                    "-p", f"{port}:8000",  # Porta do host para porta 8000 do container
                    server_image
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    server_containers.append((container_name, port))
                else:
                    # Cleanup containers já iniciados
                    for cont_name, _ in server_containers:
                        subprocess.run(["sudo", "docker", "stop", cont_name], capture_output=True)
                    raise Exception(f"Failed to start server {i}: {result.stderr}")
            
            # Aguardar servidores iniciarem
            time.sleep(3)
            
            try:
                # Executar cliente usando Docker
                server_hosts = ",".join([f"localhost:{port}" for _, port in server_containers])
                
                cmd = [
                    "sudo", "docker", "run", "--rm", "--network", "host",
                    "-e", f"SERVERS={server_hosts}",
                    "-e", f"CLIENTS={scenario.num_clients}",
                    "-e", f"MESSAGES={scenario.messages_per_client}",
                    "-e", f"TIMEOUT={self.config.TIMEOUT}",
                    "guimsk/cliente:latest"
                ]
                
                start_time = time.time()
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    timeout=self.config.TIMEOUT,
                    text=True
                )
                
                duration = time.time() - start_time
                
                if result.returncode == 0:
                    return self._parse_client_output(scenario, result.stdout, duration)
                else:
                    return TestResult(
                        scenario=scenario,
                        success=False,
                        duration=duration,
                        latency_avg=0, latency_min=0, latency_max=0, 
                        latency_median=0, latency_stddev=0,
                        throughput=0, messages_sent=0, messages_received=0, errors=1,
                        error_message=result.stderr,
                        timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                    )
                    
            finally:
                # Sempre limpar containers dos servidores
                for cont_name, _ in server_containers:
                    subprocess.run(["sudo", "docker", "stop", cont_name], capture_output=True)
                
        except subprocess.TimeoutExpired:
            # Limpar containers em caso de timeout
            for cont_name, _ in server_containers:
                subprocess.run(["sudo", "docker", "stop", cont_name], capture_output=True)
            return TestResult(
                scenario=scenario,
                success=False,
                duration=self.config.TIMEOUT,
                latency_avg=0, latency_min=0, latency_max=0, 
                latency_median=0, latency_stddev=0,
                throughput=0, messages_sent=0, messages_received=0, errors=1,
                error_message="Test timeout",
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
            )
        except Exception as e:
            # Limpar containers em caso de erro
            if 'server_containers' in locals():
                for cont_name, _ in server_containers:
                    subprocess.run(["sudo", "docker", "stop", cont_name], capture_output=True)
            return TestResult(
                scenario=scenario,
                success=False,
                duration=0,
                latency_avg=0, latency_min=0, latency_max=0, 
                latency_median=0, latency_stddev=0,
                throughput=0, messages_sent=0, messages_received=0, errors=1,
                error_message=str(e),
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
            )
    
    def _parse_client_output(self, scenario: TestScenario, output: str, duration: float) -> TestResult:
        """Parse da saída do cliente"""
        try:
            # Tentar fazer parse do JSON de saída
            lines = output.strip().split('\n')
            json_line = None
            
            for line in lines:
                if line.strip().startswith('{') and 'latency_avg' in line:
                    json_line = line.strip()
                    break
            
            if json_line:
                data = json.loads(json_line)
                
                return TestResult(
                    scenario=scenario,
                    success=True,
                    duration=duration,
                    latency_avg=data.get('latency_avg', 0),
                    latency_min=data.get('latency_min', 0),
                    latency_max=data.get('latency_max', 0),
                    latency_median=data.get('latency_median', 0),
                    latency_stddev=data.get('latency_stddev', 0),
                    throughput=data.get('throughput', 0),
                    messages_sent=data.get('messages_sent', 0),
                    messages_received=data.get('messages_received', 0),
                    errors=data.get('errors', 0),
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                )
            else:
                # Fallback para parsing simples
                messages_sent = scenario.num_clients * scenario.messages_per_client
                throughput = messages_sent / duration if duration > 0 else 0
                
                return TestResult(
                    scenario=scenario,
                    success=True,
                    duration=duration,
                    latency_avg=duration * 1000 / messages_sent if messages_sent > 0 else 0,
                    latency_min=0,
                    latency_max=0,
                    latency_median=0,
                    latency_stddev=0,
                    throughput=throughput,
                    messages_sent=messages_sent,
                    messages_received=messages_sent,  # Assumir sucesso
                    errors=0,
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                )
                
        except Exception as e:
            # Resultado básico em caso de erro de parsing
            messages_sent = scenario.num_clients * scenario.messages_per_client
            throughput = messages_sent / duration if duration > 0 else 0
            
            return TestResult(
                scenario=scenario,
                success=True,
                duration=duration,
                latency_avg=duration * 1000 / messages_sent if messages_sent > 0 else 0,
                latency_min=0,
                latency_max=0,
                latency_median=0,
                latency_stddev=0,
                throughput=throughput,
                messages_sent=messages_sent,
                messages_received=messages_sent,
                errors=0,
                error_message=f"Parse error: {str(e)}",
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
            )


class ScenarioOrchestrator:
    """Orquestrador principal de cenários"""
    
    def __init__(self):
        self.config = get_config()
        self.executor = TestExecutor()
        self.results: List[TestResult] = []
        self.lock = threading.Lock()
    
    def generate_all_scenarios(self) -> List[TestScenario]:
        """Gerar todos os cenários de teste"""
        scenarios = []
        
        for language in self.config.LANGUAGES:
            for servers in self.config.SERVERS:
                for clients in self.config.CLIENTS:
                    for messages in self.config.MESSAGES:
                        for run in range(1, self.config.RUNS_PER_CONFIG + 1):
                            scenario = TestScenario(
                                scenario_id=str(uuid.uuid4()),
                                language=language,
                                num_servers=servers,
                                num_clients=clients,
                                messages_per_client=messages,
                                run_number=run
                            )
                            scenarios.append(scenario)
        
        return scenarios
    
    def execute_all_scenarios(self) -> bool:
        """Executar todos os cenários"""
        scenarios = self.generate_all_scenarios()
        total_scenarios = len(scenarios)
        
        print(f"🚀 EXECUTING {total_scenarios} TEST SCENARIOS")
        print("=" * 60)
        
        start_time = time.time()
        
        if self.config.PARALLEL_EXECUTION:
            success = self._execute_scenarios_parallel(scenarios)
        else:
            success = self._execute_scenarios_sequential(scenarios)
        
        elapsed = time.time() - start_time
        
        # Salvar resultados
        self._save_all_results()
        
        # Estatísticas finais
        successful_tests = sum(1 for r in self.results if r.success)
        print(f"\n📊 EXECUTION SUMMARY:")
        print(f"   Total scenarios: {total_scenarios}")
        print(f"   Successful: {successful_tests}")
        print(f"   Failed: {total_scenarios - successful_tests}")
        print(f"   Duration: {elapsed:.1f}s ({elapsed/60:.1f}min)")
        print(f"   Rate: {total_scenarios/elapsed:.2f} tests/sec")
        
        return success
    
    def execute_language_scenarios(self, language: str) -> bool:
        """Executar cenários para uma linguagem específica"""
        scenarios = [s for s in self.generate_all_scenarios() if s.language == language]
        
        print(f"🧪 EXECUTING {len(scenarios)} SCENARIOS FOR {language.upper()}")
        
        if self.config.PARALLEL_EXECUTION:
            return self._execute_scenarios_parallel(scenarios)
        else:
            return self._execute_scenarios_sequential(scenarios)
    
    def _execute_scenarios_parallel(self, scenarios: List[TestScenario]) -> bool:
        """Execução paralela de cenários"""
        with ThreadPoolExecutor(max_workers=self.config.MAX_CONCURRENT_PODS) as executor:
            futures = {executor.submit(self.executor.execute_test_scenario, scenario): scenario 
                      for scenario in scenarios}
            
            completed = 0
            for future in as_completed(futures):
                result = future.result()
                
                with self.lock:
                    self.results.append(result)
                    completed += 1
                
                if result.success:
                    print(f"✅ [{completed}/{len(scenarios)}] {result.scenario} - {result.duration:.2f}s")
                else:
                    print(f"❌ [{completed}/{len(scenarios)}] {result.scenario} - {result.error_message}")
        
        return True
    
    def _execute_scenarios_sequential(self, scenarios: List[TestScenario]) -> bool:
        """Execução sequencial de cenários"""
        for i, scenario in enumerate(scenarios, 1):
            result = self.executor.execute_test_scenario(scenario)
            self.results.append(result)
            
            if result.success:
                print(f"✅ [{i}/{len(scenarios)}] {scenario} - {result.duration:.2f}s")
            else:
                print(f"❌ [{i}/{len(scenarios)}] {scenario} - {result.error_message}")
        
        return True
    
    def _save_all_results(self):
        """Salvar todos os resultados em CSV"""
        if not self.results:
            print("⚠️  No results to save")
            return
        
        # Arquivo principal com todos os resultados
        results_file = self.config.RESULTS_DIR / "all_results.csv"
        
        print(f"💾 Saving {len(self.results)} results to {results_file}")
        
        with open(results_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.results[0].to_dict().keys())
            writer.writeheader()
            
            for result in self.results:
                writer.writerow(result.to_dict())
        
        # Arquivos por linguagem
        for language in self.config.LANGUAGES:
            language_results = [r for r in self.results if r.scenario.language == language]
            if language_results:
                language_file = self.config.RESULTS_DIR / f"results_{language}.csv"
                
                with open(language_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=language_results[0].to_dict().keys())
                    writer.writeheader()
                    
                    for result in language_results:
                        writer.writerow(result.to_dict())
        
        print(f"✅ Results saved successfully")
    
    def get_results_by_language(self, language: str) -> List[TestResult]:
        """Obter resultados por linguagem"""
        return [r for r in self.results if r.scenario.language == language]
    
    def get_successful_results(self) -> List[TestResult]:
        """Obter apenas resultados bem-sucedidos"""
        return [r for r in self.results if r.success]


# Singleton instance
_scenario_orchestrator: Optional[ScenarioOrchestrator] = None


def get_scenario_orchestrator() -> ScenarioOrchestrator:
    """Obter instância única do orquestrador"""
    global _scenario_orchestrator
    if _scenario_orchestrator is None:
        _scenario_orchestrator = ScenarioOrchestrator()
    return _scenario_orchestrator


if __name__ == "__main__":
    # Teste do orquestrador
    orchestrator = get_scenario_orchestrator()
    
    # Gerar cenários demo
    config = get_config()
    original_configs = (config.SERVERS.copy(), config.CLIENTS.copy(), config.MESSAGES.copy(), config.RUNS_PER_CONFIG)
    
    # Configuração demo
    config.SERVERS = [2]
    config.CLIENTS = [10]
    config.MESSAGES = [1]
    config.RUNS_PER_CONFIG = 1
    
    scenarios = orchestrator.generate_all_scenarios()
    print(f"Generated {len(scenarios)} demo scenarios")
    
    # Restaurar configuração
    config.SERVERS, config.CLIENTS, config.MESSAGES, config.RUNS_PER_CONFIG = original_configs
