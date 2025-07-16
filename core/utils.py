"""
Módulo utilitário central para subprocessos, checagem de arquivos, logging e paralelismo.
"""
import logging
import subprocess
import threading
import concurrent.futures
from pathlib import Path
from typing import Any, Callable, Optional, List, Dict

# Configuração de logging estruturado
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("core.utils")

def run_subprocess(cmd: List[str], capture_output: bool = True, timeout: Optional[int] = None, input: Optional[str] = None) -> subprocess.CompletedProcess:
    """Executa um subprocesso de forma robusta, aceitando input opcional."""
    try:
        logger.debug(f"Executando comando: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=capture_output, text=True, timeout=timeout, input=input)
        logger.debug(f"Saída: {result.stdout.strip()}")
        return result
    except Exception as e:
        logger.error(f"Erro ao executar subprocesso: {e}")
        raise

def check_file_exists(path: str) -> bool:
    """Verifica se um arquivo existe."""
    exists = Path(path).exists()
    logger.debug(f"Arquivo {path} existe: {exists}")
    return exists

def parallel_map(func: Callable, iterable: List[Any], max_workers: int = 4) -> List[Any]:
    """Executa uma função em paralelo sobre um iterável."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(func, iterable))
    return results

def safe_import(module_name: str) -> Optional[Any]:
    """Importa um módulo de forma segura, retornando None em caso de erro."""
    try:
        return __import__(module_name)
    except ImportError as e:
        logger.warning(f"Falha ao importar {module_name}: {e}")
        return None

def get_logger(name: str = "core") -> logging.Logger:
    """Obtém um logger configurado."""
    return logging.getLogger(name)
