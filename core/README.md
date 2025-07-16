# Núcleo do Sistema de Testes de Escalabilidade

Este diretório contém todos os módulos centrais do sistema, refatorados para máxima robustez, modularidade e performance.

## Estrutura da pasta core/

- `__init__.py`: Inicialização do pacote core.
- `unified_chart_generator.py`: Script unificado e simplificado para geração de gráficos 3D interativos para todos os cenários, sem explicações de interpretação e com visual limpo. Substitui todos os scripts antigos de geração de gráficos.
- `result_analyzer.py`: Análise estatística dos resultados, exportação de resumos, detecção e remoção de outliers.
- `concurrency_manager.py`: Gerenciamento dinâmico de paralelismo e uso de recursos.
- `config.py`: Centralização de todas as configurações do sistema.
- `generate_k8s_yaml.py`: Geração automática dos manifests YAML do Kubernetes, refletindo os recursos definidos no Python.
- `infrastructure_manager.py`: Gerenciamento da infraestrutura de execução (local, Docker, Kubernetes).
- `resource_monitor.py`: Monitoramento do uso de CPU, memória e outros recursos durante os testes.
- `system_monitor.py`: Ferramentas para monitoramento geral do sistema.
- `test_executor.py`: Orquestração da execução dos testes, controle de batches, integração com o gerenciador de concorrência e coleta de resultados.
- `utils.py`: Funções utilitárias diversas usadas por outros módulos.
- `resultados/`: Pasta para resultados intermediários e gráficos gerados automaticamente.

## Como usar os módulos core

- Importe via `from core.<modulo> import ...`.
- A execução principal ocorre via `executar.py`, que integra todos os módulos core.
- Para gerar YAMLs Kubernetes: `python core/generate_k8s_yaml.py`.
- Para análise ou geração de gráficos, utilize `unified_chart_generator.py`.

**Atenção:** Os scripts antigos `chart_generator.py` e `analysis_tools.py` foram removidos. Toda a geração de gráficos está centralizada em `unified_chart_generator.py`.

Consulte os docstrings de cada função/classe para detalhes de uso e parâmetros.

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
