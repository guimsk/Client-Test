#!/usr/bin/env python3
"""
UTILITÁRIO DE CORREÇÃO DE IMAGENS DOCKER
Constrói e envia imagens para Docker Hub
"""

import subprocess
import sys
import time
from pathlib import Path

# Adicionar diretório do projeto ao path
sys.path.insert(0, str(Path(__file__).parent))

from config import get_config


def run_command(cmd, use_sudo=False):
    """Executa comando e retorna resultado"""
    if use_sudo and not cmd.startswith("sudo"):
        cmd = f"sudo {cmd}"
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def check_docker_login():
    """Verifica se está logado no Docker Hub"""
    print("🔍 Verificando login no Docker Hub...")
    
    success, stdout, stderr = run_command("docker info", use_sudo=True)
    
    if success:
        print("✅ Docker está funcionando")
        return True
    else:
        print("❌ Docker não está funcionando")
        print(f"Erro: {stderr}")
        return False


def build_and_push_image(app_name, dockerfile_path, image_name):
    """Constrói e envia imagem para Docker Hub"""
    print(f"\n🔨 Construindo imagem {app_name}...")
    
    # Build da imagem
    build_cmd = f"cd {dockerfile_path.parent} && docker build -t {image_name} ."
    success, stdout, stderr = run_command(build_cmd, use_sudo=True)
    
    if not success:
        print(f"❌ Erro no build de {app_name}")
        print(f"Erro: {stderr}")
        return False
    
    print(f"✅ Imagem {app_name} construída com sucesso")
    
    # Push da imagem
    print(f"📤 Enviando imagem {app_name} para Docker Hub...")
    push_cmd = f"docker push {image_name}"
    success, stdout, stderr = run_command(push_cmd, use_sudo=True)
    
    if not success:
        print(f"❌ Erro no push de {app_name}")
        print(f"Erro: {stderr}")
        return False
    
    print(f"✅ Imagem {app_name} enviada com sucesso para Docker Hub")
    return True


def main():
    """Função principal"""
    print("🐳 CONSTRUINDO E ENVIANDO IMAGENS PARA DOCKER HUB")
    print("=" * 60)
    
    # Verificar Docker
    if not check_docker_login():
        print("\n❌ Problema com Docker. Verifique:")
        print("1. Se o Docker está rodando: sudo systemctl start docker")
        print("2. Se está logado: docker login")
        return False
    
    config = get_config()
    
    # Definir imagens a processar
    images_to_build = [
        {
            "name": "Cliente Python",
            "dockerfile": config.APPLICATIONS_DIR / "cliente" / "Dockerfile",
            "image": config.get_docker_image_name("cliente")
        },
        {
            "name": "Servidor C",
            "dockerfile": config.APPLICATIONS_DIR / "servidor-c" / "Dockerfile",
            "image": config.get_docker_image_name("servidor", "c")
        },
        {
            "name": "Servidor C++",
            "dockerfile": config.APPLICATIONS_DIR / "servidor" / "Dockerfile",
            "image": config.get_docker_image_name("servidor", "cpp")
        }
    ]
    
    success = True
    
    for img_config in images_to_build:
        if not build_and_push_image(
            img_config["name"],
            img_config["dockerfile"], 
            img_config["image"]
        ):
            success = False
    
    print(f"\n{'='*60}")
    
    if success:
        print("🎉 TODAS AS IMAGENS ENVIADAS COM SUCESSO!")
        print("✅ Imagens disponíveis no Docker Hub:")
        for img_config in images_to_build:
            print(f"   • {img_config['image']}")
        print("\n💡 Agora você pode executar:")
        print("   python3 executar.py --skip-build")
    else:
        print("❌ FALHA NO ENVIO DAS IMAGENS")
        print("🔍 Verifique:")
        print("1. Conectividade com Docker Hub")
        print("2. Credenciais: docker login")
        print("3. Permissões de usuário")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
