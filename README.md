# 🚀 Sistema de Testes de Escalabilidade V6

**Sistema automatizado completo para testes de performance e escalabilidade de servidores C/C++ usando Docker Hub e Kubernetes**

[![Docker Hub](https://img.shields.io/badge/Docker_Hub-guimsk-blue)](https://hub.docker.com/u/guimsk)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Compatible-brightgreen)](https://kubernetes.io/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://python.org/)

## 📋 Visão Geral

Este projeto implementa um sistema de alta performance para testes automatizados de escalabilidade, coletando dados reais de latência e throughput de servidores implementados em C e C++.

### 🎯 Características Principais

- ✅ **Execução Paralela Otimizada**: Processamento simultâneo para máxima velocidade
- ✅ **Coleta de Dados Reais**: Métricas precisas de latência e throughput
- ✅ **Docker Hub Integrado**: Build e push automático das imagens
- ✅ **Kubernetes Nativo**: Orquestração completa em cluster
- ✅ **Análise Avançada**: Geração automática de relatórios e gráficos
- ✅ **Monitoramento de Recursos**: Otimização dinâmica baseada em recursos disponíveis

## 🏗️ Arquitetura do Sistema

### Componentes Principais

| Componente | Linguagem | Propósito |
|------------|-----------|-----------|
| **Servidor C** | C puro | Implementação de alta performance |
| **Servidor C++** | C++ | Implementação com recursos avançados |
| **Cliente** | Python | Geração de carga e coleta de métricas |
| **Orquestrador** | Python | Automação e coordenação dos testes |

### Estrutura do Projeto

```
TarefaV4/
├── 📁 applications/                 # Aplicações containerizadas
│   ├── 🔧 servidor-c/              # Servidor C com Dockerfile
│   ├── 🔧 servidor/                # Servidor C++ com Dockerfile  
│   └── 🐍 cliente/                 # Cliente Python com Dockerfile
├── ⚙️  config/                     # Configurações Kubernetes
│   ├── docker-compose.yml         # Orquestração local
│   ├── k8s-servidor.yaml          # Deploy servidor C++
│   ├── k8s-servidor-c.yaml        # Deploy servidor C
│   └── k8s-namespace.yaml         # Namespace isolado
├── 📊 resultados/                  # Dados de saída
│   ├── all_results.csv            # Dataset completo
│   └── graficos/                   # Visualizações geradas
├── 🐍 Módulos Python Principais
│   ├── config.py                  # Configuração centralizada
│   ├── executar.py                # Script principal
│   ├── infrastructure_manager.py  # Gerenciamento K8s/Docker
│   ├── test_executor.py           # Execução de testes
│   ├── result_analyzer.py         # Análise de resultados
│   ├── chart_generator.py         # Geração de gráficos
│   └── resource_monitor.py        # Monitoramento de recursos
└── 📋 README.md                    # Esta documentação
```

## 🚀 Quick Start

### 1. Pré-requisitos

#### Sistema Base
```bash
# Docker e Docker Compose
sudo apt update && sudo apt install -y docker.io docker-compose
sudo usermod -aG docker $USER
```

#### Kubernetes (Minikube recomendado)
```bash
# Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install kubectl /usr/local/bin/
```

#### Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configuração Inicial

#### Iniciar Cluster Kubernetes
```bash
# Iniciar Minikube com recursos adequados
minikube start --cpus=4 --memory=8192 --disk-size=20g

# Verificar status
kubectl cluster-info
```

#### Configurar Docker Hub (Opcional)
```bash
# Login no Docker Hub para push automático
docker login
```

### 3. Execução

#### Execução Completa (Recomendado)
```bash
# Sistema completo: build, teste, análise e gráficos
python executar.py
```

#### Execução Modular
```bash
# Apenas build das imagens
python executar.py --build-only

# Pular build (usar imagens existentes)
python executar.py --skip-build

# Apenas testes (sem análise)
python executar.py --skip-analysis --skip-charts

# Manter dados anteriores
python executar.py --keep-data
```

## 📊 Configuração de Testes

### Parâmetros Padrão

O sistema executa testes com os seguintes parâmetros otimizados:

```python
LANGUAGES = ["c", "cpp"]                          # Ambas as implementações
SERVERS = [2, 4, 6, 8, 10]                      # 2 a 10 servidores
CLIENTS = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]  # 10 a 100 clientes
MESSAGES = [1, 10, 100, 500, 1000, 10000]       # 1 a 10.000 mensagens
RUNS_PER_CONFIG = 10                             # 10 execuções por cenário
```

**Total de testes**: 6.000 cenários (3.000 por linguagem)

### Otimizações Automáticas

O sistema se adapta automaticamente aos recursos disponíveis:

```python
# Detecção automática de recursos
CPU_CORES = psutil.cpu_count()                  # Cores disponíveis
MEMORY_GB = psutil.virtual_memory().total       # RAM disponível
MAX_CONCURRENT_PODS = min(CPU_CORES * 2, 16)    # Pods simultâneos
```

## 📈 Coleta de Métricas

### Dados Coletados

Para cada teste, o sistema coleta:

| Métrica | Descrição | Unidade |
|---------|-----------|---------|
| **Latência Média** | Tempo médio de resposta | milissegundos |
| **Latência Mínima** | Menor tempo observado | milissegundos |
| **Latência Máxima** | Maior tempo observado | milissegundos |
| **Latência Mediana** | Valor mediano | milissegundos |
| **Desvio Padrão** | Variabilidade da latência | milissegundos |
| **Throughput** | Requisições por segundo | req/s |
| **Taxa de Erro** | Percentual de falhas | % |

### Formato de Saída

```csv
scenario_id,language,servers,clients,messages,run,success,duration,latency_avg,latency_min,latency_max,latency_median,latency_stddev,throughput,messages_sent,messages_received,error_rate
c_2s_10c_1m_r1,c,2,10,1,1,True,0.051,50.1,45.2,55.8,49.8,3.2,1000.0,10,10,0.0
```

## 🎨 Visualizações

### Gráficos Gerados

1. **📊 Latência vs Número de Clientes**: Impacto da carga na latência
2. **🚀 Throughput vs Configuração**: Performance por cenário
3. **⚖️ Comparação C vs C++**: Análise comparativa das linguagens
4. **📈 Escalabilidade**: Comportamento com aumento de recursos

### Exemplo de Análise

```python
# Comparação automática de performance
C_avg_latency = 45.2ms
CPP_avg_latency = 48.1ms
Performance_diff = 6.4% # C é 6.4% mais rápido

C_avg_throughput = 982 req/s
CPP_avg_throughput = 951 req/s
Throughput_diff = 3.3% # C tem 3.3% mais throughput
```

## 🔧 Personalização

### Modificar Parâmetros de Teste

Edite o arquivo `config.py`:

```python
class SystemConfig:
    def __init__(self):
        # Personalizar ranges de teste
        self.SERVERS = [2, 4, 8]           # Menos configurações
        self.CLIENTS = [10, 50, 100]       # Pontos específicos
        self.MESSAGES = [1, 100, 1000]     # Cargas selecionadas
        self.RUNS_PER_CONFIG = 5           # Menos repetições
```

### Adicionar Nova Implementação

1. **Criar diretório**: `applications/servidor-nova/`
2. **Implementar servidor**: Com protocolo compatível
3. **Criar Dockerfile**: Para containerização
4. **Atualizar config.py**: Adicionar nova linguagem
5. **Criar manifest K8s**: `config/k8s-servidor-nova.yaml`

## 🐛 Troubleshooting

### Problemas Comuns

#### ❌ Erro: "Insufficient CPU/Memory"
```bash
# Aumentar recursos do Minikube
minikube stop
minikube start --cpus=6 --memory=12288
```

#### ❌ Erro: "Docker Hub login required"
```bash
# Fazer login no Docker Hub
docker login
# Ou pular push automático
python executar.py --skip-build
```

#### ❌ Erro: "Namespace not found"
```bash
# Recriar namespace
kubectl delete namespace scalability-test --ignore-not-found
kubectl create namespace scalability-test
```

### Logs e Debugging

```bash
# Verificar status dos pods
kubectl get pods -n scalability-test

# Ver logs de um teste específico
kubectl logs -n scalability-test job/cliente-test-<timestamp>

# Monitorar recursos em tempo real
kubectl top nodes
kubectl top pods -n scalability-test
```

## 📋 Comandos Úteis

### Gestão do Cluster
```bash
# Status geral
kubectl cluster-info
kubectl get nodes

# Limpar namespace de testes
kubectl delete namespace scalability-test

# Verificar imagens Docker
docker images | grep guimsk
```

### Monitoramento
```bash
# Recursos do sistema
python -c "from resource_monitor import get_resource_monitor; get_resource_monitor().print_current_status()"

# Verificar configuração
python -c "from config import print_system_info; print_system_info()"
```

## 📊 Especificações Técnicas

### Recursos Mínimos Recomendados

| Componente | Mínimo | Recomendado |
|------------|--------|-------------|
| **CPU** | 4 cores | 8+ cores |
| **RAM** | 8 GB | 16+ GB |
| **Disco** | 20 GB | 50+ GB |
| **Rede** | 100 Mbps | 1 Gbps |

### Configurações de Performance

```python
# Otimizações automáticas baseadas em recursos
MAX_CONCURRENT_PODS = min(cpu_cores * 2, 16)    # Máximo 16 pods
POD_STARTUP_DELAY = 0.5                         # 500ms entre startups
PARALLEL_EXECUTION = True                       # Execução paralela
BATCH_SIZE = min(MAX_CONCURRENT_PODS, 8)        # Processamento em lotes
```

## 🤝 Contribuição

### Estrutura para Contribuições

1. **Fork** o repositório
2. **Clone** localmente
3. **Crie branch** para feature: `git checkout -b feature/nova-funcionalidade`
4. **Teste** completamente: `python executar.py`
5. **Commit** com mensagem clara: `git commit -m "Adiciona nova funcionalidade X"`
6. **Push** para o branch: `git push origin feature/nova-funcionalidade`
7. **Abra Pull Request** com descrição detalhada

### Áreas de Melhoria

- 🔄 **Novas linguagens**: Go, Rust, Java
- 📊 **Métricas avançadas**: CPU usage, memory profiling
- 🌐 **Protocolos**: HTTP, gRPC, WebSocket
- 🔒 **Segurança**: TLS, autenticação
- ☁️ **Cloud**: AWS EKS, GCP GKE, Azure AKS

## 📄 Licença

Este projeto está sob licença MIT. Veja o arquivo `LICENSE` para detalhes.

---

# TarefaV4 - Sistema de Benchmark, Orquestração e Análise de Resultados

Este repositório contém um sistema completo para benchmark, orquestração, análise de desempenho e geração de gráficos de aplicações cliente-servidor em diferentes linguagens, com suporte a execução local, Docker e Kubernetes.

## Estrutura da Raiz

- **executar.py**: Script principal para orquestração de testes, execução paralela, coleta de resultados e integração com todos os módulos do sistema. Utiliza configurações dinâmicas para otimizar o uso de recursos e simplificar a execução.
  - **Funções principais**: `main()`, integração com `core.test_executor`, controle de progresso, logging e tratamento de erros.
  - **Justificativa**: Centraliza a execução do pipeline, garantindo robustez, modularidade e máxima performance.
  - **Execução**: `python executar.py` (parâmetros opcionais via config).

- **requirements.txt**: Lista de dependências Python necessárias para rodar o sistema.

- **test_complete_system.py**: Teste automatizado de performance e estabilidade do sistema completo, validando execução paralela, uso intensivo de recursos e robustez.
  - **Funções**: Testes de stress, validação de resultados, checagem de estabilidade.
  - **Execução**: `pytest test_complete_system.py` ou via pipeline de CI.

- **config/**: Pasta com arquivos de configuração para Docker Compose e Kubernetes, gerados automaticamente pelo sistema.

- **core/**: Módulos centrais do sistema (configuração, execução, análise, geração de YAMLs, monitoramento, utilitários, etc). Veja o README da pasta para detalhes.

- **applications/**: Implementações dos servidores e clientes em diferentes linguagens (C, C++, Python), cada uma com seu Dockerfile e scripts de execução. Veja o README de cada subpasta.

- **resultados/**: Resultados consolidados dos testes, gráficos gerados e relatórios.

## Como Executar o Sistema

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Execute o pipeline principal:
   ```bash
   python executar.py
   ```
3. Os resultados serão salvos em `resultados/all_results.csv` e os gráficos em `resultados/graficos/`.

## Observações
- O sistema ajusta automaticamente o paralelismo e os limites de recursos conforme o hardware disponível.
- Os manifests Kubernetes são gerados automaticamente em `config/` via `core/generate_k8s_yaml.py`.
- Para detalhes sobre cada módulo, consulte o README da respectiva pasta.

**Última atualização**: Janeiro 2025 | **Versão**: 6.0 | **Status**: Produção

---

**Resumo das Saídas do Terminal**

- **[OK] Gráfico salvo:** Gráfico gerado e salvo com sucesso.
- **[ERRO] Arquivo de resultados não encontrado:** Falta o arquivo de resultados para análise/gráficos.
- **Carregados X resultados:** Dados lidos corretamente para análise.
- **Nenhum dado disponível para geração de gráficos:** Não há dados válidos para gerar gráficos.
- **Configuração do sistema inicializada para performance máxima segura:** Sistema ajustou recursos automaticamente.
- **Execução completa:** Pipeline finalizado com sucesso.
- **Progresso: X/Y testes:** Andamento da execução dos testes.
- **Build finalizado / Testes finalizados / Análise finalizada / Gráficos gerados:** Etapas do pipeline concluídas.

Essas mensagens ajudam a acompanhar o fluxo do sistema e identificar rapidamente falhas ou sucesso das operações.
