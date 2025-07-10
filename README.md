# SISTEMA DE TESTE DE ESCALABILIDADE CLIENTE-SERVIDOR

## 📋 VISÃO GERAL

Sistema completo para avaliar a escalabilidade de servidores C++ e C em ambiente containerizado, com análise estatística e geração de relatórios comparativos.

### 🎯 OBJETIVO
Comparar performance entre servidores C++ e C através de execução automatizada de cenários de teste com análise estatística detalhada.

## ✅ FUNCIONALIDADES IMPLEMENTADAS

### 🔌 **Protocolo Ping-Pong Socket**
- Protocolo: `PING-{client_id}-{message_id}-{timestamp}` → `PONG-{client_id}-{message_id}-{timestamp}`
- Cliente Python com conexão persistente
- Servidores C++ e C com suporte a threads (1 thread por cliente)

### ⚙️ **Configurações Flexíveis**
- **Servidores**: 2, 4, 6, 8, 10 instâncias
- **Clientes**: 10, 20, 30, ..., 100 clientes simultâneos
- **Mensagens**: 1, 10, 100, 500, 1000, 10000 por cliente
- **Execuções**: 10 repetições por configuração = 6000 execuções totais

### 📊 **Análise e Relatórios**
- Dados salvos em CSV (`execucoes_cpp.csv`, `execucoes_c.csv`)
- Estatísticas: média, mediana, desvio padrão, outliers
- Gráficos comparativos em PNG de alta qualidade
- Relatório textual com resumo executivo

### 🚀 **Execução Automatizada**
- Pipeline consolidado em arquivo único (`executar.py`)
- Modo demonstração (`--demo`)
- Execução completa (`--full`)
- Comparação de configurações (`--compare`)

## 📂 ESTRUTURA DO PROJETO

```
/
├── executar.py              # ⭐ PIPELINE PRINCIPAL
├── main.py                  # Wrapper para executar.py
├── test_system.py           # ⭐ SISTEMA DE TESTES
├── src/
│   ├── config.py           # Configurações centralizadas
│   ├── infrastructure/
│   │   └── manager.py      # Gerenciamento Docker/K8s
│   ├── orchestration/
│   │   └── executor.py     # Orquestração de cenários
│   ├── analysis/
│   │   └── analyzer.py     # Análise estatística
│   └── visualization/
│       └── charts.py       # Geração de gráficos
├── applications/
│   ├── cliente/
│   │   ├── app.py          # Cliente Python
│   │   └── Dockerfile
│   ├── servidor/
│   │   ├── app.cpp         # Servidor C++
│   │   └── Dockerfile
│   └── servidor-c/
│       ├── app.c           # Servidor C
│       ├── Makefile
│       └── Dockerfile
├── config/
│   ├── docker-compose.yml
│   ├── k8s-namespace.yaml
│   ├── k8s-servidor.yaml
│   └── k8s-servidor-c.yaml
└── resultados/             # Diretório de saída
```

## 🚀 COMO USAR

### Pré-requisitos
```bash
# Instalar dependências Python
pip install -r requirements.txt

# Verificar Docker e Kubernetes
sudo docker --version
sudo kubectl version
```

### Execução Rápida
```bash
# Modo demonstração (verificação do sistema)
python3 executar.py --demo

# Execução completa do pipeline
python3 executar.py --full

# Comparação de configurações
python3 executar.py --compare

# Através do wrapper
python3 main.py --demo
```

### Execução Interativa
```bash
# Escolha o modo via menu
python3 executar.py
```

### Testes do Sistema
```bash
# Teste rápido
python3 test_system.py --quick

# Testes completos
python3 test_system.py
```

## 📈 CENÁRIOS DE TESTE

### Especificação Completa
- **300 configurações por linguagem** (5 × 10 × 6)
- **10 execuções por configuração**
- **6000 execuções totais** (3000 C++ + 3000 C)

