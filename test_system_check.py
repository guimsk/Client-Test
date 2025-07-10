#!/usr/bin/env python3
"""
TESTE DE VERIFICAÇÃO DO SISTEMA
Verifica se todos os componentes estão funcionando corretamente
"""

import sys
import subprocess
import time
from pathlib import Path

# Adicionar diretório do projeto ao path
sys.path.insert(0, str(Path(__file__).parent))


def run_command(cmd, ignore_error=False):
    """Executa comando e retorna resultado"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0 and not ignore_error:
            return False, result.stderr
        return True, result.stdout
    except Exception as e:
        return False, str(e)


def check_kubernetes():
    """Verificar conectividade Kubernetes"""
    print("\n☸️  VERIFICANDO KUBERNETES")
    print("=" * 50)
    
    # Verificar conectividade
    success, output = run_command("sudo kubectl cluster-info", ignore_error=True)
    if success:
        print("✅ Cluster Kubernetes conectado")
    else:
        print("❌ Cluster Kubernetes não disponível")
        print("💡 Configure um cluster Kubernetes e tente novamente")
        return False
    
    # Verificar namespace
    try:
        from config import get_config
        config = get_config()
        success, output = run_command(f"sudo kubectl get namespace {config.K8S_NAMESPACE}", ignore_error=True)
        if success:
            print(f"✅ Namespace {config.K8S_NAMESPACE} existe")
        else:
            print(f"⚠️  Namespace {config.K8S_NAMESPACE} não existe (será criado)")
    except Exception as e:
        print(f"❌ Erro verificando namespace: {e}")
        return False
    
    # Verificar recursos do cluster
    success, output = run_command("sudo kubectl get nodes", ignore_error=True)
    if success:
        print("✅ Nós do cluster disponíveis")
    else:
        print("❌ Erro verificando nós do cluster")
        return False
    
    return True


def check_docker():
    """Verificar Docker"""
    print("\n🐳 VERIFICANDO DOCKER")
    print("=" * 50)
    
    # Verificar Docker
    success, output = run_command("sudo docker --version", ignore_error=True)
    if success:
        print(f"✅ Docker: {output.strip()}")
    else:
        print("❌ Docker não encontrado")
        return False
    
    # Verificar se Docker está rodando
    success, output = run_command("sudo docker info", ignore_error=True)
    if success:
        print("✅ Docker está rodando")
    else:
        print("❌ Docker não está rodando")
        return False
    
    return True


def check_images():
    """Verificar imagens Docker"""
    print("\n🖼️  VERIFICANDO IMAGENS DOCKER")
    print("=" * 50)
    
    try:
        from config import get_config
        config = get_config()
        
        images = [
            ("Cliente", config.get_docker_image_name("cliente")),
            ("Servidor C", config.get_docker_image_name("servidor", "c")),
            ("Servidor C++", config.get_docker_image_name("servidor", "cpp"))
        ]
        
        all_ok = True
        
        for name, image_name in images:
            success, output = run_command(f"docker images {image_name} --quiet", ignore_error=True)
            if success and output.strip():
                print(f"✅ {name}: {image_name}")
            else:
                print(f"❌ {name}: {image_name} - Não encontrada")
                all_ok = False
        
        return all_ok
        
    except Exception as e:
        print(f"❌ Erro verificando imagens: {e}")
        return False


def test_system():
    """Testar funcionalidades do sistema"""
    print("\n🧪 TESTANDO MÓDULOS DO SISTEMA")
    print("=" * 50)
    
    errors = []
    
    try:
        # Testar importações
        from config import get_config
        from infrastructure_manager import get_infrastructure_manager
        from test_executor import get_kubernetes_test_executor
        from result_analyzer import get_result_analyzer
        from chart_generator import get_chart_generator
        from resource_monitor import get_resource_monitor
        print("✅ Todas as importações funcionam")
        
        # Testar configuração
        config = get_config()
        print(f"✅ Configuração carregada: {len(config.SERVERS)} servidores, {len(config.CLIENTS)} clientes")
        
        # Testar inicialização dos módulos
        analyzer = get_result_analyzer()
        print("✅ Analisador de resultados inicializado")
        
        chart_gen = get_chart_generator()
        print("✅ Gerador de gráficos inicializado")
        
        monitor = get_resource_monitor()
        print("✅ Monitor de recursos inicializado")
        
        print("✅ Sistema totalmente funcional!")
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Função principal"""
    print("🧪 TESTE DE VERIFICAÇÃO DO SISTEMA")
    print("=" * 60)
    
    checks = [
        ("Docker", check_docker),
        ("Kubernetes", check_kubernetes),
        ("Imagens Docker", check_images),
        ("Módulos do Sistema", test_system)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        try:
            if not check_func():
                all_passed = False
        except Exception as e:
            print(f"❌ Erro em {check_name}: {e}")
            all_passed = False
    
    print(f"\n{'='*60}")
    
    if all_passed:
        print("🎉 SISTEMA VERIFICADO COM SUCESSO!")
        print("✅ Todos os componentes estão funcionando corretamente")
        print("\n💡 PRÓXIMOS PASSOS:")
        print("1. Execute: python3 executar.py --build-only")
        print("2. Execute: python3 executar.py --skip-build")
    else:
        print("❌ SISTEMA COM PROBLEMAS")
        print("⚠️  Alguns componentes precisam ser corrigidos")
        print("\n🔧 SOLUÇÕES RECOMENDADAS:")
        print("1. Verifique se o Docker está rodando: sudo systemctl start docker")
        print("2. Verifique se o cluster Kubernetes está disponível: kubectl cluster-info")
        print("3. Construa as imagens: python3 executar.py --build-only")
        print("4. Execute este teste novamente")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
