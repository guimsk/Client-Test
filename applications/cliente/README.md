# Pasta applications/cliente/

Esta pasta contém a implementação do cliente utilizado nos testes de benchmark do sistema, responsável por enviar requisições aos servidores e medir o desempenho das respostas.

## Arquivos e Funções

- **app.py**: Implementação principal do cliente em Python.
  - Funções: inicialização do cliente, envio de requisições, coleta de métricas de latência e throughput, integração com variáveis de ambiente para configuração dinâmica.
  - Justificativa: Permite simular diferentes cargas e modos de operação, sendo facilmente configurável via Docker/Kubernetes.
  - Execução: O container é iniciado automaticamente pelo Docker/Kubernetes, ou pode ser executado manualmente com `python app.py`.

- **app_optimized.py**: Versão otimizada do cliente, com foco em performance máxima e uso eficiente de recursos.
  - Funções: otimizações de paralelismo, redução de overhead, ajustes finos de delays e batchs.
  - Justificativa: Usado para cenários de stress e validação de limites do sistema.

- **Dockerfile**: Define o ambiente de execução do cliente para containerização.
  - Instala dependências, copia scripts e define o entrypoint.
  - Justificativa: Garante portabilidade e reprodutibilidade dos testes.

- **README.md**: Este arquivo de documentação.

## Como executar

- Via Docker Compose:
  ```bash
  docker-compose up --build cliente
  ```
- Via Kubernetes (após gerar YAML):
  ```bash
  kubectl apply -f config/k8s-cliente.yaml
  ```
- Manualmente:
  ```bash
  python app.py
  ```

## Observações
- O comportamento do cliente pode ser ajustado via variáveis de ambiente (ex: `CLIENT_MODE`, `TARGET_SERVER`, etc).
- O cliente reporta métricas automaticamente para o sistema de coleta de resultados.

---

**Resumo das Saídas do Terminal**

- **Cliente iniciado:** O cliente está pronto para enviar requisições.
- **Requisição enviada para ...:** O cliente enviou uma requisição ao servidor.
- **Resposta recebida:** O cliente recebeu resposta do servidor.
- **Métricas coletadas:** Latência, throughput e outros dados foram registrados.
- **Erro de conexão:** O cliente não conseguiu se conectar ao servidor.

Essas mensagens ajudam a acompanhar o comportamento do cliente durante os testes.
