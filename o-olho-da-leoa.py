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
            # Conforme nossa regra de negócio: Login pelo nome do Líder/Colaborador
            usuario = st.text_input("Nome do Usuário")
            botao_entrar = st.form_submit_button("Entrar")

            if botao_entrar and usuario:  # Só entra se o campo usuario tiver algo
                usuario_limpo = usuario.strip()
                # Debug: vamos ver o que o banco retorna
                resposta = supabase.table("rh_colaboradores").select("nome").execute()
                st.write("Nomes encontrados no banco:", resposta.data)

                # Busca específica
                busca = supabase.table("rh_colaboradores").select("*").ilike("nome", usuario_limpo).execute()

                if len(busca.data) > 0:
                    usuario_db = busca.data[0]
                    if usuario_db["ativo"]:
                        st.session_state["logado"] = True
                        st.session_state["nome_usuario"] = usuario_db["nome"]
                        st.session_state["usuario_id"] = usuario_db["id"]

                        tag = usuario_db["tag"]

                        # Alinhamento perfeito dos IFs e ELIFs de Tag
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

# --- 5. Estruturas Base dos 3 Scripts ---
# --- SUBSTITUA A FUNÇÃO script_manada_de_leao ---
def script_manada_de_leao():
    st.header("🚙 Manada de Leão - Tático de Rua")
    st.write(f"Líder: **{st.session_state['nome_usuario']}**")
    st.markdown("---")

    if "turno_ativo" not in st.session_state:
        st.session_state["turno_ativo"] = False
    if "turno_id_atual" not in st.session_state:
        st.session_state["turno_id_atual"] = None

    # --- 1. TELA DE ABERTURA DE TURNO ---
    if not st.session_state["turno_ativo"]:
        st.subheader("📋 Início de Turno")

        # Puxar colaboradores ativos do Supabase para o Dropdown (excluindo o próprio líder)
        try:
            resp_colab = supabase.table("rh_colaboradores").select("id, nome, tag").eq("ativo", True).execute()
            lista_colaboradores = [c for c in resp_colab.data if c["id"] != st.session_state["usuario_id"]]
            opcoes_equipe = {f"{c['nome']} ({c['tag']})": c['id'] for c in lista_colaboradores}
        except Exception as e:
            st.error(f"Erro ao carregar equipe: {e}")
            opcoes_equipe = {}

        with st.form("form_abertura_turno"):
            placa = st.text_input("Placa do Veículo (ex: ABC-1234)")

            equipe_nomes = st.multiselect(
                "Selecione a Equipe do Dia",
                options=list(opcoes_equipe.keys())
            )

            st.markdown("---")
            st.markdown("📦 **Estoque de Materiais (Trava Logística)**")
            col1, col2, col3 = st.columns(3)
            with col1:
                panfletos = st.number_input("Panfletos (Qtd)", min_value=0, step=50)
            with col2:
                adesivos = st.number_input("Adesivos de Carro", min_value=0, step=10)
            with col3:
                bandeiras = st.number_input("Bandeiras", min_value=0, step=1)

            btn_iniciar = st.form_submit_button("Registrar Veículo e Estoque")

            if btn_iniciar:
                if not placa:
                    st.error("❌ A Placa do veículo é obrigatória!")
                elif len(equipe_nomes) == 0:
                    st.error("❌ Selecione pelo menos um membro para a equipe!")
                elif panfletos == 0 and adesivos == 0 and bandeiras == 0:
                    st.error("🛑 Trava Logística Ativada: É obrigatório registrar o material embarcado!")
                else:
                    # Mapear os nomes selecionados para seus IDs
                    equipe_ids = [opcoes_equipe[nome] for nome in equipe_nomes]

                    # 1. INSERT na tabela controle_turnos
                    dados_turno = {
                        "lider_id": st.session_state["usuario_id"],
                        "placa_veiculo": placa.upper(),
                        "equipe_ids": equipe_ids  # Assumindo que a coluna é um array de INT ou JSONB
                    }
                    res_turno = supabase.table("controle_turnos").insert(dados_turno).execute()

                    if res_turno.data:
                        novo_turno_id = res_turno.data[0]["id"]

                        # 2. INSERT na tabela estoque_materiais
                        dados_estoque = {
                            "turno_id": novo_turno_id,
                            "panfletos_retirados": panfletos,
                            "adesivos_retirados": adesivos,
                            "bandeiras_retiradas": bandeiras
                        }
                        supabase.table("estoque_materiais").insert(dados_estoque).execute()

                        # Atualiza a sessão
                        st.session_state["turno_id_atual"] = novo_turno_id
                        st.session_state["turno_ativo"] = True
                        st.success("✅ Veículo e estoque registrados! Missão liberada.")
                        st.rerun()

    # --- 2. TELA DA RUA (Operação e Check-out) ---
    else:
        st.success(f"✅ Turno #{st.session_state['turno_id_atual']} ativo! Viatura na rua.")
        st.markdown("---")

        # Módulo de Captação Rápida (Exemplo estrutural para captura_eleitores)
        st.subheader("📱 Captação de Eleitores")
        with st.form("form_captura"):
            col_nome, col_zap = st.columns(2)
            with col_nome:
                nome_eleitor = st.text_input("Nome do Eleitor")
            with col_zap:
                zap_eleitor = st.text_input("WhatsApp (com DDD)")
            bairro_eleitor = st.text_input("Bairro")

            if st.form_submit_button("Salvar Contato"):
                if nome_eleitor and zap_eleitor:
                    supabase.table("captura_eleitores").insert({
                        "turno_id": st.session_state["turno_id_atual"],
                        "nome": nome_eleitor,
                        "whatsapp": zap_eleitor,
                        "bairro": bairro_eleitor
                    }).execute()
                    st.toast("✅ Contato salvo e enviado ao banco!")
                else:
                    st.warning("Preencha Nome e WhatsApp.")

        st.markdown("---")

        # Módulo de Check-out e Clima da Rua
        st.subheader("🏁 Encerrar Rota (Check-out)")
        with st.form("form_checkout"):
            clima = st.radio("Qual o nível de aceitação da rua nesta rota?",
                             ["🤩 Ótimo", "🙂 Bom", "😐 Regular", "🛑 Baixo"], horizontal=True)

            justificativa = ""
            if clima == "🛑 Baixo":
                justificativa = st.text_input("⚠️ Motivo do abandono ou baixa aceitação (Obrigatório)")

            btn_encerrar = st.form_submit_button("Registrar Clima e Encerrar Turno")

            if btn_encerrar:
                if clima == "🛑 Baixo" and not justificativa.strip():
                    st.error("🛑 Você deve justificar o motivo de classificar o clima como 'Baixo'.")
                else:
                    # INSERT na tabela rotas_e_clima
                    dados_clima = {
                        "turno_id": st.session_state["turno_id_atual"],
                        "clima_rua": clima,
                        "justificativa_abandono": justificativa
                    }
                    supabase.table("rotas_e_clima").insert(dados_clima).execute()

                    # Reseta o ciclo
                    st.session_state["turno_ativo"] = False
                    st.session_state["turno_id_atual"] = None
                    st.success("🏁 Turno encerrado com sucesso. Relatório enviado ao Olho da Leoa.")
                    st.rerun()
# --- 6. Roteamento Principal (O Guarda de Trânsito) ---
if not st.session_state["logado"]:
    tela_login()
else:
    # Direciona o usuário de acordo com o perfil
    if st.session_state["perfil"] == "Lider_Rua":
        script_manada_de_leao()
    elif st.session_state["perfil"] == "Influenciador":
        st.title("🌿 A Selva - Radar de Influência")
        st.write("Em construção...")
    elif st.session_state["perfil"] == "Coordenacao":
        st.title("👁️ O Olho da Leoa - C3")
        st.write("Em construção...")
