#!/usr/bin/env python3
"""
ANALISADOR DE RESULTADOS V6
Sistema de análise estatística dos resultados reais
"""

import json
import csv
import statistics
from typing import List, Dict, Any, Optional
from pathlib import Path
import numpy as np
import scipy.stats as stats

from config import get_config


class ResultAnalyzer:
    """Analisador de resultados de testes"""
    
    def __init__(self):
        self.config = get_config()
        self.results_file = self.config.RESULTS_DIR / "all_results.csv"
        self.data = []
        self._load_data()
    
    def _load_data(self):
        """Carregar dados dos resultados"""
        try:
            if self.results_file.exists():
                with open(self.results_file, 'r') as f:
                    reader = csv.DictReader(f)
                    self.data = list(reader)
                    
                # Converter tipos numéricos
                for row in self.data:
                    for key in ['num_servers', 'num_clients', 'messages_per_client', 
                              'run_number', 'duration', 'latency_avg', 'latency_min', 
                              'latency_max', 'latency_median', 'latency_stddev', 
                              'throughput', 'messages_sent', 'messages_received']:
                        try:
                            row[key] = float(row[key])
                        except (ValueError, KeyError):
                            row[key] = 0
                    
                    row['success'] = row.get('success', 'False') == 'True'
                
                print(f"📊 Carregados {len(self.data)} resultados")
            else:
                print("⚠️  Arquivo de resultados não encontrado")
                
        except Exception as e:
            print(f"❌ Erro carregando dados: {e}")
            self.data = []
    
    def analyze_all_results(self) -> bool:
        """Executar análise completa dos resultados"""
        print("📊 INICIANDO ANÁLISE COMPLETA DOS RESULTADOS")
        
        if not self.data:
            print("⚠️  Nenhum dado disponível para análise")
            return False
        
        try:
            # Análise por linguagem
            for language in self.config.LANGUAGES:
                if not self.analyze_language_results(language):
                    print(f"⚠️  Falha na análise de {language}")
            
            # Análise comparativa
            if not self.perform_comparative_analysis():
                print("⚠️  Falha na análise comparativa")
                return False
            
            print("✅ Análise completa realizada com sucesso")
            return True
            
        except Exception as e:
            print(f"❌ Erro na análise completa: {e}")
            return False
    
    def analyze_language_results(self, language: str) -> bool:
        """Analisar resultados de uma linguagem"""
        print(f"📊 Analisando resultados para {language.upper()}...")
        
        try:
            # Filtrar dados da linguagem
            lang_data = [row for row in self.data if row['language'] == language]
            
            if not lang_data:
                print(f"⚠️  Nenhum dado encontrado para {language}")
                return False
            
            # Análise estatística
            analysis = self._perform_statistical_analysis(lang_data)
            
            # Salvar análise
            analysis_file = self.config.RESULTS_DIR / f"analysis_{language}.json"
            with open(analysis_file, 'w') as f:
                json.dump(analysis, f, indent=2)
            
            print(f"✅ Análise de {language} salva em {analysis_file}")
            return True
            
        except Exception as e:
            print(f"❌ Erro na análise de {language}: {e}")
            return False
    
    def perform_comparative_analysis(self) -> bool:
        """Realizar análise comparativa entre linguagens"""
        print("🔍 Realizando análise comparativa...")
        
        try:
            comparative_analysis = {}
            
            for language in self.config.LANGUAGES:
                lang_data = [row for row in self.data if row['language'] == language]
                
                if lang_data:
                    comparative_analysis[language] = self._calculate_language_summary(lang_data)
            
            # Adicionar comparações diretas
            comparative_analysis['comparison'] = self._compare_languages(comparative_analysis)
            
            # Salvar análise comparativa
            comp_file = self.config.RESULTS_DIR / "comparative_analysis.json"
            with open(comp_file, 'w') as f:
                json.dump(comparative_analysis, f, indent=2)
            
            print(f"✅ Análise comparativa salva em {comp_file}")
            return True
            
        except Exception as e:
            print(f"❌ Erro na análise comparativa: {e}")
            return False
    
    def detect_and_remove_outliers(self) -> bool:
        """Detectar e remover outliers"""
        print("🔍 Detectando outliers...")
        
        try:
            outliers_analysis = {}
            
            for language in self.config.LANGUAGES:
                lang_data = [row for row in self.data if row['language'] == language]
                
                if lang_data:
                    outliers_analysis[language] = self._detect_outliers(lang_data)
            
            # Salvar análise de outliers
            outliers_file = self.config.RESULTS_DIR / "outlier_analysis.json"
            with open(outliers_file, 'w') as f:
                json.dump(outliers_analysis, f, indent=2)
            
            print(f"✅ Análise de outliers salva em {outliers_file}")
            return True
            
        except Exception as e:
            print(f"❌ Erro na detecção de outliers: {e}")
            return False
    
    def _perform_statistical_analysis(self, data: List[Dict]) -> Dict:
        """Realizar análise estatística detalhada"""
        analysis = {}
        
        # Métricas principais
        metrics = ['latency_avg', 'throughput', 'duration', 'error_rate']
        
        for metric in metrics:
            values = [row[metric] for row in data if row['success']]
            
            if values:
                analysis[metric] = {
                    'count': len(values),
                    'mean': statistics.mean(values),
                    'median': statistics.median(values),
                    'std': statistics.stdev(values) if len(values) > 1 else 0,
                    'min': min(values),
                    'max': max(values),
                    'p25': np.percentile(values, 25),
                    'p75': np.percentile(values, 75),
                    'p95': np.percentile(values, 95),
                    'p99': np.percentile(values, 99)
                }
        
        # Análise por configuração
        analysis['by_configuration'] = self._analyze_by_configuration(data)
        
        # Taxa de sucesso geral
        total_tests = len(data)
        successful_tests = len([row for row in data if row['success']])
        analysis['success_rate'] = successful_tests / total_tests if total_tests > 0 else 0
        
        return analysis
    
    def _analyze_by_configuration(self, data: List[Dict]) -> Dict:
        """Analisar por configuração (servers, clients, messages)"""
        config_analysis = {}
        
        # Agrupar por configuração
        configurations = {}
        for row in data:
            config_key = f"{int(row['num_servers'])}s_{int(row['num_clients'])}c_{int(row['messages_per_client'])}m"
            
            if config_key not in configurations:
                configurations[config_key] = []
            configurations[config_key].append(row)
        
        # Analisar cada configuração
        for config_key, config_data in configurations.items():
            successful_data = [row for row in config_data if row['success']]
            
            if successful_data:
                config_analysis[config_key] = {
                    'total_tests': len(config_data),
                    'successful_tests': len(successful_data),
                    'success_rate': len(successful_data) / len(config_data),
                    'avg_latency': statistics.mean([row['latency_avg'] for row in successful_data]),
                    'avg_throughput': statistics.mean([row['throughput'] for row in successful_data]),
                    'avg_duration': statistics.mean([row['duration'] for row in successful_data])
                }
        
        return config_analysis
    
    def _calculate_language_summary(self, data: List[Dict]) -> Dict:
        """Calcular resumo de uma linguagem"""
        successful_data = [row for row in data if row['success']]
        
        if not successful_data:
            return {'error': 'Nenhum teste bem-sucedido'}
        
        return {
            'total_tests': len(data),
            'successful_tests': len(successful_data),
            'success_rate': len(successful_data) / len(data),
            'avg_latency': statistics.mean([row['latency_avg'] for row in successful_data]),
            'avg_throughput': statistics.mean([row['throughput'] for row in successful_data]),
            'avg_duration': statistics.mean([row['duration'] for row in successful_data]),
            'avg_error_rate': statistics.mean([row['error_rate'] for row in successful_data])
        }
    
    def _compare_languages(self, analysis: Dict) -> Dict:
        """Comparar linguagens diretamente"""
        comparison = {}
        
        languages = [lang for lang in self.config.LANGUAGES if lang in analysis]
        
        if len(languages) >= 2:
            # Comparar latência
            latencies = {lang: analysis[lang]['avg_latency'] for lang in languages}
            best_latency = min(latencies, key=latencies.get)
            
            # Comparar throughput
            throughputs = {lang: analysis[lang]['avg_throughput'] for lang in languages}
            best_throughput = max(throughputs, key=throughputs.get)
            
            # Comparar taxa de sucesso
            success_rates = {lang: analysis[lang]['success_rate'] for lang in languages}
            best_success_rate = max(success_rates, key=success_rates.get)
            
            comparison = {
                'best_latency': best_latency,
                'best_throughput': best_throughput,
                'best_success_rate': best_success_rate,
                'latency_comparison': latencies,
                'throughput_comparison': throughputs,
                'success_rate_comparison': success_rates
            }
        
        return comparison
    
    def _detect_outliers(self, data: List[Dict]) -> Dict:
        """Detectar outliers usando Z-score e IQR"""
        outliers_analysis = {}
        
        successful_data = [row for row in data if row['success']]
        
        if not successful_data:
            return {'error': 'Nenhum teste bem-sucedido'}
        
        metrics = ['latency_avg', 'throughput', 'duration']
        
        for metric in metrics:
            values = [row[metric] for row in successful_data]
            
            if len(values) > 3:
                # Z-score outliers
                z_scores = np.abs(stats.zscore(values))
                z_outliers = [i for i, z in enumerate(z_scores) if z > 2]
                
                # IQR outliers
                q1 = np.percentile(values, 25)
                q3 = np.percentile(values, 75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                iqr_outliers = [i for i, val in enumerate(values) 
                               if val < lower_bound or val > upper_bound]
                
                outliers_analysis[metric] = {
                    'total_values': len(values),
                    'z_score_outliers': len(z_outliers),
                    'iqr_outliers': len(iqr_outliers),
                    'z_score_percentage': len(z_outliers) / len(values) * 100,
                    'iqr_percentage': len(iqr_outliers) / len(values) * 100
                }
        
        return outliers_analysis


def get_result_analyzer() -> ResultAnalyzer:
    """Obter analisador de resultados"""
    return ResultAnalyzer()


def get_comprehensive_analyzer() -> ResultAnalyzer:
    """Obter analisador de resultados (alias)"""
    return ResultAnalyzer()
