#!/usr/bin/env python3
"""
SCRIPT DE TESTE DE PUSH PARA DOCKER HUB
Testa apenas o build e push das imagens
"""

import sys
from pathlib import Path

# Adicionar diretório do projeto ao path
sys.path.insert(0, str(Path(__file__).parent))

from infrastructure_manager import get_infrastructure_manager


def test_docker_push():
    """Testar apenas o build e push das imagens"""
    print("🐳 TESTE DE BUILD E PUSH PARA DOCKER HUB")
    print("=" * 60)
    
    try:
        infrastructure = get_infrastructure_manager()
        
        # Verificar se tem DockerManager
        if hasattr(infrastructure, 'docker_manager'):
            docker_manager = infrastructure.docker_manager
        else:
            # Se não tiver, criar uma instância
            from infrastructure_manager import DockerManager
            docker_manager = DockerManager()
        
        # Fazer build e push
        if docker_manager.build_and_push_all():
            print("\n✅ SUCESSO: Todas as imagens foram enviadas para Docker Hub")
            return True
        else:
            print("\n❌ FALHA: Algumas imagens não foram enviadas")
            return False
            
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        return False


if __name__ == "__main__":
    success = test_docker_push()
    sys.exit(0 if success else 1)
