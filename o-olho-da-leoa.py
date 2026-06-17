import streamlit as st
from supabase import create_client, Client
import time
import pandas as pd
from datetime import date

# --- 1. Configuração Inicial da Página ---
st.set_page_config(page_title="O Olho da Leoa", page_icon="🦁", layout="wide")

# --- 2. Conexão com o Banco de Dados (Supabase) ---
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# --- 3. Inicialização do Estado da Sessão ---
if "logado" not in st.session_state: st.session_state["logado"] = False
if "perfil" not in st.session_state: st.session_state["perfil"] = None
if "nome_usuario" not in st.session_state: st.session_state["nome_usuario"] = None
if "usuario_id" not in st.session_state: st.session_state["usuario_id"] = None

# --- 4. Módulo de Login ---
def tela_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🦁 O Olho da Leoa")
        st.subheader("Acesso Restrito")
        st.markdown("---")

        with st.form("form_login"):
            usuario = st.text_input("Nome do Usuário")
            botao_entrar = st.form_submit_button("Entrar")

            if botao_entrar and usuario:
                busca = supabase.table("rh_colaboradores").select("*").ilike("nome", usuario.strip()).execute()
                if len(busca.data) > 0:
                    usuario_db = busca.data[0]
                    if usuario_db["ativo"]:
                        st.session_state["logado"] = True
                        st.session_state["nome_usuario"] = usuario_db["nome"]
                        st.session_state["usuario_id"] = usuario_db["id"]
                        tag = usuario_db["tag"]

                        if tag in ["Motorista", "Apoio"]: st.session_state["perfil"] = "Lider_Rua"
                        elif tag == "Influenciador": st.session_state["perfil"] = "Influenciador"
                        elif tag == "Coordenacao": st.session_state["perfil"] = "Coordenacao"
                        st.rerun()
                    else: st.error("❌ Usuário inativo no sistema.")
                else: st.error("❌ Usuário não encontrado.")

