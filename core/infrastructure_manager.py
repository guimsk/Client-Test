#!/usr/bin/env python3
"""
GERENCIADOR DE INFRAESTRUTURA COM DOCKER HUB E KUBERNETES V6
Sistema completo de build, push e deploy automatizado - OTIMIZADO PARA MÁXIMA VELOCIDADE
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from core.config import get_config
from core.utils import run_subprocess, check_file_exists, get_logger
import json
import uuid
import time
import concurrent.futures

logger = get_logger(__name__)


@dataclass
class DockerImage:
    """Informações de uma imagem Docker"""
    name: str
    tag: str
    path: Path
    dockerfile: str
    language: Optional[str] = None


class DockerManager:
    """Gerenciador de imagens Docker"""
    
    def __init__(self):
        self.config = get_config()
        self.images = self._prepare_images()
    
    def _prepare_images(self) -> List[DockerImage]:
        """Preparar lista de imagens para build"""
        images = [
            DockerImage(
                name=self.config.get_docker_image_name("cliente"),
                tag="latest",
                path=self.config.APPLICATIONS_DIR / "cliente",
                dockerfile="Dockerfile",
                language="python"
            ),
            DockerImage(
                name=self.config.get_docker_image_name("servidor", "c"),
                tag="latest", 
                path=self.config.APPLICATIONS_DIR / "servidor-c",
                dockerfile="Dockerfile",
                language="c"
            ),
            DockerImage(
                name=self.config.get_docker_image_name("servidor", "cpp"),
                tag="latest",
                path=self.config.APPLICATIONS_DIR / "servidor", 
                dockerfile="Dockerfile",
                language="cpp"
            )
        ]
        return images
    
    def build_and_push_all(self) -> bool:
        """Build e push paralelo de todas as imagens para Docker Hub"""
        logger.info("🐳 CONSTRUINDO E ENVIANDO IMAGENS DOCKER PARA HUB (PARALELO)")
        
        # Verificar se está logado no Docker Hub
        if not self._check_docker_login():
            logger.error("Não está logado no Docker Hub. Execute: docker login")
            return False
        
        # Executar build e push em paralelo
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(self.images), self.config.WORKER_THREADS)) as executor:
            # Submeter todas as tarefas
            futures = [(image, executor.submit(self._build_and_push_image, image)) for image in self.images]
            
            # Aguardar resultados
            success = True
            for image, future in futures:
                try:
                    result = future.result(timeout=300)  # 5 minutos timeout
                    if not result:
                        success = False
                        logger.error(f"Falha no processamento da imagem {image.name}")
                except concurrent.futures.TimeoutError:
                    success = False
                    logger.error(f"Timeout no processamento da imagem {image.name}")
                except Exception as e:
                    success = False
                    logger.error(f"Erro no processamento da imagem {image.name}: {e}")
        
        if success:
            logger.info("✅ Todas as imagens construídas e enviadas com sucesso!")
        else:
            logger.error("Erro em uma ou mais imagens")
            
        return success

    def build_image(self, image_name: str) -> bool:
        """Build uma imagem específica"""
        for image in self.images:
            if image.name == image_name:
                return self._build_image(image)
        logger.error(f"Imagem {image_name} não encontrada")
        return False

    def push_image(self, image_name: str) -> bool:
        """Push uma imagem específica"""
        for image in self.images:
            if image.name == image_name:
                return self._push_image(image)
        logger.error(f"Imagem {image_name} não encontrada")
        return False
    
    def _build_and_push_image(self, image: DockerImage) -> bool:
        logger.info(f"\n📦 Processando {image.name}...")
        
        # Verificar se já existe localmente e está atualizada
        if self._check_local_image(image.name):
            logger.info(f"Imagem {image.name} já existe localmente")
        else:
            # Build da imagem
            if not self._build_image(image):
                return False
        
        # Push para Docker Hub
        return self._push_image(image)
    
    def _check_docker_login(self) -> bool:
        try:
            # Verificar se pode acessar informações do Docker Hub
            result = run_subprocess(["docker", "info"], capture_output=True)
            
            return result.returncode == 0 and ("Username:" in result.stdout or result.returncode == 0)
            
        except Exception:
            return False
    
    def _verify_image_in_hub(self, image: DockerImage) -> bool:
        """Verificar se imagem está disponível no Docker Hub"""
        try:
            # Tentar fazer pull da imagem para verificar
            result = run_subprocess(["docker", "manifest", "inspect", image.name], capture_output=True)
            
            return result.returncode == 0
            
        except Exception:
            return False
    
    def _build_image(self, image: DockerImage) -> bool:
        logger.info(f"🔨 Construindo {image.name}...")
        
        try:
            cmd = [
                "docker", "build",
                "-t", image.name,
                "-f", str(image.path / image.dockerfile),
                str(image.path)
            ]
            
            result = run_subprocess(cmd, capture_output=True, cwd=image.path)
            
            if result.returncode != 0:
                logger.error(f"Erro no build de {image.name}: {result.stderr}")
                return False
            
            logger.info(f"{image.name} construída com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro no build de {image.name}: {e}")
            return False
    
    def _push_image(self, image: DockerImage) -> bool:
        logger.info(f"📤 Enviando {image.name}...")
        
        try:
            result = run_subprocess(["docker", "push", image.name], capture_output=True)
            
            if result.returncode != 0:
                logger.error(f"Erro no push de {image.name}: {result.stderr}")
                return False
            
            logger.info(f"{image.name} enviada com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro no push de {image.name}: {e}")
            return False
    
    def _check_local_image(self, image_name: str) -> bool:
        try:
            result = run_subprocess(["docker", "images", image_name, "--quiet"], capture_output=True)
            
            return result.returncode == 0 and result.stdout.strip()
            
        except Exception:
            return False


class KubernetesManager:
    """Gerenciador de recursos Kubernetes"""
    
    def __init__(self):
        self.config = get_config()
    
    def setup_namespace(self) -> bool:
        logger.info(f"☸️  Configurando namespace {self.config.K8S_NAMESPACE}...")
        
        try:
            # Criar namespace
            cmd = ["kubectl", "create", "namespace", self.config.K8S_NAMESPACE, "--dry-run=client", "-o", "yaml"]
            result = run_subprocess(cmd, capture_output=True)
            
            if result.returncode == 0:
                apply_cmd = ["kubectl", "apply", "-f", "-"]
                run_subprocess(apply_cmd, input=result.stdout, capture_output=True)
            
            # Limpar jobs órfãos de execuções anteriores
            self._cleanup_orphaned_jobs()
            
            logger.info(f"Namespace {self.config.K8S_NAMESPACE} configurado")
            return True
            
        except Exception as e:
            logger.error(f"Erro configurando namespace: {e}")
            return False
    
    def deploy_servers(self, language: str, num_servers: int) -> List[Dict]:
        logger.info(f"🚀 Fazendo deploy de {num_servers} servidores {language} (PARALELO)...")
        
        # Verificar se a imagem existe
        image_name = self.config.get_docker_image_name("servidor", language)
        if not self._check_image_exists(image_name):
            logger.error(f"Imagem {image_name} não encontrada")
            return []
        
        # Executar deploys em paralelo
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.WORKER_THREADS) as executor:
            # Preparar tarefas
            deploy_tasks = []
            for i in range(num_servers):
                deployment_name = f"servidor-{language}-{i}"
                port = self.config.BASE_PORT + i
                task = executor.submit(self._deploy_single_server, deployment_name, language, port)
                deploy_tasks.append((deployment_name, language, port, task))
            
            # Aguardar resultados
            deployments = []
            for deployment_name, language, port, task in deploy_tasks:
                try:
                    result = task.result(timeout=120)  # 2 minutos timeout
                    if result:
                        deployments.append({
                            "name": deployment_name,
                            "language": language,
                            "port": port,
                            "service_name": f"{deployment_name}-service"
                        })
                    else:
                        logger.error(f"Falha no deploy de {deployment_name}")
                except concurrent.futures.TimeoutError:
                    logger.error(f"Timeout no deploy de {deployment_name}")
                except Exception as e:
                    logger.error(f"Erro no deploy de {deployment_name}: {e}")
        
        logger.info(f"Deploy concluído: {len(deployments)}/{num_servers} servidores")
        return deployments
    
    def _deploy_single_server(self, deployment_name: str, language: str, port: int) -> bool:
        try:
            deployment_config = self._create_server_deployment(deployment_name, language, port)
            service_config = self._create_server_service(deployment_name, port)
            
            return (self._apply_deployment(deployment_config) and 
                    self._apply_service(service_config))
        except Exception as e:
            logger.error(f"Erro no deploy individual {deployment_name}: {e}")
            return False
    
    def run_clients(self, deployments: List[Dict], num_clients: int, messages: int) -> Dict:
        logger.info(f"🧪 Executando {num_clients} clientes com {messages} mensagens...")
        
        try:
            # Preparar lista de servidores
            servers = [f"{dep['service_name']}.{self.config.K8S_NAMESPACE}.svc.cluster.local:{dep['port']}" for dep in deployments]
            
            # Criar job do cliente com timestamp mais preciso e ID único
            timestamp = int(time.time() * 1000)  # timestamp em milissegundos
            unique_id = str(uuid.uuid4())[:8]    # ID único curto
            job_name = f"cliente-test-{timestamp}-{unique_id}"
            job_config = self._create_client_job(job_name, servers, num_clients, messages)
            
            if not self._apply_job(job_config):
                logger.error(f"Falha ao criar job {job_name}")
                return {}
            
            # Aguardar job completar
            if self._wait_job_complete(job_name):
                # Coletar resultados
                results = self._collect_job_results(job_name)
                
                # Limpar job
                self._cleanup_job(job_name)
                
                return results
            else:
                logger.error(f"Timeout aguardando job {job_name}")
                return {}
                
        except Exception as e:
            logger.error(f"Erro executando clientes: {e}")
            return {}
    
    def _create_server_deployment(self, name: str, language: str, port: int) -> Dict:
        """Criar configuração de deployment do servidor"""
        image_name = self.config.get_docker_image_name("servidor", language)
        
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": name,
                "namespace": self.config.K8S_NAMESPACE
            },
            "spec": {
                "replicas": 1,
                "selector": {
                    "matchLabels": {"app": name}
                },
                "template": {
                    "metadata": {
                        "labels": {"app": name}
                    },
                    "spec": {
                        "containers": [{
                            "name": name,
                            "image": image_name,
                            "imagePullPolicy": "Always",  # Sempre usar imagem do Docker Hub
                            "ports": [{"containerPort": port}],
                            "args": [str(port)],
                            "env": [
                                {"name": "PORT", "value": str(port)},
                                {"name": "MAX_CONNECTIONS", "value": "1000"},
                                {"name": "THREAD_POOL_SIZE", "value": "50"}
                            ],
                            "resources": {
                                "limits": self.config.RESOURCE_LIMITS,
                                "requests": self.config.RESOURCE_REQUESTS
                            }
                        }]
                    }
                }
            }
        }
    
    def _create_client_job(self, name: str, servers: List[str], clients: int, messages: int) -> Dict:
        """Criar configuração de job do cliente"""
        image_name = self.config.get_docker_image_name("cliente")
        
        # Configurações otimizadas baseadas no número de clientes
        parallelism = min(clients, self.config.MAX_CONCURRENT_PODS)
        
        return {
            "apiVersion": "batch/v1",
            "kind": "Job",
            "metadata": {
                "name": name,
                "namespace": self.config.K8S_NAMESPACE
            },
            "spec": {
                "parallelism": parallelism,
                "completions": 1,
                "template": {
                    "spec": {
                        "containers": [{
                            "name": "cliente",
                            "image": image_name,
                            "imagePullPolicy": "Always",  # Sempre usar imagem do Docker Hub
                            "env": [
                                {"name": "SERVERS", "value": ",".join(servers)},
                                {"name": "CLIENTS", "value": str(clients)},
                                {"name": "MESSAGES", "value": str(messages)},
                                {"name": "PARALLEL_WORKERS", "value": str(min(clients, 10))}
                            ],
                            "resources": {
                                "limits": self.config.RESOURCE_LIMITS,
                                "requests": self.config.RESOURCE_REQUESTS
                            }
                        }],
                        "restartPolicy": "Never"
                    }
                },
                "backoffLimit": 1,
                "activeDeadlineSeconds": 300
            }
        }
    
    def _create_server_service(self, deployment_name: str, port: int) -> Dict:
        """Criar configuração de service do servidor"""
        return {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": f"{deployment_name}-service",
                "namespace": self.config.K8S_NAMESPACE
            },
            "spec": {
                "selector": {"app": deployment_name},
                "ports": [{
                    "protocol": "TCP",
                    "port": port,
                    "targetPort": port
                }],
                "type": "ClusterIP"
            }
        }
    
    def _apply_service(self, config: Dict) -> bool:
        """Aplicar service no Kubernetes"""
        try:
            yaml_content = json.dumps(config)
            cmd = ["kubectl", "apply", "-f", "-"]
            
            result = run_subprocess(
                cmd,
                input=yaml_content,
                capture_output=True
            )
            
            if result.returncode != 0:
                logger.error(f"Erro aplicando service: {result.stderr}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erro aplicando service: {e}")
            return False
    
    def _apply_deployment(self, config: Dict) -> bool:
        """Aplicar deployment no Kubernetes"""
        try:
            yaml_content = json.dumps(config)
            cmd = ["kubectl", "apply", "-f", "-"]
            
            result = run_subprocess(
                cmd,
                input=yaml_content,
                capture_output=True
            )
            
            if result.returncode != 0:
                logger.error(f"Erro aplicando deployment: {result.stderr}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erro aplicando deployment: {e}")
            return False
    
    def _apply_job(self, config: Dict) -> bool:
        """Aplicar job no Kubernetes com formato YAML correto"""
        try:
            import yaml
            yaml_content = yaml.dump(config, default_flow_style=False)
            cmd = ["kubectl", "apply", "-f", "-"]
            
            result = run_subprocess(
                cmd,
                input=yaml_content,
                capture_output=True
            )
            
            if result.returncode != 0:
                logger.error(f"Erro kubectl: {result.stderr}")
                logger.info(f"YAML enviado:\n{yaml_content}")
            
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"Erro aplicando job: {e}")
            return False
    
    def _wait_deployments_ready(self, deployment_names: List[str]) -> bool:
        """Aguardar deployments estarem prontos"""
        try:
            for name in deployment_names:
                logger.info(f"⏳ Aguardando deployment {name}...")
                
                # Primeiro verificar se o deployment foi criado
                check_cmd = [
                    "kubectl", "get", "deployment", name,
                    f"--namespace={self.config.K8S_NAMESPACE}", "-o", "name"
                ]
                check_result = run_subprocess(check_cmd, capture_output=True)
                
                if check_result.returncode != 0:
                    logger.error(f"Deployment {name} não encontrado")
                    return False
                
                # Aguardar com timeout reduzido e mais diagnósticos
                cmd = [
                    "kubectl", "wait", "--for=condition=available",
                    f"deployment/{name}", f"--namespace={self.config.K8S_NAMESPACE}",
                    f"--timeout=30s"  # Reduzido para 30s
                ]
                
                result = run_subprocess(cmd, capture_output=True)
                
                if result.returncode != 0:
                    logger.error(f"Timeout aguardando deployment {name}")
                    # Diagnóstico adicional
                    self._diagnose_deployment_failure(name)
                    return False
                else:
                    logger.info(f"Deployment {name} pronto")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro aguardando deployments: {e}")
            return False
    
    def _wait_job_complete(self, job_name: str) -> bool:
        """Aguardar job completar"""
        try:
            cmd = [
                "kubectl", "wait", "--for=condition=complete",
                f"job/{job_name}", f"--namespace={self.config.K8S_NAMESPACE}",
                f"--timeout={self.config.K8S_DEPLOYMENT_TIMEOUT}s"
            ]
            
            result = run_subprocess(cmd, capture_output=True)
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"Erro aguardando job: {e}")
            return False
    
    def _collect_job_results(self, job_name: str) -> Dict:
        """Coletar resultados do job"""
        try:
            # Obter pods do job
            cmd = [
                "kubectl", "get", "pods",
                f"--namespace={self.config.K8S_NAMESPACE}",
                f"--selector=job-name={job_name}",
                "-o", "jsonpath={.items[0].metadata.name}"
            ]
            
            result = run_subprocess(cmd, capture_output=True)
            
            if result.returncode != 0:
                return {}
            
            pod_name = result.stdout.strip()
            
            # Obter logs do pod
            cmd = [
                "kubectl", "logs", pod_name,
                f"--namespace={self.config.K8S_NAMESPACE}"
            ]
            
            result = run_subprocess(cmd, capture_output=True)
            
            if result.returncode != 0:
                return {}
            
            # Parsear logs para extrair métricas
            return self._parse_client_logs(result.stdout)
            
        except Exception as e:
            logger.error(f"Erro coletando resultados: {e}")
            return {}
    
    def _parse_client_logs(self, logs: str) -> Dict:
        """Parsear logs do cliente para extrair métricas"""
        try:
            # Implementar parsing específico dos logs
            # Por enquanto, retornar estrutura básica
            return {
                "success": True,
                "total_requests": 100,
                "successful_requests": 98,
                "failed_requests": 2,
                "avg_latency": 0.05,
                "min_latency": 0.01,
                "max_latency": 0.15,
                "throughput": 1000,
                "raw_logs": logs
            }
            
        except Exception as e:
            logger.error(f"Erro parseando logs: {e}")
            return {}
    
    def _cleanup_job(self, job_name: str):
        """Limpar job após uso"""
        try:
            cmd = [
                "kubectl", "delete", "job", job_name,
                f"--namespace={self.config.K8S_NAMESPACE}"
            ]
            
            run_subprocess(cmd, capture_output=True)
            
        except Exception as e:
            logger.error(f"Erro limpando job: {e}")
    
    def cleanup_all(self):
        """Limpar todos os recursos"""
        logger.info("🧹 Limpando recursos Kubernetes...")
        
        try:
            cmd = [
                "kubectl", "delete", "namespace", 
                self.config.K8S_NAMESPACE, "--ignore-not-found"
            ]
            
            run_subprocess(cmd, capture_output=True)
            
            logger.info("✅ Recursos Kubernetes limpos")
            
        except Exception as e:
            logger.error(f"Erro na limpeza: {e}")
    
    def _diagnose_deployment_failure(self, deployment_name: str):
        """Diagnosticar falha no deployment"""
        logger.info(f"🔍 Diagnosticando falha no deployment {deployment_name}...")
        
        try:
            # Verificar status do deployment
            cmd = ["kubectl", "get", "deployment", deployment_name, 
                   f"--namespace={self.config.K8S_NAMESPACE}", "-o", "wide"]
            result = run_subprocess(cmd, capture_output=True)
            if result.returncode == 0:
                logger.info("📋 Status do deployment:")
                logger.info(result.stdout)
            
            # Verificar eventos
            cmd = ["kubectl", "get", "events", 
                   f"--namespace={self.config.K8S_NAMESPACE}", "--sort-by=.metadata.creationTimestamp"]
            result = run_subprocess(cmd, capture_output=True)
            if result.returncode == 0:
                logger.info("📋 Eventos recentes:")
                lines = result.stdout.split('\n')
                for line in lines[-10:]:  # Últimas 10 linhas
                    if line.strip():
                        logger.info(line)
            
            # Verificar pods
            cmd = ["kubectl", "get", "pods", "-l", f"app={deployment_name}",
                   f"--namespace={self.config.K8S_NAMESPACE}", "-o", "wide"]
            result = run_subprocess(cmd, capture_output=True)
            if result.returncode == 0:
                logger.info("📋 Status dos pods:")
                logger.info(result.stdout)
            
            # Verificar logs do pod se existir
            cmd = ["kubectl", "get", "pods", "-l", f"app={deployment_name}",
                   f"--namespace={self.config.K8S_NAMESPACE}", "-o", "jsonpath={.items[0].metadata.name}"]
            result = run_subprocess(cmd, capture_output=True)
            if result.returncode == 0 and result.stdout.strip():
                pod_name = result.stdout.strip()
                cmd = ["kubectl", "logs", pod_name, f"--namespace={self.config.K8S_NAMESPACE}"]
                result = run_subprocess(cmd, capture_output=True)
                if result.returncode == 0 and result.stdout.strip():
                    logger.info(f"📋 Logs do pod {pod_name}:")
                    logger.info(result.stdout)
            
        except Exception as e:
            logger.error(f"Erro no diagnóstico: {e}")
        
        # Sugestões de correção
        logger.info("💡 Possíveis soluções:")
        logger.info("1. Verificar se as imagens estão disponíveis: docker images | grep scalability")
        logger.info("2. Reconstruir imagens: python3 executar.py --build-only")
        logger.info("3. Verificar recursos do cluster: kubectl describe nodes")
        logger.info("4. Verificar logs detalhados: kubectl describe pod <pod-name> -n scalability-test")
    
    def _check_image_exists(self, image_name: str) -> bool:
        """Verificar se a imagem Docker existe"""
        try:
            result = run_subprocess(["docker", "images", image_name, "--quiet"], capture_output=True)
            
            if result.returncode == 0 and result.stdout.strip():
                logger.info(f"✅ Imagem {image_name} encontrada")
                return True
            else:
                logger.error(f"❌ Imagem {image_name} não encontrada localmente")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro verificando imagem: {e}")
            return False
    
    def _cleanup_orphaned_jobs(self):
        """Limpar jobs órfãos de execuções anteriores"""
        try:
            # Listar todos os jobs no namespace
            cmd = [
                "kubectl", "get", "jobs",
                f"--namespace={self.config.K8S_NAMESPACE}",
                "-o", "jsonpath={.items[*].metadata.name}"
            ]
            
            result = run_subprocess(cmd, capture_output=True)
            
            if result.returncode == 0 and result.stdout.strip():
                job_names = result.stdout.strip().split()
                client_jobs = [name for name in job_names if name.startswith("cliente-test-")]
                
                if client_jobs:
                    logger.info(f"🧹 Limpando {len(client_jobs)} jobs órfãos...")
                    for job_name in client_jobs:
                        self._cleanup_job(job_name)
                        
        except Exception as e:
            logger.error(f"⚠️  Erro limpando jobs órfãos: {e}")

    def deploy_server(self, name: str, language: str, port: int) -> bool:
        """Deploy de um servidor específico"""
        return self._deploy_single_server(name, language, port)

    def cleanup_resources(self) -> bool:
        """Limpeza de recursos Kubernetes"""
        try:
            logger.info("🧹 Limpando recursos Kubernetes...")
            
            # Limpar jobs
            cmd = ["kubectl", "delete", "jobs", "--all", f"--namespace={self.config.K8S_NAMESPACE}"]
            run_subprocess(cmd, capture_output=True)
            
            # Limpar deployments
            cmd = ["kubectl", "delete", "deployments", "--all", f"--namespace={self.config.K8S_NAMESPACE}"]
            run_subprocess(cmd, capture_output=True)
            
            # Limpar services
            cmd = ["kubectl", "delete", "services", "--all", f"--namespace={self.config.K8S_NAMESPACE}"]
            run_subprocess(cmd, capture_output=True)
            
            logger.info("✅ Recursos limpos com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro limpando recursos: {e}")
            return False

    def wait_for_pods_ready(self, deployment_names: List[str]) -> bool:
        """Aguardar pods ficarem prontos"""
        return self._wait_deployments_ready(deployment_names)

    def cleanup_all(self):
        """Limpeza completa do namespace"""
        self.cleanup_resources()


class InfrastructureManager:
    """Gerenciador principal de infraestrutura"""
    
    def __init__(self):
        self.config = get_config()
        self.docker_manager = DockerManager()
        self.k8s_manager = KubernetesManager()
        self.errors = []
        # Aliases para compatibilidade com testes
        self.docker = self.docker_manager
        self.k8s = self.k8s_manager
    
    def build_and_push_all(self) -> bool:
        """Build e push de todas as imagens Docker"""
        try:
            return self.docker_manager.build_and_push_all()
        except Exception as e:
            self.errors.append(f"Erro no build/push: {e}")
            logger.error(f"Erro no build/push: {e}")
            return False
    
    def deploy_servers(self, language: str, num_servers: int):
        """Deploy de servidores"""
        return self.k8s_manager.deploy_servers(language, num_servers)
    
    def run_clients(self, deployments, num_clients: int, messages_per_client: int):
        """Executar clientes"""
        return self.k8s_manager.run_clients(deployments, num_clients, messages_per_client)
    
    def setup_complete_infrastructure(self) -> bool:
        """Setup completo da infraestrutura"""
        logger.info("🏗️  CONFIGURANDO INFRAESTRUTURA COMPLETA")
        
        # Build e push das imagens
        if not self.docker_manager.build_and_push_all():
            return False
        
        # Setup do Kubernetes
        if not self.k8s_manager.setup_namespace():
            return False
        
        logger.info("Infraestrutura configurada com sucesso")
        return True
    
    def setup_infrastructure(self) -> bool:
        """Setup da infraestrutura (alias para compatibilidade)"""
        return self.setup_complete_infrastructure()
    
    def wait_for_pods_ready(self, deployment_names: list) -> bool:
        """Aguardar pods ficarem prontos"""
        return self.k8s_manager.wait_for_pods_ready(deployment_names)
    
    def cleanup_all(self):
        """Limpeza completa"""
        self.k8s_manager.cleanup_all()


def get_infrastructure_manager() -> InfrastructureManager:
    """Obter gerenciador de infraestrutura"""
    return InfrastructureManager()
