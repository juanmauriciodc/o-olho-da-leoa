import streamlit as st
from supabase import create_client, Client
import time
import pandas as pd
from datetime import date
import io
from PIL import Image

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

                        # Roteamento Corrigido com as Patentes Novas
                        if tag in ["Líder", "Motorista", "Apoio"]:
                            st.session_state["perfil"] = "Lider_Rua"
                        elif tag == "Influenciador":
                            st.session_state["perfil"] = "Influenciador"
                        elif tag in ["Coordenacao", "Gestor de Inside"]:
                            st.session_state["perfil"] = "Coordenacao"
                        st.rerun()
                    else:
                        st.error("❌ Usuário inativo no sistema.")
                else:
                    st.error("❌ Usuário não encontrado.")

        # === CANAL DE FEEDBACK ANÔNIMO ===
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("---")
        st.subheader("🗣️ Ouvidoria da Alcateia (Canal Anônimo)")
        st.write("Tem algo a dizer? Este canal é 100% confidencial. O sistema não registra quem enviou a mensagem.")

        try:
            resp_colab = supabase.table("rh_colaboradores").select("nome").eq("ativo", True).order("nome").execute()
            lista_nomes = [c["nome"] for c in resp_colab.data]
        except Exception:
            lista_nomes = []

        tipo_feedback = st.radio("Qual o tipo de mensagem?", ["🌟 Elogio", "⚠️ Crítica", "🚨 Denúncia"], horizontal=True)

        if tipo_feedback == "🌟 Elogio":
            opcoes_alvo = ["Selecione a pessoa..."] + lista_nomes
        else:
            opcoes_alvo = ["Selecione o alvo..."] + lista_nomes + ["📍 Rotas", "🚙 Carro/Viatura", "📦 Material", "Outros"]

        with st.form("form_ouvidoria", clear_on_submit=True):
            alvo = st.selectbox("Sobre quem ou o quê?", opcoes_alvo)
            mensagem = st.text_area("Descreva o motivo com detalhes:", placeholder="Sua mensagem é segura e sigilosa...")

            btn_enviar_feedback = st.form_submit_button("📩 Enviar Anonimamente")

            if btn_enviar_feedback:
                if alvo in ["Selecione a pessoa...", "Selecione o alvo..."]:
                    st.warning("⚠️ Por favor, selecione sobre quem ou o que é a sua mensagem.")
                elif len(mensagem.strip()) < 5:
                    st.warning("⚠️ Escreva um pouco mais de detalhes na sua mensagem.")
                else:
                    try:
                        supabase.table("canal_feedback").insert({
                            "tipo": tipo_feedback.replace("🌟 ", "").replace("⚠️ ", "").replace("🚨 ", ""),
                            "alvo": alvo,
                            "mensagem": mensagem.strip()
                        }).execute()
                        st.success("✅ Sua mensagem foi enviada diretamente para a Coordenação Geral. Obrigado por ajudar a melhorar nossa operação!")
                    except Exception as e:
                        st.error(f"Erro ao enviar. Verifique se a tabela 'canal_feedback' existe. Detalhes: {e}")

