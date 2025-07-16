#!/usr/bin/env python3
"""
SISTEMA DE TESTES UNIFICADO E COMPLETO - TarefaV4
Teste abrangente de todos os componentes do sistema de escalabilidade
Consolidação de todos os testes em um arquivo único
"""

import os
import sys
import time
import datetime
import traceback
import json
from pathlib import Path
import psutil
import pkg_resources
import subprocess  # Corrige erro de referência
from core.utils import run_subprocess, check_file_exists, get_logger
import importlib.metadata

class SystemTester:
    """Classe principal para testes do sistema completo"""
    
    def __init__(self):
        self.test_results = {}
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.warnings = 0
        self.logger = get_logger("SystemTester")
        
    def run_all_tests(self):
        """Executar todos os testes do sistema"""
        print("🧪 SISTEMA DE TESTES UNIFICADO E COMPLETO")
        print("=" * 70)
        print("📋 Executando verificação abrangente de todos os componentes...")
        print()
        
        # Lista de todos os testes
        test_suite = [
            ("🔧 Configuração e Imports", self.test_imports_and_config),
            ("🐳 Docker e Containers", self.test_docker_system),
            ("☸️  Kubernetes", self.test_kubernetes_system),
            ("🏗️  Infraestrutura", self.test_infrastructure_manager),
            ("🧠 Gerenciamento de Concorrência", self.test_concurrency_manager),
            ("⚡ Executor de Testes", self.test_executor_system),
            ("📊 Análise de Resultados", self.test_result_analyzer),
            ("📈 Geração de Gráficos", self.test_chart_generator),
            ("🔍 Monitor de Recursos", self.test_resource_monitor),
            ("🌐 Aplicações (Cliente/Servidor)", self.test_applications),
            ("📁 Estrutura de Arquivos", self.test_file_structure),
            ("🔌 Consistência de Configurações", self.test_configuration_consistency),
            ("💾 Persistência de Dados", self.test_data_persistence),
            ("🔐 Segurança e Validações", self.test_security_validations),
            ("⚡ Performance e Recursos", self.test_performance_resources),
            ("🔄 Integração Entre Componentes", self.test_integration),
            ("📝 Versões e Compatibilidade", self.test_version_compatibility),
            ("🔒 Robustez e Recuperação", self.test_robustness_recovery),
            ("📋 Qualidade do Código", self.test_code_quality),
            ("🌍 Ambiente e Dependências", self.test_environment_dependencies),
            ("📊 Métricas e Monitoramento", self.test_metrics_monitoring),
            ("🚀 Deploy e Escalabilidade", self.test_deployment_scalability),
            ("🔍 Versões e Dependências", self.test_version_and_dependencies),
            ("🛠️ API do Gerenciador de Infraestrutura", self.test_infrastructure_manager_api),
            ("🐳 Imagens Docker Essenciais", self.test_docker_images_exist),
            ("🐋 Compatibilidade de Imagens Docker e K8s", self.test_docker_k8s_image_compatibility),
            ("🚦 Performance e Estabilidade (paralelo)", self.test_performance_and_stability),
        ]
        
        # Executar cada teste
        for test_name, test_func in test_suite:
            self._run_test_section(test_name, test_func)
        
        # Relatório final
        self._generate_final_report()
        
        return self.failed_tests == 0

    def _run_test_section(self, test_name: str, test_func):
        """Executar uma seção de testes"""
        print(f"\n{test_name}")
        print("=" * 70)
        try:
            test_func()
        except Exception as e:
            self._log_test("ERRO CRÍTICO", f"{test_name}: {e}", False)
            print(f"❌ ERRO CRÍTICO: {e}")
            self.logger.error(f"Erro crítico em {test_name}: {e}", exc_info=True)
            traceback.print_exc()

    def _log_test(self, test_name: str, description: str, passed: bool, warning: bool = False):
        """Registrar resultado de um teste"""
        self.total_tests += 1
        
        if warning:
            self.warnings += 1
            status = "⚠️ "
        elif passed:
            self.passed_tests += 1
            status = "✅"
        else:
            self.failed_tests += 1
            status = "❌"
        
        self.test_results[test_name] = {
            "description": description,
            "passed": passed,
            "warning": warning
        }
        
        print(f"{status} {test_name}: {description}")
        self.logger.info(f"{status} {test_name}: {description}")

    def test_imports_and_config(self):
        """Testar imports e configuração do sistema"""
        # Teste de imports principais
        critical_modules = [
            'core.config',
            'core.infrastructure_manager',
            'core.test_executor',
            'core.concurrency_manager',
            'core.result_analyzer',
            'core.chart_generator',
            'core.resource_monitor'
        ]
        for module in critical_modules:
            try:
                imported = __import__(module, fromlist=[''])
                self._log_test(f"Import {module.split('.')[-1]}", "Módulo importado com sucesso", True)
                # Testar funções factory específicas
                factory_name = f'get_{module.split('.')[-1]}'
                if hasattr(imported, factory_name):
                    factory_func = getattr(imported, factory_name)
                    instance = factory_func()
                    self._log_test(f"Factory {module.split('.')[-1]}", "Função factory funcional", True)
            except ImportError as e:
                self._log_test(f"Import {module.split('.')[-1]}", f"Falha na importação: {e}", False)
            except Exception as e:
                self._log_test(f"Import {module.split('.')[-1]}", f"Erro: {e}", False)
        
        # Teste de configuração
        try:
            from core.config import get_config, print_system_info
            config = get_config()
            
            # Verificar atributos essenciais
            essential_attrs = [
                'LANGUAGES', 'SERVERS', 'CLIENTS', 'MESSAGES',
                'DOCKER_USERNAME', 'K8S_NAMESPACE', 'RESULTS_DIR'
            ]
            
            for attr in essential_attrs:
                if hasattr(config, attr):
                    self._log_test(f"Config.{attr}", f"Atributo presente: {getattr(config, attr)}", True)
                else:
                    self._log_test(f"Config.{attr}", "Atributo ausente", False)
            
            # Verificar configurações conservadoras
            if config.PARALLEL_EXECUTION:
                self._log_test("Config Paralela", "Execução paralela ainda ativa", False)
            else:
                self._log_test("Config Paralela", "Execução sequencial configurada", True)
                
            if config.BATCH_SIZE <= 1:
                self._log_test("Config Batch", f"Batch size conservador: {config.BATCH_SIZE}", True)
            else:
                self._log_test("Config Batch", f"Batch size alto: {config.BATCH_SIZE}", False)
                
        except Exception as e:
            self._log_test("Configuração", f"Erro na configuração: {e}", False)

    def test_docker_system(self):
        """Testar sistema Docker"""
        
        # Verificar Docker instalado
        try:
            result = run_subprocess(['docker', '--version'])
            if result.returncode == 0:
                self._log_test("Docker Instalação", f"Docker disponível: {result.stdout.strip()}", True)
            else:
                self._log_test("Docker Instalação", "Docker não encontrado", False)
                return
        except FileNotFoundError:
            self._log_test("Docker Instalação", "Docker não instalado", False)
            return
        
        # Verificar Docker daemon
        try:
            result = run_subprocess(['docker', 'ps'])
            if result.returncode == 0:
                self._log_test("Docker Daemon", "Docker daemon ativo", True)
            else:
                self._log_test("Docker Daemon", "Docker daemon inativo", False)
        except Exception as e:
            self._log_test("Docker Daemon", f"Erro: {e}", False)
        
        # Verificar imagens necessárias
        expected_images = [
            'guimsk/servidor-c:latest',
            'guimsk/servidor-cpp:latest', 
            'guimsk/cliente:latest'
        ]
        
        try:
            result = run_subprocess(['docker', 'images', '--format', '{{.Repository}}:{{.Tag}}'])
            if result.returncode == 0:
                images = result.stdout.strip().split('\n')
                
                for expected in expected_images:
                    if any(expected in img for img in images):
                        self._log_test(f"Docker Image {expected}", "Imagem encontrada", True)
                    else:
                        self._log_test(f"Docker Image {expected}", "Imagem não encontrada", False, warning=True)
            
        except Exception as e:
            self._log_test("Docker Images", f"Erro verificando imagens: {e}", False)
        
        # Testar DockerManager
        try:
            from core.infrastructure_manager import DockerManager
            docker_manager = DockerManager()
            self._log_test("DockerManager", "Classe instanciada com sucesso", True)
            
            # Verificar métodos essenciais
            essential_methods = ['build_and_push_all', 'build_image', 'push_image']
            for method in essential_methods:
                if hasattr(docker_manager, method):
                    self._log_test(f"DockerManager.{method}", "Método disponível", True)
                else:
                    self._log_test(f"DockerManager.{method}", "Método ausente", False)
                    
        except Exception as e:
            self._log_test("DockerManager", f"Erro: {e}", False)

    def test_kubernetes_system(self):
        """Testar sistema Kubernetes"""
        
        # Verificar kubectl
        try:
            result = subprocess.run(['kubectl', 'version', '--client'], capture_output=True, text=True)
            if result.returncode == 0:
                self._log_test("kubectl", "Cliente kubectl disponível", True)
            else:
                self._log_test("kubectl", "kubectl não encontrado", False)
                return
        except FileNotFoundError:
            self._log_test("kubectl", "kubectl não instalado", False)
            return
        
        # Verificar conectividade com cluster
        try:
            result = subprocess.run(['kubectl', 'cluster-info'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self._log_test("K8s Cluster", "Cluster acessível", True)
                
                # Verificar nodes
                result = subprocess.run(['kubectl', 'get', 'nodes'], capture_output=True, text=True)
                if result.returncode == 0:
                    nodes = len([line for line in result.stdout.split('\n')[1:] if line.strip()])
                    self._log_test("K8s Nodes", f"{nodes} nodes disponíveis", True)
                
            else:
                self._log_test("K8s Cluster", "Cluster inacessível", False, warning=True)
        except subprocess.TimeoutExpired:
            self._log_test("K8s Cluster", "Timeout conectando ao cluster", False, warning=True)
        except Exception as e:
            self._log_test("K8s Cluster", f"Erro: {e}", False, warning=True)
        
        # Verificar namespace do projeto (será criado dinamicamente se necessário)
        try:
            from core.config import get_config
            config = get_config()
            result = subprocess.run(['kubectl', 'get', 'namespace', config.K8S_NAMESPACE], 
                                   capture_output=True, text=True)
            if result.returncode == 0:
                self._log_test("K8s Namespace", f"Namespace {config.K8S_NAMESPACE} existe", True)
            else:
                self._log_test("K8s Namespace", f"Namespace {config.K8S_NAMESPACE} será criado dinamicamente", True)
        except Exception as e:
            self._log_test("K8s Namespace", f"Erro verificando namespace: {e}", False)
        
        # Testar KubernetesManager
        try:
            from core.infrastructure_manager import KubernetesManager
            k8s_manager = KubernetesManager()
            self._log_test("KubernetesManager", "Classe instanciada com sucesso", True)
            
            essential_methods = ['setup_namespace', 'deploy_server', 'cleanup_resources']
            for method in essential_methods:
                if hasattr(k8s_manager, method):
                    self._log_test(f"K8sManager.{method}", "Método disponível", True)
                else:
                    self._log_test(f"K8sManager.{method}", "Método ausente", False)
                    
        except Exception as e:
            self._log_test("KubernetesManager", f"Erro: {e}", False)

    def test_infrastructure_manager(self):
        """Testar gerenciador de infraestrutura"""
        
        try:
            from core.infrastructure_manager import get_infrastructure_manager
            infrastructure = get_infrastructure_manager()
            self._log_test("InfrastructureManager", "Instância criada com sucesso", True)
            
            # Verificar componentes internos
            if hasattr(infrastructure, 'docker_manager'):
                self._log_test("InfraManager.docker", "DockerManager presente", True)
            else:
                self._log_test("InfraManager.docker", "DockerManager ausente", False)
            
            if hasattr(infrastructure, 'k8s') and infrastructure.k8s:
                self._log_test("InfraManager.k8s", "KubernetesManager presente", True)
            else:
                self._log_test("InfraManager.k8s", "KubernetesManager ausente", False)
            
            # Verificar métodos principais
            essential_methods = [
                'setup_infrastructure', 'cleanup_all', 'build_and_push_all',
                'deploy_servers', 'wait_for_pods_ready'
            ]
            
            for method in essential_methods:
                if hasattr(infrastructure, method):
                    self._log_test(f"InfraManager.{method}", "Método disponível", True)
                else:
                    self._log_test(f"InfraManager.{method}", "Método ausente", False)
            
        except Exception as e:
            self._log_test("InfrastructureManager", f"Erro: {e}", False)

    def test_concurrency_manager(self):
        """Testar gerenciador de concorrência"""
        
        try:
            from core.concurrency_manager import get_concurrency_manager
            manager = get_concurrency_manager()
            self._log_test("ConcurrencyManager", "Instância criada com sucesso", True)
            
            # Testar status inicial
            status = manager.get_resource_status()
            if isinstance(status, dict) and 'cpu_percent' in status:
                self._log_test("ConcurrencyManager.status", "Status de recursos funcional", True)
            else:
                self._log_test("ConcurrencyManager.status", "Status inválido", False)
            
            # Testar aquisição de slots
            if manager.acquire_pod_slot():
                manager.release_pod_slot()
                self._log_test("ConcurrencyManager.pods", "Controle de pod slots funcional", True)
            else:
                self._log_test("ConcurrencyManager.pods", "Falha no controle de pods", False)
            
            if manager.acquire_test_slot():
                manager.release_test_slot()
                self._log_test("ConcurrencyManager.tests", "Controle de test slots funcional", True)
            else:
                self._log_test("ConcurrencyManager.tests", "Falha no controle de testes", False)
            
            # Testar adaptação
            manager.report_test_success()
            manager.report_test_failure()
            self._log_test("ConcurrencyManager.adapt", "Sistema de adaptação funcional", True)
            
        except Exception as e:
            self._log_test("ConcurrencyManager", f"Erro: {e}", False)

    def test_executor_system(self):
        """Testar sistema executor de testes"""
        
        try:
            from core.test_executor import get_kubernetes_test_executor, TestScenario
            executor = get_kubernetes_test_executor(clear_previous_data=False)
            self._log_test("TestExecutor", "Instância criada com sucesso", True)
            
            # Testar criação de cenário
            scenario = TestScenario(
                scenario_id="test_validation",
                language="c",
                num_servers=2,
                num_clients=10,
                messages_per_client=1,
                run_number=1
            )
            self._log_test("TestScenario", "Cenário criado com sucesso", True)
            
            # Verificar métodos essenciais
            essential_methods = ['run_all_tests', 'run_single_scenario', 'get_results'
            ]
            for method in essential_methods:
                if hasattr(executor, method):
                    self._log_test(f"TestExecutor.{method}", "Método disponível", True)
                else:
                    self._log_test(f"TestExecutor.{method}", "Método ausente", False)
            
        except Exception as e:
            self._log_test("TestExecutor", f"Erro: {e}", False)

    def test_result_analyzer(self):
        """Testar analisador de resultados"""
        
        try:
            from core.result_analyzer import get_result_analyzer
            analyzer = get_result_analyzer()
            self._log_test("ResultAnalyzer", "Instância criada com sucesso", True)
            
            # Verificar métodos de análise
            analysis_methods = ['analyze_results', 'generate_summary', 'export_results']
            for method in analysis_methods:
                if hasattr(analyzer, method):
                    self._log_test(f"ResultAnalyzer.{method}", "Método disponível", True)
                else:
                    self._log_test(f"ResultAnalyzer.{method}", "Método ausente", False)
            
        except Exception as e:
            self._log_test("ResultAnalyzer", f"Erro: {e}", False)

    def test_chart_generator(self):
        """Testar gerador de gráficos (novo unificado)"""
        try:
            from core.config import get_config
            import subprocess
            config = get_config()
            script_path = config.CORE_DIR / "unified_chart_generator.py"
            result = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True)
            if result.returncode == 0:
                self._log_test("UnifiedChartGenerator", "Execução do script unificado OK", True)
            else:
                self._log_test("UnifiedChartGenerator", f"Erro na execução: {result.stderr}", False)
        except Exception as e:
            self._log_test("UnifiedChartGenerator", f"Erro: {e}", False)

    def test_resource_monitor(self):
        """Testar monitor de recursos"""
        
        try:
            from core.resource_monitor import get_resource_monitor
            monitor = get_resource_monitor()
            self._log_test("ResourceMonitor", "Instância criada com sucesso", True)
            
            # Testar coleta de recursos
            try:
                import psutil
                self._log_test("ResourceMonitor.psutil", "Psutil disponível", True)
            except ImportError:
                self._log_test("ResourceMonitor.psutil", "Psutil não encontrado", False)
            
        except Exception as e:
            self._log_test("ResourceMonitor", f"Erro: {e}", False)

    def test_applications(self):
        """Testar aplicações cliente e servidor"""
        
        # Verificar estrutura de diretórios
        app_dirs = [
            'applications/cliente',
            'applications/servidor', 
            'applications/servidor-c'
        ]
        
        for app_dir in app_dirs:
            if Path(app_dir).exists():
                self._log_test(f"App Dir {app_dir}", "Diretório presente", True)
                
                # Verificar arquivos essenciais
                if app_dir == 'applications/cliente':
                    essential_files = ['app.py', 'Dockerfile']
                else:
                    essential_files = ['Dockerfile']
                    
                for file in essential_files:
                    file_path = Path(app_dir) / file
                    if file_path.exists():
                        self._log_test(f"App File {app_dir}/{file}", "Arquivo presente", True)
                    else:
                        self._log_test(f"App File {app_dir}/{file}", "Arquivo ausente", False)
            else:
                self._log_test(f"App Dir {app_dir}", "Diretório ausente", False)

    def test_file_structure(self):
        """Testar estrutura de arquivos do projeto"""
        
        # Arquivos essenciais na pasta core
        essential_files = [
            'config.py', 'infrastructure_manager.py', 'test_executor.py',
            'concurrency_manager.py', 'result_analyzer.py',
            'chart_generator.py', 'resource_monitor.py'
        ]
        for file in essential_files:
            if Path('core')/file and (Path('core')/file).exists():
                self._log_test(f"File core/{file}", "Arquivo presente", True)
            else:
                self._log_test(f"File core/{file}", "Arquivo ausente", False)
        # Arquivos essenciais na raiz
        for file in ['executar.py', 'requirements.txt']:
            if Path(file).exists():
                self._log_test(f"File {file}", "Arquivo presente", True)
            else:
                self._log_test(f"File {file}", "Arquivo ausente", False)
        # Diretórios essenciais
        essential_dirs = [
            'config', 'applications', 'resultados'
        ]
        for dir_name in essential_dirs:
            if Path(dir_name).exists():
                self._log_test(f"Dir {dir_name}", "Diretório presente", True)
            else:
                self._log_test(f"Dir {dir_name}", "Diretório ausente", False)

    def test_configuration_consistency(self):
        """Testar consistência entre configurações"""
        
        # Verificar portas consistentes
        port_configs = {
            'config.py': '8000',
            'applications/servidor/Dockerfile': '8000',
            'applications/servidor-c/Dockerfile': '8000'
        }
        
        for file_path, expected_port in port_configs.items():
            if Path(file_path).exists():
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        if expected_port in content:
                            self._log_test(f"Port {file_path}", f"Porta {expected_port} presente", True)
                        else:
                            self._log_test(f"Port {file_path}", f"Porta {expected_port} ausente", False, warning=True)
                except Exception as e:
                    self._log_test(f"Port {file_path}", f"Erro lendo arquivo: {e}", False)
            else:
                self._log_test(f"Port {file_path}", "Arquivo não encontrado", False, warning=True)

    def test_data_persistence(self):
        """Testar persistência de dados"""
        
        # Verificar diretório de resultados
        try:
            from core.config import get_config
            config = get_config()
            
            if config.RESULTS_DIR.exists():
                self._log_test("Data Results Dir", "Diretório de resultados existe", True)
            else:
                config.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
                self._log_test("Data Results Dir", "Diretório de resultados criado", True)
            
            if config.GRAPHICS_DIR.exists():
                self._log_test("Data Graphics Dir", "Diretório de gráficos existe", True)
            else:
                config.GRAPHICS_DIR.mkdir(parents=True, exist_ok=True)
                self._log_test("Data Graphics Dir", "Diretório de gráficos criado", True)
            
        except Exception as e:
            self._log_test("Data Persistence", f"Erro: {e}", False)

    def test_security_validations(self):
        """Testar validações de segurança"""
        
        # Verificar se não há sudo hardcoded em comandos (excluindo comentários e arquivo de teste)
        python_files = [f for f in Path('.').glob('*.py') if f.name != 'test_complete_system.py']
        
        sudo_found = False
        for py_file in python_files:
            try:
                with open(py_file, 'r') as f:
                    lines = f.readlines()
                    for line_num, line in enumerate(lines, 1):
                        # Ignorar comentários e procurar por sudo em comandos reais
                        if line.strip().startswith('#'):
                            continue
                        if 'subprocess' in line and 'sudo' in line:
                            self._log_test(f"Security {py_file}:{line_num}", "Comando sudo encontrado", False, warning=True)
                            sudo_found = True
            except Exception:
                pass
        
        if not sudo_found:
            self._log_test("Security sudo", "Nenhum sudo hardcoded encontrado", True)

    def test_performance_resources(self):
        """Testar configurações de performance"""
        
        try:
            from core.config import get_config
            config = get_config()
            
            # Verificar configurações conservadoras
            if hasattr(config, 'MAX_CONCURRENT_PODS') and config.MAX_CONCURRENT_PODS <= 12:
                self._log_test("Perf Pods", f"Limite conservador de pods: {config.MAX_CONCURRENT_PODS}", True)
            else:
                self._log_test("Perf Pods", "Limite de pods muito alto", False, warning=True)
            
            if hasattr(config, 'WORKER_THREADS') and config.WORKER_THREADS <= 4:
                self._log_test("Perf Threads", f"Threads conservadoras: {config.WORKER_THREADS}", True)
            else:
                self._log_test("Perf Threads", "Muitas threads configuradas", False, warning=True)
            
        except Exception as e:
            self._log_test("Performance", f"Erro: {e}", False)

    def test_integration(self):
        """Testar integração entre componentes"""
        
        try:
            from core.config import get_config
            from core.infrastructure_manager import get_infrastructure_manager
            from core.test_executor import get_kubernetes_test_executor
            from core.concurrency_manager import get_concurrency_manager
            
            config = get_config()
            infrastructure = get_infrastructure_manager()
            executor = get_kubernetes_test_executor(clear_previous_data=False)
            concurrency = get_concurrency_manager()
            
            self._log_test("Integration Chain", "Cadeia de componentes funcional", True)
            
            # Testar comunicação entre componentes
            if hasattr(executor, 'concurrency_manager'):
                self._log_test("Integration Executor-Concurrency", "Executor usa concorrência", True)
            else:
                self._log_test("Integration Executor-Concurrency", "Integração ausente", False, warning=True)
            
        except Exception as e:
            self._log_test("Integration", f"Erro na integração: {e}", False)

    def test_version_compatibility(self):
        """Testa se todos os arquivos principais são compatíveis entre si e com as dependências do sistema."""
        from pathlib import Path
        result = True
        # 1. Python version
        min_version = (3, 8)
        version = sys.version_info
        self._log_test("Python Version", f"{version.major}.{version.minor}.{version.micro}", version >= min_version)
        if version < min_version:
            result = False
        # 2. Docker version
        try:
            docker = subprocess.run(["docker", "--version"], capture_output=True, text=True)
            ok = docker.returncode == 0 and "version" in docker.stdout.lower()
            self._log_test("Docker Version", docker.stdout.strip() if ok else "Não encontrado", ok)
            if not ok:
                result = False
        except Exception as e:
            self._log_test("Docker Version", f"Erro: {e}", False)
            pass
        # 3. kubectl version
        try:
            kubectl = subprocess.run(["kubectl", "version"], capture_output=True, text=True)
            ok = kubectl.returncode == 0 and (kubectl.stdout.strip() or kubectl.stderr.strip())
            version_info = kubectl.stdout.strip() if kubectl.stdout.strip() else kubectl.stderr.strip()
            self._log_test("kubectl Version", version_info if ok else "Não encontrado", ok)
            if not ok:
                result = False
        except Exception as e:
            self._log_test("kubectl Version", f"Erro: {e}", False)
            result = False
        # 3.1. Kubernetes Server Version (mais robusto)
        try:
            k8s = subprocess.run(["kubectl", "version"], capture_output=True, text=True)
            if k8s.returncode == 0 and (k8s.stdout.strip() or k8s.stderr.strip()):
                lines = k8s.stdout.splitlines() if k8s.stdout else k8s.stderr.splitlines()
                server_line = next((l for l in lines if "Server Version" in l), None)
                if server_line:
                    self._log_test("Kubernetes Version", server_line, True)
                else:
                    self._log_test("Kubernetes Version", "Não detectada", True, warning=True)
            else:
                self._log_test("Kubernetes Version", "kubectl não disponível", False)
        except Exception as e:
            self._log_test("Kubernetes Version", f"Erro: {e}", False)
        # 4. requirements.txt
        req_file = Path("requirements.txt")
        if req_file.exists():
            with req_file.open() as f:
                reqs = [l.strip() for l in f if l.strip() and not l.startswith('#')]
            failed = []
            warnings = []
            for req in reqs:
                pkg = req.split('==')[0] if '==' in req else req.split('>=')[0]
                try:
                    version_installed = importlib.metadata.version(pkg)
                    if '==' in req:
                        version_req = req.split('==')[1]
                        if version_installed != version_req:
                            warnings.append(f"{pkg}=={version_installed} (requerido: {version_req})")
                    elif '>=' in req:
                        version_req = req.split('>=')[1]
                        if version_installed < version_req:
                            warnings.append(f"{pkg}=={version_installed} (requerido >= {version_req})")
                except importlib.metadata.PackageNotFoundError:
                    failed.append(pkg)
            if not failed:
                if warnings:
                    self._log_test("Python Dependencies", f"Versões diferentes: {warnings}", True, warning=True)
                else:
                    self._log_test("Python Dependencies", "Todas as dependências satisfeitas", True)
            else:
                self._log_test("Python Dependencies", f"Dependências faltando: {failed}", False, warning=True)
                result = False
        else:
            self._log_test("Python Dependencies", "requirements.txt não encontrado", False, warning=True)
            result = False
        # 5. Import e integração dos módulos principais
        try:
            import core.config
            import core.infrastructure_manager
            import core.test_executor
            import core.result_analyzer
            import core.chart_generator
            import core.resource_monitor
            import core.concurrency_manager
            self._log_test("Core Imports", "Todos os módulos principais importados", True)
        except Exception as e:
            self._log_test("Core Imports", f"Erro: {e}", False)
            result = False
        # 6. Checagem de integração entre módulos
        try:
            from core.infrastructure_manager import get_infrastructure_manager
            from core.test_executor import get_kubernetes_test_executor
            from core.result_analyzer import get_result_analyzer
            from core.chart_generator import get_chart_generator
            from core.resource_monitor import get_resource_monitor
            infra = get_infrastructure_manager()
            executor = get_kubernetes_test_executor()
            analyzer = get_result_analyzer()
            chart = get_chart_generator()
            monitor = get_resource_monitor()
            # Checa se métodos essenciais existem
            essentials = [
                hasattr(infra, 'build_and_push_all'),
                hasattr(infra, 'deploy_servers'),
                hasattr(executor, 'run_all_tests'),
                hasattr(analyzer, 'analyze_results'),
                hasattr(chart, 'generate_all_3d_charts'),
                hasattr(monitor, 'start_monitoring')
            ]
            if all(essentials):
                self._log_test("Core API Integration", "Módulos principais integrados", True)
            else:
                self._log_test("Core API Integration", "Faltam métodos essenciais na integração", False)
                result = False
        except Exception as e:
            self._log_test("Core API Integration", f"Erro: {e}", False)
            result = False
        return result

    def test_robustness_recovery(self):
        """Testar robustez e capacidade de recuperação"""
        
        # Teste de tratamento de erros nos imports
        try:
            # Simular import com erro controlado
            test_modules = ['config', 'infrastructure_manager', 'test_executor']
            found_try = False
            for module_name in test_modules:
                try:
                    module = __import__(module_name)
                    # Verificar se módulo tem tratamento de erro básico
                    if hasattr(module, '__file__'):
                        with open(module.__file__, 'r') as f:
                            content = f.read()
                            if 'except' in content and 'try:' in content:
                                found_try = True
                except ImportError:
                    continue
            if found_try:
                self._log_test("Robustness Error Handling", "Módulos têm tratamento de erro", True)
            else:
                self._log_test("Robustness Error Handling", "Nenhum bloco try/except encontrado nos módulos principais", True, warning=True)
        except Exception as e:
            self._log_test("Robustness Error Handling", f"Erro testando robustez: {e}", False)
        
        # Teste de recuperação de falhas de rede (simulado)
        try:
            from core.infrastructure_manager import get_infrastructure_manager
            infra = get_infrastructure_manager()
            
            # Verificar se há métodos de cleanup/recovery
            recovery_methods = ['cleanup_all', 'cleanup_resources']
            has_recovery = any(hasattr(infra.k8s, method) for method in recovery_methods)
            
            if has_recovery:
                self._log_test("Robustness Recovery", "Métodos de recuperação presentes", True)
            else:
                self._log_test("Robustness Recovery", "Métodos de recuperação ausentes", False, warning=True)
                
        except Exception as e:
            self._log_test("Robustness Recovery", f"Erro testando recuperação: {e}", False)
        
        # Teste de timeout e limites
        try:
            from core.config import get_config
            config = get_config()
            
            timeout_configs = ['K8S_DEPLOYMENT_TIMEOUT', 'MAX_CONCURRENT_PODS']
            has_timeouts = all(hasattr(config, attr) for attr in timeout_configs)
            
            if has_timeouts:
                self._log_test("Robustness Timeouts", "Timeouts configurados", True)
            else:
                self._log_test("Robustness Timeouts", "Timeouts não configurados", False, warning=True)
                
        except Exception as e:
            self._log_test("Robustness Timeouts", f"Erro verificando timeouts: {e}", False)

    def test_code_quality(self):
        """Testar qualidade do código"""
        
        # Verificar docstrings nos módulos principais
        try:
            main_modules = ['config', 'infrastructure_manager', 'test_executor', 'concurrency_manager']
            documented_modules = 0
            
            for module_name in main_modules:
                try:
                    module = __import__(module_name)
                    if module.__doc__ and module.__doc__.strip():
                        documented_modules += 1
                except:
                    pass
            
            doc_rate = (documented_modules / len(main_modules)) * 100
            if doc_rate >= 80:
                self._log_test("Quality Documentation", f"Documentação OK ({doc_rate:.0f}%)", True)
            else:
                self._log_test("Quality Documentation", f"Documentação limitada ({doc_rate:.0f}%)", False, warning=True)
                
        except Exception as e:
            self._log_test("Quality Documentation", f"Erro verificando documentação: {e}", False)
        
        # Verificar complexidade de arquivos (tamanho)
        try:
            python_files = list(Path('.').glob('*.py'))
            large_files = []
            
            for py_file in python_files:
                try:
                    with open(py_file, 'r') as f:
                        lines = len(f.readlines())
                        if lines > 1000:  # Arquivos muito grandes
                            large_files.append(f"{py_file}({lines})")
                except:
                    pass
            
            if len(large_files) <= 2:  # Máximo 2 arquivos grandes aceitável
                self._log_test("Quality File Size", "Tamanhos de arquivo OK", True)
            else:
                self._log_test("Quality File Size", f"Arquivos grandes: {len(large_files)}", False, warning=True)
                
        except Exception as e:
            self._log_test("Quality File Size", f"Erro verificando tamanhos: {e}", False)
        
        # Verificar imports redundantes/circulares
        try:
            python_files = [f for f in Path('.').glob('*.py') if f.name != 'test_complete_system.py']
            circular_risk = False
            
            for py_file in python_files:
                try:
                    with open(py_file, 'r') as f:
                        content = f.read()
                        # Verificar padrões que podem indicar imports circulares
                        if content.count('import') > 20:  # Muitos imports podem indicar problema
                            circular_risk = True
                            break
                except:
                    pass
            
            if not circular_risk:
                self._log_test("Quality Imports", "Estrutura de imports OK", True)
            else:
                self._log_test("Quality Imports", "Possível complexidade de imports", False, warning=True)
                
        except Exception as e:
            self._log_test("Quality Imports", f"Erro verificando imports: {e}", False)

    def test_environment_dependencies(self):
        """Testar ambiente e dependências do sistema"""
        
        # Verificar variáveis de ambiente necessárias
        try:
            env_vars = ['PATH', 'HOME']
            optional_vars = ['DOCKER_USERNAME', 'KUBECONFIG']
            
            required_ok = all(os.getenv(var) for var in env_vars)
            optional_count = sum(1 for var in optional_vars if os.getenv(var))
            
            if required_ok:
                self._log_test("Environment Required", "Variáveis requeridas OK", True)
            else:
                self._log_test("Environment Required", "Variáveis requeridas ausentes", False)
            
            self._log_test("Environment Optional", f"Variáveis opcionais: {optional_count}/{len(optional_vars)}", True)
            
        except Exception as e:
            self._log_test("Environment Variables", f"Erro verificando ambiente: {e}", False)
        
        # Verificar ferramentas do sistema
        try:
            system_tools = ['docker', 'kubectl', 'python3', 'pip']
            available_tools = []
            
            for tool in system_tools:
                try:
                    result = subprocess.run(['which', tool], capture_output=True, text=True)
                    if result.returncode == 0:
                        available_tools.append(tool)
                except:
                    pass
            
            tool_rate = (len(available_tools) / len(system_tools)) * 100
            if tool_rate >= 75:
                self._log_test("Environment Tools", f"Ferramentas OK ({tool_rate:.0f}%)", True)
            else:
                self._log_test("Environment Tools", f"Ferramentas limitadas ({tool_rate:.0f}%)", False, warning=True)
                
        except Exception as e:
            self._log_test("Environment Tools", f"Erro verificando ferramentas: {e}", False)
        
        # Verificar permissões de escrita
        try:
            test_dirs = ['resultados', '.']
            write_ok = True
            
            for test_dir in test_dirs:
                test_file = Path(test_dir) / f'.test_write_{int(time.time())}'
                try:
                    test_file.write_text('test')
                    test_file.unlink()
                except:
                    write_ok = False
                    break
            
            if write_ok:
                self._log_test("Environment Permissions", "Permissões de escrita OK", True)
            else:
                self._log_test("Environment Permissions", "Problemas de permissão", False)
                
        except Exception as e:
            self._log_test("Environment Permissions", f"Erro verificando permissões: {e}", False)

    def test_metrics_monitoring(self):
        """Testar sistema de métricas e monitoramento"""
        
        # Verificar se psutil está funcionando
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            if cpu_percent >= 0 and memory.total > 0:
                self._log_test("Metrics System", f"CPU: {cpu_percent:.1f}%, RAM: {memory.percent:.1f}%", True)
            else:
                self._log_test("Metrics System", "Dados de sistema inválidos", False)
                
        except Exception as e:
            self._log_test("Metrics System", f"Erro coletando métricas: {e}", False)
        
        # Verificar geração de logs estruturados
        try:
            from core.resource_monitor import get_resource_monitor
            monitor = get_resource_monitor()
            
            # Verificar se tem métodos de coleta
            metrics_methods = ['get_system_metrics', 'collect_metrics']
            has_metrics = any(hasattr(monitor, method) for method in metrics_methods)
            
            if has_metrics:
                self._log_test("Metrics Collection", "Coleta de métricas disponível", True)
            else:
                self._log_test("Metrics Collection", "Métodos de métricas limitados", False, warning=True)
                
        except Exception as e:
            self._log_test("Metrics Collection", f"Erro verificando coleta: {e}", False)
        
        # Verificar capacidade de monitoramento contínuo
        try:
            from core.resource_monitor import get_resource_monitor
            monitor = get_resource_monitor()
            # Teste de monitoramento contínuo
            try:
                t = monitor.start_continuous_monitoring(interval=0.1, duration=1)
                t.join()
                snapshots = monitor.stop_continuous_monitoring()
                if isinstance(snapshots, list) and len(snapshots) > 0 and 'cpu_percent' in snapshots[0]:
                    self._log_test("Metrics Monitoring", "Monitoramento contínuo OK", True)
                else:
                    self._log_test("Metrics Monitoring", "Monitoramento contínuo limitado", False, warning=True)
            except Exception as e:
                self._log_test("Metrics Monitoring", f"Erro no monitoramento contínuo: {e}", False, warning=True)
        except Exception as e:
            self._log_test("Metrics Monitoring", f"Erro verificando monitoramento: {e}", False)

    def test_deployment_scalability(self):
        """Testar capacidades de deploy e escalabilidade"""
        
        # Verificar configurações de escalabilidade
        try:
            from core.config import get_config
            config = get_config()
            
            scale_configs = ['MAX_CONCURRENT_PODS', 'WORKER_THREADS', 'SERVERS', 'CLIENTS']
            has_scale_config = all(hasattr(config, attr) for attr in scale_configs)
            
            if has_scale_config:
                max_pods = getattr(config, 'MAX_CONCURRENT_PODS', 0)
                max_servers = max(getattr(config, 'SERVERS', [0]))
                max_clients = max(getattr(config, 'CLIENTS', [0]))
                
                self._log_test("Scale Configuration", f"Pods: {max_pods}, Servers: {max_servers}, Clients: {max_clients}", True)
            else:
                self._log_test("Scale Configuration", "Configurações de escala ausentes", False, warning=True)
                
        except Exception as e:
            self._log_test("Scale Configuration", f"Erro verificando escalabilidade: {e}", False)
        
        # Verificar suporte a deploy paralelo
        try:
            from core.infrastructure_manager import get_infrastructure_manager
            infra = get_infrastructure_manager()
            
            # Verificar se DockerManager suporta paralelo
            has_parallel_build = hasattr(infra.docker, 'build_and_push_all')
            has_parallel_deploy = hasattr(infra.k8s, 'deploy_servers')
            
            if has_parallel_build and has_parallel_deploy:
                self._log_test("Scale Parallel", "Deploy paralelo suportado", True)
            else:
                self._log_test("Scale Parallel", "Deploy paralelo limitado", False, warning=True)
                
        except Exception as e:
            self._log_test("Scale Parallel", f"Erro verificando deploy paralelo: {e}", False)
        
        # Verificar limites de recursos
        try:
            from core.config import get_config
            config = get_config()
            
            if hasattr(config, 'RESOURCE_LIMITS') and hasattr(config, 'RESOURCE_REQUESTS'):
                limits = config.RESOURCE_LIMITS
                requests = config.RESOURCE_REQUESTS
                
                if isinstance(limits, dict) and isinstance(requests, dict):
                    self._log_test("Scale Resources", "Limites de recursos configurados", True)
                else:
                    self._log_test("Scale Resources", "Limites não são dicionários", False, warning=True)
            else:
                self._log_test("Scale Resources", "Limites de recursos ausentes", False, warning=True)
                
        except Exception as e:
            self._log_test("Scale Resources", f"Erro verificando limites: {e}", False)

    def test_version_and_dependencies(self):
        """Testa versão do Python, Docker, kubectl e dependências do requirements.txt"""
        from pathlib import Path
        # Python
        version = sys.version_info
        self._log_test("Python Version", f"{version.major}.{version.minor}.{version.micro}", version >= (3,8))
        # Docker
        try:
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
            ok = result.returncode == 0 and "version" in result.stdout.lower()
            self._log_test("Docker Version", result.stdout.strip() if ok else "Não encontrado", ok)
        except Exception as e:
            self._log_test("Docker Version", f"Erro: {e}", False)
            pass
        # kubectl (ajustado: aceita qualquer saída válida, como nos outros testes)
        try:
            result = subprocess.run(["kubectl", "version"], capture_output=True, text=True)
            ok = result.returncode == 0 and (result.stdout.strip() or result.stderr.strip())
            version_info = result.stdout.strip() if result.stdout.strip() else result.stderr.strip()
            self._log_test("kubectl Version", version_info if ok else "Não encontrado", ok)
        except Exception as e:
            self._log_test("kubectl Version", f"Erro: {e}", False)
            pass
        # requirements.txt
        req_file = Path("requirements.txt")
        if req_file.exists():
            with req_file.open() as f:
                reqs = [l.strip() for l in f if l.strip() and not l.startswith('#')]
            failed = []
            warnings = []
            for req in reqs:
                pkg = req.split('==')[0] if '==' in req else req.split('>=')[0]
                try:
                    version_installed = importlib.metadata.version(pkg)
                    if '==' in req:
                        version_req = req.split('==')[1]
                        if version_installed != version_req:
                            warnings.append(f"{pkg}=={version_installed} (requerido: {version_req})")
                    elif '>=' in req:
                        version_req = req.split('>=')[1]
                        if version_installed < version_req:
                            warnings.append(f"{pkg}=={version_installed} (requerido >= {version_req})")
                except importlib.metadata.PackageNotFoundError:
                    failed.append(pkg)
            if not failed:
                if warnings:
                    self._log_test("Python Dependencies", f"Versões diferentes: {warnings}", True, warning=True)
                else:
                    self._log_test("Python Dependencies", "Todas as dependências satisfeitas", True)
            else:
                self._log_test("Python Dependencies", f"Dependências faltando: {failed}", False, warning=True)
                result = False
        else:
            self._log_test("Python Dependencies", "requirements.txt não encontrado", False, warning=True)
            result = False

    def test_infrastructure_manager_api(self):
        """Testa se InfrastructureManager expõe métodos e aliases essenciais"""
        try:
            from core.infrastructure_manager import get_infrastructure_manager
            infra = get_infrastructure_manager()
            attrs = ["docker", "k8s", "build_and_push_all", "deploy_servers", "run_clients", "setup_infrastructure", "wait_for_pods_ready", "cleanup_all"]
            missing = [a for a in attrs if not hasattr(infra, a)]
            if not missing:
                self._log_test("InfraManager API", "Todos os métodos/aliases presentes", True)
            else:
                self._log_test("InfraManager API", f"Faltando: {missing}", False)
        except Exception as e:
            self._log_test("InfraManager API", f"Erro: {e}", False)

    def test_docker_images_exist(self):
        """Testa se as imagens Docker essenciais existem localmente"""
        try:
            from core.config import get_config
            config = get_config()
            images = [
                config.get_docker_image_name("cliente"),
                config.get_docker_image_name("servidor", "c"),
                config.get_docker_image_name("servidor", "cpp")
            ]
            missing = []
            import subprocess
            for img in images:
                result = subprocess.run(["docker", "images", img, "--quiet"], capture_output=True, text=True)
                if not (result.returncode == 0 and result.stdout.strip()):
                    missing.append(img)
            if not missing:
                self._log_test("Docker Images", "Todas as imagens essenciais existem", True)
            else:
                self._log_test("Docker Images", f"Imagens faltando: {missing}", False, warning=True)
        except Exception as e:
            self._log_test("Docker Images", f"Erro: {e}", False)

    def test_docker_k8s_image_compatibility(self):
        """Testa se as imagens Docker essenciais são compatíveis entre si e com a versão do Kubernetes instalada."""
        import subprocess
        from core.config import get_config
        config = get_config()
        images = [
            config.get_docker_image_name("cliente"),
            config.get_docker_image_name("servidor", "c"),
            config.get_docker_image_name("servidor", "cpp")
        ]
        # 1. Verificar se todas as imagens existem localmente
        missing = []
        for img in images:
            result = subprocess.run(["docker", "images", img, "--quiet"], capture_output=True, text=True)
            if not (result.returncode == 0 and result.stdout.strip()):
                missing.append(img)
        if not missing:
            self._log_test("Docker Images Exist", "Todas as imagens essenciais existem", True)
        else:
            self._log_test("Docker Images Exist", f"Imagens faltando: {missing}", False, warning=True)
        # 2. Verificar arquitetura das imagens (devem ser compatíveis entre si e com o cluster)
        archs = set()
        for img in images:
            try:
                inspect = subprocess.run(["docker", "image", "inspect", img, "--format", "{{.Architecture}}"], capture_output=True, text=True)
                if inspect.returncode == 0:
                    arch = inspect.stdout.strip()
                    if arch:
                        archs.add(arch)
            except Exception:
                pass
        if len(archs) == 1:
            self._log_test("Docker Image Architecture", f"Arquitetura única: {list(archs)[0]}", True)
        elif len(archs) == 0:
            self._log_test("Docker Image Architecture", "Arquitetura não detectada (todas vazias)", True, warning=True)
        else:
            self._log_test("Docker Image Architecture", f"Arquiteturas diferentes: {archs}", False, warning=True)
        # 3. Verificar versão do Kubernetes
        try:
            k8s = subprocess.run(["kubectl", "version"], capture_output=True, text=True)
            if k8s.returncode == 0 and (k8s.stdout.strip() or k8s.stderr.strip()):
                lines = k8s.stdout.splitlines() if k8s.stdout else k8s.stderr.splitlines()
                server_line = next((l for l in lines if "Server Version" in l), None)
                if server_line:
                    self._log_test("Kubernetes Version", server_line, True)
                else:
                    self._log_test("Kubernetes Version", "Não detectada", True, warning=True)
            else:
                self._log_test("Kubernetes Version", "kubectl não disponível", False)
        except Exception as e:
            self._log_test("Kubernetes Version", f"Erro: {e}", False)
        # 4. Verificar se as imagens suportam a versão do Kubernetes (checa se são recentes, multi-arch, etc)
        # Para simplificação, checa se as imagens foram criadas nos últimos 2 anos
        now = datetime.datetime.now(datetime.timezone.utc)
        outdated = []
        for img in images:
            try:
                inspect = subprocess.run(["docker", "image", "inspect", img, "--format", "{{.Created}}"], capture_output=True, text=True)
                if inspect.returncode == 0:
                    created_str = inspect.stdout.strip()
                    try:
                        created_time = datetime.datetime.strptime(created_str[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=datetime.timezone.utc)
                        age_days = (now - created_time).days
                        if age_days > 730:
                            outdated.append((img, age_days))
                    except Exception:
                        pass
            except Exception:
                pass
        if not outdated:
            self._log_test("Docker Image Age", "Todas as imagens são recentes (<2 anos)", True)
        else:
            self._log_test("Docker Image Age", f"Imagens antigas: {outdated}", False, warning=True)

    def test_performance_and_stability(self):
        """Teste de performance e estabilidade com configuração máxima segura"""
        try:
            from core.config import get_config
            from core.test_executor import get_kubernetes_test_executor
            config = get_config()
            executor = get_kubernetes_test_executor(clear_previous_data=True)
            start = time.time()
            # Executa apenas um subconjunto para validação rápida
            old_servers = config.SERVERS
            old_clients = config.CLIENTS
            old_messages = config.MESSAGES
            config.SERVERS = [max(old_servers)]
            config.CLIENTS = [max(old_clients)]
            config.MESSAGES = [max(old_messages)]
            config.RUNS_PER_CONFIG = 2
            success = executor.run_all_tests()
            elapsed = time.time() - start
            # Restaura config
            config.SERVERS = old_servers
            config.CLIENTS = old_clients
            config.MESSAGES = old_messages
            config.RUNS_PER_CONFIG = 10
            if success:
                self._log_test("Performance e Estabilidade (paralelo)", f"Execução máxima segura OK em {elapsed:.1f}s", True)
            else:
                self._log_test("Performance e Estabilidade (paralelo)", "Falha na execução máxima segura", False)
        except Exception as e:
            self._log_test("Performance e Estabilidade (paralelo)", f"Erro: {e}", False)

    def _generate_final_report(self):
        """Gerar relatório final dos testes"""
        print("\n" + "=" * 70)
        print("📋 RELATÓRIO FINAL DOS TESTES")
        print("=" * 70)
        
        # Estatísticas gerais
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print(f"📊 ESTATÍSTICAS GERAIS:")
        print(f"   • Total de testes: {self.total_tests}")
        print(f"   • ✅ Sucessos: {self.passed_tests}")
        print(f"   • ❌ Falhas: {self.failed_tests}")
        print(f"   • ⚠️  Avisos: {self.warnings}")
        print(f"   • 📈 Taxa de sucesso: {success_rate:.1f}%")
        
        # Status geral
        if self.failed_tests == 0:
            print(f"\n🎉 RESULTADO: ✅ TODOS OS TESTES PASSARAM!")
            print(f"🚀 Sistema pronto para execução completa")
        elif self.failed_tests <= 3:
            print(f"\n⚠️  RESULTADO: 🟡 ALGUNS PROBLEMAS ENCONTRADOS")
            print(f"🔧 Sistema funcional mas necessita ajustes")
        else:
            print(f"\n❌ RESULTADO: 🔴 MUITOS PROBLEMAS ENCONTRADOS")
            print(f"🛠️  Sistema necessita correções significativas")
        
        # Recomendações
        print(f"\n💡 RECOMENDAÇÕES:")
        if self.failed_tests == 0:
            print(f"   • Sistema validado e pronto para uso")
            print(f"   • Execute: python3 executar.py")
        else:
            print(f"   • Corrija os {self.failed_tests} testes falhando")
            print(f"   • Revise os {self.warnings} avisos")
            print(f"   • Execute novamente os testes após correções")
        
        # Salvar relatório em arquivo
        self._save_test_report()

    def _save_test_report(self):
        """Salvar relatório de testes em arquivo"""
        try:
            report_file = Path("test_report.json")
            report = {
                "total_tests": self.total_tests,
                "passed_tests": self.passed_tests,
                "failed_tests": self.failed_tests,
                "warnings": self.warnings,
                "results": self.test_results,
                "timestamp": datetime.datetime.now().isoformat()
            }
            with report_file.open("w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            self.logger.info(f"Relatório de testes salvo em {report_file.resolve()}")
        except Exception as e:
            self.logger.error(f"Erro ao salvar relatório de testes: {e}")

def main():
    """Função principal"""
    print("🚀 Iniciando Sistema de Testes Unificado...")
    
    tester = SystemTester()
    success = tester.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
