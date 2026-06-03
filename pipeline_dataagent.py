"""
DataAgent — Agente de IA para Análise Autônoma de Dados
Autor: Clayton Dias Santos | Cientista de Dados Sênior
Arquitetura: ReAct Agent + LLM (Claude/OpenAI) + SQL
"""

import os
import json
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

print("=" * 60)
print("DataAgent — Agente de IA para Análise Autônoma")
print("Autor: Clayton Dias Santos | Cientista de Dados Sênior")
print("=" * 60)

# ─────────────────────────────────────────────
# 1. BANCO DE DADOS SINTÉTICO (SQLite)
# ─────────────────────────────────────────────
print("\n[STEP 1] Criando banco de dados sintético...")

conn = sqlite3.connect(":memory:")

np.random.seed(42)
n = 1000
produtos   = ["Notebook","Smartphone","Tablet","Monitor","Teclado","Mouse","Headset","Webcam"]
regioes    = ["Sul","Sudeste","Norte","Nordeste","Centro-Oeste"]
vendedores = [f"Vendedor_{i}" for i in range(1, 11)]

datas = [datetime(2023,1,1) + timedelta(days=int(x)) for x in np.random.randint(0,365,n)]

df_vendas = pd.DataFrame({
    "id":        range(1, n+1),
    "data":      [d.strftime("%Y-%m-%d") for d in datas],
    "produto":   np.random.choice(produtos, n),
    "regiao":    np.random.choice(regioes, n),
    "vendedor":  np.random.choice(vendedores, n),
    "quantidade":np.random.randint(1, 20, n),
    "preco":     np.random.choice([1299,2499,899,1599,199,89,349,279], n),
})
df_vendas["receita"] = df_vendas["quantidade"] * df_vendas["preco"]
df_vendas.to_sql("vendas", conn, index=False, if_exists="replace")

print(f"✔ Tabela 'vendas' criada: {n} registros")
print(f"  Receita total: R$ {df_vendas['receita'].sum():,.0f}")


# ─────────────────────────────────────────────
# 2. FERRAMENTAS DO AGENTE (Tools)
# ─────────────────────────────────────────────
print("\n[STEP 2] Definindo ferramentas do agente...")

def execute_sql(query: str) -> str:
    """Executa uma query SQL e retorna resultado como string."""
    try:
        result = pd.read_sql_query(query, conn)
        return result.to_string(index=False)
    except Exception as e:
        return f"Erro SQL: {str(e)}"

def get_schema() -> str:
    """Retorna o schema do banco de dados."""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    schema = []
    for (table,) in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        cols = cursor.fetchall()
        schema.append(f"Tabela: {table}")
        for col in cols:
            schema.append(f"  - {col[1]} ({col[2]})")
    return "\n".join(schema)

def calculate_stats(column: str, table: str = "vendas") -> str:
    """Calcula estatísticas descritivas de uma coluna."""
    try:
        df = pd.read_sql_query(f"SELECT {column} FROM {table}", conn)
        stats = df[column].describe()
        return stats.to_string()
    except Exception as e:
        return f"Erro: {str(e)}"

TOOLS = {
    "execute_sql":    execute_sql,
    "get_schema":     get_schema,
    "calculate_stats": calculate_stats,
}

print(f"✔ {len(TOOLS)} ferramentas disponíveis: {list(TOOLS.keys())}")


# ─────────────────────────────────────────────
# 3. LOOP ReAct (sem LLM externo — simulado)
# ─────────────────────────────────────────────
print("\n[STEP 3] Executando loop ReAct Agent (simulado)...")

def react_agent(pergunta: str, max_steps: int = 5) -> str:
    """
    Agente ReAct simulado.
    Em produção: integrar com Claude API ou OpenAI para geração
    dinâmica das etapas Thought → Action → Observation.
    """
    print(f"\n{'─'*50}")
    print(f"❓ Pergunta: {pergunta}")
    print(f"{'─'*50}")

    # Etapas ReAct simuladas para demonstração
    steps = []

    # Step 1: Thought + Action → get_schema
    thought1 = "Preciso entender a estrutura do banco antes de responder."
    action1  = {"tool": "get_schema", "args": {}}
    obs1     = TOOLS["get_schema"]()
    steps.append(("Thought", thought1))
    steps.append(("Action", f"get_schema()"))
    steps.append(("Observation", obs1[:200] + "..."))

    # Step 2: montar e executar SQL baseado na pergunta
    if "produto" in pergunta.lower() or "mais vendido" in pergunta.lower():
        query = "SELECT produto, SUM(receita) as receita_total, SUM(quantidade) as qtd FROM vendas GROUP BY produto ORDER BY receita_total DESC LIMIT 5"
        thought2 = "Vou agrupar vendas por produto para identificar os mais vendidos."
    elif "região" in pergunta.lower() or "regiao" in pergunta.lower():
        query = "SELECT regiao, SUM(receita) as receita_total, COUNT(*) as transacoes FROM vendas GROUP BY regiao ORDER BY receita_total DESC"
        thought2 = "Vou agrupar por região para comparar performance geográfica."
    elif "vendedor" in pergunta.lower():
        query = "SELECT vendedor, SUM(receita) as receita_total, COUNT(*) as vendas FROM vendas GROUP BY vendedor ORDER BY receita_total DESC LIMIT 5"
        thought2 = "Vou ranquear os vendedores por receita gerada."
    else:
        query = "SELECT COUNT(*) as total_vendas, SUM(receita) as receita_total, AVG(receita) as ticket_medio FROM vendas"
        thought2 = "Vou calcular métricas gerais das vendas."

    obs2 = TOOLS["execute_sql"](query)
    steps.append(("Thought", thought2))
    steps.append(("Action", f"execute_sql('{query[:60]}...')"))
    steps.append(("Observation", obs2))

    # Step 3: Gerar resposta final
    thought3 = "Com os dados obtidos, posso formular uma resposta clara e objetiva."
    steps.append(("Thought", thought3))
    steps.append(("Final Answer", f"Análise concluída com base nos dados da tabela 'vendas':\n{obs2}"))

    # Imprimir trace
    for step_type, content in steps:
        emoji = {"Thought":"💭","Action":"⚡","Observation":"👁️","Final Answer":"✅"}.get(step_type,"•")
        print(f"\n{emoji} [{step_type}]\n{content}")

    return steps[-1][1]

# Executar perguntas de exemplo
perguntas = [
    "Quais são os produtos mais vendidos por receita?",
    "Como estão as vendas por região?",
    "Quais são os top 5 vendedores?",
]

for p in perguntas:
    react_agent(p)

print(f"\n\n{'='*60}")
print("✔ Pipeline DataAgent concluída!")
print("Para uso em produção: configure ANTHROPIC_API_KEY ou OPENAI_API_KEY")
print("e substitua o loop ReAct simulado pela chamada real à API.")
print("="*60)
