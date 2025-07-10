# SISTEMA DE TESTES DE ESCALABILIDADE V6
## Sistema Automatizado com Docker Hub e Kubernetes

### VISÃO GERAL
Sistema completamente refatorado que elimina dados sintéticos e executa testes reais usando:
- **Docker Hub** para distribuição de imagens
- **Kubernetes** para orquestração de pods
- **Coleta de dados reais** de interações cliente-servidor
- **Análise estatística avançada** dos resultados
- **Gráficos otimizados** para visualização

### ARQUITETURA DO SISTEMA

#### 1. CONFIGURAÇÃO (`config.py`)
- Configurações globais otimizadas para notebooks
- Parâmetros de Docker Hub e Kubernetes
- Limites de recursos adaptáveis

#### 2. GERENCIAMENTO DE INFRAESTRUTURA (`infrastructure_manager.py`)
- **DockerManager**: Build e push automático de imagens
- **KubernetesManager**: Deploy e gerenciamento de pods
- **InfrastructureManager**: Coordenação completa

#### 3. EXECUTOR DE TESTES (`test_executor.py`)
- **KubernetesTestExecutor**: Execução de testes em pods
- Coleta de dados reais de latência e throughput
- Processamento automático de resultados

#### 4. ANÁLISE DE RESULTADOS (`result_analyzer.py`)
- **ResultAnalyzer**: Análise estatística completa
- Detecção de outliers (Z-score e IQR)
- Comparação entre linguagens C e C++

#### 5. GERAÇÃO DE GRÁFICOS (`chart_generator.py`)
- **ChartGenerator**: Visualizações otimizadas
- Gráficos comparativos de performance
- Análise de tendências e correlações

#### 6. APLICAÇÕES
- **Cliente** (`applications/cliente/`): Cliente Kubernetes otimizado
- **Servidor C** (`applications/servidor-c/`): Servidor C configurável
- **Servidor C++** (`applications/servidor/`): Servidor C++ configurável

### FUNCIONALIDADES PRINCIPAIS

#### ✅ ELIMINAÇÃO DE DADOS SINTÉTICOS
- Todos os dados são coletados de execuções reais
- Interações reais cliente-servidor via pods Kubernetes
- Nenhuma geração artificial de métricas

#### ✅ DOCKER HUB INTEGRATION
- Build automático de imagens Docker
- Push para Docker Hub com sucesso garantido
- Versionamento automático de imagens

#### ✅ KUBERNETES ORCHESTRATION
- Deploy automático de pods servidores
- Execução de jobs cliente com coleta de dados
- Cleanup automático de recursos

#### ✅ ANÁLISE ESTATÍSTICA AVANÇADA
- Cálculo de métricas de latência e throughput
- Detecção e remoção de outliers
- Comparação estatística entre linguagens
- Análise de correlação entre variáveis

#### ✅ OTIMIZAÇÃO PARA NOTEBOOKS
- Configuração adaptada para recursos limitados
- Timeouts e limites otimizados
- Uso eficiente de CPU e memória

### EXECUÇÃO DO SISTEMA

#### REQUISITOS
```bash
# Docker e Docker Hub
sudo apt-get install docker.io
sudo docker login

# Kubernetes
sudo apt-get install kubectl
# Configurar kubectl para seu cluster

# Python e dependências
sudo pip install -r requirements.txt
```

#### COMANDOS PRINCIPAIS

1. **Executar sistema completo**:
```bash
python3 executar.py
```

2. **Modo demo rápido**:
```bash
python3 executar.py --demo
```

3. **Manter dados anteriores**:
```bash
python3 executar.py --keep-data
```

4. **Informações do sistema**:
```bash
python3 executar.py --info
```

### FLUXO DE EXECUÇÃO

1. **SETUP DA INFRAESTRUTURA**
   - Build e push de imagens Docker
   - Configuração do namespace Kubernetes
   - Verificação de conectividade

2. **EXECUÇÃO DOS TESTES**
   - Deploy de servidores C e C++ em pods
   - Execução de clientes com diferentes configurações
   - Coleta automática de métricas reais

3. **ANÁLISE DOS RESULTADOS**
   - Processamento estatístico dos dados
   - Detecção de outliers
   - Comparação entre linguagens

4. **GERAÇÃO DE GRÁFICOS**
   - Gráficos comparativos de performance
   - Análise de escalabilidade
   - Visualizações de tendências

5. **RELATÓRIO FINAL**
   - Resumo executivo dos resultados
   - Localização dos arquivos gerados
   - Estatísticas de execução

### ARQUIVOS GERADOS

- **CSV**: `resultados/all_results.csv` - Dados brutos
- **JSON**: `resultados/analysis_*.json` - Análises estatísticas
- **PNG**: `resultados/graficos/*.png` - Gráficos comparativos

### CONFIGURAÇÃO PADRÃO

```python
LANGUAGES = ["c", "cpp"]
SERVERS = [1, 2, 3]
CLIENTS = [5, 10, 20]
MESSAGES = [10, 50, 100]
RUNS_PER_CONFIG = 3
```

### CARACTERÍSTICAS TÉCNICAS

- **Sem dados sintéticos**: Todos os dados são reais
- **Limpeza automática**: Remove dados anteriores por padrão
- **Otimização de recursos**: Configurado para notebooks
- **Uso de sudo**: Comandos Docker e Kubernetes com privilégios
- **Sem menus**: Execução completamente automatizada
- **Logs estruturados**: Saída clara e organizada

### BENEFÍCIOS

1. **Dados Reais**: Métricas precisas de performance
2. **Automatização**: Zero intervenção manual
3. **Escalabilidade**: Configuração adaptável
4. **Análise Completa**: Estatísticas avançadas
5. **Visualização**: Gráficos otimizados
6. **Limpeza**: Ambiente sempre limpo

### TROUBLESHOOTING

- **Erro Docker**: Verificar login no Docker Hub
- **Erro Kubernetes**: Verificar configuração do kubectl
- **Erro Python**: Instalar dependências com pip
- **Erro Memória**: Usar modo demo para testes menores

### SUPORTE

Sistema completamente automatizado que funciona através do `executar.py` sem necessidade de menus ou interação manual.

Todos os dados são coletados de execuções reais de pods Kubernetes, garantindo precisão e confiabilidade dos resultados.
