#!/usr/bin/env python3
"""
Teste rápido para verificar se o carregamento das imagens está funcionando
"""

import sys
from pathlib import Path

# Adicionar diretório do projeto ao path
sys.path.insert(0, str(Path(__file__).parent))

from infrastructure_manager import get_infrastructure_manager

def test_image_loading():
    """Testar carregamento de imagens"""
    print("🧪 TESTANDO CARREGAMENTO DE IMAGENS")
    print("=" * 50)
    
    manager = get_infrastructure_manager()
    
    # Testar build e push
    if manager.build_and_push_all():
        print("✅ Build e push realizado com sucesso")
        return True
    else:
        print("❌ Falha no build e push")
        return False

if __name__ == "__main__":
    success = test_image_loading()
    sys.exit(0 if success else 1)