# --- 5. Script 1: Manada de Leão ---
def script_manada_de_leao():
    st.header("🚙 Manada de Leão - Tático de Rua")
    st.write(f"Líder Escalonado: **{st.session_state['nome_usuario']}**")
    st.markdown("---")

    if "turno_ativo" not in st.session_state: st.session_state["turno_ativo"] = False
    if "turno_id_atual" not in st.session_state: st.session_state["turno_id_atual"] = None
    if "viatura_atual" not in st.session_state: st.session_state["viatura_atual"] = None

    if not st.session_state["turno_ativo"]:
        st.subheader("📋 Abertura de Turno e Bate-Ponto")
        try:
            resp_colab = supabase.table("rh_colaboradores").select("id, nome, tag").eq("ativo", True).execute()
            lista_colaboradores = [c for c in resp_colab.data if c["id"] != st.session_state["usuario_id"]]
            motoristas = {c['nome']: c['id'] for c in lista_colaboradores if c['tag'] == 'Motorista'}
            influenciadores = {c['nome']: c['id'] for c in lista_colaboradores if c['tag'] == 'Influenciador'}
            apoios = {c['nome']: c['id'] for c in lista_colaboradores if c['tag'] == 'Apoio'}
        except Exception:
            motoristas, influenciadores, apoios = {}, {}, {}

        with st.form("form_abertura_turno"):
            col_v, col_t = st.columns(2)
            with col_v:
                viatura_selecionada = st.selectbox("Qual Viatura você está assumindo?", [f"Viatura {str(i).zfill(2)}" for i in range(1, 11)])
                placa = st.text_input("Placa do Veículo (Opcional)", placeholder="ABC-1234")
            with col_t:
                turno_trabalho = st.selectbox("Turno deste expediente", ["Manhã", "Tarde", "Noite", "Integral"])

            st.markdown("👥 **Montagem da Equipe (O Ponto será batido para todos)**")
            col_mot, col_inf, col_apo = st.columns(3)
            with col_mot: sel_mot = st.multiselect("Motorista(s)", options=list(motoristas.keys()))
            with col_inf: sel_inf = st.multiselect("Influenciador(es)", options=list(influenciadores.keys()))
            with col_apo: sel_apo = st.multiselect("Apoio(s)", options=list(apoios.keys()))

            st.markdown("📦 **Trava Logística: Material Embarcado**")
            col1, col2, col3 = st.columns(3)
            with col1: panfletos = st.number_input("Panfletos", min_value=0, step=50)
            with col2: adesivos = st.number_input("Adesivos", min_value=0, step=10)
            with col3: bandeiras = st.number_input("Bandeiras", min_value=0, step=1)

            btn_iniciar = st.form_submit_button("🚀 Iniciar Missão e Bater Ponto")

            if btn_iniciar:
                equipe_total = sel_mot + sel_inf + sel_apo
                if len(equipe_total) == 0: st.error("❌ O carro não pode sair vazio!")
                elif panfletos == 0 and adesivos == 0 and bandeiras == 0: st.error("🛑 Registre o material embarcado!")
                else:
                    try:
                        equipe_ids = [motoristas[n] for n in sel_mot] + [influenciadores[n] for n in sel_inf] + [apoios[n] for n in sel_apo]

                        res_turno = supabase.table("controle_turnos").insert({
                            "lider_id": st.session_state["usuario_id"], "placa_veiculo": placa, "equipe_ids": equipe_ids
                        }).execute()
                        novo_turno_id = res_turno.data[0]["id"]

                        lista_ponto = [{"colaborador_id": st.session_state["usuario_id"], "data_trabalho": str(date.today()), "turno_trabalho": turno_trabalho, "setor": "Rua"}]
                        for colab_id in equipe_ids:
                            lista_ponto.append({"colaborador_id": colab_id, "data_trabalho": str(date.today()), "turno_trabalho": turno_trabalho, "setor": "Rua"})
                        supabase.table("controle_ponto").insert(lista_ponto).execute()

                        materiais = [
                            {"turno_id": novo_turno_id, "material_nome": "Panfletos", "qtd_embarcada": panfletos, "qtd_sobra": 0},
                            {"turno_id": novo_turno_id, "material_nome": "Adesivos", "qtd_embarcada": adesivos, "qtd_sobra": 0},
                            {"turno_id": novo_turno_id, "material_nome": "Bandeiras", "qtd_embarcada": bandeiras, "qtd_sobra": 0}
                        ]
                        materiais = [m for m in materiais if m["qtd_embarcada"] > 0]
                        if materiais: supabase.table("estoque_materiais").insert(materiais).execute()

                        st.session_state["turno_id_atual"] = novo_turno_id
                        st.session_state["viatura_atual"] = viatura_selecionada
                        st.session_state["turno_ativo"] = True
                        st.rerun()
                    except Exception as e: st.error(f"🚨 Erro: {str(e)}")

    else:
        st.success(f"🟢 {st.session_state['viatura_atual']} na rua! Turno #{st.session_state['turno_id_atual']}")

        try:
            resp_rotas = supabase.table("planejamento_rotas").select("*").eq("status", "Pendente").eq("viatura_alocada", st.session_state["viatura_atual"]).order("id").limit(1).execute()
            rota_atual = resp_rotas.data[0] if len(resp_rotas.data) > 0 else None
            rota_id_db = rota_atual["id"] if rota_atual else None
        except Exception:
            rota_atual, rota_id_db = None, None

        st.markdown("---")
        if rota_atual:
            st.title(f"📍 Rota Alocada: {rota_atual['nome_rota']}")
            st.subheader(f"🎯 Alvo: {rota_atual['bairro_alvo']} ({rota_atual.get('regiao', '')})")
            if rota_atual.get("descricao"): st.info(f"Missão: {rota_atual['descricao']}")
        else:
            st.title("📍 Rota Livre (Atuação por Oportunidade)")
            st.info(f"Não há missões pendentes na gaveta da {st.session_state['viatura_atual']}.")
        st.markdown("---")

        st.subheader("📱 1. Captação de Eleitores")
        with st.form("form_captura", clear_on_submit=True):
            col_n, col_z = st.columns(2)
            with col_n: nome_eleitor = st.text_input("Nome do Eleitor")
            with col_z: zap_eleitor = st.text_input("WhatsApp (com DDD)")
            bairro_eleitor = st.text_input("Bairro")

            if st.form_submit_button("Salvar Contato (+3 Pontos)"):
                if nome_eleitor and zap_eleitor:
                    try:
                        supabase.table("captura_eleitores").insert({
                            "turno_id": st.session_state["turno_id_atual"], "rota_id": rota_id_db,
                            "nome_eleitor": nome_eleitor.strip(), "whatsapp": zap_eleitor.strip(), "bairro": bairro_eleitor.strip()
                        }).execute()
                        st.toast("✅ Lead capturado!")
                    except Exception: st.error("Erro ao salvar.")
                else: st.warning("⚠️ Preencha Nome e WhatsApp.")

        st.markdown("---")
        st.subheader("📊 2. Senso da Rua (Pesquisa Rápida)")
        try:
            resp_cand = supabase.table("candidatos").select("nome").eq("ativo", True).execute()
            nomes_candidatos = [c["nome"] for c in resp_cand.data]
        except Exception: nomes_candidatos = []

        with st.form("form_pesquisa", clear_on_submit=True):
            nome_eleitor_pesq = st.text_input("Nome do Eleitor (Obrigatório)")
            candidato_escolhido = st.selectbox("Intenção de Voto:", ["Selecione..."] + nomes_candidatos + ["Outros Oponentes", "Branco / Nulo", "Indeciso / Não sabe"])

            if st.form_submit_button("Registrar Voto (+1 Ponto)"):
                if not nome_eleitor_pesq.strip(): st.error("🛑 Nome obrigatório!")
                elif candidato_escolhido == "Selecione...": st.warning("⚠️ Selecione a intenção.")
                else:
                    try:
                        supabase.table("pesquisas_rua").insert({
                            "turno_id": st.session_state["turno_id_atual"], "rota_id": rota_id_db,
                            "nome_eleitor": nome_eleitor_pesq.strip(), "intencao_voto": candidato_escolhido
                        }).execute()
                        st.toast("✅ Voto computado!")
                    except Exception: st.error("Erro ao salvar pesquisa.")

        st.markdown("---")
        st.subheader("🏁 3. Check-out da Rota Atual")
        with st.form("form_checkout"):
            clima = st.radio("Clima da rua:", ["🤩 Ótimo", "🙂 Bom", "😐 Regular", "🛑 Baixo"], horizontal=True)
            justificativa = st.text_input("⚠️ Motivo da baixa aceitação") if clima == "🛑 Baixo" else ""

            if st.form_submit_button("✅ Finalizar Rota e Puxar Próxima"):
                if clima == "🛑 Baixo" and not justificativa: st.error("🛑 Justifique o motivo.")
                else:
                    try:
                        supabase.table("rotas_e_clima").insert({
                            "turno_id": st.session_state["turno_id_atual"], "rota_id": rota_id_db,
                            "clima_rua": clima, "justificativa_abandono": justificativa
                        }).execute()
                        if rota_atual: supabase.table("planejamento_rotas").update({"status": "Concluída"}).eq("id", rota_atual["id"]).execute()
                        st.success("Rota finalizada!")
                        st.rerun()
                    except Exception as e: st.error(f"Erro: {e}")

        st.markdown("---")
        if st.button("🛑 Fim de Expediente (Encerrar Turno)", use_container_width=True, type="primary"):
            st.session_state["turno_ativo"] = False
            st.session_state["turno_id_atual"] = None
            st.session_state["viatura_atual"] = None
            st.rerun()

