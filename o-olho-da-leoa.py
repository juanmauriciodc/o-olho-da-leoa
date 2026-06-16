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

            if botao_entrar:
                usuario_limpo = usuario.strip()
                # Debug: vamos ver o que o banco retorna
                resposta = supabase.table("rh_colaboradores").select("nome").execute()
                st.write("Nomes encontrados no banco:", resposta.data)  # Isso vai listar tudo na tela

                # Busca específica
                busca = supabase.table("rh_colaboradores").select("*").eq("nome", usuario_limpo).execute()
                if len(busca.data) > 0:
                # ... (mantém o resto do seu código de login aqui)
                else:
                    st.error(f"❌ Não achei '{usuario_limpo}'. Verifique se há espaços ou acentos.")

# --- 5. Estruturas Base dos 3 Scripts ---
# --- SUBSTITUA A FUNÇÃO script_manada_de_leao ---
def script_manada_de_leao():
    st.header("🚙 Manada de Leão - Tático de Rua")
    st.write(f"Líder: **{st.session_state['nome_usuario']}**")

    # Verifica se o turno já está aberto
    turno_ativo = supabase.table("controle_turnos").select("*").eq("lider_id", st.session_state['usuario_id']).eq(
        "status", "Em Rota").execute()

    if not turno_ativo.data:
        st.subheader("📋 Início de Turno")
        with st.form("checkin_turno"):
            placa = st.text_input("Placa do Veículo (ex: ABC-1234)")
            equipe = st.multiselect("Selecione a Equipe do Dia", options=["Motorista", "Influenciador", "Apoio"])
            btn_iniciar = st.form_submit_button("Registrar Veículo e Estoque")

            if btn_iniciar and placa:
                # Cria o registro no banco
                novo_turno = {
                    "lider_id": st.session_state['usuario_id'],
                    "placa_veiculo": placa,
                    "equipe_ids": [1],  # Placeholder: Ajustaremos para pegar IDs reais da equipe
                    "status": "Aguardando Estoque"
                }
                supabase.table("controle_turnos").insert(novo_turno).execute()
                st.success("Veículo registrado! Agora, registre o estoque embarcado.")
                st.rerun()
    else:
        st.success("✅ Turno em andamento. Foco na missão!")
        # Aqui entraremos com a captação de eleitores em breve

def script_a_selva():
    st.header("📱 A Selva - Radar de Influenciadores")
    st.write(f"Influenciador(a): **{st.session_state['nome_usuario']}**")
    st.info("🚧 Módulo em Construção: Aqui entrará o Cadastro de Postagens.")
    if st.button("Encerrar Sessão"):
        st.session_state.clear()
        st.rerun()

def script_o_olho_da_leoa():
    st.header("👁️ O Olho da Leoa - Sala de Guerra (C3)")
    st.write(f"Comandante logado: **{st.session_state['nome_usuario']}**")
    st.info("🚧 Módulo em Construção: Aqui entrará o Despacho de Carros e Dashboards.")
    if st.button("Encerrar Sessão"):
        st.session_state.clear()
        st.rerun()

# --- 6. O Roteador Principal ---
if not st.session_state["logado"]:
    tela_login()
else:
    if st.session_state["perfil"] == "Lider_Rua":
        script_manada_de_leao()
    elif st.session_state["perfil"] == "Influenciador":
        script_a_selva()
    elif st.session_state["perfil"] == "Coordenacao":
        script_o_olho_da_leoa()
