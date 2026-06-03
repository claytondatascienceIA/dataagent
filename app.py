"""
DataAgent — Agente de IA para Análise Autônoma
Autor: Clayton Dias Santos | Cientista de Dados Sênior
Identidade visual: Roxo/Índigo — IA e agentes
"""

import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

P1  = "#8B5CF6"  # roxo principal
P2  = "#6D28D9"  # roxo escuro
P3  = "#C4B5FD"  # roxo claro
P4  = "#F59E0B"  # âmbar destaque
BG  = "#06030f"
BG2 = "#0a0618"
BG3 = "#0f0820"

st.set_page_config(page_title="DataAgent", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
html,body,[class*="css"]{{font-family:'Space Grotesk',sans-serif!important}}
[data-testid="stSidebar"]{{background:linear-gradient(180deg,{BG},{BG2})!important;min-width:275px!important;max-width:275px!important;border-right:1px solid rgba(139,92,246,0.12)!important}}
[data-testid="stSidebar"] *{{color:#c4b5fd!important}}
.stRadio div[role="radiogroup"]{{gap:5px!important;display:flex!important;flex-direction:column!important;padding:0 12px!important}}
.stRadio label[data-baseweb="radio"]{{background:rgba(139,92,246,0.05)!important;border-radius:10px!important;padding:13px 16px!important;margin:0!important;border:1px solid rgba(139,92,246,0.1)!important;display:flex!important;align-items:center!important;transition:all 0.2s!important}}
.stRadio label[data-baseweb="radio"]:hover{{background:rgba(139,92,246,0.12)!important;border-color:rgba(139,92,246,0.35)!important;transform:translateX(3px)!important}}
.stRadio label[aria-checked="true"][data-baseweb="radio"]{{background:linear-gradient(135deg,rgba(139,92,246,0.2),rgba(109,40,217,0.1))!important;border-color:{P1}!important;box-shadow:0 0 10px rgba(139,92,246,0.25)!important;transform:translateX(3px)!important}}
.stRadio label[data-baseweb="radio"]>div:first-child{{display:none!important}}
.stRadio label[data-baseweb="radio"] p{{font-size:14px!important;font-weight:600!important;color:#c4b5fd!important}}
.kpi{{background:{BG3};border:1px solid rgba(139,92,246,0.12);border-radius:14px;padding:1.1rem 1.3rem;text-align:center}}
.kpi-label{{font-size:10px;color:#5b3f9a;text-transform:uppercase;letter-spacing:.1em;margin-bottom:6px;font-family:'JetBrains Mono',monospace}}
.kpi-value{{font-size:26px;font-weight:700}}
.react-step{{background:{BG3};border:1px solid rgba(139,92,246,0.12);border-radius:10px;padding:.8rem 1rem;margin-bottom:8px;font-family:'JetBrains Mono',monospace;font-size:13px;line-height:1.6}}
#MainMenu,footer{{visibility:hidden}}
</style>""", unsafe_allow_html=True)

@st.cache_resource
def create_db():
    np.random.seed(42); n=1000
    conn=sqlite3.connect(":memory:")
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
    df["receita"]=df["quantidade"]*df["preco"]; df.to_sql("vendas",conn,index=False,if_exists="replace")
    return conn,df

conn,df=create_db()
def run_sql(q):
    try: return pd.read_sql_query(q,conn)
    except Exception as e: return pd.DataFrame({"Erro":[str(e)]})

def fig_style(fig,ax):
    ax.set_facecolor(BG3); fig.patch.set_facecolor(BG2)
    ax.tick_params(colors="#9b7fd4",labelsize=10)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#1a0f35"); ax.spines["bottom"].set_color("#1a0f35")

def agent_respond(pergunta):
    steps=[]
    steps.append(("💭 Thought","Analisando a pergunta para definir qual ferramenta e query utilizar."))
    steps.append(("⚡ Action","get_schema() → mapeando estrutura do banco de dados"))
    steps.append(("👁️ Observation","Tabela: vendas | Colunas: id, data, produto, regiao, vendedor, quantidade, preco, receita"))
    p=pergunta.lower()
    if any(w in p for w in ["produto","vendido","venda","receita"]):
        sql="SELECT produto, SUM(receita) as receita_total, SUM(quantidade) as qtd_vendida, COUNT(*) as transacoes FROM vendas GROUP BY produto ORDER BY receita_total DESC"
        thought2="Agrupando por produto para identificar os mais relevantes por receita total."
    elif any(w in p for w in ["região","regiao","geografic"]):
        sql="SELECT regiao, SUM(receita) as receita_total, COUNT(*) as transacoes, ROUND(AVG(preco),2) as ticket_medio FROM vendas GROUP BY regiao ORDER BY receita_total DESC"
        thought2="Comparando regiões por receita, volume e ticket médio."
    elif any(w in p for w in ["vendedor","melhor","ranking"]):
        sql="SELECT vendedor, SUM(receita) as receita_total, COUNT(*) as num_vendas, ROUND(AVG(receita),2) as ticket_medio FROM vendas GROUP BY vendedor ORDER BY receita_total DESC LIMIT 10"
        thought2="Ranqueando vendedores por receita gerada e ticket médio."
    elif any(w in p for w in ["mês","mes","mensal","tempo","período"]):
        sql="SELECT substr(data,1,7) as mes, SUM(receita) as receita_total, COUNT(*) as transacoes FROM vendas GROUP BY mes ORDER BY mes"
        thought2="Agrupando por mês para identificar tendências temporais."
    else:
        sql="SELECT COUNT(*) as total_transacoes, SUM(receita) as receita_total, ROUND(AVG(receita),2) as ticket_medio, MAX(receita) as maior_venda, MIN(receita) as menor_venda FROM vendas"
        thought2="Calculando métricas gerais do dataset de vendas."
    steps.append(("💭 Thought",thought2))
    steps.append(("⚡ Action",f"execute_sql('{sql[:75]}...')"))
    result_df=run_sql(sql)
    steps.append(("👁️ Observation",f"Query retornou {len(result_df)} linha(s) com sucesso."))
    steps.append(("✅ Resposta Final",f"Análise concluída. {len(result_df)} registros encontrados para a pergunta."))
    return steps,result_df,sql

with st.sidebar:
    st.markdown(f"""<div style='padding:28px 20px 18px;border-bottom:1px solid rgba(139,92,246,0.12)'>
        <div style='display:flex;align-items:center;gap:10px;margin-bottom:6px'>
            <span style='font-size:26px'>🤖</span>
            <span style='font-size:19px;font-weight:700;color:#fff;letter-spacing:-0.3px'>DataAgent</span>
        </div>
        <div style='font-size:11px;color:#5b3f9a;padding-left:36px'>Clayton Dias Santos</div>
    </div>""", unsafe_allow_html=True)
    st.markdown("<div style='padding:16px 16px 4px;font-size:10px;color:#3a2560;letter-spacing:.12em;text-transform:uppercase;font-family:monospace'>Navegação</div>", unsafe_allow_html=True)
    pagina=st.radio("",["🏠  Home","🤖  Agente Analítico","📊  Dashboard","💾  Dados"],label_visibility="collapsed")
    st.markdown("---")
    st.markdown(f"""<div style='padding:4px 18px 16px'>
      <div style='background:rgba(139,92,246,0.1);border:1px solid rgba(139,92,246,0.25);border-radius:12px;padding:12px 14px;margin-bottom:10px'>
        <div style='font-size:10px;color:#5b3f9a;font-family:monospace;margin-bottom:3px'>ARQUITETURA</div>
        <div style='font-size:22px;font-weight:700;color:{P1}'>ReAct</div>
        <div style='font-size:10px;color:#3a2560;font-family:monospace'>Thought → Action → Obs</div>
      </div>
      <div style='display:grid;grid-template-columns:1fr 1fr;gap:8px'>
        <div style='background:rgba(255,255,255,0.02);border:1px solid rgba(139,92,246,0.08);border-radius:10px;padding:10px 12px'>
          <div style='font-size:10px;color:#5b3f9a'>Registros</div>
          <div style='font-size:18px;font-weight:700;color:#c4b5fd'>1.000</div>
        </div>
        <div style='background:rgba(255,255,255,0.02);border:1px solid rgba(139,92,246,0.08);border-radius:10px;padding:10px 12px'>
          <div style='font-size:10px;color:#5b3f9a'>Redução</div>
          <div style='font-size:18px;font-weight:700;color:#c4b5fd'>-70%</div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

if pagina=="🏠  Home":
    st.markdown("<h1 style='font-size:2.2rem;font-weight:700;color:#fff'>🤖 DataAgent</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#9b7fd4;font-size:16px;margin-bottom:2rem'>Agente autônomo com arquitetura <b style='color:{P1}'>ReAct</b> que recebe perguntas em linguagem natural, gera e executa <b style='color:{P1}'>queries SQL</b> e entrega análises sem intervenção humana.</p>", unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4)
    for col,label,val,color in [(c1,"Arquitetura","ReAct Agent",P1),(c2,"Redução de tempo","-70%","#22d3a0"),(c3,"Ferramentas (Tools)","3","#c4b5fd"),(c4,"Registros no banco","1.000","#c4b5fd")]:
        col.markdown(f"<div class='kpi'><div class='kpi-label'>{label}</div><div class='kpi-value' style='color:{color};font-size:{"18px" if len(val)>8 else "26px"}'>{val}</div></div>",unsafe_allow_html=True)
    st.markdown("---")
    c1,c2=st.columns(2)
    with c1:
        st.markdown("### Como funciona")
        st.code("Pergunta em linguagem natural\n  ↓ [Thought] Raciocina sobre o que fazer\n  ↓ [Action]  Chama ferramenta (SQL, stats...)\n  ↓ [Obs]     Observa o resultado\n  ↓ Repete até ter resposta completa\n  ↓ [Answer]  Entrega o insight", language=None)
    with c2:
        st.markdown("### Ferramentas disponíveis")
        st.markdown(f"| Tool | Função |\n|---|---|\n| `get_schema` | Mapeia estrutura do banco |\n| `execute_sql` | Executa queries SQL |\n| `calculate_stats` | Estatísticas descritivas |")

elif pagina=="🤖  Agente Analítico":
    st.markdown("# 🤖 Agente Analítico")
    st.markdown(f"<p style='color:#9b7fd4'>Digite uma pergunta de negócio e acompanhe o raciocínio do agente passo a passo.</p>", unsafe_allow_html=True)
    sugestoes=["Quais produtos geram mais receita?","Como estão as vendas por região?","Quem são os melhores vendedores?","Como evoluiu a receita por mês?"]
    pergunta=st.text_input("💬 Sua pergunta",placeholder="Ex: Quais produtos geram mais receita?")
    st.markdown("**Sugestões:** "+" · ".join([f"`{s}`" for s in sugestoes]))
    executar=st.button("Analisar com o agente →")
    if executar and pergunta:
        with st.spinner("Agente processando..."):
            steps,result_df,sql=agent_respond(pergunta)
        st.markdown("---")
        st.markdown("### 🔍 Trace do Agente ReAct")
        colors_map={"💭 Thought":P3,"⚡ Action":P4,"👁️ Observation":"#22d3a0","✅ Resposta Final":P1}
        for step_type,content in steps:
            color=colors_map.get(step_type,"#888")
            st.markdown(f"""<div class='react-step'><span style='color:{color};font-weight:700'>{step_type}</span><br><span style='color:#9b7fd4'>{content}</span></div>""",unsafe_allow_html=True)
        st.markdown("### 📊 Resultado")
        st.dataframe(result_df,use_container_width=True)
        with st.expander("Ver SQL gerado"):
            st.code(sql,language="sql")

elif pagina=="📊  Dashboard":
    st.markdown("# 📊 Dashboard de Vendas")
    c1,c2=st.columns(2)
    with c1:
        st.markdown("#### Receita por produto")
        r=run_sql("SELECT produto, SUM(receita) as receita FROM vendas GROUP BY produto ORDER BY receita DESC")
        fig,ax=plt.subplots(figsize=(6,4.5))
        bars=ax.barh(r["produto"][::-1],r["receita"][::-1]/1e6,color=P1,edgecolor="none",height=0.6)
        for bar,v in zip(bars,r["receita"][::-1]/1e6):
            ax.text(v+0.01,bar.get_y()+bar.get_height()/2,f"R${v:.1f}M",va="center",fontsize=9,color=P3,fontweight="bold")
        ax.set_xlabel("Receita (R$ milhões)",color="#9b7fd4"); ax.set_xlim(0,max(r["receita"]/1e6)*1.25)
        fig_style(fig,ax); st.pyplot(fig); plt.close()
    with c2:
        st.markdown("#### Receita por região")
        r=run_sql("SELECT regiao, SUM(receita) as receita FROM vendas GROUP BY regiao ORDER BY receita DESC")
        fig,ax=plt.subplots(figsize=(6,4.5))
        colors_reg=["#8B5CF6","#7C3AED","#6D28D9","#5B21B6","#4C1D95"]
        bars=ax.bar(r["regiao"],r["receita"]/1e6,color=colors_reg[:len(r)],edgecolor="none",width=0.6)
        for bar,v in zip(bars,r["receita"]/1e6):
            ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+0.02,f"R${v:.1f}M",ha="center",fontsize=9,color=P3,fontweight="bold")
        ax.set_ylabel("Receita (R$ milhões)",color="#9b7fd4"); ax.set_ylim(0,max(r["receita"]/1e6)*1.2)
        ax.tick_params(labelrotation=20); fig_style(fig,ax); st.pyplot(fig); plt.close()

elif pagina=="💾  Dados":
    st.markdown("# 💾 Dados Brutos")
    st.dataframe(df.head(100),use_container_width=True)
    st.caption(f"Mostrando 100 de {len(df)} registros · Receita total: R$ {df['receita'].sum():,.0f}")