### Matriz de Testes
| Servidores | Clientes | Mensagens | Execuções |
|------------|----------|-----------|-----------|
| 2,4,6,8,10 | 10-100   | 1-10000   | 10/config |

## 🔧 ARQUITETURA TÉCNICA

### Cliente Python
- **Conexão persistente** por thread de cliente
- **Carga realística** com processamento MD5
- **Pausa variável** baseada na carga de mensagens
- **Coleta de métricas** detalhada

### Servidores
- **C++**: `std::thread`, processamento incremental
- **C**: `pthread`, otimizações de performance
- **Thread-safe**: Mutex/atomic para controle de concorrência

### Infraestrutura
- **Docker**: Containerização das aplicações
- **Kubernetes**: Orquestração e escalonamento
- **Paralelização**: Execução simultânea de cenários

## 📊 RESULTADOS ESPERADOS

### Escalabilidade Observável
- **1 mensagem**: ~1ms tempo de resposta
- **10 mensagens**: ~5-10ms tempo total
- **100 mensagens**: ~50-100ms tempo total
- **1000 mensagens**: ~500-1000ms tempo total
- **10000 mensagens**: ~5-10s tempo total

### Análise Comparativa
- Gráficos de latência C++ vs C
- Distribuições estatísticas
- Análise de outliers
- Relatórios executivos

## 🔍 VALIDAÇÃO E TESTES

### Conformidade com Requisitos
- ✅ Protocolo socket ping-pong
- ✅ Parâmetros configuráveis
- ✅ Threads no servidor (1 por cliente)
- ✅ Registro em CSV
- ✅ Geração de gráficos
- ✅ Duas linguagens (C++ e C)
- ✅ Script de execução automatizada

### Testes Automatizados
- Importação de módulos
- Validação de arquivos essenciais
- Configurações do sistema
- Infraestrutura Docker/K8s
- Pipeline de execução
- Geração de relatórios

## 🔨 CORREÇÕES IMPLEMENTADAS

### Build das Imagens Docker
- Comando `sudo` garantido em todos os builds
- Timeout de 600s para builds longos
- Tratamento robusto de erros
- Limpeza automática de recursos

### Servidor C
- Correção `usleep()` não declarado (`#define _GNU_SOURCE`)
- Supressão de warnings de parâmetros não utilizados
- Makefile otimizado para compilação

### Cliente Python
- Conexão persistente (não reconecta a cada mensagem)
- Carga realística proporcional ao número de mensagens
- Pausa variável baseada na intensidade

## 🚀 CONSOLIDAÇÃO REALIZADA

### Arquivos Unificados
- `executar.py` - Pipeline principal consolidado
- `test_system.py` - Sistema de testes unificado
- `README.md` - Documentação consolidada (este arquivo)

### Arquivos Removidos
- ❌ `executar_final.py`, `executar_backup.py` - Redundantes
- ❌ `test_unified.py`, `test_graphics.py` - Consolidados
- ❌ `validador.py` - Funcionalidade integrada
- ❌ Múltiplos READMEs - Unificados neste arquivo

### Benefícios
- **Simplicidade**: 3 arquivos principais bem definidos
- **Manutenibilidade**: Código centralizado e organizado
- **Performance**: Menos I/O, imports otimizados
- **Robustez**: Tratamento de erros centralizado

## 🔗 DEPENDÊNCIAS

```
pandas>=1.3.0
numpy>=1.21.0
matplotlib>=3.4.0
seaborn>=0.11.0
psutil>=5.8.0
```

## 📞 SUPORTE

Para problemas ou dúvidas:
1. Execute `python3 test_system.py` para diagnóstico
2. Verifique logs em `resultados/`
3. Consulte documentação dos módulos em `src/`

---

**Status**: ✅ Sistema completo e operacional  
**Última atualização**: 2025-01-07  
**Versão**: Consolidada Final
