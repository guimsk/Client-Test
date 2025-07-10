#!/usr/bin/env python3
"""
GERADOR DE GRÁFICOS V6
Sistema de visualização dos resultados reais
"""

import json
import csv
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import seaborn as sns
import numpy as np
import pandas as pd
from typing import Dict, List, Any
from pathlib import Path

from config import get_config


class ChartGenerator:
    """Gerador de gráficos comparativos"""
    
    def __init__(self):
        self.config = get_config()
        self.results_file = self.config.RESULTS_DIR / "all_results.csv"
        self.data = None
        self._load_data()
        
        # Configurar estilo
        plt.style.use('default')
        try:
            plt.style.use('seaborn-v0_8')
        except OSError:
            try:
                plt.style.use('seaborn')
            except OSError:
                pass  # Usar style padrão
        sns.set_palette("husl")
    
    def _load_data(self):
        """Carregar dados dos resultados"""
        try:
            if self.results_file.exists():
                self.data = pd.read_csv(self.results_file)
                # Filtrar apenas sucessos
                self.data = self.data[self.data['success'] == True]
                print(f"📊 Carregados {len(self.data)} resultados para gráficos")
            else:
                print("⚠️  Arquivo de resultados não encontrado")
                
        except Exception as e:
            print(f"❌ Erro carregando dados: {e}")
            self.data = None
    
    def generate_all_charts(self) -> bool:
        """Gerar todos os gráficos do sistema"""
        print("📈 GERANDO TODOS OS GRÁFICOS")
        
        if self.data is None or self.data.empty:
            print("⚠️  Nenhum dado disponível para gráficos")
            return False
        
        try:
            # Gerar gráfico principal
            if not self.generate_complete_comparison_chart():
                print("⚠️  Falha no gráfico principal")
                return False
            
            # Gerar gráficos por linguagem
            for language in self.config.LANGUAGES:
                if not self.generate_language_specific_charts(language):
                    print(f"⚠️  Falha nos gráficos de {language}")
            
            # Gerar gráficos de análise detalhada
            if not self.generate_detailed_analysis_charts():
                print("⚠️  Falha nos gráficos de análise detalhada")
                return False
            
            print("✅ Todos os gráficos gerados com sucesso")
            return True
            
        except Exception as e:
            print(f"❌ Erro na geração de gráficos: {e}")
            return False
    
    def generate_complete_comparison_chart(self) -> bool:
        """Gerar gráfico de comparação completo principal"""
        print("📈 Gerando gráfico de comparação completo...")
        
        if self.data is None or len(self.data) == 0:
            print("❌ Nenhum dado disponível para gráficos")
            return False
        
        try:
            # Criar figura com múltiplos subplots
            fig, axes = plt.subplots(2, 2, figsize=(20, 16))
            fig.suptitle('COMPARAÇÃO COMPLETA DE PERFORMANCE - C vs C++', 
                        fontsize=20, fontweight='bold')
            
            # Subplot 1: Latência por configuração
            self._plot_latency_comparison(axes[0, 0])
            
            # Subplot 2: Throughput por configuração
            self._plot_throughput_comparison(axes[0, 1])
            
            # Subplot 3: Escalabilidade (servidores vs performance)
            self._plot_scalability_analysis(axes[1, 0])
            
            # Subplot 4: Distribuição de performance
            self._plot_performance_distribution(axes[1, 1])
            
            # Ajustar layout
            plt.tight_layout()
            plt.subplots_adjust(top=0.93)
            
            # Salvar gráfico
            chart_file = self.config.GRAPHICS_DIR / "complete_comparison.png"
            plt.savefig(chart_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"✅ Gráfico principal salvo em {chart_file}")
            return True
            
        except Exception as e:
            print(f"❌ Erro gerando gráfico: {e}")
            return False
    
    def _plot_latency_comparison(self, ax):
        """Plotar comparação de latência"""
        try:
            # Agrupar por configuração e linguagem
            grouped = self.data.groupby(['language', 'num_servers', 'num_clients'])['latency_avg'].mean().unstack(level=0)
            
            # Criar gráfico de barras
            grouped.plot(kind='bar', ax=ax, width=0.8)
            ax.set_title('Latência Média por Configuração', fontsize=14, fontweight='bold')
            ax.set_xlabel('Configuração (Servidores, Clientes)', fontsize=12)
            ax.set_ylabel('Latência Média (s)', fontsize=12)
            ax.legend(title='Linguagem', title_fontsize=12)
            ax.grid(True, alpha=0.3)
            
            # Rotacionar labels
            ax.tick_params(axis='x', rotation=45)
            
        except Exception as e:
            print(f"⚠️  Erro no gráfico de latência: {e}")
    
    def _plot_throughput_comparison(self, ax):
        """Plotar comparação de throughput"""
        try:
            # Agrupar por configuração e linguagem
            grouped = self.data.groupby(['language', 'num_servers', 'num_clients'])['throughput'].mean().unstack(level=0)
            
            # Criar gráfico de barras
            grouped.plot(kind='bar', ax=ax, width=0.8)
            ax.set_title('Throughput Médio por Configuração', fontsize=14, fontweight='bold')
            ax.set_xlabel('Configuração (Servidores, Clientes)', fontsize=12)
            ax.set_ylabel('Throughput (req/s)', fontsize=12)
            ax.legend(title='Linguagem', title_fontsize=12)
            ax.grid(True, alpha=0.3)
            
            # Rotacionar labels
            ax.tick_params(axis='x', rotation=45)
            
        except Exception as e:
            print(f"⚠️  Erro no gráfico de throughput: {e}")
    
    def _plot_scalability_analysis(self, ax):
        """Plotar análise de escalabilidade"""
        try:
            # Análise de escalabilidade por número de servidores
            scalability_data = self.data.groupby(['language', 'num_servers'])['throughput'].mean().unstack(level=0)
            
            # Criar gráfico de linha
            scalability_data.plot(kind='line', ax=ax, marker='o', linewidth=2, markersize=8)
            ax.set_title('Escalabilidade - Throughput vs Número de Servidores', fontsize=14, fontweight='bold')
            ax.set_xlabel('Número de Servidores', fontsize=12)
            ax.set_ylabel('Throughput Médio (req/s)', fontsize=12)
            ax.legend(title='Linguagem', title_fontsize=12)
            ax.grid(True, alpha=0.3)
            
        except Exception as e:
            print(f"⚠️  Erro no gráfico de escalabilidade: {e}")
    
    def _plot_performance_distribution(self, ax):
        """Plotar distribuição de performance"""
        try:
            # Criar boxplot para comparar distribuições
            data_for_box = []
            labels = []
            
            for lang in self.config.LANGUAGES:
                lang_data = self.data[self.data['language'] == lang]
                if len(lang_data) > 0:
                    data_for_box.append(lang_data['latency_avg'])
                    labels.append(lang.upper())
            
            if data_for_box:
                ax.boxplot(data_for_box, labels=labels)
                ax.set_title('Distribuição de Latência por Linguagem', fontsize=14, fontweight='bold')
                ax.set_ylabel('Latência (s)', fontsize=12)
                ax.grid(True, alpha=0.3)
            
        except Exception as e:
            print(f"⚠️  Erro no gráfico de distribuição: {e}")
    
    def generate_detailed_analysis_charts(self) -> bool:
        """Gerar gráficos de análise detalhada"""
        print("📊 Gerando gráficos de análise detalhada...")
        
        if self.data is None or len(self.data) == 0:
            print("❌ Nenhum dado disponível para análise detalhada")
            return False
        
        try:
            # Gráfico de correlação
            self._generate_correlation_chart()
            
            # Gráfico de heatmap de performance
            self._generate_performance_heatmap()
            
            # Gráfico de tendências
            self._generate_trends_chart()
            
            return True
            
        except Exception as e:
            print(f"❌ Erro gerando análise detalhada: {e}")
            return False
    
    def _generate_correlation_chart(self):
        """Gerar gráfico de correlação"""
        try:
            # Selecionar colunas numéricas
            numeric_cols = ['num_servers', 'num_clients', 'messages_per_client', 
                           'latency_avg', 'throughput', 'duration']
            
            correlation_data = self.data[numeric_cols].corr()
            
            # Criar heatmap
            plt.figure(figsize=(10, 8))
            sns.heatmap(correlation_data, annot=True, cmap='coolwarm', center=0)
            plt.title('Matriz de Correlação das Métricas', fontsize=16, fontweight='bold')
            
            # Salvar
            chart_file = self.config.GRAPHICS_DIR / "correlation_analysis.png"
            plt.savefig(chart_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"✅ Gráfico de correlação salvo em {chart_file}")
            
        except Exception as e:
            print(f"⚠️  Erro no gráfico de correlação: {e}")
    
    def _generate_performance_heatmap(self):
        """Gerar heatmap de performance"""
        try:
            # Criar pivot table para heatmap
            pivot_data = self.data.pivot_table(
                values='latency_avg',
                index='num_servers',
                columns='num_clients',
                aggfunc='mean'
            )
            
            # Criar heatmap para cada linguagem
            for lang in self.config.LANGUAGES:
                lang_data = self.data[self.data['language'] == lang]
                
                if len(lang_data) > 0:
                    pivot_lang = lang_data.pivot_table(
                        values='latency_avg',
                        index='num_servers',
                        columns='num_clients',
                        aggfunc='mean'
                    )
                    
                    plt.figure(figsize=(10, 6))
                    sns.heatmap(pivot_lang, annot=True, cmap='YlOrRd', fmt='.3f')
                    plt.title(f'Heatmap de Latência - {lang.upper()}', fontsize=16, fontweight='bold')
                    plt.xlabel('Número de Clientes', fontsize=12)
                    plt.ylabel('Número de Servidores', fontsize=12)
                    
                    # Salvar
                    chart_file = self.config.GRAPHICS_DIR / f"heatmap_{lang}.png"
                    plt.savefig(chart_file, dpi=300, bbox_inches='tight')
                    plt.close()
                    
                    print(f"✅ Heatmap {lang} salvo em {chart_file}")
            
        except Exception as e:
            print(f"⚠️  Erro no heatmap: {e}")
    
    def _generate_trends_chart(self):
        """Gerar gráfico de tendências"""
        try:
            # Análise de tendências por número de mensagens
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
            
            # Tendência de latência
            for lang in self.config.LANGUAGES:
                lang_data = self.data[self.data['language'] == lang]
                if len(lang_data) > 0:
                    trend_data = lang_data.groupby('messages_per_client')['latency_avg'].mean()
                    ax1.plot(trend_data.index, trend_data.values, marker='o', 
                            label=lang.upper(), linewidth=2)
            
            ax1.set_title('Tendência de Latência vs Mensagens', fontsize=14, fontweight='bold')
            ax1.set_xlabel('Mensagens por Cliente', fontsize=12)
            ax1.set_ylabel('Latência Média (s)', fontsize=12)
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Tendência de throughput
            for lang in self.config.LANGUAGES:
                lang_data = self.data[self.data['language'] == lang]
                if len(lang_data) > 0:
                    trend_data = lang_data.groupby('messages_per_client')['throughput'].mean()
                    ax2.plot(trend_data.index, trend_data.values, marker='o', 
                            label=lang.upper(), linewidth=2)
            
            ax2.set_title('Tendência de Throughput vs Mensagens', fontsize=14, fontweight='bold')
            ax2.set_xlabel('Mensagens por Cliente', fontsize=12)
            ax2.set_ylabel('Throughput Médio (req/s)', fontsize=12)
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Salvar
            chart_file = self.config.GRAPHICS_DIR / "trends_analysis.png"
            plt.savefig(chart_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"✅ Gráfico de tendências salvo em {chart_file}")
            
        except Exception as e:
            print(f"⚠️  Erro no gráfico de tendências: {e}")


def get_chart_generator() -> ChartGenerator:
    """Obter gerador de gráficos"""
    return ChartGenerator()
