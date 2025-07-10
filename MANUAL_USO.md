# MANUAL DE USO - SISTEMA DE TESTES DE ESCALABILIDADE V6

## 🚀 CONFIGURAÇÃO INICIAL

### 1. Preparar Ambiente

#### Instalar Dependências
```bash
# Instalar Docker
sudo apt-get update
sudo apt-get install docker.io
sudo systemctl start docker
sudo systemctl enable docker

# Instalar kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Configurar cluster Kubernetes (use seu cluster existente)
# Exemplo para cluster remoto:
# kubectl config set-cluster mycluster --server=https://mycluster.example.com
# kubectl config set-context mycluster --cluster=mycluster
# kubectl config use-context mycluster
```

#### Configurar Docker Hub
```bash
# Fazer login no Docker Hub
docker login
# Insira suas credenciais do Docker Hub
```

### 2. Configurar Cluster Kubernetes

#### Usar Cluster Existente
```bash
# Verificar se há cluster disponível
kubectl cluster-info

# Se não houver cluster, configure um:
# - Para desenvolvimento: Docker Desktop, k3s, etc.
# - Para produção: EKS, GKE, AKS, etc.

# Verificar se está funcionando
kubectl get nodes
```

## 🐳 ENVIO DE IMAGENS PARA DOCKER HUB

### Passo 1: Construir e Enviar Imagens
```bash
# Verificar se sistema está configurado corretamente
python3 test_system_check.py

# Construir e enviar todas as imagens
python3 executar.py --build-only
```

### Passo 2: Verificar Imagens no Docker Hub
```bash
# Verificar imagens locais
docker images | grep scalability

# Verificar no Docker Hub (via navegador)
# https://hub.docker.com/u/guimsk
```

## 🧪 EXECUÇÃO DOS TESTES

### Execução Completa
```bash
# Executar todos os testes (após build)
python3 executar.py --skip-build
```

### Execução Personalizada
```bash
# Apenas construir imagens
python3 executar.py --build-only

# Apenas executar testes
python3 executar.py --skip-build --skip-analysis --skip-charts

# Apenas analisar resultados
python3 executar.py --skip-build --skip-tests --skip-charts

# Apenas gerar gráficos
python3 executar.py --skip-build --skip-tests --skip-analysis
```

## 🔧 SOLUÇÃO DE PROBLEMAS

### Problema: ImagePullBackOff
```bash
# Verificar se imagens estão no Docker Hub
python3 fix_images.py

# Verificar pods com problema
kubectl get pods -n scalability-test
kubectl describe pod <pod-name> -n scalability-test
```

### Problema: Cluster Kubernetes não disponível
```bash
# Verificar status do cluster
kubectl cluster-info

# Verificar contexto
kubectl config current-context

# Verificar se há nós disponíveis
kubectl get nodes
```

### Problema: Recursos insuficientes
```bash
# Verificar recursos do cluster
kubectl top nodes
kubectl describe nodes

# Reduzir configurações no config.py se necessário
```

## 📊 ESTRUTURA DOS RESULTADOS

### Arquivos Gerados
- `resultados/all_results.csv`: Dados brutos de todos os testes
- `resultados/graficos/`: Gráficos comparativos
  - `throughput_by_language.png`: Throughput por linguagem
  - `latency_by_servers.png`: Latência por número de servidores
  - `scalability_comparison.png`: Comparação de escalabilidade

### Dados Coletados
- **Throughput**: Mensagens por segundo
- **Latência**: Tempo de resposta (ms)
- **Utilização de recursos**: CPU e memória
- **Estatísticas**: Média, mediana, desvio padrão

## 🎯 CENÁRIOS DE TESTE

### Configuração Padrão
- **Linguagens**: C e C++
- **Servidores**: 2, 4, 6, 8, 10
- **Clientes**: 10, 20, 30, 40, 50, 60, 70, 80, 90, 100
- **Mensagens**: 1, 10, 100, 500, 1000, 10000
- **Execuções**: 10 por configuração

### Total de Testes
- **Combinações**: 5 × 10 × 6 = 300 configurações
- **Execuções**: 300 × 10 = 3000 testes por linguagem
- **Total**: 3000 × 2 = 6000 testes

## 🚀 FLUXO DE EXECUÇÃO COMPLETO

### 1. Preparação
```bash
# Verificar sistema
python3 test_system_check.py

# Verificar cluster Kubernetes
kubectl cluster-info

# Fazer login no Docker
docker login
```

### 2. Construção e Envio
```bash
# Construir e enviar imagens
python3 executar.py --build-only
```

### 3. Execução
```bash
# Executar todos os testes
python3 executar.py --skip-build
```

### 4. Análise
```bash
# Verificar resultados
ls resultados/
ls resultados/graficos/

# Analisar CSV
python3 -c "import pandas as pd; df = pd.read_csv('resultados/all_results.csv'); print(df.head())"
```

## 🔍 MONITORAMENTO

### Durante a Execução
```bash
# Monitorar pods
kubectl get pods -n scalability-test -w

# Monitorar recursos
kubectl top nodes
kubectl top pods -n scalability-test

# Ver logs
kubectl logs -f deployment/servidor-c-0 -n scalability-test
```

### Recursos do Sistema
```bash
# Monitor de recursos do sistema
python3 resource_monitor.py

# Monitorar em tempo real
htop
```

## 📝 CONFIGURAÇÃO PERSONALIZADA

### Modificar Cenários (config.py)
```python
# Alterar configurações
self.SERVERS = [2, 4, 6]  # Menos servidores
self.CLIENTS = [10, 20, 30]  # Menos clientes
self.MESSAGES = [100, 1000]  # Menos mensagens
self.RUNS_PER_CONFIG = 5  # Menos execuções
```

### Recursos Kubernetes (config.py)
```python
# Ajustar recursos
self.RESOURCE_LIMITS = {
    "cpu": "500m",      # Menos CPU
    "memory": "256Mi"   # Menos memória
}
```

## 🎉 RESULTADO ESPERADO

Após execução completa:
- **6000 testes executados**
- **Arquivo CSV com todos os resultados**
- **Gráficos comparativos gerados**
- **Análise estatística completa**
- **Recomendações de otimização**

---

**Sistema totalmente automatizado para testes de escalabilidade client-server com Docker Hub e Kubernetes!**
