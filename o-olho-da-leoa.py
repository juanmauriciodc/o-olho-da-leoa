import streamlit as st
from supabase import create_client, Client

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
if "logado" not in st.session_state:
    st.session_state["logado"] = False
if "perfil" not in st.session_state:
    st.session_state["perfil"] = None
if "nome_usuario" not in st.session_state:
    st.session_state["nome_usuario"] = None
if "usuario_id" not in st.session_state:
    st.session_state["usuario_id"] = None

# --- 4. Módulo de Login (A Catraca Real) ---
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
                usuario_limpo = usuario.strip()
                busca = supabase.table("rh_colaboradores").select("*").ilike("nome", usuario_limpo).execute()

                if len(busca.data) > 0:
                    usuario_db = busca.data[0]
                    if usuario_db["ativo"]:
                        st.session_state["logado"] = True
                        st.session_state["nome_usuario"] = usuario_db["nome"]
                        st.session_state["usuario_id"] = usuario_db["id"]

                        tag = usuario_db["tag"]

                        if tag in ["Motorista", "Apoio"]:
                            st.session_state["perfil"] = "Lider_Rua"
                        elif tag == "Influenciador":
                            st.session_state["perfil"] = "Influenciador"
                        elif tag == "Coordenacao":
                            st.session_state["perfil"] = "Coordenacao"

                        st.rerun()
                    else:
                        st.error("❌ Usuário inativo no sistema.")
                else:
                    st.error(f"❌ Não achei '{usuario_limpo}'.")

