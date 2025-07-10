#!/usr/bin/env python3
"""
EXECUTOR PRINCIPAL DO SISTEMA V6 - TESTES DE ESCALABILIDADE
Sistema completo automatizado com Docker Hub e Kubernetes
"""

import argparse
import sys
import time
from pathlib import Path

# Adicionar diretório do projeto ao path
sys.path.insert(0, str(Path(__file__).parent))

from config import get_config, print_system_info
from infrastructure_manager import get_infrastructure_manager
from test_executor import get_kubernetes_test_executor
from result_analyzer import get_result_analyzer
from chart_generator import get_chart_generator
from resource_monitor import get_resource_monitor


def main():
    """Função principal do sistema"""
    parser = argparse.ArgumentParser(
        description="Sistema de Testes de Escalabilidade V6"
    )
    parser.add_argument(
        "--keep-data", 
        action="store_true",
        help="Manter dados anteriores (não limpar)"
    )
    parser.add_argument(
        "--skip-build", 
        action="store_true",
        help="Pular build das imagens Docker"
    )
    parser.add_argument(
        "--skip-tests", 
        action="store_true",
        help="Pular execução dos testes"
    )
    parser.add_argument(
        "--skip-analysis", 
        action="store_true",
        help="Pular análise dos resultados"
    )
    parser.add_argument(
        "--skip-charts", 
        action="store_true",
        help="Pular geração de gráficos"
    )
    parser.add_argument(
        "--build-only", 
        action="store_true",
        help="Apenas construir e enviar imagens Docker"
    )
    
    args = parser.parse_args()
    
    # Configuração do sistema
    config = get_config()
    
    # Inicializar monitor de recursos
    monitor = get_resource_monitor()
    monitor.print_current_status()
    
    print("=" * 60)
    print("🚀 SISTEMA DE TESTES DE ESCALABILIDADE V6")
    print("=" * 60)
    print()
    
    # Informações do sistema
    print_system_info()
    
    start_time = time.time()
    
    try:
        # Se apenas build, fazer só isso e sair
        if args.build_only:
            print("\n" + "=" * 60)
            print("🐳 MODO: APENAS BUILD E PUSH DAS IMAGENS")
            print("=" * 60)
            
            infrastructure = get_infrastructure_manager()
            if infrastructure.build_and_push_all():
                print("✅ Imagens construídas e enviadas com sucesso")
                return True
            else:
                print("❌ Falha no build das imagens Docker")
                return False
        
        # 1. BUILD E PUSH DAS IMAGENS DOCKER
        if not args.skip_build:
            print("\n" + "=" * 60)
            print("🐳 FASE 1: BUILD E PUSH DAS IMAGENS DOCKER")
            print("=" * 60)
            
            infrastructure = get_infrastructure_manager()
            if not infrastructure.build_and_push_all():
                print("❌ Falha no build das imagens Docker")
                return False
            
            print("✅ Imagens Docker construídas e enviadas com sucesso")
        
        # 2. EXECUÇÃO DOS TESTES
        if not args.skip_tests:
            print("\n" + "=" * 60)
            print("🧪 FASE 2: EXECUÇÃO DOS TESTES")
            print("=" * 60)
            
            # Iniciar monitoramento
            monitor.start_monitoring()
            
            executor = get_kubernetes_test_executor(
                clear_previous_data=not args.keep_data
            )
            
            # Executar todos os testes
            if not executor.run_all_tests():
                print("❌ Falha na execução dos testes")
                return False
            
            # Parar monitoramento e salvar relatório
            monitor.stop_monitoring()
            monitor.save_monitoring_report()
            
            print("✅ Todos os testes executados com sucesso")
        
        # 3. ANÁLISE DOS RESULTADOS
        if not args.skip_analysis:
            print("\n" + "=" * 60)
            print("📊 FASE 3: ANÁLISE DOS RESULTADOS")
            print("=" * 60)
            
            analyzer = get_result_analyzer()
            if not analyzer.analyze_all_results():
                print("❌ Falha na análise dos resultados")
                return False
            
            print("✅ Análise concluída com sucesso")
        
        # 4. GERAÇÃO DE GRÁFICOS
        if not args.skip_charts:
            print("\n" + "=" * 60)
            print("📈 FASE 4: GERAÇÃO DE GRÁFICOS")
            print("=" * 60)
            
            chart_generator = get_chart_generator()
            if not chart_generator.generate_all_charts():
                print("❌ Falha na geração de gráficos")
                return False
            
            print("✅ Gráficos gerados com sucesso")
        
        # RESUMO FINAL
        total_time = time.time() - start_time
        print("\n" + "=" * 60)
        print("🎉 EXECUÇÃO COMPLETA")
        print("=" * 60)
        print(f"⏱️  Tempo total: {total_time:.2f} segundos")
        print(f"📁 Resultados em: {config.RESULTS_DIR}")
        print(f"📊 Gráficos em: {config.GRAPHICS_DIR}")
        
        # Mostrar recomendações de recursos
        if monitor.snapshots:
            print("\n🔍 RECOMENDAÇÕES DE RECURSOS:")
            recommendations = monitor.get_resource_recommendations()
            for key, value in recommendations.items():
                if key != "stats":
                    print(f"• {key}: {value}")
        
        print()
        
        return True
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Execução interrompida pelo usuário")
        return False
    except Exception as e:
        print(f"\n❌ Erro durante a execução: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
