import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import date, timedelta
import panorama_client as api

# ── 1. Page config — obrigatoriamente a primeira chamada Streamlit ────────────
st.set_page_config(page_title="Medway Panorama", page_icon="📊", layout="wide")

# ── 2. CSS — único bloco, imediatamente após set_page_config ──────────────────
#    Usar @import dentro do <style> evita o bug do <link> sendo exibido como texto.
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,400;9..40,500;9..40,600;9..40,700&display=swap');

html, body, [class*="css"], .stApp { font-family: 'DM Sans', sans-serif !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem !important; }

/* Cabeçalho */
.page-title    { font-size: 1.5rem; font-weight: 700; color: #1e3a5f; margin-bottom: 2px; }
.page-subtitle { font-size: 0.82rem; color: #94a3b8; margin-bottom: 18px; }

/* KPI Cards */
.kpi-row { display: flex; gap: 14px; margin-bottom: 28px; }
.kpi-card {
  background: #fff; border: 1px solid #e2e8f0; border-radius: 12px;
  padding: 18px 22px; flex: 1;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.kpi-card.alert-card {
  flex: 1.35; border-color: #fecaca;
  background: linear-gradient(135deg, #fff5f5 0%, #fff 60%);
}
.kpi-value         { font-size: 2rem; font-weight: 700; line-height: 1.1; }
.kpi-value.neutral { color: #1e293b; }
.kpi-value.green   { color: #16a34a; }
.kpi-value.yellow  { color: #d97706; }
.kpi-value.red     { color: #dc2626; }
.kpi-value.alert   { color: #b91c1c; font-size: 2.25rem; }
.kpi-label { font-size: 0.72rem; font-weight: 600; color: #64748b; margin-top: 7px; letter-spacing: 0.045em; text-transform: uppercase; }
.kpi-trend      { font-size: 0.78rem; font-weight: 600; margin-top: 5px; }
.kpi-trend.up   { color: #16a34a; }
.kpi-trend.down { color: #dc2626; }

/* Rótulos de seção */
.section-label    { font-size: 0.68rem; font-weight: 700; color: #94a3b8; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 10px; }
.section-label-mt { font-size: 0.68rem; font-weight: 700; color: #94a3b8; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 10px; margin-top: 28px; }

/* Scorecard IES */
.sc-wrap { background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
.sc-table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
.sc-table th { background: #f8fafc; color: #64748b; font-weight: 600; font-size: 0.71rem; letter-spacing: 0.055em; text-transform: uppercase; padding: 11px 16px; text-align: left; border-bottom: 2px solid #e2e8f0; }
.sc-table td { padding: 13px 16px; border-bottom: 1px solid #f1f5f9; color: #1e293b; vertical-align: middle; }
.sc-table tr:last-child td { border-bottom: none; }
.ies-name { font-weight: 600; color: #1e3a5f; }

/* Badges semáforo (Adesão / Média) */
.badge { display: inline-block; padding: 3px 11px; border-radius: 999px; font-weight: 600; font-size: 0.8rem; min-width: 58px; text-align: center; }
.bg-green  { background: #DCFCE7; color: #15803d; }
.bg-yellow { background: #FEF9C3; color: #a16207; }
.bg-red    { background: #FEE2E2; color: #b91c1c; }

/* Células coloridas Alerta / Crítico */
.cell-alerta       { background: #FEF9C3 !important; color: #92400e; font-weight: 600; }
.cell-critico      { background: #FEE2E2 !important; color: #991b1b; font-weight: 600; }
.cell-critico-bold { background: #FEE2E2 !important; color: #7f1d1d; font-weight: 800; }

/* Sub-tabela turmas */
.turma-wrap { background: #f8fafc; border-radius: 8px; padding: 4px 0; }
.turma-table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
.turma-table th { color: #94a3b8; font-size: 0.7rem; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase; padding: 7px 14px; text-align: left; border-bottom: 1px solid #e2e8f0; }
.turma-table td { padding: 9px 14px; border-bottom: 1px solid #f1f5f9; color: #334155; }
.turma-table tr:last-child td { border-bottom: none; }

/* Seção de acionáveis */
.action-header { font-size: 0.68rem; font-weight: 700; color: #94a3b8; letter-spacing: 0.08em; text-transform: uppercase; padding: 10px 0 4px 0; }
.action-turma-name { font-size: 0.82rem; color: #334155; font-weight: 500; line-height: 1.8; }
</style>
""", unsafe_allow_html=True)

# ── Query UIDs (imutáveis) ────────────────────────────────────────────────────
QUERY_DISTRIBUICAO = "e21e22ab-6da4-4808-ad51-ca6b470703c9"
QUERY_MEDIA_GERAL  = "100e49fc-8041-4cdc-ae03-7d47acff9470"
QUERY_ADESAO       = "b3ca3fd1-be26-4207-81ef-3adaf381a564"
QUERY_MATRICULADOS = "fbe59dab-e999-4d63-885d-d0bb6031bdcd"

# ── Session state: período selecionado ───────────────────────────────────────
if "period_days" not in st.session_state:
    st.session_state.period_days = 30

# ── Cabeçalho + botões de período ────────────────────────────────────────────
st.markdown('<div class="page-title">Medway Panorama</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Engajamento e desempenho dos alunos por IES</div>', unsafe_allow_html=True)

col_7, col_30, col_90, col_pad = st.columns([1, 1, 1, 8])
with col_7:
    if st.button("7 dias", use_container_width=True,
                 type="primary" if st.session_state.period_days == 7 else "secondary"):
        st.session_state.period_days = 7
        st.rerun()
with col_30:
    if st.button("30 dias", use_container_width=True,
                 type="primary" if st.session_state.period_days == 30 else "secondary"):
        st.session_state.period_days = 30
        st.rerun()
with col_90:
    if st.button("90 dias", use_container_width=True,
                 type="primary" if st.session_state.period_days == 90 else "secondary"):
        st.session_state.period_days = 90
        st.rerun()

period_days = st.session_state.period_days

# ── Helpers de extração de dados da API ──────────────────────────────────────
def _first_val(rows, uid, key):
    for row in rows:
        if row["uid"] == uid and row.get("data"):
            return row["data"][0].get(key)
    return None

# ── Carregamento principal (lógica de API preservada) ────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def load_dashboard(period_days):
    institutions = api.get_institutions()
    records = []
    for inst in institutions:
        inst_uid  = inst["uid"]
        inst_name = inst["name"]
        try:
            dist         = api.get_report_results(QUERY_DISTRIBUICAO, institution=inst_uid, period_days=period_days)
            media        = api.get_report_results(QUERY_MEDIA_GERAL,  institution=inst_uid, period_days=period_days)
            adesao       = api.get_report_results(QUERY_ADESAO,       institution=inst_uid, period_days=period_days)
            matriculados = api.get_report_results(QUERY_MATRICULADOS, institution=inst_uid, period_days=period_days)
        except Exception as e:
            st.warning(f"Erro ao carregar {inst_name}: {e}")
            continue
        for turma_row in dist:
            turma_uid  = turma_row["uid"]
            turma_name = turma_row["turma"]
            counts = {"Excelente": 0, "Adequado": 0, "Alerta": 0, "Crítico": 0}
            for d in turma_row.get("data", []):
                faixa = d.get("faixa_desempenho", "")
                if faixa in counts:
                    counts[faixa] = int(d.get("qtd_alunos", 0))
            raw_media  = _first_val(media,        turma_uid, "media_percentual_por_aluno")
            raw_adesao = _first_val(adesao,        turma_uid, "pct_alunos_login")
            raw_alunos = _first_val(matriculados,  turma_uid, "total_alunos")
            records.append({
                "IES":       inst_name,
                "Turma":     turma_name,
                "Alunos":    int(raw_alunos) if raw_alunos is not None else sum(counts.values()),
                "Adesão %":  round(float(raw_adesao), 1) if raw_adesao is not None else None,
                "Média %":   round(float(raw_media) * 100, 1) if raw_media is not None else None,
                "Excelente": counts["Excelente"],
                "Adequado":  counts["Adequado"],
                "Alerta":    counts["Alerta"],
                "Crítico":   counts["Crítico"],
            })
    return pd.DataFrame(records)

# ── Tendência: compara período atual vs período anterior ─────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def load_trend(period_days):
    """
    Tenta buscar o período anterior para calcular delta nos KPI cards.
    Retorna dict com 'adesao_delta' e/ou 'media_delta' se a API suportar.
    Falha silenciosa em qualquer erro.
    """
    today     = date.today()
    curr_end  = today.strftime("%Y-%m-%d")
    curr_start= (today - timedelta(days=period_days)).strftime("%Y-%m-%d")
    prev_end  = (today - timedelta(days=period_days + 1)).strftime("%Y-%m-%d")
    prev_start= (today - timedelta(days=period_days * 2 + 1)).strftime("%Y-%m-%d")

    curr_adesao, curr_media, prev_adesao, prev_media = [], [], [], []

    try:
        institutions = api.get_institutions()
        for inst in institutions:
            uid = inst["uid"]
            try:
                for row in api.get_report_results(QUERY_ADESAO,      institution=uid, start_date=curr_start, end_date=curr_end):
                    for d in row.get("data", []):
                        v = d.get("pct_alunos_login")
                        if v is not None: curr_adesao.append(float(v))
                for row in api.get_report_results(QUERY_MEDIA_GERAL,  institution=uid, start_date=curr_start, end_date=curr_end):
                    for d in row.get("data", []):
                        v = d.get("media_percentual_por_aluno")
                        if v is not None: curr_media.append(float(v) * 100)
                for row in api.get_report_results(QUERY_ADESAO,      institution=uid, start_date=prev_start, end_date=prev_end):
                    for d in row.get("data", []):
                        v = d.get("pct_alunos_login")
                        if v is not None: prev_adesao.append(float(v))
                for row in api.get_report_results(QUERY_MEDIA_GERAL,  institution=uid, start_date=prev_start, end_date=prev_end):
                    for d in row.get("data", []):
                        v = d.get("media_percentual_por_aluno")
                        if v is not None: prev_media.append(float(v) * 100)
            except Exception:
                continue
    except Exception:
        return {}

    result = {}
    if curr_adesao and prev_adesao:
        result["adesao_delta"] = (sum(curr_adesao) / len(curr_adesao)) - (sum(prev_adesao) / len(prev_adesao))
    if curr_media and prev_media:
        result["media_delta"] = (sum(curr_media) / len(curr_media)) - (sum(prev_media) / len(prev_media))
    return result

# ── Carregar dados ────────────────────────────────────────────────────────────
with st.spinner("Carregando dados..."):
    df    = load_dashboard(period_days)
    trend = load_trend(period_days)

if df.empty:
    st.error("Nenhum dado encontrado. Verifique as credenciais no .env.")
    st.stop()

# ── Agrega por IES (ordenado por Crítico desc) ────────────────────────────────
ies_df = (
    df.groupby("IES").agg(
        Alunos    =("Alunos",    "sum"),
        Adesao_pct=("Adesão %",  "mean"),
        Media_pct =("Média %",   "mean"),
        Excelente =("Excelente", "sum"),
        Adequado  =("Adequado",  "sum"),
        Alerta    =("Alerta",    "sum"),
        Critico   =("Crítico",   "sum"),
    )
    .reset_index()
    .rename(columns={"Adesao_pct": "Adesão %", "Media_pct": "Média %", "Critico": "Crítico"})
)
ies_df["Adesão %"] = ies_df["Adesão %"].round(1)
ies_df["Média %"]  = ies_df["Média %"].round(1)
ies_df = ies_df.sort_values("Crítico", ascending=False).reset_index(drop=True)

# ── KPI globais ───────────────────────────────────────────────────────────────
total_alunos         = int(df["Alunos"].sum())
avg_adesao           = df["Adesão %"].mean()
avg_media            = df["Média %"].mean()
total_alerta_critico = int(df["Alerta"].sum() + df["Crítico"].sum())

def _kpi_color(val, low, mid):
    if val is None: return "neutral"
    return "green" if val >= mid else ("yellow" if val >= low else "red")

def _trend_html(delta):
    if delta is None: return ""
    arrow = "↑" if delta >= 0 else "↓"
    cls   = "up" if delta >= 0 else "down"
    return f'<div class="kpi-trend {cls}">{arrow} {abs(delta):.1f}pp vs período anterior</div>'

adesao_trend = trend.get("adesao_delta")
media_trend  = trend.get("media_delta")

# ── Layer 1: KPI Cards ────────────────────────────────────────────────────────
st.markdown(f"""
<div class="kpi-row">
  <div class="kpi-card">
    <div class="kpi-value neutral">{total_alunos:,}</div>
    <div class="kpi-label">Alunos Matriculados</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-value {_kpi_color(avg_adesao, 60, 80)}">{avg_adesao:.1f}%</div>
    <div class="kpi-label">Adesão à Plataforma</div>
    {_trend_html(adesao_trend)}
  </div>
  <div class="kpi-card">
    <div class="kpi-value {_kpi_color(avg_media, 60, 75)}">{avg_media:.1f}%</div>
    <div class="kpi-label">Média Geral</div>
    {_trend_html(media_trend)}
  </div>
  <div class="kpi-card alert-card">
    <div class="kpi-value alert">{total_alerta_critico:,}</div>
    <div class="kpi-label">Alunos em Alerta + Crítico</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Helpers de renderização do scorecard ─────────────────────────────────────
def _badge(val, low, mid):
    if val is None: return "—"
    cls = "bg-green" if val >= mid else ("bg-yellow" if val >= low else "bg-red")
    return f'<span class="badge {cls}">{val:.1f}%</span>'

def _alerta_td(n):
    cls = ' class="cell-alerta"' if n > 0 else ""
    return f"<td{cls}>{n}</td>"

def _critico_td(n, total):
    if n == 0: return f"<td>{n}</td>"
    cls = "cell-critico-bold" if (total > 0 and n / total > 0.10) else "cell-critico"
    return f'<td class="{cls}">{n}</td>'

# ── Layer 2: Scorecard por IES ────────────────────────────────────────────────
st.markdown('<div class="section-label">Scorecard por IES</div>', unsafe_allow_html=True)

rows_html = ""
for _, row in ies_df.iterrows():
    rows_html += f"""
    <tr>
      <td class="ies-name">{row["IES"]}</td>
      <td>{row["Alunos"]:,}</td>
      <td>{_badge(row["Adesão %"], 60, 80)}</td>
      <td>{_badge(row["Média %"],  60, 75)}</td>
      <td>{row["Excelente"]}</td>
      <td>{row["Adequado"]}</td>
      {_alerta_td(row["Alerta"])}
      {_critico_td(row["Crítico"], row["Alunos"])}
    </tr>"""

st.markdown(f"""
<div class="sc-wrap">
  <table class="sc-table">
    <thead>
      <tr>
        <th>IES</th><th>Alunos</th><th>Adesão %</th><th>Média %</th>
        <th>Excelente</th><th>Adequado</th><th>⚠ Alerta</th><th>🔴 Crítico</th>
      </tr>
    </thead>
    <tbody>{rows_html}</tbody>
  </table>
</div>
""", unsafe_allow_html=True)

# ── Botão clipboard via JS (componente reutilizável) ─────────────────────────
def _copy_button(text):
    """Renderiza botão que copia `text` para o clipboard via navigator.clipboard."""
    # Escapa caracteres especiais para uso em template literal JS
    safe = text.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
    components.html(f"""
    <style>
      .cpbtn {{
        background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 6px;
        padding: 5px 13px; font-size: 0.78rem; font-weight: 600; color: #475569;
        cursor: pointer; font-family: 'DM Sans', sans-serif; white-space: nowrap;
        transition: background 0.15s;
      }}
      .cpbtn:hover {{ background: #e2e8f0; }}
    </style>
    <button class="cpbtn" onclick="
      var btn = this;
      navigator.clipboard.writeText(`{safe}`).then(function() {{
        btn.textContent = '✅ Copiado!';
        btn.style.background = '#DCFCE7';
        btn.style.color = '#15803d';
        btn.style.borderColor = '#86efac';
        setTimeout(function() {{
          btn.textContent = '📋 Copiar resumo';
          btn.style.background = '';
          btn.style.color = '';
          btn.style.borderColor = '';
        }}, 2500);
      }}).catch(function() {{
        btn.textContent = '⚠ Tente novamente';
      }});
    ">📋 Copiar resumo</button>
    """, height=42)

# ── Layer 3: Detalhamento por Turma (expansível por IES) ─────────────────────
st.markdown('<div class="section-label-mt">Detalhamento por Turma</div>', unsafe_allow_html=True)

for ies_name in ies_df["IES"].tolist():
    turmas = df[df["IES"] == ies_name].sort_values("Crítico", ascending=False)

    with st.expander(f"{ies_name}  —  {len(turmas)} turma(s)"):

        # Tabela de turmas
        turma_rows = ""
        for _, t in turmas.iterrows():
            turma_rows += f"""
            <tr>
              <td>{t["Turma"]}</td>
              <td>{t["Alunos"]:,}</td>
              <td>{_badge(t["Adesão %"], 60, 80)}</td>
              <td>{_badge(t["Média %"],  60, 75)}</td>
              <td>{t["Excelente"]}</td>
              <td>{t["Adequado"]}</td>
              {_alerta_td(t["Alerta"])}
              {_critico_td(t["Crítico"], t["Alunos"])}
            </tr>"""

        st.markdown(f"""
        <div class="turma-wrap">
          <table class="turma-table">
            <thead>
              <tr>
                <th>Turma</th><th>Alunos</th><th>Adesão %</th><th>Média %</th>
                <th>Excelente</th><th>Adequado</th><th>⚠ Alerta</th><th>🔴 Crítico</th>
              </tr>
            </thead>
            <tbody>{turma_rows}</tbody>
          </table>
        </div>
        """, unsafe_allow_html=True)

        # Acionáveis: botão de cópia apenas para turmas com Crítico > 0
        # ou Alerta > 10% do total de alunos
        action_turmas = turmas[
            (turmas["Crítico"] > 0) |
            (turmas.apply(lambda r: r["Alerta"] / r["Alunos"] > 0.10
                          if r["Alunos"] > 0 else False, axis=1))
        ]

        if not action_turmas.empty:
            st.markdown('<div class="action-header">Acionáveis</div>', unsafe_allow_html=True)
            for _, t in action_turmas.iterrows():
                pct_critico = round(t["Crítico"] / t["Alunos"] * 100, 1) if t["Alunos"] > 0 else 0
                pct_alerta  = round(t["Alerta"]  / t["Alunos"] * 100, 1) if t["Alunos"] > 0 else 0
                adesao_str  = f'{t["Adesão %"]}%' if t["Adesão %"] is not None else "N/D"
                media_str   = f'{t["Média %"]}%'  if t["Média %"]  is not None else "N/D"

                resumo = (
                    f"IES: {ies_name}\n"
                    f"Turma: {t['Turma']}\n"
                    f"Período analisado: {period_days} dias\n\n"
                    f"Situação atual:\n"
                    f"- Total de alunos: {t['Alunos']}\n"
                    f"- Adesão à plataforma: {adesao_str}\n"
                    f"- Média geral: {media_str}\n"
                    f"- Alunos Críticos: {t['Crítico']} ({pct_critico}% da turma)\n"
                    f"- Alunos em Alerta: {t['Alerta']} ({pct_alerta}% da turma)\n\n"
                    f"Ação sugerida: acompanhamento prioritário dos alunos em status Crítico e Alerta."
                )

                col_nome, col_btn = st.columns([6, 1])
                with col_nome:
                    st.markdown(f'<div class="action-turma-name">{t["Turma"]}</div>',
                                unsafe_allow_html=True)
                with col_btn:
                    _copy_button(resumo)