# --- 5. Script 1: Manada de Leão ---
def script_manada_de_leao():
    st.header("🚙 Manada de Leão - Tático de Rua")
    st.write(f"Líder Escalonado: **{st.session_state['nome_usuario']}**")
    st.markdown("---")

    if "turno_ativo" not in st.session_state:
        st.session_state["turno_ativo"] = False
    if "turno_id_atual" not in st.session_state:
        st.session_state["turno_id_atual"] = None

    # ==========================================
    # TELA DE ABERTURA DE TURNO (Logística)
    # ==========================================
    if not st.session_state["turno_ativo"]:
        st.subheader("📋 Abertura de Turno e Check-in")

        try:
            resp_colab = supabase.table("rh_colaboradores").select("id, nome, tag").eq("ativo", True).execute()
            lista_colaboradores = [c for c in resp_colab.data if c["id"] != st.session_state["usuario_id"]]

            motoristas = {c['nome']: c['id'] for c in lista_colaboradores if c['tag'] == 'Motorista'}
            influenciadores = {c['nome']: c['id'] for c in lista_colaboradores if c['tag'] == 'Influenciador'}
            apoios = {c['nome']: c['id'] for c in lista_colaboradores if c['tag'] == 'Apoio'}
        except Exception as e:
            st.error(f"Erro de conexão com o RH: {e}")
            motoristas, influenciadores, apoios = {}, {}, {}

        with st.form("form_abertura_turno"):
            placa = st.text_input("Placa do Veículo (ex: ABC-1234)")

            st.markdown("👥 **Montagem da Equipe (Filtrada por Função)**")
            col_mot, col_inf, col_apo = st.columns(3)
            with col_mot:
                sel_mot = st.multiselect("Motorista(s)", options=list(motoristas.keys()))
            with col_inf:
                sel_inf = st.multiselect("Influenciador(es)", options=list(influenciadores.keys()))
            with col_apo:
                sel_apo = st.multiselect("Apoio(s)", options=list(apoios.keys()))

            st.markdown("---")
            st.markdown("📦 **Trava Logística: Material Embarcado**")
            col1, col2, col3 = st.columns(3)
            with col1:
                panfletos = st.number_input("Panfletos (Unidades)", min_value=0, step=50)
            with col2:
                adesivos = st.number_input("Adesivos (Unidades)", min_value=0, step=10)
            with col3:
                bandeiras = st.number_input("Bandeiras (Unidades)", min_value=0, step=1)

            btn_iniciar = st.form_submit_button("🚀 Iniciar Missão")

            if btn_iniciar:
                equipe_total = sel_mot + sel_inf + sel_apo

                if not placa:
                    st.error("❌ A Placa do veículo é obrigatória!")
                elif len(equipe_total) == 0:
                    st.error("❌ O carro não pode sair vazio. Selecione a equipe!")
                elif panfletos == 0 and adesivos == 0 and bandeiras == 0:
                    st.error("🛑 Trava Logística: Registre ao menos um tipo de material embarcado!")
                else:
                    try:
                        equipe_ids = [motoristas[n] for n in sel_mot] + \
                                     [influenciadores[n] for n in sel_inf] + \
                                     [apoios[n] for n in sel_apo]

                        dados_turno = {
                            "lider_id": st.session_state["usuario_id"],
                            "placa_veiculo": placa.upper(),
                            "equipe_ids": equipe_ids
                        }
                        res_turno = supabase.table("controle_turnos").insert(dados_turno).execute()
                        novo_turno_id = res_turno.data[0]["id"]

                        materiais_para_inserir = [
                            {"turno_id": novo_turno_id, "material_nome": "Panfletos", "qtd_embarcada": panfletos,
                             "qtd_sobra": 0},
                            {"turno_id": novo_turno_id, "material_nome": "Adesivos", "qtd_embarcada": adesivos,
                             "qtd_sobra": 0},
                            {"turno_id": novo_turno_id, "material_nome": "Bandeiras", "qtd_embarcada": bandeiras,
                             "qtd_sobra": 0}
                        ]
                        materiais_para_inserir = [m for m in materiais_para_inserir if m["qtd_embarcada"] > 0]

                        if materiais_para_inserir:
                            supabase.table("estoque_materiais").insert(materiais_para_inserir).execute()

                        st.session_state["turno_id_atual"] = novo_turno_id
                        st.session_state["turno_ativo"] = True
                        st.rerun()
                    except Exception as e:
                        st.error(f"🚨 Erro no banco de dados: {str(e)}")

    # ==========================================
    # TELA DA RUA (Operação Tática)
    # ==========================================
    else:
        st.success(f"🟢 Turno #{st.session_state['turno_id_atual']} Em Andamento. Viatura na rua!")

        # --- NOVO: O LETREIRO DE ROTA INTELIGENTE ---
        try:
            # Puxa do banco a primeira rota com status 'Pendente'
            resp_rotas = supabase.table("planejamento_rotas").select("*").eq("status", "Pendente").order("id").limit(
                1).execute()
            rota_atual = resp_rotas.data[0] if len(resp_rotas.data) > 0 else None
        except Exception:
            rota_atual = None

        st.markdown("---")
        if rota_atual:
            st.title(f"📍 Rota Ativa: {rota_atual['nome_rota']}")
            st.subheader(f"🎯 Bairro Alvo: {rota_atual['bairro_alvo']}")
            if rota_atual.get('descricao'):
                st.info(f"**Missão/Instrução:** {rota_atual['descricao']}")
        else:
            # Se não tiver rota enviada pelo Script 3, o líder não fica travado
            st.title("📍 Rota Livre (Atuação por Oportunidade)")
            st.subheader("🎯 Bairro: Atuação Dinâmica")
            st.info("A fila de missões despachadas pela coordenação está vazia.")
        st.markdown("---")

        # --- MÓDULO 1: CAPTAÇÃO DE LEADS ---
        st.subheader("📱 1. Captação de Eleitores")
        with st.form("form_captura", clear_on_submit=True):
            col_nome, col_zap = st.columns(2)
            with col_nome:
                nome_eleitor = st.text_input("Nome do Eleitor")
            with col_zap:
                zap_eleitor = st.text_input("WhatsApp (com DDD)")
            bairro_eleitor = st.text_input("Bairro")

            if st.form_submit_button("Salvar Contato (+3 Pontos)"):
                if nome_eleitor and zap_eleitor:
                    try:
                        supabase.table("captura_eleitores").insert({
                            "turno_id": st.session_state["turno_id_atual"],
                            "nome_eleitor": nome_eleitor.strip(),
                            "whatsapp": zap_eleitor.strip(),
                            "bairro": bairro_eleitor.strip()
                        }).execute()
                        st.toast("✅ Lead capturado e salvo na base!")
                    except Exception as e:
                        st.error("Erro ao salvar contato.")
                else:
                    st.warning("⚠️ Preencha Nome e WhatsApp para pontuar.")

        st.markdown("---")

        # --- MÓDULO 2: SENSO DA RUA ---
        st.subheader("📊 2. Senso da Rua (Pesquisa Rápida)")
        try:
            resp_cand = supabase.table("candidatos").select("nome").eq("ativo", True).execute()
            nomes_candidatos = [c["nome"] for c in resp_cand.data]
        except Exception:
            nomes_candidatos = []

        opcoes_voto = ["Selecione..."] + nomes_candidatos + ["Outros Oponentes", "Branco / Nulo", "Indeciso / Não sabe"]

        with st.form("form_pesquisa", clear_on_submit=True):
            nome_eleitor_pesq = st.text_input("Nome do Eleitor (Obrigatório para validar a pesquisa)")
            candidato_escolhido = st.selectbox("Intenção de Voto (Espontânea/Estimulada):", opcoes_voto)

            if st.form_submit_button("Registrar Voto (+1 Ponto)"):
                if not nome_eleitor_pesq.strip():
                    st.error("🛑 Trava de Segurança: É obrigatório informar o nome do eleitor!")
                elif candidato_escolhido == "Selecione...":
                    st.warning("⚠️ Selecione uma intenção de voto válida.")
                else:
                    try:
                        supabase.table("pesquisas_rua").insert({
                            "turno_id": st.session_state["turno_id_atual"],
                            "nome_eleitor": nome_eleitor_pesq.strip(),
                            "intencao_voto": candidato_escolhido
                        }).execute()
                        st.toast("✅ Voto validado e computado no radar!")
                    except Exception as e:
                        st.error(f"Erro ao salvar pesquisa: {e}")

        st.markdown("---")

        # --- MÓDULO 3: CHECK-OUT DA ROTA ---
        st.subheader("🏁 3. Check-out da Rota Atual")
        with st.form("form_checkout"):
            clima = st.radio("Nível de aceitação da rua nesta rota:",
                             ["🤩 Ótimo", "🙂 Bom", "😐 Regular", "🛑 Baixo"], horizontal=True)
            justificativa = ""
            if clima == "🛑 Baixo":
                justificativa = st.text_input("⚠️ Motivo da baixa aceitação (Obrigatório)")

            btn_encerrar_rota = st.form_submit_button("✅ Finalizar Rota e Puxar Próxima")

            if btn_encerrar_rota:
                if clima == "🛑 Baixo" and not justificativa.strip():
                    st.error("🛑 Justifique o motivo de classificar o clima como 'Baixo'.")
                else:
                    try:
                        rota_id_db = rota_atual["id"] if rota_atual else None

                        # 1. Salva o clima enviando também o ID da rota
                        supabase.table("rotas_e_clima").insert({
                            "turno_id": st.session_state["turno_id_atual"],
                            "rota_id": rota_id_db,
                            "clima_rua": clima,
                            "justificativa_abandono": justificativa
                        }).execute()

                        # 2. Muda o status da rota no banco para que a próxima apareça
                        if rota_atual:
                            supabase.table("planejamento_rotas").update({"status": "Concluída"}).eq("id", rota_atual[
                                "id"]).execute()

                        st.success("Rota finalizada com sucesso! O letreiro vai atualizar.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao encerrar a rota: {e}")

        # --- MÓDULO 4: FIM DO DIA (Apenas para fechar o Turno) ---
        st.markdown("---")
        st.subheader("🛑 Fim de Expediente")
        st.info("Atenção: Aperte este botão apenas quando a viatura estiver voltando para a base.")
        if st.button("Encerrar Turno Definitivamente", use_container_width=True, type="primary"):
            st.session_state["turno_ativo"] = False
            st.session_state["turno_id_atual"] = None
            st.rerun()

    # ==========================================
    # TELA DA RUA (Operação Tática)
    # ==========================================
    else:
        st.success(f"🟢 Turno #{st.session_state['turno_id_atual']} Em Andamento. Viatura na rua!")
        st.markdown("---")

        # --- MÓDULO 1: CAPTAÇÃO DE LEADS ---
        st.subheader("📱 1. Captação de Eleitores")
        with st.form("form_captura", clear_on_submit=True):
            col_nome, col_zap = st.columns(2)
            with col_nome:
                nome_eleitor = st.text_input("Nome do Eleitor")
            with col_zap:
                zap_eleitor = st.text_input("WhatsApp (com DDD)")
            bairro_eleitor = st.text_input("Bairro")

            if st.form_submit_button("Salvar Contato (+3 Pontos)"):
                if nome_eleitor and zap_eleitor:
                    try:
                        supabase.table("captura_eleitores").insert({
                            "turno_id": st.session_state["turno_id_atual"],
                            "nome_eleitor": nome_eleitor.strip(),
                            "whatsapp": zap_eleitor.strip(),
                            "bairro": bairro_eleitor.strip()
                        }).execute()
                        st.toast("✅ Lead capturado e salvo na base!")
                    except Exception as e:
                        st.error("Erro ao salvar contato.")
                else:
                    st.warning("⚠️ Preencha Nome e WhatsApp para pontuar.")

        st.markdown("---")

        # --- MÓDULO 2: SENSO DA RUA ---
        st.subheader("📊 2. Senso da Rua (Pesquisa Rápida)")

        try:
            resp_cand = supabase.table("candidatos").select("nome").eq("ativo", True).execute()
            nomes_candidatos = [c["nome"] for c in resp_cand.data]
        except Exception:
            nomes_candidatos = []

        opcoes_voto = ["Selecione..."] + nomes_candidatos + ["Outros Oponentes", "Branco / Nulo", "Indeciso / Não sabe"]

        with st.form("form_pesquisa", clear_on_submit=True):
            nome_eleitor_pesq = st.text_input("Nome do Eleitor (Obrigatório para validar a pesquisa)")
            candidato_escolhido = st.selectbox(
                "Intenção de Voto (Espontânea/Estimulada):",
                opcoes_voto
            )

            if st.form_submit_button("Registrar Voto (+1 Ponto)"):
                # A nova trava antifraude entra aqui:
                if not nome_eleitor_pesq.strip():
                    st.error("🛑 Trava de Segurança: É obrigatório informar o nome do eleitor!")
                elif candidato_escolhido == "Selecione...":
                    st.warning("⚠️ Selecione uma intenção de voto válida.")
                else:
                    try:
                        supabase.table("pesquisas_rua").insert({
                            "turno_id": st.session_state["turno_id_atual"],
                            "nome_eleitor": nome_eleitor_pesq.strip(),
                            "intencao_voto": candidato_escolhido
                        }).execute()
                        st.toast("✅ Voto validado e computado no radar!")
                    except Exception as e:
                        st.error(f"Erro ao salvar pesquisa: {e}")

        st.markdown("---")

        # --- MÓDULO 3: CHECK-OUT ---
        st.subheader("🏁 3. Encerrar Rota (Check-out)")
        with st.form("form_checkout"):
            clima = st.radio("Nível de aceitação da rua nesta rota:",
                             ["🤩 Ótimo", "🙂 Bom", "😐 Regular", "🛑 Baixo"], horizontal=True)

            justificativa = ""
            if clima == "🛑 Baixo":
                justificativa = st.text_input("⚠️ Motivo da baixa aceitação (Obrigatório)")

            btn_encerrar = st.form_submit_button("Encerrar Turno e Gerar Relatório")

            if btn_encerrar:
                if clima == "🛑 Baixo" and not justificativa.strip():
                    st.error("🛑 Justifique o motivo de classificar o clima como 'Baixo'.")
                else:
                    try:
                        supabase.table("rotas_e_clima").insert({
                            "turno_id": st.session_state["turno_id_atual"],
                            "clima_rua": clima,
                            "justificativa_abandono": justificativa
                        }).execute()

                        st.session_state["turno_ativo"] = False
                        st.session_state["turno_id_atual"] = None
                        st.rerun()
                    except Exception as e:
                        st.error("Erro ao encerrar o turno.")

# --- 6. Roteamento Principal (O Guarda de Trânsito) ---
if not st.session_state["logado"]:
    tela_login()
else:
    if st.session_state["perfil"] == "Lider_Rua":
        script_manada_de_leao()
    elif st.session_state["perfil"] == "Influenciador":
        st.title("🌿 A Selva - Radar de Influência")
        st.write("Em construção...")
    elif st.session_state["perfil"] == "Coordenacao":
        st.title("👁️ O Olho da Leoa - C3")
        st.write("Em construção...")