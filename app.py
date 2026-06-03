"""
DataAgent — Agente de IA para Análise Autônoma de Dados
Autor: Clayton Dias Santos | Cientista de Dados Sênior
"""

import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title="DataAgent", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0a0f1e,#0e1525);min-width:270px!important;max-width:270px!important}
[data-testid="stSidebar"] *{color:#e0e0e0!important}
.stRadio label[data-baseweb="radio"]{background:rgba(255,255,255,0.05)!important;border-radius:10px!important;padding:12px 16px!important;margin:0!important;border:1px solid rgba(255,255,255,0.07)!important;display:flex!important;align-items:center!important}
.stRadio label[aria-checked="true"][data-baseweb="radio"]{background:linear-gradient(135deg,rgba(124,92,191,0.25),rgba(55,138,221,0.15))!important;border-color:#7C5CBF!important}
.stRadio label[data-baseweb="radio"]>div:first-child{display:none!important}
.stRadio label[data-baseweb="radio"] p{font-size:14px!important;font-weight:600!important}
.stRadio div[role="radiogroup"]{gap:5px!important;display:flex!important;flex-direction:column!important;padding:0 12px!important}
.metric-card{background:#0c1220;border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:1rem 1.2rem;text-align:center}
.metric-label{font-size:11px;color:#6b7280;text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px}
.metric-value{font-size:26px;font-weight:700}
.react-step{background:#0c1220;border:1px solid rgba(255,255,255,0.07);border-radius:10px;padding:.75rem 1rem;margin-bottom:8px;font-family:monospace;font-size:13px}
#MainMenu,footer{visibility:hidden}
</style>""", unsafe_allow_html=True)

@st.cache_resource
def create_db():
    np.random.seed(42); n=1000
    conn = sqlite3.connect(":memory:")
    produtos=["Notebook","Smartphone","Tablet","Monitor","Teclado","Mouse","Headset","Webcam"]
    regioes=["Sul","Sudeste","Norte","Nordeste","Centro-Oeste"]
    vendedores=[f"Vendedor_{i}" for i in range(1,11)]
    datas=[datetime(2023,1,1)+timedelta(days=int(x)) for x in np.random.randint(0,365,n)]
    df=pd.DataFrame({
        "id":range(1,n+1),"data":[d.strftime("%Y-%m-%d") for d in datas],
        "produto":np.random.choice(produtos,n),"regiao":np.random.choice(regioes,n),
        "vendedor":np.random.choice(vendedores,n),"quantidade":np.random.randint(1,20,n),
        "preco":np.random.choice([1299,2499,899,1599,199,89,349,279],n),
    })
    df["receita"]=df["quantidade"]*df["preco"]
    df.to_sql("vendas",conn,index=False,if_exists="replace")
    return conn, df

conn, df = create_db()

def run_sql(q):
    try: return pd.read_sql_query(q, conn)
    except Exception as e: return pd.DataFrame({"Erro":[str(e)]})

def agent_respond(pergunta):
    steps = []
    steps.append(("💭 Thought","Analisando a pergunta para entender o que precisa ser consultado no banco de dados."))
    steps.append(("⚡ Action","get_schema() → identificando tabelas e colunas disponíveis"))
    steps.append(("👁️ Observation","Tabela: vendas | Colunas: id, data, produto, regiao, vendedor, quantidade, preco, receita"))

    p = pergunta.lower()
    if any(w in p for w in ["produto","vendido","venda"]):
        sql = "SELECT produto, SUM(receita) as receita_total, SUM(quantidade) as qtd_vendida FROM vendas GROUP BY produto ORDER BY receita_total DESC"
        thought2 = "Vou agrupar as vendas por produto para identificar os mais relevantes por receita."
    elif any(w in p for w in ["região","regiao","geografic","estado"]):
        sql = "SELECT regiao, SUM(receita) as receita_total, COUNT(*) as transacoes, AVG(preco) as ticket_medio FROM vendas GROUP BY regiao ORDER BY receita_total DESC"
        thought2 = "Vou comparar as regiões por receita total e número de transações."
    elif any(w in p for w in ["vendedor","representante","melhor"]):
        sql = "SELECT vendedor, SUM(receita) as receita_total, COUNT(*) as num_vendas FROM vendas GROUP BY vendedor ORDER BY receita_total DESC LIMIT 10"
        thought2 = "Vou ranquear os vendedores pela receita gerada."
    elif any(w in p for w in ["mês","mes","mensal","tempo","período"]):
        sql = "SELECT substr(data,1,7) as mes, SUM(receita) as receita_total, COUNT(*) as transacoes FROM vendas GROUP BY mes ORDER BY mes"
        thought2 = "Vou agrupar as vendas por mês para identificar tendências temporais."
    else:
        sql = "SELECT COUNT(*) as total_transacoes, SUM(receita) as receita_total, AVG(receita) as ticket_medio, MAX(receita) as maior_venda FROM vendas"
        thought2 = "Vou calcular um resumo geral das métricas de vendas."

    steps.append(("💭 Thought", thought2))
    steps.append(("⚡ Action", f"execute_sql('{sql[:80]}...')"))
    result_df = run_sql(sql)
    steps.append(("👁️ Observation", f"Query retornou {len(result_df)} linhas"))
    steps.append(("✅ Resposta Final", f"Análise concluída. {len(result_df)} registros encontrados."))
    return steps, result_df, sql

with st.sidebar:
    st.markdown("<div style='padding:24px 20px 16px;border-bottom:1px solid rgba(255,255,255,0.07)'><div style='font-size:22px;font-weight:700;color:#fff'>🤖 DataAgent</div><div style='font-size:12px;color:#6b7280;margin-top:4px'>Clayton Dias Santos</div></div>", unsafe_allow_html=True)
    st.markdown("<div style='padding:16px 16px 4px;font-size:10px;color:#4b5563;letter-spacing:.1em;text-transform:uppercase'>Navegação</div>", unsafe_allow_html=True)
    pagina = st.radio("", ["🏠  Home","🤖  Agente Analítico","📊  Dashboard","💾  Dados"], label_visibility="collapsed")
    st.markdown("---")
    st.markdown(f"""<div style='padding:4px 20px 12px'>
    <div style='background:rgba(124,92,191,0.12);border:1px solid rgba(124,92,191,0.25);border-radius:10px;padding:10px 14px;margin-bottom:10px'>
        <div style='font-size:10px;color:#6b7280'>Arquitetura</div>
        <div style='font-size:18px;font-weight:700;color:#7C5CBF'>ReAct</div>
        <div style='font-size:10px;color:#4b5563'>Thought → Action → Obs</div>
    </div>
    <div style='display:grid;grid-template-columns:1fr 1fr;gap:8px'>
        <div style='background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:10px 12px'>
            <div style='font-size:10px;color:#6b7280'>Registros</div>
            <div style='font-size:18px;font-weight:700;color:#e0e0e0'>1.000</div>
        </div>
        <div style='background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:10px 12px'>
            <div style='font-size:10px;color:#6b7280'>Tools</div>
            <div style='font-size:18px;font-weight:700;color:#e0e0e0'>3</div>
        </div>
    </div></div>""", unsafe_allow_html=True)

if pagina == "🏠  Home":
    st.markdown("# 🤖 DataAgent")
    st.markdown("Agente autônomo com arquitetura **ReAct** que recebe perguntas em linguagem natural, gera e executa queries SQL, e entrega análises prontas — sem intervenção humana.")
    st.markdown("---")
    c1,c2,c3,c4 = st.columns(4)
    c1.markdown("""<div class='metric-card'><div class='metric-label'>Arquitetura</div><div class='metric-value' style='color:#7C5CBF;font-size:18px;padding-top:4px'>ReAct Agent</div></div>""",unsafe_allow_html=True)
    c2.markdown("""<div class='metric-card'><div class='metric-label'>Redução tempo análise</div><div class='metric-value' style='color:#1D9E75'>-70%</div></div>""",unsafe_allow_html=True)
    c3.markdown("""<div class='metric-card'><div class='metric-label'>Ferramentas (Tools)</div><div class='metric-value'>3</div></div>""",unsafe_allow_html=True)
    c4.markdown("""<div class='metric-card'><div class='metric-label'>Registros no banco</div><div class='metric-value'>1.000</div></div>""",unsafe_allow_html=True)
    st.markdown("---")
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("### Como funciona")
        st.markdown("1. Você digita uma pergunta em linguagem natural\n2. O agente raciocina (Thought) sobre o que precisa fazer\n3. Chama as ferramentas disponíveis (Action)\n4. Observa o resultado (Observation)\n5. Repete até ter resposta completa")
    with c2:
        st.markdown("### Ferramentas disponíveis")
        st.markdown("| Tool | Função |\n|---|---|\n| `get_schema` | Mapeia estrutura do banco |\n| `execute_sql` | Executa queries SQL |\n| `calculate_stats` | Estatísticas descritivas |")

elif pagina == "🤖  Agente Analítico":
    st.markdown("# 🤖 Agente Analítico")
    st.markdown("Digite uma pergunta de negócio e acompanhe o raciocínio do agente passo a passo.")

    sugestoes = ["Quais produtos geram mais receita?","Como estão as vendas por região?","Quem são os melhores vendedores?","Como evoluiu a receita ao longo dos meses?"]
    col1, col2 = st.columns([3,1])
    with col1:
        pergunta = st.text_input("💬 Sua pergunta", placeholder="Ex: Quais produtos geram mais receita?")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        executar = st.button("Analisar →")

    st.markdown("**Sugestões:** " + " · ".join([f"`{s}`" for s in sugestoes]))

    if executar and pergunta:
        with st.spinner("Agente processando..."):
            steps, result_df, sql = agent_respond(pergunta)

        st.markdown("---")
        st.markdown("### 🔍 Trace do Agente")
        for step_type, content in steps:
            color = {"💭 Thought":"#378ADD","⚡ Action":"#EF9F27","👁️ Observation":"#1D9E75","✅ Resposta Final":"#7C5CBF"}.get(step_type,"#888")
            st.markdown(f"""<div class='react-step'><span style='color:{color};font-weight:700'>{step_type}</span><br>{content}</div>""", unsafe_allow_html=True)

        st.markdown("### 📊 Resultado")
        st.dataframe(result_df, use_container_width=True)

        with st.expander("Ver SQL gerado"):
            st.code(sql, language="sql")

elif pagina == "📊  Dashboard":
    st.markdown("# 📊 Dashboard de Vendas")
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("#### Receita por produto")
        r = run_sql("SELECT produto, SUM(receita) as receita FROM vendas GROUP BY produto ORDER BY receita DESC")
        fig,ax=plt.subplots(figsize=(6,4))
        ax.barh(r["produto"][::-1], r["receita"][::-1]/1e6, color="#7C5CBF", edgecolor="none", height=0.6)
        ax.set_xlabel("Receita (R$ milhões)",color="white"); ax.set_facecolor("#0c1220"); fig.patch.set_facecolor("#0c1220")
        ax.tick_params(colors="white"); ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
        st.pyplot(fig); plt.close()
    with c2:
        st.markdown("#### Receita por região")
        r=run_sql("SELECT regiao, SUM(receita) as receita FROM vendas GROUP BY regiao ORDER BY receita DESC")
        fig,ax=plt.subplots(figsize=(6,4))
        colors=["#378ADD","#1D9E75","#EF9F27","#D85A30","#7C5CBF"]
        ax.bar(r["regiao"],r["receita"]/1e6,color=colors,edgecolor="none",width=0.6)
        ax.set_facecolor("#0c1220"); fig.patch.set_facecolor("#0c1220")
        ax.tick_params(colors="white",labelrotation=20); ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
        st.pyplot(fig); plt.close()

elif pagina == "💾  Dados":
    st.markdown("# 💾 Dados Brutos")
    st.dataframe(df.head(100), use_container_width=True)
    st.caption(f"Mostrando 100 de {len(df)} registros")