# --- Script 2: A Selva ---
def script_a_selva():
    st.header("🌿 A Selva - Radar de Influência")
    st.write("Módulo em construção...")

# --- Script 3: O Olho da Leoa (Sala de Guerra) ---
def script_o_olho_da_leoa():
    st.title("👁️ O Olho da Leoa - Comando C3")
    st.write("A central de inteligência e controle de toda a operação.")
    st.markdown("---")

    aba1, aba2, aba3, aba4, aba5 = st.tabs([
        "👁️ Visão", "👑 Gamificação", "🔎 O Covil", "🐾 Despacho", "💰 O Tesouro (Controle de Turnos e AC)"
    ])

    with aba1: st.info("Gráficos Visuais")
    with aba2: st.info("Ranking de Pontos")
    with aba3: st.info("Auditoria")

    with aba4:
        st.header("🐾 Controle da Manada (Despacho)")
        tab_rotas, tab_candidatos = st.tabs(["📍 Territórios de Caça", "🦁 Realeza"])

        with tab_rotas:
            st.subheader("Mapear Novo Território (Alocar Rota para Viatura)")
            with st.form("form_rotas", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    nome_rota = st.text_input("Nome da Operação")
                    regiao = st.selectbox("Macrorregião", ["Plano Piloto", "Asa Norte", "Asa Sul", "Taguatinga", "Ceilândia", "Gama", "Águas Claras", "Outras"])
                with col2:
                    bairro_alvo = st.text_input("Bairro / Ponto")
                    viatura_alocada = st.selectbox("Qual carro fará esta rota?", [f"Viatura {str(i).zfill(2)}" for i in range(1, 11)])

                descricao = st.text_area("Instruções da Missão")
                if st.form_submit_button("Despachar Rota"):
                    try:
                        supabase.table("planejamento_rotas").insert({
                            "nome_rota": nome_rota, "regiao": regiao, "bairro_alvo": bairro_alvo,
                            "descricao": descricao, "viatura_alocada": viatura_alocada, "status": "Pendente"
                        }).execute()
                        st.success(f"✅ Rota colocada na gaveta da {viatura_alocada}!")
                    except Exception as e: st.error(f"Erro: {e}")

            st.markdown("---")
            try:
                resp_rotas = supabase.table("planejamento_rotas").select("*").eq("status", "Pendente").execute()
                if resp_rotas.data:
                    df_rotas = pd.DataFrame(resp_rotas.data)
                    st.dataframe(df_rotas[["viatura_alocada", "nome_rota", "regiao", "bairro_alvo"]], use_container_width=True)
            except: pass

        with tab_candidatos: st.info("Cadastro de candidatos")

    # --- ABA DE RELATÓRIOS E RH (TERMOS BLINDADOS) ---
    with aba5:
        st.header("💰 O Tesouro da Leoa (Controle de Ponto e AC)")
        tab_qg, tab_relatorio = st.tabs(["🏢 Bater Ponto Manual (Equipe QG)", "📊 Extrato de Fechamento (AC)"])

        with tab_qg:
            st.subheader("Registrar Presença - Base Interna")
            try:
                resp_colab = supabase.table("rh_colaboradores").select("id, nome").eq("ativo", True).execute()
                opcoes_rh = {c['nome']: c['id'] for c in resp_colab.data}
            except: opcoes_rh = {}

            with st.form("form_ponto_qg"):
                col_c, col_d, col_t = st.columns(3)
                with col_c: pessoa = st.selectbox("Colaborador", options=list(opcoes_rh.keys()))
                with col_d: data_ponto = st.date_input("Data do Expediente")
                with col_t: turno_ponto = st.selectbox("Turno Trabalhado", ["Manhã", "Tarde", "Noite", "Integral"])

                if st.form_submit_button("Registrar Ponto QG"):
                    try:
                        supabase.table("controle_ponto").insert({
                            "colaborador_id": opcoes_rh[pessoa],
                            "data_trabalho": str(data_ponto),
                            "turno_trabalho": turno_ponto,
                            "setor": "QG"
                        }).execute()
                        st.success(f"✅ Ponto de {pessoa} registrado com sucesso!")
                    except Exception as e: st.error(f"Erro: {e}")

        with tab_relatorio:
            st.subheader("Relatório Sintético de Turnos (Base para Liberação de AC)")
            st.write("Este painel resume quantos dias e quantos turnos cada pessoa trabalhou, fornecendo a métrica exata para a consolidação das Ajudas de Custo.")
            if st.button("🔄 Gerar Extrato de AC"):
                try:
                    resp_ponto = supabase.table("controle_ponto").select("*").execute()
                    resp_rh = supabase.table("rh_colaboradores").select("id, nome, tag").execute()

                    if resp_ponto.data and resp_rh.data:
                        df_ponto = pd.DataFrame(resp_ponto.data)
                        df_rh = pd.DataFrame(resp_rh.data)

                        df_merged = df_ponto.merge(df_rh, left_on='colaborador_id', right_on='id')

                        resumo = df_merged.groupby(['nome', 'tag']).agg(
                            Dias_Trabalhados=('data_trabalho', 'nunique'),
                            Total_de_Turnos=('turno_trabalho', 'count')
                        ).reset_index()

                        st.dataframe(resumo.sort_values(by="Total_de_Turnos", ascending=False), use_container_width=True)
                    else:
                        st.warning("Ainda não há registros de ponto no sistema.")
                except Exception as e:
                    st.error(f"Erro ao compilar o extrato: {e}")

# --- 6. Roteamento Principal ---
if not st.session_state["logado"]: tela_login()
else:
    if st.session_state["perfil"] == "Lider_Rua": script_manada_de_leao()
    elif st.session_state["perfil"] == "Influenciador": script_a_selva()
    elif st.session_state["perfil"] == "Coordenacao": script_o_olho_da_leoa()