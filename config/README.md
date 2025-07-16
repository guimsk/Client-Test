# Pasta config/

A pasta `config/` armazena todos os arquivos de configuração necessários para a orquestração e execução do sistema em ambientes Docker e Kubernetes.

## Arquivos e Funções

- **docker-compose.yml**: Define os serviços, redes e volumes para execução local dos containers Docker (cliente, servidores, etc).
  - Permite subir todo o ambiente com `docker-compose up`.
  - Justificativa: Facilita testes e desenvolvimento local sem necessidade de Kubernetes.

- **k8s-namespace.yaml**: Manifesto Kubernetes para criação do namespace utilizado pelo sistema.
  - Garante isolamento dos recursos no cluster.

- **k8s-servidor-c.yaml**: Manifesto Kubernetes de deployment para o servidor em C.
  - Gerado automaticamente pelo script `core/generate_k8s_yaml.py`.
  - Define imagem, recursos, variáveis de ambiente e porta do container.

- **k8s-servidor-cpp.yaml**: Manifesto Kubernetes de deployment para o servidor em C++.
  - Gerado automaticamente pelo script `core/generate_k8s_yaml.py`.
  - Define imagem, recursos, variáveis de ambiente e porta do container.

- **k8s-cliente.yaml**: Manifesto Kubernetes de deployment para o cliente.
  - Gerado automaticamente pelo script `core/generate_k8s_yaml.py`.
  - Define imagem, recursos, variáveis de ambiente e porta do container.

## Como são gerados e utilizados

- Os arquivos de deployment Kubernetes são gerados automaticamente conforme as configurações do Python, garantindo sincronização entre código e infraestrutura.
- Para gerar/atualizar os YAMLs, execute:
  ```bash
  python core/generate_k8s_yaml.py
  ```
- Para aplicar no cluster Kubernetes:
  ```bash
  kubectl apply -f config/k8s-namespace.yaml
  kubectl apply -f config/k8s-servidor-c.yaml
  kubectl apply -f config/k8s-servidor-cpp.yaml
  kubectl apply -f config/k8s-cliente.yaml
  ```
- O `docker-compose.yml` pode ser usado para rodar o sistema localmente sem Kubernetes:
  ```bash
  docker-compose up --build
  ```

## Justificativa

Centralizar os arquivos de configuração facilita a manutenção, automação e portabilidade do sistema entre diferentes ambientes de execução.

---

**Resumo das Saídas do Terminal**

- **Arquivo de configuração carregado:** O sistema leu corretamente o arquivo de configuração.
- **YAML gerado com sucesso:** Manifesto Kubernetes criado sem erros.
- **Erro ao aplicar YAML:** Algum problema ao aplicar o manifesto no cluster.
- **Configuração sincronizada:** As configurações do Python e dos YAMLs estão alinhadas.

Essas mensagens ajudam a acompanhar a geração e aplicação dos arquivos de configuração.
