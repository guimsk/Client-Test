#!/usr/bin/env python3
"""
GERADOR DE GRÁFICOS 3D INTERATIVOS V6
Sistema de visualização 3D interativa dos resultados reais
"""

# Arquivo descontinuado. Toda a lógica de geração de gráficos foi migrada para unified_chart_generator.py.

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from pathlib import Path
from scipy.interpolate import griddata
from core.config import get_config


class ChartGenerator:
    """Gerador de gráficos 3D interativos com superfícies em onda"""
    
    def __init__(self):
        self.config = get_config()
        self.results_file = self.config.RESULTS_DIR / "all_results.csv"
        self.graphics_dir = self.config.GRAPHICS_DIR
        self.data = None
        self.errors = []
        self._load_data()
        
        # Definir comparações com explicações detalhadas
        self.comparisons = [
            {
                "metric": "latency_avg",
                "title": "Latência Média por Configuração",
                "z_label": "Latência (segundos)",
                "filename": "latency_avg_3d_overlapped.html",
                "description": "Tempo médio de resposta do servidor. Valores menores = melhor performance",
                "color_scale": "Viridis_r"  # Invertido: azul=melhor, amarelo=pior
            },
            {
                "metric": "throughput", 
                "title": "Throughput por Configuração",
                "z_label": "Throughput (req/s)",
                "filename": "throughput_3d_overlapped.html", 
                "description": "Taxa de requisições processadas por segundo. Valores maiores = melhor performance",
                "color_scale": "Viridis"  # Normal: amarelo=melhor, azul=pior
            },
            {
                "metric": "latency_stddev",
                "title": "Variabilidade da Latência",
                "z_label": "Desvio Padrão (segundos)", 
                "filename": "latency_stddev_3d_overlapped.html",
                "description": "Consistência do tempo de resposta. Valores menores = maior estabilidade",
                "color_scale": "Reds"  # Vermelho=instável
            },
            {
                "metric": "duration",
                "title": "Duração Total dos Testes", 
                "z_label": "Duração (segundos)",
                "filename": "duration_3d_overlapped.html",
                "description": "Tempo total para completar todos os testes. Menor = mais eficiente",
                "color_scale": "Blues_r"  # Azul escuro=melhor
            }
        ]

    def _load_data(self):
        """Carregar dados dos resultados"""
        try:
            if self.results_file.exists():
                self.data = pd.read_csv(self.results_file)
                # Filtrar apenas sucessos
                self.data = self.data[self.data['success'] == True]
                print(f"📊 Carregados {len(self.data)} resultados para gráficos 3D interativos")
                print(f"🔍 Colunas disponíveis: {list(self.data.columns)}")
                print(f"🏷️  Linguagens: {self.data['language'].unique()}")
                print(f"🖥️  Servidores: {sorted(self.data['num_servers'].unique())}")
                print(f"👥 Clientes: {sorted(self.data['num_clients'].unique())}")
            else:
                print("⚠️  Arquivo de resultados não encontrado")
                self.data = None
        except Exception as e:
            print(f"❌ Erro carregando dados: {e}")
            self.data = None

    def generate_all_charts(self):
        """Gerar todos os gráficos 3D interativos do sistema"""
        print("\n🌊 GERANDO GRÁFICOS 3D INTERATIVOS COM SUPERFÍCIES SOBREPOSTAS")
        print("🔵 Azul = Servidor C | 🔴 Vermelho = Servidor C++ | 🟢 Verde = Diferença")
        
        if self.data is None or self.data.empty:
            print("⚠️  Nenhum dado disponível para gráficos 3D")
            return False
        
        # Criar diretório gráfico se não existir
        self.graphics_dir.mkdir(parents=True, exist_ok=True)
        
        success_count = 0
        for comparison in self.comparisons:
            try:
                if comparison["metric"] in self.data.columns:
                    self._generate_3d_surface_comparison(comparison)
                    success_count += 1
                else:
                    print(f"⚠️  Métrica '{comparison['metric']}' não encontrada nos dados")
            except Exception as e:
                print(f"❌ Erro gerando gráfico {comparison['filename']}: {e}")
                self.errors.append(f"Erro gerando gráfico {comparison['filename']}: {e}")
        
        print(f"\n✅ {success_count}/{len(self.comparisons)} gráficos 3D interativos gerados com sucesso!")
        return success_count > 0

    def generate_all_3d_charts(self):
        """Alias para compatibilidade com testes: gera todos os gráficos 3D"""
        return self.generate_all_charts()

    def _generate_3d_surface_comparison(self, comparison):
        """Gerar gráfico 3D com superfícies sobrepostas comparando C vs C++"""
        
        # Criar figura única para sobreposição
        fig = go.Figure()
        
        # Configurações por linguagem
        languages = ['c', 'cpp']
        configs = {
            'c': {
                'name': 'Servidor C',
                'colorscale': [
                    [0.0, 'rgba(0, 0, 255, 0.8)'],   # Azul transparente
                    [0.5, 'rgba(30, 144, 255, 0.9)'], # Azul médio
                    [1.0, 'rgba(0, 0, 139, 1.0)']    # Azul escuro
                ],
                'opacity': 0.7
            },
            'cpp': {
                'name': 'Servidor C++', 
                'colorscale': [
                    [0.0, 'rgba(255, 0, 0, 0.8)'],   # Vermelho transparente
                    [0.5, 'rgba(255, 69, 0, 0.9)'],  # Vermelho médio
                    [1.0, 'rgba(139, 0, 0, 1.0)']    # Vermelho escuro
                ],
                'opacity': 0.7
            }
        }
        
        # Dados para cálculo de diferenças
        surfaces_data = {}
        
        for lang in languages:
            # Filtrar dados para a linguagem
            lang_data = self.data[self.data['language'] == lang].copy()
            
            if lang_data.empty:
                print(f"⚠️  Sem dados para linguagem '{lang}'")
                continue
            
            # Preparar grid para superfície suave
            x_unique = sorted(lang_data['num_servers'].unique())
            y_unique = sorted(lang_data['num_clients'].unique())
            
            # Agregar dados por configuração (média)
            grouped = lang_data.groupby(['num_servers', 'num_clients'])[comparison['metric']].mean().reset_index()
            
            # Criar grid regular para interpolação (mais denso para suavidade)
            xi = np.linspace(min(x_unique), max(x_unique), 30)
            yi = np.linspace(min(y_unique), max(y_unique), 30)
            Xi, Yi = np.meshgrid(xi, yi)
            
            # Interpolar valores para criar superfície suave
            try:
                points = grouped[['num_servers', 'num_clients']].values
                values = grouped[comparison['metric']].values
                Zi = griddata(points, values, (Xi, Yi), method='cubic', fill_value=np.nan)
                
                # Substituir NaN por interpolação linear quando cubic falha
                if np.isnan(Zi).any():
                    Zi = griddata(points, values, (Xi, Yi), method='linear', fill_value=np.mean(values))
                
            except Exception as e:
                print(f"⚠️  Erro na interpolação para {lang}: {e}")
                # Fallback: usar dados originais sem interpolação
                Xi, Yi = np.meshgrid(x_unique, y_unique)
                Zi = np.zeros((len(y_unique), len(x_unique)))
                for x_idx, x_val in enumerate(x_unique):
                    for y_idx, y_val in enumerate(y_unique):
                        subset = grouped[(grouped['num_servers'] == x_val) & 
                                       (grouped['num_clients'] == y_val)]
                        if not subset.empty:
                            Zi[y_idx, x_idx] = subset[comparison['metric']].iloc[0]
                        else:
                            Zi[y_idx, x_idx] = np.mean(values)
            
            # Armazenar dados para cálculo de diferenças
            surfaces_data[lang] = {'X': Xi, 'Y': Yi, 'Z': Zi, 'values': values}
            
            # Criar superfície 3D sobreposta
            surface = go.Surface(
                x=Xi,
                y=Yi, 
                z=Zi,
                colorscale=configs[lang]['colorscale'],
                name=configs[lang]['name'],
                opacity=configs[lang]['opacity'],
                showscale=False,  # Desabilitar escala individual
                hovertemplate=f"""
                <b>{configs[lang]['name']}</b><br>
                📊 Servidores: %{{x:.1f}}<br>
                👥 Clientes: %{{y:.1f}}<br>
                📈 {comparison['z_label']}: %{{z:.6f}}<br>
                <extra></extra>
                """,
                contours={
                    "x": {"show": True, "size": 1, "color": configs[lang]['colorscale'][2][1]},
                    "y": {"show": True, "size": 10, "color": configs[lang]['colorscale'][2][1]},
                    "z": {"show": True, "size": 0.05}
                }
            )
            
            fig.add_trace(surface)
        
        # Calcular e adicionar superfície de diferença se ambas existem
        if len(surfaces_data) == 2:
            self._add_difference_surface(fig, surfaces_data, comparison)
        
        # Configurar layout com instruções claras
        fig.update_layout(
            title={
                'text': f"""
                <b>🌊 {comparison['title']} - Comparação Sobreposta C vs C++</b><br>
                <sub style="color: blue;">🔵 Azul = Servidor C</sub> | 
                <sub style="color: red;">🔴 Vermelho = Servidor C++</sub> | 
                <sub style="color: green;">🟢 Verde = Diferença (C++ - C)</sub><br>
                <sub>{comparison['description']}</sub><br>
                <sub style="font-size:10px;">🔄 Clique+Arraste=Rotacionar | 🔍 Scroll=Zoom | 📌 Hover=Detalhes | 👁️ Clique na legenda para mostrar/ocultar</sub>
                """,
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 14}
            },
            scene=dict(
                xaxis_title="📊 Número de Servidores",
                yaxis_title="👥 Número de Clientes", 
                zaxis_title=f"📈 {comparison['z_label']}",
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.2)  # Ângulo otimizado para visualização
                ),
                aspectmode='cube'
            ),
            height=700,
            width=1000,
            font=dict(size=11),
            legend=dict(
                x=0.02,
                y=0.98,
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="gray",
                borderwidth=1
            )
        )
        
        # Adicionar anotações explicativas detalhadas
        fig.add_annotation(
            text=f"""
            <b>📊 COMO INTERPRETAR O GRÁFICO:</b><br><br>
            
            <b>🎯 Eixos:</b><br>
            • <b>X (Horizontal)</b>: Número de servidores (2-10)<br>
            • <b>Y (Profundidade)</b>: Número de clientes (10-100)<br>  
            • <b>Z (Altura)</b>: {comparison['z_label']}<br><br>
            
            <b>🎨 Cores das Superfícies:</b><br>
            • <b style="color: blue;">🔵 Azul</b>: Performance do Servidor C<br>
            • <b style="color: red;">🔴 Vermelho</b>: Performance do Servidor C++<br>
            • <b style="color: green;">🟢 Verde</b>: Diferença entre C++ e C<br><br>
            
            <b>🔍 Análise Visual:</b><br>
            • <b>Sobreposição</b>: Veja onde uma superfície fica acima da outra<br>
            • <b>Distância vertical</b>: Maior diferença de performance<br>
            • <b>Padrões</b>: Identifique tendências com carga crescente<br>
            • <b>Superfície verde positiva</b>: C++ melhor que C<br>
            • <b>Superfície verde negativa</b>: C melhor que C++
            """,
            xref="paper", yref="paper",
            x=1.02, y=0.98,
            showarrow=False,
            font=dict(size=9),
            bgcolor="rgba(245,245,245,0.95)",
            bordercolor="gray",
            borderwidth=1,
            align="left"
        )
        
        # Salvar gráfico interativo
        output_file = self.graphics_dir / comparison['filename']
        fig.write_html(str(output_file))
        
        print(f"✅ Gráfico 3D sobreposto salvo: {output_file}")
        
        # Calcular e exibir insights detalhados
        self._generate_detailed_insights(comparison, surfaces_data)

    def _add_difference_surface(self, fig, surfaces_data, comparison):
        """Adicionar superfície de diferença entre C++ e C"""
        try:
            # Interpolar ambas as superfícies no mesmo grid
            c_z = surfaces_data['c']['Z']
            cpp_z = surfaces_data['cpp']['Z']
            x_grid = surfaces_data['c']['X']
            y_grid = surfaces_data['c']['Y']
            
            # Calcular diferença (C++ - C)
            diff_z = cpp_z - c_z
            
            # Criar superfície de diferença
            diff_surface = go.Surface(
                x=x_grid,
                y=y_grid,
                z=diff_z,
                colorscale=[
                    [0.0, 'rgba(0, 255, 0, 0.1)'],    # Verde claro transparente (C melhor)
                    [0.5, 'rgba(255, 255, 255, 0.3)'], # Branco (neutro)
                    [1.0, 'rgba(0, 128, 0, 0.8)']     # Verde escuro (C++ melhor)
                ],
                name="Diferença (C++ - C)",
                opacity=0.4,
                showscale=True,
                colorbar=dict(
                    title=f"Diferença<br>{comparison['z_label']}",
                    x=1.1,
                    len=0.5
                ),
                hovertemplate=f"""
                <b>Diferença (C++ - C)</b><br>
                📊 Servidores: %{{x:.1f}}<br>
                👥 Clientes: %{{y:.1f}}<br>
                📈 Diferença: %{{z:.6f}}<br>
                💡 %{{z}} > 0: C++ melhor<br>
                💡 %{{z}} < 0: C melhor<br>
                <extra></extra>
                """
            )
            
            fig.add_trace(diff_surface)
            
        except Exception as e:
            print(f"⚠️  Erro criando superfície de diferença: {e}")

    def _generate_detailed_insights(self, comparison, surfaces_data):
        """Gerar insights detalhados sobre os dados com análise estatística"""
        metric = comparison['metric']
        
        # Comparar performance média entre linguagens
        c_data = self.data[self.data['language'] == 'c'][metric]
        cpp_data = self.data[self.data['language'] == 'cpp'][metric]
        
        if len(c_data) > 0 and len(cpp_data) > 0:
            c_mean = c_data.mean()
            cpp_mean = cpp_data.mean()
            c_std = c_data.std()
            cpp_std = cpp_data.std()
            c_min = c_data.min()
            cpp_min = cpp_data.min()
            c_max = c_data.max()
            cpp_max = cpp_data.max()
            
            print(f"\n📊 ANÁLISE DETALHADA - {comparison['title']}")
            print("=" * 60)
            
            # Estatísticas básicas
            print(f"📈 SERVIDOR C:")
            print(f"   • Média: {c_mean:.6f} {comparison['z_label']}")
            print(f"   • Desvio: ±{c_std:.6f}")
            print(f"   • Faixa: {c_min:.6f} - {c_max:.6f}")
            
            print(f"📈 SERVIDOR C++:")
            print(f"   • Média: {cpp_mean:.6f} {comparison['z_label']}")
            print(f"   • Desvio: ±{cpp_std:.6f}")
            print(f"   • Faixa: {cpp_min:.6f} - {cpp_max:.6f}")
            
            # Comparação direta
            diff_abs = abs(cpp_mean - c_mean)
            diff_pct = (diff_abs / max(c_mean, cpp_mean)) * 100
            
            if metric in ['latency_avg', 'latency_stddev', 'duration']:
                # Para essas métricas, menor é melhor
                if c_mean < cpp_mean:
                    better_lang = "C"
                    winner_value = c_mean
                    loser_value = cpp_mean
                    advantage = ((cpp_mean - c_mean) / cpp_mean) * 100
                else:
                    better_lang = "C++"
                    winner_value = cpp_mean
                    loser_value = c_mean
                    advantage = ((c_mean - cpp_mean) / c_mean) * 100
                print(f"\n🏆 VENCEDOR: {better_lang} (menor {comparison['z_label'].lower()} é melhor)")
            else:
                # Para throughput, maior é melhor
                if c_mean > cpp_mean:
                    better_lang = "C"
                    winner_value = c_mean
                    loser_value = cpp_mean
                    advantage = ((c_mean - cpp_mean) / cpp_mean) * 100
                else:
                    better_lang = "C++"
                    winner_value = cpp_mean
                    loser_value = c_mean
                    advantage = ((cpp_mean - c_mean) / c_mean) * 100
                print(f"\n🏆 VENCEDOR: {better_lang} (maior {comparison['z_label'].lower()} é melhor)")
            
            print(f"📊 VANTAGEM: {advantage:.2f}% ({winner_value:.6f} vs {loser_value:.6f})")
            
            # Análise de consistência
            if c_std < cpp_std:
                print(f"🎯 CONSISTÊNCIA: C é mais consistente (±{c_std:.6f} vs ±{cpp_std:.6f})")
            else:
                print(f"🎯 CONSISTÊNCIA: C++ é mais consistente (±{cpp_std:.6f} vs ±{c_std:.6f})")
            
            # Recomendação baseada nos dados
            print(f"\n💡 RECOMENDAÇÃO:")
            if advantage < 1:
                print(f"   • Performance praticamente IDÊNTICA ({advantage:.2f}% diferença)")
                print(f"   • Escolha baseada em outros fatores (manutenibilidade, etc.)")
            elif advantage < 5:
                print(f"   • Diferença PEQUENA ({advantage:.2f}%) - ambos são boas opções")
            elif advantage < 15:
                print(f"   • Diferença MODERADA ({advantage:.2f}%) - {better_lang} tem vantagem clara")
            else:
                print(f"   • Diferença SIGNIFICATIVA ({advantage:.2f}%) - {better_lang} é claramente superior")
            
            print("=" * 60)


def get_chart_generator():
    """Obter gerador de gráficos 3D interativos"""
    return ChartGenerator()


if __name__ == "__main__":
    print("🌊 GERADOR DE GRÁFICOS 3D SOBREPOSTOS")
    print("=" * 50)
    
    generator = get_chart_generator()
    
    if generator.data is not None:
        generator.generate_all_charts()
        print(f"\n🎯 Gráficos sobrepostos salvos em: {generator.graphics_dir}")
        print("📱 Abra os arquivos .html no navegador para interação completa!")
        print("🔍 Compare visualmente as superfícies azuis (C) e vermelhas (C++)")
        print("💡 Superfície verde mostra onde C++ supera C (positivo) ou vice-versa (negativo)")
    else:
        print("❌ Não foi possível carregar os dados")
