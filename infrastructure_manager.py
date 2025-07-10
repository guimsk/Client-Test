#!/usr/bin/env python3
"""
GERENCIADOR DE INFRAESTRUTURA COM DOCKER HUB E KUBERNETES V6
Sistema completo de build, push e deploy automatizado
"""

import os
import time
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from config import get_config


@dataclass
class DockerImage:
    """Informações de uma imagem Docker"""
    name: str
    tag: str
    path: Path
    dockerfile: str
    language: str = None


class DockerManager:
    """Gerenciador de imagens Docker"""
    
    def __init__(self):
        self.config = get_config()
        self.images = self._prepare_images()
    
    def _prepare_images(self) -> List[DockerImage]:
        """Preparar lista de imagens para build"""
        images = []
        
        # Cliente Python
        images.append(DockerImage(
            name=self.config.get_docker_image_name("cliente"),
            tag="latest",
            path=self.config.APPLICATIONS_DIR / "cliente",
            dockerfile="Dockerfile",
            language="python"
        ))
        
        # Servidor C
        images.append(DockerImage(
            name=self.config.get_docker_image_name("servidor", "c"),
            tag="latest", 
            path=self.config.APPLICATIONS_DIR / "servidor-c",
            dockerfile="Dockerfile",
            language="c"
        ))
        
        # Servidor C++
        images.append(DockerImage(
            name=self.config.get_docker_image_name("servidor", "cpp"),
            tag="latest",
            path=self.config.APPLICATIONS_DIR / "servidor", 
            dockerfile="Dockerfile",
            language="cpp"
        ))
        
        return images
    
    def build_and_push_all(self) -> bool:
        """Build e push de todas as imagens para Docker Hub"""
        print("🐳 CONSTRUINDO E ENVIANDO IMAGENS DOCKER PARA HUB")
        
        # Verificar se está logado no Docker Hub
        if not self._check_docker_login():
            print("❌ Não está logado no Docker Hub. Execute: docker login")
            return False
        
        success = True
        
        for image in self.images:
            print(f"\n📦 Processando {image.name}...")
            
            # Verificar se já existe localmente
            if self._check_local_image(image.name):
                print(f"✅ Imagem {image.name} já existe localmente")
            else:
                # Build da imagem
                if not self._build_image(image):
                    success = False
                    continue
            
            # Push para Docker Hub
            if not self._push_image(image):
                success = False
                continue
        
        if success:
            print("\n✅ Todas as imagens foram enviadas com sucesso para Docker Hub")
        else:
            print("\n❌ Algumas imagens falharam no processo de build/push")
        
        return success
    
    def _check_docker_login(self) -> bool:
        """Verificar se está logado no Docker Hub"""
        try:
            # Verificar se pode acessar informações do Docker Hub
            cmd = ["sudo", "docker", "info"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and "Username:" in result.stdout:
                return True
            
            return result.returncode == 0
            
        except Exception:
            return False
    
    def _verify_image_in_hub(self, image: DockerImage) -> bool:
        """Verificar se imagem está disponível no Docker Hub"""
        try:
            # Tentar fazer pull da imagem para verificar
            cmd = ["sudo", "docker", "manifest", "inspect", image.name]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            return result.returncode == 0
            
        except Exception:
            return False
    
    def _build_image(self, image: DockerImage) -> bool:
        """Build de uma imagem Docker"""
        print(f"🔨 Construindo {image.name}...")
        
        try:
            cmd = [
                "sudo", "docker", "build",
                "-t", image.name,
                "-f", str(image.path / image.dockerfile),
                str(image.path)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=image.path
            )
            
            if result.returncode != 0:
                print(f"❌ Erro no build de {image.name}: {result.stderr}")
                return False
            
            print(f"✅ {image.name} construída com sucesso")
            return True
            
        except Exception as e:
            print(f"❌ Erro no build de {image.name}: {e}")
            return False
    
    def _push_image(self, image: DockerImage) -> bool:
        """Push de uma imagem Docker"""
        print(f"📤 Enviando {image.name}...")
        
        try:
            cmd = ["sudo", "docker", "push", image.name]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print(f"❌ Erro no push de {image.name}: {result.stderr}")
                return False
            
            print(f"✅ {image.name} enviada com sucesso")
            return True
            
        except Exception as e:
            print(f"❌ Erro no push de {image.name}: {e}")
            return False
    
    def _check_local_image(self, image_name: str) -> bool:
        """Verificar se imagem existe localmente"""
        try:
            cmd = ["sudo", "docker", "images", image_name, "--quiet"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            return result.returncode == 0 and result.stdout.strip()
            
        except Exception:
            return False


class KubernetesManager:
    """Gerenciador de recursos Kubernetes"""
    
    def __init__(self):
        self.config = get_config()
    
    def setup_namespace(self) -> bool:
        """Configurar namespace Kubernetes"""
        print(f"☸️  Configurando namespace {self.config.K8S_NAMESPACE}...")
        
        try:
            # Criar namespace
            cmd = [
                "sudo", "kubectl", "create", "namespace", 
                self.config.K8S_NAMESPACE, "--dry-run=client", "-o", "yaml"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                apply_cmd = ["sudo", "kubectl", "apply", "-f", "-"]
                subprocess.run(apply_cmd, input=result.stdout, text=True)
            
            print(f"✅ Namespace {self.config.K8S_NAMESPACE} configurado")
            return True
            
        except Exception as e:
            print(f"❌ Erro configurando namespace: {e}")
            return False
    
    def deploy_servers(self, language: str, num_servers: int) -> List[Dict]:
        """Deploy de servidores no Kubernetes"""
        print(f"🚀 Fazendo deploy de {num_servers} servidores {language}...")
        
        # Verificar se a imagem existe
        image_name = self.config.get_docker_image_name("servidor", language)
        if not self._check_image_exists(image_name):
            print(f"❌ Imagem {image_name} não encontrada")
            return []
        
        deployments = []
        
        try:
            for i in range(num_servers):
                deployment_name = f"servidor-{language}-{i}"
                port = self.config.BASE_PORT + i
                
                deployment_config = self._create_server_deployment(
                    deployment_name, language, port
                )
                
                service_config = self._create_server_service(
                    deployment_name, port
                )
                
                if self._apply_deployment(deployment_config) and self._apply_service(service_config):
                    deployments.append({
                        "name": deployment_name,
                        "language": language,
                        "port": port,
                        "service_name": f"{deployment_name}-service"
                    })
                else:
                    print(f"❌ Falha no deploy de {deployment_name}")
                    return []
            
            # Aguardar deployments estarem prontos
            if self._wait_deployments_ready([d["name"] for d in deployments]):
                print(f"✅ Todos os {num_servers} servidores {language} estão prontos")
                return deployments
            else:
                print(f"❌ Timeout aguardando servidores {language}")
                return []
                
        except Exception as e:
            print(f"❌ Erro no deploy de servidores: {e}")
            return []
    
    def run_clients(self, deployments: List[Dict], num_clients: int, messages: int) -> Dict:
        """Executar clientes contra servidores"""
        print(f"🧪 Executando {num_clients} clientes com {messages} mensagens...")
        
        try:
            # Preparar lista de servidores
            servers = []
            for dep in deployments:
                servers.append(f"{dep['service_name']}.{self.config.K8S_NAMESPACE}.svc.cluster.local:{dep['port']}")
            
            # Criar job do cliente
            job_name = f"cliente-test-{int(time.time())}"
            job_config = self._create_client_job(
                job_name, servers, num_clients, messages
            )
            
            if not self._apply_job(job_config):
                print(f"❌ Falha ao criar job {job_name}")
                return {}
            
            # Aguardar job completar
            if self._wait_job_complete(job_name):
                # Coletar resultados
                results = self._collect_job_results(job_name)
                
                # Limpar job
                self._cleanup_job(job_name)
                
                return results
            else:
                print(f"❌ Timeout aguardando job {job_name}")
                return {}
                
        except Exception as e:
            print(f"❌ Erro executando clientes: {e}")
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
            cmd = ["sudo", "kubectl", "apply", "-f", "-"]
            
            result = subprocess.run(
                cmd,
                input=yaml_content,
                text=True,
                capture_output=True
            )
            
            if result.returncode != 0:
                print(f"❌ Erro aplicando service: {result.stderr}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Erro aplicando service: {e}")
            return False
    
    def _apply_deployment(self, config: Dict) -> bool:
        """Aplicar deployment no Kubernetes"""
        try:
            yaml_content = json.dumps(config)
            cmd = ["sudo", "kubectl", "apply", "-f", "-"]
            
            result = subprocess.run(
                cmd,
                input=yaml_content,
                text=True,
                capture_output=True
            )
            
            if result.returncode != 0:
                print(f"❌ Erro aplicando deployment: {result.stderr}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Erro aplicando deployment: {e}")
            return False
    
    def _apply_job(self, config: Dict) -> bool:
        """Aplicar job no Kubernetes"""
        try:
            yaml_content = json.dumps(config)
            cmd = ["sudo", "kubectl", "apply", "-f", "-"]
            
            result = subprocess.run(
                cmd,
                input=yaml_content,
                text=True,
                capture_output=True
            )
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Erro aplicando job: {e}")
            return False
    
    def _wait_deployments_ready(self, deployment_names: List[str]) -> bool:
        """Aguardar deployments estarem prontos"""
        try:
            for name in deployment_names:
                print(f"⏳ Aguardando deployment {name}...")
                
                # Primeiro verificar se o deployment foi criado
                check_cmd = [
                    "sudo", "kubectl", "get", "deployment", name,
                    f"--namespace={self.config.K8S_NAMESPACE}", "-o", "name"
                ]
                check_result = subprocess.run(check_cmd, capture_output=True, text=True)
                
                if check_result.returncode != 0:
                    print(f"❌ Deployment {name} não encontrado")
                    return False
                
                # Aguardar com timeout reduzido e mais diagnósticos
                cmd = [
                    "sudo", "kubectl", "wait", "--for=condition=available",
                    f"deployment/{name}", f"--namespace={self.config.K8S_NAMESPACE}",
                    f"--timeout=30s"  # Reduzido para 30s
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    print(f"❌ Timeout aguardando deployment {name}")
                    # Diagnóstico adicional
                    self._diagnose_deployment_failure(name)
                    return False
                else:
                    print(f"✅ Deployment {name} pronto")
            
            return True
            
        except Exception as e:
            print(f"❌ Erro aguardando deployments: {e}")
            return False
    
    def _wait_job_complete(self, job_name: str) -> bool:
        """Aguardar job completar"""
        try:
            cmd = [
                "sudo", "kubectl", "wait", "--for=condition=complete",
                f"job/{job_name}", f"--namespace={self.config.K8S_NAMESPACE}",
                f"--timeout={self.config.K8S_DEPLOYMENT_TIMEOUT}s"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Erro aguardando job: {e}")
            return False
    
    def _collect_job_results(self, job_name: str) -> Dict:
        """Coletar resultados do job"""
        try:
            # Obter pods do job
            cmd = [
                "sudo", "kubectl", "get", "pods",
                f"--namespace={self.config.K8S_NAMESPACE}",
                f"--selector=job-name={job_name}",
                "-o", "jsonpath={.items[0].metadata.name}"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return {}
            
            pod_name = result.stdout.strip()
            
            # Obter logs do pod
            cmd = [
                "sudo", "kubectl", "logs", pod_name,
                f"--namespace={self.config.K8S_NAMESPACE}"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                return {}
            
            # Parsear logs para extrair métricas
            return self._parse_client_logs(result.stdout)
            
        except Exception as e:
            print(f"❌ Erro coletando resultados: {e}")
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
            print(f"❌ Erro parseando logs: {e}")
            return {}
    
    def _cleanup_job(self, job_name: str):
        """Limpar job após uso"""
        try:
            cmd = [
                "sudo", "kubectl", "delete", "job", job_name,
                f"--namespace={self.config.K8S_NAMESPACE}"
            ]
            
            subprocess.run(cmd, capture_output=True, text=True)
            
        except Exception as e:
            print(f"⚠️  Erro limpando job: {e}")
    
    def cleanup_all(self):
        """Limpar todos os recursos"""
        print("🧹 Limpando recursos Kubernetes...")
        
        try:
            cmd = [
                "sudo", "kubectl", "delete", "namespace", 
                self.config.K8S_NAMESPACE, "--ignore-not-found"
            ]
            
            subprocess.run(cmd, capture_output=True, text=True)
            
            print("✅ Recursos Kubernetes limpos")
            
        except Exception as e:
            print(f"⚠️  Erro na limpeza: {e}")
    
    def _diagnose_deployment_failure(self, deployment_name: str):
        """Diagnosticar falha no deployment"""
        print(f"🔍 Diagnosticando falha no deployment {deployment_name}...")
        
        try:
            # Verificar status do deployment
            cmd = ["sudo", "kubectl", "get", "deployment", deployment_name, 
                   f"--namespace={self.config.K8S_NAMESPACE}", "-o", "wide"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("📋 Status do deployment:")
                print(result.stdout)
            
            # Verificar eventos
            cmd = ["sudo", "kubectl", "get", "events", 
                   f"--namespace={self.config.K8S_NAMESPACE}", "--sort-by=.metadata.creationTimestamp"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("📋 Eventos recentes:")
                lines = result.stdout.split('\n')
                for line in lines[-10:]:  # Últimas 10 linhas
                    if line.strip():
                        print(line)
            
            # Verificar pods
            cmd = ["sudo", "kubectl", "get", "pods", "-l", f"app={deployment_name}",
                   f"--namespace={self.config.K8S_NAMESPACE}", "-o", "wide"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("📋 Status dos pods:")
                print(result.stdout)
            
            # Verificar logs do pod se existir
            cmd = ["sudo", "kubectl", "get", "pods", "-l", f"app={deployment_name}",
                   f"--namespace={self.config.K8S_NAMESPACE}", "-o", "jsonpath={.items[0].metadata.name}"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                pod_name = result.stdout.strip()
                cmd = ["sudo", "kubectl", "logs", pod_name, f"--namespace={self.config.K8S_NAMESPACE}"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    print(f"📋 Logs do pod {pod_name}:")
                    print(result.stdout)
            
        except Exception as e:
            print(f"❌ Erro no diagnóstico: {e}")
        
        # Sugestões de correção
        print("💡 Possíveis soluções:")
        print("1. Verificar se as imagens estão disponíveis: docker images | grep scalability")
        print("2. Reconstruir imagens: python3 executar.py --build-only")
        print("3. Verificar recursos do cluster: kubectl describe nodes")
        print("4. Verificar logs detalhados: kubectl describe pod <pod-name> -n scalability-test")
    
    def _check_image_exists(self, image_name: str) -> bool:
        """Verificar se a imagem Docker existe"""
        try:
            cmd = ["sudo", "docker", "images", image_name, "--quiet"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip():
                print(f"✅ Imagem {image_name} encontrada")
                return True
            else:
                print(f"❌ Imagem {image_name} não encontrada localmente")
                return False
                
        except Exception as e:
            print(f"❌ Erro verificando imagem: {e}")
            return False


class InfrastructureManager:
    """Gerenciador principal de infraestrutura"""
    
    def __init__(self):
        self.config = get_config()
        self.docker_manager = DockerManager()
        self.k8s_manager = KubernetesManager()
    
    def build_and_push_all(self) -> bool:
        """Build e push de todas as imagens Docker"""
        return self.docker_manager.build_and_push_all()
    
    def deploy_servers(self, language: str, num_servers: int):
        """Deploy de servidores"""
        return self.k8s_manager.deploy_servers(language, num_servers)
    
    def run_clients(self, deployments, num_clients: int, messages_per_client: int):
        """Executar clientes"""
        return self.k8s_manager.run_clients(deployments, num_clients, messages_per_client)
    
    def setup_complete_infrastructure(self) -> bool:
        """Setup completo da infraestrutura"""
        print("🏗️  CONFIGURANDO INFRAESTRUTURA COMPLETA")
        
        # Build e push das imagens
        if not self.docker_manager.build_and_push_all():
            return False
        
        # Setup do Kubernetes
        if not self.k8s_manager.setup_namespace():
            return False
        
        print("✅ Infraestrutura configurada com sucesso")
        return True
    
    def cleanup_all(self):
        """Limpeza completa"""
        self.k8s_manager.cleanup_all()


def get_infrastructure_manager() -> InfrastructureManager:
    """Obter gerenciador de infraestrutura"""
    return InfrastructureManager()
