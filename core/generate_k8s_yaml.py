import os
from core.config import get_config
from typing import Optional

def generate_k8s_deployment_yaml(
    name: str,
    image: str,
    replicas: int = 1,
    container_port: int = 8000,
    env: Optional[list] = None,
    cpu_request: Optional[str] = None,
    cpu_limit: Optional[str] = None,
    mem_request: Optional[str] = None,
    mem_limit: Optional[str] = None,
    namespace: Optional[str] = None
) -> str:
    """Gera um YAML de deployment Kubernetes parametrizado"""
    env_yaml = ""
    if env:
        env_yaml = "      env:\n" + "\n".join([
            f"        - name: {e['name']}\n          value: \"{e['value']}\"" for e in env
        ])
    ns = namespace or get_config().K8S_NAMESPACE
    cpu_request = cpu_request or get_config().RESOURCE_REQUESTS['cpu']
    cpu_limit = cpu_limit or get_config().RESOURCE_LIMITS['cpu']
    mem_request = mem_request or get_config().RESOURCE_REQUESTS['memory']
    mem_limit = mem_limit or get_config().RESOURCE_LIMITS['memory']
    return (
        f"apiVersion: apps/v1\n"
        f"kind: Deployment\n"
        f"metadata:\n"
        f"  name: {name}\n"
        f"  namespace: {ns}\n"
        f"spec:\n"
        f"  replicas: {replicas}\n"
        f"  selector:\n"
        f"    matchLabels:\n"
        f"      app: {name}\n"
        f"  template:\n"
        f"    metadata:\n"
        f"      labels:\n"
        f"        app: {name}\n"
        f"    spec:\n"
        f"      containers:\n"
        f"      - name: {name}\n"
        f"        image: {image}\n"
        f"        ports:\n"
        f"        - containerPort: {container_port}\n"
        f"        resources:\n"
        f"          requests:\n"
        f"            cpu: {cpu_request}\n"
        f"            memory: {mem_request}\n"
        f"          limits:\n"
        f"            cpu: {cpu_limit}\n"
        f"            memory: {mem_limit}\n"
        f"{env_yaml if env else ''}\n"
    )

def save_deployment_yaml(yaml_str: str, filename: str):
    with open(filename, 'w') as f:
        f.write(yaml_str)

def generate_all_deployments():
    config = get_config()
    ns = config.K8S_NAMESPACE
    config_dir = str(config.BASE_DIR / "config")
    os.makedirs(config_dir, exist_ok=True)
    # Servidor C
    save_deployment_yaml(
        generate_k8s_deployment_yaml(
            name="servidor-c",
            image=config.get_docker_image_name("servidor", "c"),
            replicas=1,
            container_port=8000,
            env=[{"name": "SERVER_LANGUAGE", "value": "c"}],
            namespace=ns
        ),
        os.path.join(config_dir, "k8s-servidor-c.yaml")
    )
    # Servidor C++
    save_deployment_yaml(
        generate_k8s_deployment_yaml(
            name="servidor-cpp",
            image=config.get_docker_image_name("servidor", "cpp"),
            replicas=1,
            container_port=8000,
            env=[{"name": "SERVER_LANGUAGE", "value": "cpp"}],
            namespace=ns
        ),
        os.path.join(config_dir, "k8s-servidor-cpp.yaml")
    )
    # Cliente
    save_deployment_yaml(
        generate_k8s_deployment_yaml(
            name="cliente",
            image=config.get_docker_image_name("cliente"),
            replicas=1,
            container_port=8000,
            env=[{"name": "CLIENT_MODE", "value": "benchmark"}],
            namespace=ns
        ),
        os.path.join(config_dir, "k8s-cliente.yaml")
    )
    print("YAMLs de deployment gerados em:")
    print(f"- {os.path.join(config_dir, 'k8s-servidor-c.yaml')}")
    print(f"- {os.path.join(config_dir, 'k8s-servidor-cpp.yaml')}")
    print(f"- {os.path.join(config_dir, 'k8s-cliente.yaml')}")

if __name__ == "__main__":
    generate_all_deployments()
