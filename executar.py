#!/usr/bin/env python3
"""
EXECUTOR PRINCIPAL DO SISTEMA V6 - TESTES DE ESCALABILIDADE
Sistema completo automatizado com Docker Hub e Kubernetes - OTIMIZADO PARA MÁXIMA VELOCIDADE
"""
import sys
import os
import time
import argparse
import shutil
import subprocess
from pathlib import Path
from core.config import get_config, print_system_info
from core.infrastructure_manager import get_infrastructure_manager
from core.test_executor import get_kubernetes_test_executor
from core.result_analyzer import get_result_analyzer
from core.resource_monitor import get_resource_monitor
from core.utils import get_logger

def main() -> int:
    """Função principal do sistema"""
    logger = get_logger("Executor")
    parser = argparse.ArgumentParser(description="Sistema de Testes de Escalabilidade V6")
    parser.add_argument("--keep-data", action="store_true", help="Manter dados anteriores (não limpar)")
    parser.add_argument("--skip-build", action="store_true", help="Pular build das imagens Docker")
    parser.add_argument("--skip-tests", action="store_true", help="Pular execução dos testes")
    parser.add_argument("--skip-analysis", action="store_true", help="Pular análise dos resultados")
    parser.add_argument("--skip-charts", action="store_true", help="Pular geração de gráficos")
    parser.add_argument("--build-only", action="store_true", help="Apenas construir e enviar imagens Docker")
    args = parser.parse_args()

    config = get_config()
    monitor = get_resource_monitor()
    monitor.print_current_status()
    print("=" * 60)
    print("🚀 SISTEMA DE TESTES DE ESCALABILIDADE V6")
    print("=" * 60)
    print()
    print_system_info()
    logger.info(f"Python executável: {sys.executable}")
    logger.info(f"sys.path: {sys.path}")
    logger.info(f"PATH: {os.environ.get('PATH')}")
    kubectl_path = shutil.which('kubectl')
    docker_path = shutil.which('docker')
    logger.info(f"kubectl path: {kubectl_path}")
    logger.info(f"docker path: {docker_path}")
    success = True  # Inicializa success para evitar UnboundLocalError
    try:
        result = subprocess.run(['kubectl', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"kubectl version: {result.stdout.strip()}")
        else:
            logger.warning(f"kubectl version erro: {result.stderr.strip()}")
    except Exception as e:
        logger.warning(f"Erro ao executar 'kubectl version': {e}")
    try:
        req_file = Path("requirements.txt")
        if req_file.exists():
            logger.info("requirements.txt encontrado")
        else:
            logger.warning("requirements.txt não encontrado")
    except Exception as e:
        logger.warning(f"Erro ao checar requirements.txt: {e}")
    try:
        total_tests = getattr(config, 'TOTAL_TESTS', None)
        if total_tests is None:
            # Fallback: calcula total_tests se não existir
            if hasattr(config, 'get_total_tests'):
                total_tests = config.get_total_tests() * len(getattr(config, 'LANGUAGES', []))
            else:
                total_tests = 0
        print(f"DEBUG: total_tests = {total_tests}")
        runs_per_config = getattr(config, 'RUNS_PER_CONFIG', 10)
        avg_test_time = getattr(config, 'AVG_TEST_TIME', 2.5)
        if total_tests:
            est_total_sec = total_tests * avg_test_time
            est_h = int(est_total_sec // 3600)
            est_m = int((est_total_sec % 3600) // 60)
            est_s = int(est_total_sec % 60)
            print(f"⏳ Estimativa de tempo total: {est_h}h {est_m}m {est_s}s para {total_tests} testes")
            etapas = [
                (not args.skip_build, "Build e push das imagens Docker"),
                (not args.skip_tests, "Execução dos testes"),
                (not args.skip_analysis, "Análise dos resultados"),
                (not args.skip_charts, "Geração de gráficos")
            ]
            etapa_atual = 1
            total_etapas = sum(1 for e, _ in etapas if e)
            start_time = time.time()
            success = True
            try:
                infra = get_infrastructure_manager()
                if args.build_only:
                    print(f"[1/{total_etapas}] Build e push das imagens Docker...")
                    logger.info("Iniciando build e push das imagens Docker...")
                    success = infra.build_and_push_all()
                    print("✔️  Build finalizado.")
                    logger.info("Build e push das imagens Docker finalizado.")
                    return 0 if success else 1
                if not args.skip_build:
                    print(f"[{etapa_atual}/{total_etapas}] Build e push das imagens Docker...")
                    logger.info("Iniciando build e push das imagens Docker...")
                    success = infra.build_and_push_all()
                    print("✔️  Build finalizado.")
                    logger.info("Build e push das imagens Docker finalizado.")
                    etapa_atual += 1
                if not args.skip_tests and success:
                    print(f"[{etapa_atual}/{total_etapas}] Executando testes...")
                    logger.info("Iniciando execução dos testes de escalabilidade...")
                    executor = get_kubernetes_test_executor(clear_previous_data=not args.keep_data)
                    # Progresso dos testes
                    def progress_callback(done, total):
                        elapsed = time.time() - start_time
                        percent = 100 * done / total if total else 0
                        print(f"\r   Progresso: {done}/{total} testes ({percent:.1f}%) | Tempo: {int(elapsed)}s", end="", flush=True)
                    if hasattr(executor, 'run_all_tests'):
                        success = executor.run_all_tests(progress_callback=progress_callback)
                        print()  # Nova linha após barra de progresso
                    else:
                        success = executor.run_all_tests()
                    print("✔️  Testes finalizados.")
                    logger.info("Execução dos testes finalizada.")
                    etapa_atual += 1
                if not args.skip_analysis and success:
                    print(f"[{etapa_atual}/{total_etapas}] Analisando resultados...")
                    logger.info("Iniciando análise dos resultados...")
                    analyzer = get_result_analyzer()
                    analyzer.analyze_results([])
                    print("✔️  Análise finalizada.")
                    logger.info("Análise dos resultados finalizada.")
                    etapa_atual += 1
                if not args.skip_charts and success:
                    print(f"[{etapa_atual}/{total_etapas}] Gerando gráficos...")
                    logger.info("Iniciando geração de gráficos...")
                    # Substituir chamada antiga por execução do script unificado
                    import subprocess
                    subprocess.run([sys.executable, str(config.CORE_DIR / "unified_chart_generator.py")], check=True)
                    print("✔️  Gráficos gerados.")
                    logger.info("Geração de gráficos finalizada.")
                total_time = time.time() - start_time
                print("\n==============================")
                print("🎉 EXECUÇÃO COMPLETA")
                print(f"⏱️  Tempo total: {int(total_time//60)}m {int(total_time%60)}s")
                print(f"📁 Resultados: {config.RESULTS_DIR}")
                print(f"📊 Gráficos: {config.GRAPHICS_DIR}")
                logger.info("Execução completa do pipeline.")
            except KeyboardInterrupt:
                logger.warning("Execução interrompida pelo usuário.")
                print("\nExecução interrompida pelo usuário.")
                return 1
            except Exception as e:
                logger.error(f"Erro fatal: {e}", exc_info=True)
                print(f"\nErro fatal: {e}")
                return 1
        else:
            print("Nenhum teste a executar: verifique a configuração de TOTAL_TESTS ou parâmetros de teste.")
            logger.warning("Nenhum teste a executar: TOTAL_TESTS não definido ou igual a zero.")
            return 1
    except Exception as e:
        logger.warning(f"Não foi possível estimar o tempo total de execução: {e}")
        print(f"\nNão foi possível estimar o tempo total de execução: {e}")
    finally:
        print("\nFim da execução do executar.py.")
        logger.info("Fim da execução do executar.py.")
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
