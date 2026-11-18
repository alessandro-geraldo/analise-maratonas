"""Atividade 2 UTFPR — análise exploratória da base CMU Boston Marathon 2021–2024.
Uso: python analisar_maratonas.py [caminho_para_csv_ou_csv.gz]
Dependências: pip install pandas matplotlib numpy
Baixe: https://cmustatistics.github.io/data-repository/data/boston-marathon-2021-2024.csv.gz
"""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

path = Path(sys.argv[1]) if len(sys.argv)>1 else Path('boston-marathon-2021-2024.csv.gz')
if not path.exists():
    raise SystemExit(f'Arquivo não encontrado: {path}. Baixe o CSV.gz no link informado no cabeçalho.')
df = pd.read_csv(path)
out = Path('resultados_atividade2'); out.mkdir(exist_ok=True)
print('Linhas:', len(df), 'Colunas:', len(df.columns)); print('Variáveis:', list(df.columns))
num_names=['Age','5K','10K','15K','20K','HALF','25K','30K','35K','40K','Finish Net','Year']
for c in num_names:
    if c in df: df[c] = pd.to_numeric(df[c],errors='coerce')
missing=df.isna().sum().sort_values(ascending=False)
missing.to_csv(out/'valores_ausentes.csv',header=['quantidade'])
dup=int(df.duplicated().sum())
checks = {}
for c in ['Age','5K','10K','15K','20K','HALF','25K','30K','35K','40K','Finish Net']:
    if c in df: checks[f'{c}: <= 0'] = int((df[c].notna() & (df[c]<=0)).sum())
if 'Age' in df: checks['Age fora da faixa plausível 18–100 (para revisão)']=int((df['Age'].notna() & ~df['Age'].between(18,100)).sum())
if 'Year' in df: checks['Year fora de 2021–2024']=int((df['Year'].notna() & ~df['Year'].between(2021,2024)).sum())
order=['5K','10K','15K','20K','HALF','25K','30K','35K','40K','Finish Net']
for a,b in zip(order,order[1:]):
    if a in df and b in df: checks[f'Tempo decrescente {a} > {b}']=int((df[a].notna() & df[b].notna() & (df[a]>df[b])).sum())
if 'M/F' in df: checks['Sexo fora de M/F ou ausente'] = int((~df['M/F'].isin(['M','F'])).sum())
pd.Series(checks).to_csv(out/'inconsistencias.csv',header=['quantidade'])
cols=[c for c in ['Age','5K','10K','HALF','Finish Net'] if c in df]
iqrs=[]
for c in cols:
    x=df[c].dropna(); q1=x.quantile(.25);q3=x.quantile(.75);iqr=q3-q1
    iqrs.append({'variavel':c,'q1':q1,'q3':q3,'iqr':iqr,'limite_inferior':q1-1.5*iqr,'limite_superior':q3+1.5*iqr,'outliers_iqr':int(((x<q1-1.5*iqr)|(x>q3+1.5*iqr)).sum())})
pd.DataFrame(iqrs).to_csv(out/'outliers_iqr.csv',index=False)
if cols:
    fig,ax=plt.subplots(figsize=(9,5)); ax.boxplot([df[c].dropna().to_numpy() for c in cols], tick_labels=cols)
    ax.set_title('Boxplot — variáveis numéricas (escalas distintas)'); ax.set_ylabel('Valores originais')
    fig.tight_layout(); fig.savefig(out/'boxplot.png',dpi=160);plt.close(fig)
if 'Finish Net' in df:
    fig,ax=plt.subplots(figsize=(8,5)); ax.hist(df['Finish Net'].dropna()/60,bins=45);ax.set_xlabel('Tempo final (minutos)'); ax.set_ylabel('Frequência');ax.set_title('Distribuição do tempo final')
    fig.tight_layout();fig.savefig(out/'distribuicao_tempo_final.png',dpi=160);plt.close(fig)
lines=[f'Total de registros: {len(df):,}',f'Total de colunas: {df.shape[1]}',f'Registros integralmente duplicados: {dup}', '', 'Valores ausentes por variável:',missing.to_string(),'', 'Inconsistências encontradas:',pd.Series(checks).to_string(),'', 'Valores discrepantes segundo IQR:',pd.DataFrame(iqrs).to_string(index=False), '', 'Categorias M/F:', df['M/F'].value_counts(dropna=False).to_string() if 'M/F' in df else 'coluna não encontrada', '', 'Registros por ano:',df['Year'].value_counts(dropna=False).sort_index().to_string() if 'Year' in df else 'coluna não encontrada', '', 'IMPORTANTE: outliers não devem ser removidos automaticamente; investigar plausibilidade esportiva.']
(out/'resumo_analise.txt').write_text('\n'.join(lines),encoding='utf-8')
print('\n'.join(lines));print('\nResultados salvos em:',out.resolve())
