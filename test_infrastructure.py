#!/usr/bin/env python3
"""
Teste específico para verificar se o método build_and_push_all existe
"""

def test_infrastructure_manager():
    try:
        from infrastructure_manager import get_infrastructure_manager
        
        infra = get_infrastructure_manager()
        print("✅ InfrastructureManager carregado")
        
        # Verificar se o método existe
        if hasattr(infra, 'build_and_push_all'):
            print("✅ Método build_and_push_all encontrado")
            print(f"Tipo: {type(infra.build_and_push_all)}")
        else:
            print("❌ Método build_and_push_all não encontrado")
            print(f"Métodos disponíveis: {[m for m in dir(infra) if not m.startswith('_')]}")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_infrastructure_manager()
    exit(0 if success else 1)