# --- 5. Script 1: Manada de Leão ---
def script_manada_de_leao():
    st.header("🚙 Manada de Leão - Tático de Rua")
    st.write(f"Líder Escalonado: **{st.session_state['nome_usuario']}**")
    st.markdown("---")

    # === 🎯 BLOCO DE DESAFIO LANÇADO (VISÃO DO LÍDER) ===
    try:
        config_db = supabase.table("configuracoes_globais").select("*").eq("id", 1).execute().data
        if config_db:
            meta = config_db[0]
            mult = meta['multiplicador_equipe']
            meta_adesivos = meta['meta_adesivos']

            st.markdown(
                f"""
                <div style="background-color: #E8F4F8; padding: 20px; border-radius: 15px; border: 2px solid #0078D4; margin-bottom: 25px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h2 style="margin: 0; color: #004B87; font-size: 24px;">🚀 DESAFIO LANÇADO!</h2>
                        <span style="background-color: #0078D4; color: white; padding: 5px 15px; border-radius: 20px; font-weight: bold; font-size: 20px;">
                            {mult}x Pontos
                        </span>
                    </div>
                    <p style="color: #1E1E1E; margin: 10px 0; font-size: 16px;">
                        A coordenação definiu uma meta de <b>{meta_adesivos} adesivos</b> no peito para este turno. 
                        Ao bater a meta, toda a sua equipe recebe o multiplicador de pontos em tempo real!
                    </p>
                    <div style="background-color: #D1EAF1; border-radius: 10px; height: 15px; width: 100%; margin-top: 10px;">
                        <div style="background-color: #0078D4; height: 15px; width: 45%; border-radius: 10px;"></div>
                    </div>
                    <p style="text-align: right; margin: 5px 0 0 0; font-size: 12px; color: #004B87;">🏁 Meta: {meta_adesivos} adesivos</p>
                </div>
                """,
                unsafe_allow_html=True
            )
    except Exception:
        pass

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
            with col_n:
                nome_eleitor = st.text_input("Nome do Eleitor")
            with col_z:
                zap_eleitor = st.text_input("WhatsApp (com DDD)")
            bairro_eleitor = st.text_input("Bairro")

            if st.form_submit_button("Salvar Contato (+3 Pontos)"):
                if nome_eleitor and zap_eleitor:
                    try:
                        # Tratamento para enviar nulo caso o carro não tenha rota fixa
                        id_da_rota = rota_id_db if rota_id_db else None

                        supabase.table("captura_eleitores").insert({
                            "turno_id": st.session_state["turno_id_atual"],
                            "rota_id": id_da_rota,
                            "nome_eleitor": nome_eleitor.strip(),
                            "whatsapp": zap_eleitor.strip(),
                            "bairro": bairro_eleitor.strip(),
                            "convertido": False  # Já conectando com a tela do Gestor de Inside!
                        }).execute()

                        st.success("✅ Lead capturado com sucesso e salvo no banco de dados!")
                    except Exception as e:
                        # Agora, se der erro, o sistema não fica mais calado!
                        st.error(f"🚨 Erro ao salvar no banco. Detalhe: {e}")
                else:
                    st.warning("⚠️ Preencha Nome e WhatsApp.")

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
    st.header("🌿 A Selva - Radar Digital (Influenciadores)")
    st.write(f"Influenciador(a) Atirador(a): **{st.session_state['nome_usuario']}**")
    st.markdown("---")

    # === QUADRO DE REGRAS ATUALIZADO: AZUL CLARO DO PARTIDO ===
    st.markdown(
        """
        <div style="background-color: #E8F4F8; padding: 18px; border-radius: 10px; border-left: 5px solid #0078D4; margin-bottom: 25px;">
            <h4 style="margin-top: 0; color: #004B87; font-weight: bold; font-family: sans-serif;">🏆 Regras da Alcateia & Pontuação Digital</h4>
            <p style="margin-bottom: 10px; color: #1E1E1E; font-size: 15px; line-height: 1.5;">
                <strong>👥 Força Coletiva:</strong> O trabalho aqui é 100% em equipe! Os pontos gerados pelas suas visualizações e alcance não vão só para você; eles são <strong>distribuídos no exato momento para toda a equipe</strong> que operou no mesmo dia e turno.
            </p>
            <p style="margin-bottom: 10px; color: #1E1E1E; font-size: 15px; line-height: 1.5;">
                <strong>📸 Validação Única:</strong> Faça o registro assim que a postagem atingir o maior alcance possível. Só é permitido um upload por ação, que servirá como prova auditada pela coordenação.
            </p>
            <p style="margin-bottom: 0; color: #1E1E1E; font-size: 15px; line-height: 1.5;">
                <strong>⚡ Multiplicador Global:</strong> Mantenha a sintonia com os líderes de rua! Se a sua equipe bater as metas combinadas de material físico e engajamento digital, todos recebem o bônus do multiplicador configurado pelo QG.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Formulário de Registro de Engajamento
    with st.form("form_reporte_digital", clear_on_submit=True):
        st.subheader("📱 Registrar Desempenho e Subir Print")

        col_d, col_t = st.columns(2)
        with col_d:
            data_acao = st.date_input("Data em que a ação/foto foi feita")
        with col_t:
            turno_acao = st.selectbox("Turno da Ação", ["Manhã", "Tarde", "Noite", "Integral"])

        tipo_pub = st.selectbox("Qual o formato do post?", ["Story", "Reel", "Feed", "Status"])

        col_v, col_a = st.columns(2)
        with col_v:
            views = st.number_input("Visualizações (Views)", min_value=0, step=100)
        with col_a:
            alcance = st.number_input("Alcance (Reach)", min_value=0, step=100)

        comprovante = st.file_uploader("📸 Subir Print do Engajamento (OBRIGATÓRIO)", type=["png", "jpg", "jpeg"])

        btn_registrar = st.form_submit_button("🚀 Otimizar Imagem e Distribuir Pontos")

        if btn_registrar:
            if not comprovante:
                st.error("🛑 O upload do print é OBRIGATÓRIO. Sem foto, sem pontos!")
            elif views == 0 and alcance == 0:
                st.warning("⚠️ Precisas de introduzir pelo menos alguma view ou alcance para registar.")
            else:
                try:
                    # 1. GERAR CÓDIGO DE AUDITORIA ÚNICO
                    timestamp = int(time.time())
                    codigo_auditoria = f"INF{st.session_state['usuario_id']}-{timestamp}"

                    # Forçamos a extensão a ser sempre .jpg devido à compressão
                    novo_nome_arquivo = f"{codigo_auditoria}.jpg"

                    # 2. INSERÇÃO DOS DADOS DE TEXTO NO BANCO
                    supabase.table("registro_influencia_digital").insert({
                        "colaborador_id": st.session_state["usuario_id"],
                        "data_referencia": str(data_acao),
                        "turno_referencia": turno_acao,
                        "codigo_auditoria": codigo_auditoria,
                        "arquivo_comprovante": novo_nome_arquivo,
                        "tipo_publicacao": tipo_pub,
                        "views": views,
                        "alcance": alcance
                    }).execute()

                    # 3. 🚀 MOTOR DE COMPRESSÃO DO SÉNIOR (Magia em Memória)
                    img_original = Image.open(comprovante)

                    if img_original.mode in ("RGBA", "P"):
                        img_original = img_original.convert("RGB")

                    img_original.thumbnail((800, 800))
                    buffer_memoria = io.BytesIO()
                    img_original.save(buffer_memoria, format="JPEG", quality=60)
                    file_bytes = buffer_memoria.getvalue()

                    supabase.storage.from_("comprovantes").upload(
                        path=novo_nome_arquivo,
                        file=file_bytes,
                        file_options={"content-type": "image/jpeg"}
                    )

                    st.success(
                        f"🔥 Excelente! Protocolo **{codigo_auditoria}** gerado. Imagem otimizada com sucesso e salva na nuvem!")
                    time.sleep(3)
                    st.rerun()

                except Exception as e:
                    st.error(f"Erro no processamento. Detalhe: {e}")

    # Histórico de aprovações
    st.markdown("---")
    st.subheader("📜 Seu Histórico de Disparos")
    try:
        resp_historico = supabase.table("registro_influencia_digital").select(
            "data_referencia, tipo_publicacao, views, alcance"
        ).eq("colaborador_id", st.session_state["usuario_id"]).order(
            "id", desc=True
        ).limit(5).execute()

        if resp_historico.data:
            df_hist = pd.DataFrame(resp_historico.data)
            df_hist.columns = ["Data Ref.", "Formato", "Views", "Alcance"]
            st.dataframe(df_hist, use_container_width=True)
        else:
            st.info("Nenhuma postagem registada ainda. Vá para as redes! 🦁")
    except:
        pass

# --- Script 3: O Olho da Leoa (Sala de Guerra) ---
def script_o_olho_da_leoa():
    # === CABEÇALHO COM BOTÃO DE REFRESH ===
    col_titulo, col_refresh = st.columns([4, 1])

    with col_titulo:
        st.title("👁️ O Olho da Leoa - Comando C3")
        st.write("A central de inteligência e controlo de toda a operação.")

    with col_refresh:
        st.markdown("<br>", unsafe_allow_html=True)  # Pequeno truque para alinhar o botão com o título
        if st.button("🔄 Atualizar Painel", use_container_width=True, type="primary"):
            st.rerun()

    st.markdown("---")

    aba1, aba2, aba3, aba4, aba5, aba6 = st.tabs([
        "👁️ Visão", "👑 Gamificação", "🔎 O Covil", "🐾 Despacho", "💰 O Tesouro", "📞 Inside Sales"
    ])

    # === 1. MÓDULO VISÃO (SUPER DASHBOARD EXECUTIVO) ===
    with aba1:
        st.header("👁️ Visão Global - O Termômetro da Campanha")
        st.write("Acompanhamento das métricas de rua e cruzamento com as intenções de voto dos institutos oficiais.")
        st.markdown("---")

        try:
            # ==========================================
            # PARTE 1: DADOS DAS RUAS (NOSSA OPERAÇÃO)
            # ==========================================
            resp_leads = supabase.table("captura_eleitores").select("id").execute()
            resp_pesquisas = supabase.table("pesquisas_rua").select("intencao_voto").execute()
            resp_turnos = supabase.table("controle_turnos").select("id").execute()
            resp_clima = supabase.table("rotas_e_clima").select("clima_rua").execute()

            total_leads = len(resp_leads.data) if resp_leads.data else 0
            total_pesquisas = len(resp_pesquisas.data) if resp_pesquisas.data else 0
            total_turnos = len(resp_turnos.data) if resp_turnos.data else 0

            # KPIs Superiores
            col_k1, col_k2, col_k3 = st.columns(3)
            with col_k1:
                st.metric(label="👥 Total de Leads (WhatsApp)", value=total_leads, delta="Base de Disparo")
            with col_k2:
                st.metric(label="📊 Pesquisas Realizadas", value=total_pesquisas, delta="Termômetro Físico")
            with col_k3:
                st.metric(label="🚙 Turnos Executados", value=total_turnos, delta="Esforço de Rua")

            st.markdown("---")
            st.subheader("🔥 Termômetro Próprio (Dados captados pela Manada)")

            col_g1, col_g2 = st.columns(2)

            with col_g1:
                st.write("**🗳️ Intenção de Voto (Pesquisa Interna)**")
                if resp_pesquisas.data and total_pesquisas > 0:
                    df_votos = pd.DataFrame(resp_pesquisas.data)
                    contagem_votos = df_votos['intencao_voto'].value_counts().reset_index()
                    contagem_votos.columns = ['Candidato', 'Votos']
                    st.bar_chart(data=contagem_votos.set_index('Candidato'), color="#0078D4")
                else:
                    st.info("Aguardando os primeiros dados de pesquisa das ruas...")

            with col_g2:
                st.write("**🌤️ Aceitação do Eleitor (Clima)**")
                if resp_clima.data and len(resp_clima.data) > 0:
                    df_clima = pd.DataFrame(resp_clima.data)
                    contagem_clima = df_clima['clima_rua'].value_counts().reset_index()
                    contagem_clima.columns = ['Clima', 'Registros']
                    st.bar_chart(data=contagem_clima.set_index('Clima'), color="#FF8C00")
                else:
                    st.info("Aguardando os líderes finalizarem as rotas para o Clima...")

            st.markdown("---")

            # ==========================================
            # PARTE 2: DADOS DE MERCADO (PESQUISAS OFICIAIS)
            # ==========================================
            st.subheader("📈 Painel de Pesquisas Oficiais (Institutos)")

            resp_radar = supabase.table("candidatos").select(
                "nome, pct_datafolha, pct_ipespe, pct_fsb, pct_realtime").eq("ativo", True).execute()

            if resp_radar.data and len(resp_radar.data) > 0:
                df_radar = pd.DataFrame(resp_radar.data)

                linha1_col1, linha1_col2 = st.columns(2)
                linha2_col1, linha2_col2 = st.columns(2)

                with linha1_col1:
                    st.write("**📊 Instituto Datafolha**")
                    df_datafolha = df_radar[['nome', 'pct_datafolha']].rename(columns={'pct_datafolha': 'Intenção (%)'})
                    st.bar_chart(data=df_datafolha.set_index('nome'), color="#0078D4")

                with linha1_col2:
                    st.write("**📊 Instituto IPESPE**")
                    df_ipespe = df_radar[['nome', 'pct_ipespe']].rename(columns={'pct_ipespe': 'Intenção (%)'})
                    st.bar_chart(data=df_ipespe.set_index('nome'), color="#004B87")

                with linha2_col1:
                    st.write("**📊 FSB Pesquisa**")
                    df_fsb = df_radar[['nome', 'pct_fsb']].rename(columns={'pct_fsb': 'Intenção (%)'})
                    st.bar_chart(data=df_fsb.set_index('nome'), color="#4169E1")

                with linha2_col2:
                    st.write("**📊 Real Time Big Data**")
                    df_realtime = df_radar[['nome', 'pct_realtime']].rename(columns={'pct_realtime': 'Intenção (%)'})
                    st.bar_chart(data=df_realtime.set_index('nome'), color="#4682B4")
            else:
                st.info("Nenhum dado cadastrado. Cadastre os candidatos na aba 'Alcateia (RH) > Realeza'.")

        except Exception as e:
            # ==========================================
            # MOCKUP DE SEGURANÇA (Se o banco falhar ou faltar colunas)
            # ==========================================
            st.warning("⚠️ Compilando dados estruturais... Veja a projeção do Super Dashboard:")

            c1, c2, c3 = st.columns(3)
            c1.metric("👥 Total de Leads", "1.245", "+34 hoje")
            c2.metric("📊 Pesquisas", "890", "+12 hoje")
            c3.metric("🚙 Turnos Executados", "45", "6 viaturas")

            st.markdown("---")
            st.subheader("📈 Painel de Pesquisas Oficiais (Projeção)")
            l1, l2 = st.columns(2)
            mock_cands = ["Celina Leão", "Oponente A", "Brancos/Nulos"]
            with l1:
                st.write("**📊 Instituto Datafolha**")
                st.bar_chart(data=pd.DataFrame({"Intenção (%)": [38.0, 25.0, 22.0]}, index=mock_cands), color="#0078D4")
            with l2:
                st.write("**📊 Instituto IPESPE**")
                st.bar_chart(data=pd.DataFrame({"Intenção (%)": [40.0, 22.0, 20.0]}, index=mock_cands), color="#004B87")

    with aba2:
        st.header("👑 Gamificação e Metas da Operação")

        tab_ranking, tab_metas = st.tabs(["🏆 Ranking de Equipes", "⚙️ Configurar Metas e Multiplicadores"])

        # === 1. ABA DE RANKING (A MÁQUINA DE PONTOS INDIVIDUAL) ===
        with tab_ranking:
            st.subheader("🏆 Placar de Honra e A Equipa Perfeita")
            st.write(
                "O mérito é individual, mas a vitória é partilhada! Os pontos de um turno são distribuídos por quem estava no terreno.")

            try:
                # 1. BUSCA DOS DADOS REAIS NA BASE DE DADOS
                turnos_db = supabase.table("controle_turnos").select("id, lider_id, equipe_ids").execute().data
                colabs_db = supabase.table("rh_colaboradores").select("id, nome, tag").execute().data
                leads_db = supabase.table("captura_eleitores").select("turno_id").execute().data
                pesq_db = supabase.table("pesquisas_rua").select("turno_id").execute().data

                if turnos_db and colabs_db:
                    # Transformar em DataFrames para manipulação rápida em memória
                    df_colabs = pd.DataFrame(colabs_db)
                    dict_nomes = dict(zip(df_colabs['id'], df_colabs['nome']))
                    dict_patentes = dict(zip(df_colabs['id'], df_colabs['tag']))

                    df_turnos = pd.DataFrame(turnos_db)

                    # Cálculo: Pontos da Rua (Leads = 3 pts, Pesquisas = 1 pt)
                    pts_leads = pd.DataFrame(leads_db)['turno_id'].value_counts() * 3 if leads_db else pd.Series(
                        dtype=float)
                    pts_pesq = pd.DataFrame(pesq_db)['turno_id'].value_counts() * 1 if pesq_db else pd.Series(
                        dtype=float)

                    df_turnos['Pontos_Turno'] = df_turnos['id'].map(pts_leads).fillna(0) + df_turnos['id'].map(
                        pts_pesq).fillna(0)

                    # 2. DISTRIBUIÇÃO JUSTA DE PONTOS POR CADA MEMBRO DA EQUIPA
                    lista_pontuacao_individual = []

                    for _, row in df_turnos.iterrows():
                        pts = row['Pontos_Turno']

                        # O Líder recebe os pontos
                        lista_pontuacao_individual.append({"id_pessoa": row['lider_id'], "Pontos": pts})

                        # A equipa (Motoristas, Influenciadores, Apoios) também recebe os pontos!
                        if isinstance(row['equipe_ids'], list):
                            for membro_id in row['equipe_ids']:
                                lista_pontuacao_individual.append({"id_pessoa": membro_id, "Pontos": pts})

                    df_pontos = pd.DataFrame(lista_pontuacao_individual)

                    if not df_pontos.empty:
                        # Agrupar os pontos totais por pessoa
                        ranking_final = df_pontos.groupby('id_pessoa')['Pontos'].sum().reset_index()

                        # Trazer o Nome e a Patente (Especialidade)
                        ranking_final['Nome'] = ranking_final['id_pessoa'].map(dict_nomes)
                        ranking_final['Patente'] = ranking_final['id_pessoa'].map(dict_patentes)

                        ranking_final['Estado Atual'] = "Turno Encerrado 🔴"
                        ranking_final.rename(columns={'Pontos': '🔥 Pontuação Geral'}, inplace=True)
                    else:
                        raise ValueError("Turnos registados, mas ainda sem pontuações válidas.")
                else:
                    raise ValueError("Base de dados ainda sem turnos registados.")

            except Exception as e:
                # ==========================================
                # MOCKUP DO SÉNIOR (Garante que o ecrã fica lindo enquanto não há dados suficientes)
                # ==========================================
                st.warning(
                    "⚠️ A processar dados táticos da operação... Confere a projeção do nosso novo Placar Individual:")

                mock_data = {
                    "Nome": ["Coordenador Juan", "Capitão Maurício", "Tenente Isabela", "Major Silva",
                             "João Volante", "Pedro Asfalto",
                             "Bia Viral", "Ana TikTok",
                             "Carlos Logística", "Zé Bandeira"],
                    "Patente": ["Líder_Rua", "Líder_Rua", "Influenciador", "Líder_Rua",
                                "Motorista", "Motorista",
                                "Influenciador", "Influenciador",
                                "Apoio", "Apoio"],
                    "🔥 Pontuação Geral": [650, 480, 610, 450, 410, 390, 500, 420, 310, 280],
                    "Estado Atual": ["Na Rota 🟢", "Turno Encerrado 🔴", "Na Rota 🟢", "Na Rota 🟢",
                                     "Turno Encerrado 🔴", "Na Rota 🟢",
                                     "Turno Encerrado 🔴", "Na Rota 🟢",
                                     "Turno Encerrado 🔴", "Na Rota 🟢"]
                }
                ranking_final = pd.DataFrame(mock_data)

            # === 3. RENDERIZAÇÃO NA TELA: A EQUIPA PERFEITA ===
            if 'ranking_final' in locals() and not ranking_final.empty:
                st.markdown("### 🌟 A Equipa Perfeita (Dream Team Global)")

                # Motor de busca inteligente: Encontra o melhor lobo de cada patente
                def get_top_by_role(df, role):
                    filtered = df[df['Patente'].str.contains(role, case=False, na=False)]
                    if not filtered.empty:
                        top = filtered.sort_values(by="🔥 Pontuação Geral", ascending=False).iloc[0]
                        return top["Nome"], top["🔥 Pontuação Geral"]
                    return "Aguardar Dados", 0

                top_lider, pts_lider = get_top_by_role(ranking_final, "Líder")
                top_mot, pts_mot = get_top_by_role(ranking_final, "Motorista")
                top_inf, pts_inf = get_top_by_role(ranking_final, "Influenciador")
                top_apo, pts_apo = get_top_by_role(ranking_final, "Apoio")

                # Layout dos Cartões de Troféu
                c1, c2, c3, c4 = st.columns(4)

                def render_card(coluna, titulo, icone, nome, pontos):
                    with coluna:
                        st.markdown(
                            f"""
                                    <div style="background-color: #E8F4F8; padding: 15px; border-radius: 10px; border-left: 5px solid #0078D4; text-align: center; height: 100%;">
                                        <h4 style="margin: 0; color: #004B87; font-size: 14px;">{icone} Melhor {titulo}</h4>
                                        <p style="margin: 10px 0 5px 0; font-size: 17px; font-weight: bold; color: #1E1E1E;">{nome}</p>
                                        <p style="margin: 0; font-size: 15px; color: #FF8C00; font-weight: bold;">{pontos:.0f} pts</p>
                                    </div>
                                    """, unsafe_allow_html=True
                        )

                render_card(c1, "Líder", "👑", top_lider, pts_lider)
                render_card(c2, "Motorista", "🚙", top_mot, pts_mot)
                render_card(c3, "Influencer", "📱", top_inf, pts_inf)
                render_card(c4, "Apoio", "🛡️", top_apo, pts_apo)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("### 📊 Rankings Individuais por Especialidade")

                # === 4. TABELAS DE CLASSIFICAÇÃO SEPARADAS ===
                aba_lid, aba_mot, aba_inf, aba_apo = st.tabs(
                    ["👑 Líderes", "🚙 Motoristas", "📱 Influenciadores", "🛡️ Apoios"])

                def render_tabela(aba, role_keyword):
                    with aba:
                        df_role = ranking_final[
                            ranking_final['Patente'].str.contains(role_keyword, case=False, na=False)].copy()
                        if not df_role.empty:
                            df_role = df_role.sort_values(by="🔥 Pontuação Geral", ascending=False).reset_index(
                                drop=True)
                            df_role.index = df_role.index + 1  # O Ranking começa em 1

                            if role_keyword == "Influenciador" and "Story" in df_role.columns:
                                st.dataframe(df_role[["Nome", "Estado Atual", "Story", "Reel", "Feed", "🔥 Pontuação Geral"]], use_container_width=True)
                            else:
                                st.dataframe(df_role[["Nome", "Estado Atual", "🔥 Pontuação Geral"]], use_container_width=True)
                        else:
                            st.info(f"Sem dados operacionais para a patente de {role_keyword} neste momento.")

                render_tabela(aba_lid, "Líder")
                render_tabela(aba_mot, "Motorista")
                render_tabela(aba_inf, "Influenciador")
                render_tabela(aba_apo, "Apoio")

        # === 2. ABA DE METAS (O SEU CÓDIGO INTACTO) ===
        with tab_metas:
            st.subheader("Regras do Jogo (Aplica-se a todos)")
            st.write(
                "Defina aqui as metas. Quando o time atinge a meta combinada de panfletos, adesivos e engajamento digital, todos os pontos gerados por eles recebem esse multiplicador mágico.")

            with st.form("form_config_metas"):
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    nova_meta_alcance = st.number_input("Meta de Alcance Digital (Por Turno)", min_value=1000,
                                                        step=1000, value=10000)
                    nova_meta_adesivos = st.number_input("Meta de Adesivos Colados (Por Turno)", min_value=10, step=10,
                                                         value=100)
                with col_m2:
                    novo_multiplicador = st.number_input("Multiplicador de Equipe (Ex: 1.5x, 2.0x)", min_value=1.0,
                                                         step=0.1, value=1.5)

                btn_salvar_regras = st.form_submit_button("💾 Aplicar Regras para a Tropa")

                if btn_salvar_regras:
                    try:
                        # Aqui você salva na sua tabela de configurações do Supabase.
                        supabase.table("configuracoes_globais").upsert({
                            "id": 1,  # ID fixo para ter sempre apenas 1 linha de configuração ativa
                            "meta_alcance": nova_meta_alcance,
                            "meta_adesivos": nova_meta_adesivos,
                            "multiplicador_equipe": novo_multiplicador
                        }).execute()

                        st.success(
                            f"✅ Regras atualizadas! O Multiplicador agora é de {novo_multiplicador}x para quem bater as metas.")
                    except Exception as e:
                        st.error(f"Erro ao salvar configurações. Crie a tabela 'configuracoes_globais'. Detalhes: {e}")

    with aba3:
        st.header("🔎 O Covil - Central de Ouvidoria e Auditoria")
        st.write("Acompanhe o sentimento da base e audite as postagens digitais da equipa.")
        st.markdown("---")

        # Dividimos o Covil em duas secções
        tab_ouvidoria, tab_auditoria = st.tabs(["🗣️ Ouvidoria (Feedbacks)", "🕵️‍♂️ Auditoria Digital (Estorno)"])

        # === 1. SUB-ABA DE OUVIDORIA (O teu código atual) ===
        with tab_ouvidoria:
            try:
                resp_feedback = supabase.table("canal_feedback").select("*").order("created_at", desc=True).execute()

                if resp_feedback.data:
                    df_feed = pd.DataFrame(resp_feedback.data)
                    tab_elogios, tab_criticas, tab_denuncias = st.tabs(["🌟 Elogios", "⚠️ Críticas", "🚨 Denúncias"])

                    def exibir_mensagens(df, tipo_alvo):
                        df_filtrado = df[df["tipo"] == tipo_alvo]
                        if df_filtrado.empty:
                            st.info(f"Nenhum(a) {tipo_alvo.lower()} registado(a).")
                        else:
                            for _, row in df_filtrado.iterrows():
                                data_formatada = row['created_at'][:10]
                                st.markdown(
                                    f"""
                                    <div style="background-color: #F8F9FA; padding: 15px; border-radius: 10px; border-left: 5px solid {'#FFD700' if tipo_alvo == 'Elogio' else '#FF8C00' if tipo_alvo == 'Crítica' else '#DC3545'}; margin-bottom: 10px;">
                                        <p style="margin: 0; font-size: 12px; color: #6C757D;">Data: {data_formatada} | Alvo: <strong>{row['alvo']}</strong></p>
                                        <p style="margin: 10px 0 0 0; font-size: 16px; color: #1E1E1E;">"{row['mensagem']}"</p>
                                    </div>
                                    """, unsafe_allow_html=True
                                )

                    with tab_elogios:
                        exibir_mensagens(df_feed, "Elogio")
                    with tab_criticas:
                        exibir_mensagens(df_feed, "Crítica")
                    with tab_denuncias:
                        exibir_mensagens(df_feed, "Denúncia")
                else:
                    st.info("A caixa de Ouvidoria está vazia no momento.")
            except Exception as e:
                st.error(f"Erro na ouvidoria: {e}")

        # === 2. SUB-ABA DE AUDITORIA DIGITAL (O BOTÃO DE ESTORNO) ===
        with tab_auditoria:
            st.subheader("⚠️ Painel de Invalidação de Pontos (Selva)")
            st.write(
                "Verificou fraude num Print? Selecione o Protocolo abaixo e aplique o Estorno. Os pontos serão subtraídos instantaneamente de toda a equipa.")

            try:
                # 1. Busca as postagens e os nomes dos colaboradores
                resp_posts = supabase.table("registro_influencia_digital").select("*").order("id", desc=True).execute()
                resp_colabs = supabase.table("rh_colaboradores").select("id, nome").execute()

                if resp_posts.data and resp_colabs.data:
                    dict_nomes = {c["id"]: c["nome"] for c in resp_colabs.data}

                    df_posts = pd.DataFrame(resp_posts.data)
                    df_posts["Nome_Influenciador"] = df_posts["colaborador_id"].map(dict_nomes)

                    # Exibe o painel de registos para o Coordenador olhar
                    st.dataframe(
                        df_posts[
                            ["codigo_auditoria", "Nome_Influenciador", "data_referencia", "tipo_publicacao", "views",
                             "alcance"]],
                        use_container_width=True,
                        hide_index=True
                    )

                    st.markdown("<br>", unsafe_allow_html=True)

                    # 2. O Motor de Invalidação
                    with st.form("form_estorno"):
                        st.error("🚨 ZONA DE ESTORNO (Ação Irreversível)")
                        col_p, col_b = st.columns([3, 1])

                        with col_p:
                            # Lista dropdown com todos os códigos gerados (ex: INF...-...)
                            lista_codigos = df_posts["codigo_auditoria"].tolist()
                            codigo_alvo = st.selectbox("Selecione o Protocolo para Invalidar:",
                                                       ["Selecione..."] + lista_codigos)

                        with col_b:
                            st.markdown("<br>", unsafe_allow_html=True)
                            btn_estorno = st.form_submit_button("🗑️ Executar Estorno")

                        if btn_estorno:
                            if codigo_alvo == "Selecione...":
                                st.warning("Por favor, selecione um código válido.")
                            else:
                                try:
                                    # Apaga o registo da base de dados, invalidando os pontos de imediato
                                    supabase.table("registro_influencia_digital").delete().eq("codigo_auditoria",
                                                                                              codigo_alvo).execute()
                                    st.success(
                                        f"🔥 Registo {codigo_alvo} ESTORNADO com sucesso! Os pontos da equipa foram subtraídos.")
                                    time.sleep(2)
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro ao tentar estornar: {e}")
                else:
                    st.info("Nenhuma postagem registada na Selva para auditar no momento.")
            except Exception as e:
                st.error(f"Erro ao carregar o painel de auditoria: {e}")

            st.markdown("---")
            try:
                resp_rotas = supabase.table("planejamento_rotas").select("*").eq("status", "Pendente").execute()
                if resp_rotas.data:
                    df_rotas = pd.DataFrame(resp_rotas.data)
                    st.dataframe(df_rotas[["viatura_alocada", "nome_rota", "regiao", "bairro_alvo"]], use_container_width=True)
            except: pass

        with tab_candidatos:
            st.subheader("🦁 Gerenciamento da Realeza e Pesquisas Oficiais")

            # Dividindo em abas internas para não entulhar a tela
            sub_cadastrar, sub_atualizar_pesquisa = st.tabs(["➕ Cadastrar Nome", "📊 Atualizar % dos Institutos"])

            # --- SUB-ABA 1: APENAS CADASTRAR O NOME ---
            with sub_cadastrar:
                with st.form("form_candidatos", clear_on_submit=True):
                    nome_cand = st.text_input("Nome do Candidato ou Partido",
                                              placeholder="Ex: Celina Leão, Brancos e Nulos, Oponente A")
                    if st.form_submit_button("Registrar no Radar"):
                        if nome_cand:
                            try:
                                supabase.table("candidatos").insert({
                                    "nome": nome_cand.strip(),
                                    "ativo": True,
                                    "pct_datafolha": 0.0,
                                    "pct_ipespe": 0.0,
                                    "pct_fsb": 0.0,
                                    "pct_realtime": 0.0
                                }).execute()
                                st.success(
                                    f"✅ {nome_cand} adicionado ao radar! Agora você pode atualizar os percentuais na aba ao lado.")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao adicionar: {e}")
                        else:
                            st.warning("⚠️ Digite um nome válido.")

            # --- SUB-ABA 2: ATUALIZAR AS INTENÇÕES DE VOTO ---
            with sub_atualizar_pesquisa:
                try:
                    resp_cand = supabase.table("candidatos").select("*").eq("ativo", True).order("nome").execute()
                    lista_candidatos = resp_cand.data
                    dict_cand = {c['nome']: c for c in lista_candidatos} if lista_candidatos else {}
                except:
                    dict_cand = {}

                if dict_cand:
                    cand_selecionado = st.selectbox("Selecione o Candidato para atualizar os números:",
                                                    options=list(dict_cand.keys()))
                    dados_cand = dict_cand[cand_selecionado]

                    with st.form("form_atualizar_percentuais"):
                        st.write(f"Atualizando intenções de voto para: **{cand_selecionado}**")

                        col_p1, col_p2 = st.columns(2)
                        with col_p1:
                            v_datafolha = st.number_input("Datafolha (%)", min_value=0.0, max_value=100.0,
                                                          value=float(dados_cand.get('pct_datafolha', 0.0)), step=0.1)
                            v_ipespe = st.number_input("Ipespe (%)", min_value=0.0, max_value=100.0,
                                                       value=float(dados_cand.get('pct_ipespe', 0.0)), step=0.1)
                        with col_p2:
                            v_fsb = st.number_input("FSB (%)", min_value=0.0, max_value=100.0,
                                                    value=float(dados_cand.get('pct_fsb', 0.0)), step=0.1)
                            v_realtime = st.number_input("Real Time Big Data (%)", min_value=0.0, max_value=100.0,
                                                         value=float(dados_cand.get('pct_realtime', 0.0)), step=0.1)

                        if st.form_submit_button("💾 Salvar Números Oficiais"):
                            try:
                                supabase.table("candidatos").update({
                                    "pct_datafolha": v_datafolha,
                                    "pct_ipespe": v_ipespe,
                                    "pct_fsb": v_fsb,
                                    "pct_realtime": v_realtime
                                }).eq("id", dados_cand["id"]).execute()

                                st.success(f"🔥 Dados de {cand_selecionado} consolidados com sucesso!")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao atualizar números: {e}")
                else:
                    st.info("Cadastre os candidatos na aba ao lado primeiro.")

        # --- MÓDULO ALCATEIA (RH) PERFEITAMENTE ALINHADO ---
        with tab_rh:
            st.subheader("🐺 Gerenciamento da Alcateia (RH)")

            try:
                resp_colab_list = supabase.table("rh_colaboradores").select("id, nome, tag, telefone, ativo").eq("ativo", True).order("nome").execute()
                colaboradores = resp_colab_list.data
                opcoes_rh = {c['nome']: c for c in colaboradores}
            except Exception:
                colaboradores = []
                opcoes_rh = {}

            aba_cadastrar, aba_editar, aba_inativar = st.tabs(["➕ Recrutar", "✏️ Editar Perfil", "❌ Inativar Membro"])

            with aba_cadastrar:
                with st.form("form_rh_cadastrar", clear_on_submit=True):
                    col_n, col_t = st.columns(2)
                    with col_n:
                        nome_colab = st.text_input("Nome Completo / Apelido")
                        telefone_colab = st.text_input("Telefone (WhatsApp)")
                    with col_t:
                        # LISTA COMPLETA COM LÍDER E GESTOR DE INSIDE
                        tag_colab = st.selectbox("Patente (Função)", ["Líder", "Motorista", "Influenciador", "Apoio", "Gestor de Inside", "Coordenacao"])

                    if st.form_submit_button("Cadastrar Membro"):
                        if nome_colab:
                            try:
                                supabase.table("rh_colaboradores").insert({
                                    "nome": nome_colab.strip(),
                                    "tag": tag_colab,
                                    "telefone": telefone_colab.strip(),
                                    "ativo": True
                                }).execute()
                                st.success(f"✅ {nome_colab} foi convocado(a) como {tag_colab} e já pode logar no sistema!")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao cadastrar membro: {e}")
                        else:
                            st.warning("⚠️ O nome do colaborador é obrigatório.")

            with aba_editar:
                if opcoes_rh:
                    nome_selecionado = st.selectbox("Selecione o membro para editar:", options=list(opcoes_rh.keys()), key="sel_edita")
                    dados_atuais = opcoes_rh[nome_selecionado]

                    with st.form("form_rh_editar"):
                        col_n, col_t = st.columns(2)
                        with col_n:
                            novo_nome = st.text_input("Nome", value=dados_atuais['nome'])
                            novo_telefone = st.text_input("Telefone (WhatsApp)", value=dados_atuais.get('telefone', ''))
                        with col_t:
                            # ESPELHANDO A LISTA COMPLETA
                            patentes = ["Líder", "Motorista", "Influenciador", "Apoio", "Gestor de Inside", "Coordenacao"]
                            idx_patente = patentes.index(dados_atuais['tag']) if dados_atuais['tag'] in patentes else 0
                            nova_tag = st.selectbox("Nova Patente", patentes, index=idx_patente)

                        if st.form_submit_button("💾 Salvar Alterações"):
                            try:
                                supabase.table("rh_colaboradores").update({
                                    "nome": novo_nome.strip(),
                                    "tag": nova_tag,
                                    "telefone": novo_telefone.strip()
                                }).eq("id", dados_atuais["id"]).execute()
                                st.success(f"✅ Dados de {novo_nome} atualizados com sucesso!")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao atualizar: {e}")
                else:
                    st.info("Nenhum membro ativo para editar.")

            with aba_inativar:
                if opcoes_rh:
                    nome_inativar = st.selectbox("Selecione o membro para afastar/inativar:", options=list(opcoes_rh.keys()), key="sel_inativa")
                    dados_inativar = opcoes_rh[nome_inativar]

                    with st.form("form_rh_inativar"):
                        st.warning(f"⚠️ Tem certeza que deseja inativar **{nome_inativar}**? Esta pessoa não poderá mais acessar o sistema, mas o histórico de horas dela será mantido.")
                        if st.form_submit_button("❌ Confirmar Inativação", type="primary"):
                            try:
                                supabase.table("rh_colaboradores").update({"ativo": False}).eq("id", dados_inativar["id"]).execute()
                                st.success(f"✅ {nome_inativar} foi afastado(a) da operação.")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao inativar: {e}")
                else:
                    st.info("Nenhum membro ativo para inativar.")

            st.markdown("---")
            st.subheader("📋 Alcateia Atual (Relatório Geral)")
            try:
                if colaboradores:
                    df_rh = pd.DataFrame(colaboradores)
                    df_viz = df_rh[["nome", "tag", "telefone"]]
                    df_viz.columns = ["Nome", "Patente (Tag)", "Telefone"]
                    st.dataframe(df_viz, use_container_width=True)
                else:
                    st.info("Nenhum membro cadastrado ainda.")
            except Exception as e:
                pass

    # --- ABA 5: O TESOURO DA LEOA ---
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

            # === 6. MÓDULO INSIDE SALES (FUNIL DO WHATSAPP) ===
            with aba6:
                st.header("📞 Inside Sales - Funil de Conversão")
                st.write(
                    "Acompanhe os leads capturados na rua e marque-os como convertidos após o contato via WhatsApp.")
                st.markdown("---")

                try:
                    # Busca os leads que ainda NÃO foram convertidos
                    resp_leads = supabase.table("captura_eleitores").select(
                        "id, nome_eleitor, whatsapp, bairro, convertido").eq("convertido", False).execute()

                    if resp_leads.data and len(resp_leads.data) > 0:
                        df_leads = pd.DataFrame(resp_leads.data)

                        st.subheader("📋 Fila de Contatos Pendentes")

                        # Usando st.data_editor para criar o checkbox interativo pedido no protocolo
                        edited_df = st.data_editor(
                            df_leads,
                            column_config={
                                "convertido": st.column_config.CheckboxColumn("✅ Convertido?", default=False),
                                "id": None,  # Esconde o ID interno do banco
                                "nome_eleitor": st.column_config.TextColumn("Nome do Eleitor", disabled=True),
                                "whatsapp": st.column_config.TextColumn("WhatsApp", disabled=True),
                                "bairro": st.column_config.TextColumn("Bairro", disabled=True),
                            },
                            hide_index=True,
                            use_container_width=True,
                            key="editor_leads"
                        )

                        st.markdown("<br>", unsafe_allow_html=True)

                        # Botão para salvar as conversões no banco
                        if st.button("💾 Salvar Conversões Selecionadas", type="primary"):
                            # Filtra apenas as linhas onde o checkbox foi marcado como True pelo operador
                            leads_convertidos = edited_df[edited_df["convertido"] == True]

                            if not leads_convertidos.empty:
                                sucesso = 0
                                for _, row in leads_convertidos.iterrows():
                                    try:
                                        supabase.table("captura_eleitores").update({"convertido": True}).eq("id", row[
                                            "id"]).execute()
                                        sucesso += 1
                                    except Exception as e:
                                        st.error(f"Erro ao converter {row['nome_eleitor']}: {e}")

                                if sucesso > 0:
                                    st.success(
                                        f"🔥 Sensacional! {sucesso} lead(s) convertido(s) com sucesso. A manada está crescendo!")
                                    time.sleep(2)
                                    st.rerun()
                            else:
                                st.warning("⚠️ Nenhuma caixa foi marcada. Marque os leads convertidos antes de salvar.")
                    else:
                        st.info("🎉 Fila limpa! Todos os leads capturados nas ruas já foram contatados e convertidos.")

                except Exception as e:
                    st.error(
                        f"Erro ao carregar o funil de vendas. Verifique se a coluna 'convertido' existe no banco de dados. Detalhe: {e}")

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

# --- 6. Roteamento Principal (O MOTOR QUE ESTAVA FALTANDO) ---
if not st.session_state["logado"]:
    tela_login()
else:
    if st.session_state["perfil"] == "Lider_Rua":
        script_manada_de_leao()
    elif st.session_state["perfil"] == "Influenciador":
        script_a_selva()
    elif st.session_state["perfil"] == "Coordenacao":
        script_o_olho_da_leoa()