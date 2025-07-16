#!/usr/bin/env python3
"""
UNIFIED CHART GENERATOR
Geração simplificada e unificada de gráficos 3D interativos para todos os cenários.
"""

import plotly.graph_objects as go
import pandas as pd
import numpy as np
from pathlib import Path
from scipy.interpolate import griddata
from core.config import get_config


def load_data(results_file):
    if not results_file.exists():
        print(f"[ERRO] Arquivo de resultados não encontrado: {results_file}")
        return None
    data = pd.read_csv(results_file)
    data = data[data['success'] == True]
    return data


def remove_outliers_iqr(df, metric):
    q1 = df[metric].quantile(0.25)
    q3 = df[metric].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return df[(df[metric] >= lower) & (df[metric] <= upper)]


def generate_surface(data, metric, x_col, y_col, title, z_label, filename, graphics_dir):
    # Remove outliers
    data = remove_outliers_iqr(data, metric)
    x_unique = sorted(data[x_col].unique())
    y_unique = sorted(data[y_col].unique())
    grouped = data.groupby([x_col, y_col])[metric].mean().reset_index()
    xi = np.linspace(min(x_unique), max(x_unique), 30)
    yi = np.linspace(min(y_unique), max(y_unique), 30)
    Xi, Yi = np.meshgrid(xi, yi)
    points = grouped[[x_col, y_col]].values
    values = grouped[metric].values
    try:
        Zi = griddata(points, values, (Xi, Yi), method='cubic', fill_value=np.nan)
        if np.isnan(Zi).any():
            Zi = griddata(points, values, (Xi, Yi), method='linear', fill_value=np.mean(values))
    except Exception:
        Xi, Yi = np.meshgrid(x_unique, y_unique)
        Zi = np.zeros((len(y_unique), len(x_unique)))
        for x_idx, x_val in enumerate(x_unique):
            for y_idx, y_val in enumerate(y_unique):
                subset = grouped[(grouped[x_col] == x_val) & (grouped[y_col] == y_val)]
                Zi[y_idx, x_idx] = subset[metric].iloc[0] if not subset.empty else np.mean(values)
    fig = go.Figure(go.Surface(x=Xi, y=Yi, z=Zi, colorscale="Viridis", opacity=0.85, showscale=True,
        colorbar=dict(title="Escala de Cores")))
    fig.update_layout(
        title=title,
        scene=dict(
            xaxis_title=x_col,
            yaxis_title=y_col,
            zaxis_title=z_label,
            aspectmode='cube'
        ),
        height=600,
        width=900,
        margin=dict(l=0, r=0, b=0, t=40),
        legend_title_text=""
    )
    # Adiciona legenda simples sobre as cores
    fig.add_annotation(
        text="Cores: Azul = valores baixos, Amarelo/Verde = valores altos",
        xref="paper", yref="paper", x=0.5, y=1.08, showarrow=False, font=dict(size=13), align="center"
    )
    output_file = graphics_dir / filename
    fig.write_html(str(output_file))
    print(f"[OK] Gráfico salvo: {output_file}")


def generate_per_scenario(data, metric, x_col, y_col, scenario_col, graphics_dir):
    scenarios = data[scenario_col].unique()
    for scenario in scenarios:
        scenario_data = data[data[scenario_col] == scenario]
        if scenario_data.empty:
            continue
        title = f"{metric} - {scenario_col}: {scenario}"
        z_label = metric
        filename = f"{metric}_{scenario_col}_{scenario}.html"
        generate_surface(scenario_data, metric, x_col, y_col, title, z_label, filename, graphics_dir)


def main():
    config = get_config()
    results_file = config.RESULTS_DIR / "all_results.csv"
    graphics_dir = config.GRAPHICS_DIR
    graphics_dir.mkdir(parents=True, exist_ok=True)
    data = load_data(results_file)
    if data is None or data.empty:
        print("[ERRO] Nenhum dado disponível para geração de gráficos.")
        return
    # Métricas principais
    metrics = [
        ("latency_avg", "Latência Média"),
        ("throughput", "Throughput"),
        ("latency_stddev", "Desvio Padrão Latência"),
        ("duration", "Duração Total")
    ]
    # Geração geral (todos os dados)
    for metric, label in metrics:
        if metric in data.columns:
            generate_surface(data, metric, "num_servers", "num_clients", label, label, f"{metric}_3d.html", graphics_dir)
    # Geração por cenário/iteração
    for metric, label in metrics:
        if metric in data.columns:
            generate_per_scenario(data, metric, "num_servers", "num_clients", "run_number", graphics_dir)

if __name__ == "__main__":
    main()
