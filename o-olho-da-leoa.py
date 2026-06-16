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
                usuario_limpo = usuario.strip()  # Limpa espaços no início e no fim
                # O Guarda de Trânsito vai até o Supabase perguntar se a pessoa existe
                try:
                    resposta = supabase.table("rh_colaboradores").select("*").eq("nome", usuario_limpo).execute()
                    dados = resposta.data

                    if len(dados) > 0:
                        usuario_db = dados[0]
                        if usuario_db["ativo"]:
                            # Libera a catraca
                            st.session_state["logado"] = True
                            st.session_state["nome_usuario"] = usuario_db["nome"]
                            st.session_state["usuario_id"] = usuario_db["id"]

                            # Roteamento baseado na Tag do Banco de Dados
                            tag = usuario_db["tag"]
                            if tag in ["Motorista", "Apoio"]:
                                st.session_state["perfil"] = "Lider_Rua"
                            elif tag == "Influenciador":
                                st.session_state["perfil"] = "Influenciador"
                            elif tag == "Coordenacao":
                                st.session_state["perfil"] = "Coordenacao"

                            st.rerun() # Recarrega a página para liberar a tela certa
                        else:
                            st.error("❌ Usuário inativo no sistema.")
                    else:
                        st.error("❌ Usuário não encontrado. Digite o nome exato.")
                except Exception as e:
                    st.error(f"⚠️ Erro de conexão com o banco: {e}")

# --- 5. Estruturas Base dos 3 Scripts ---
def script_manada_de_leao():
    st.header("🚙 Manada de Leão - Tático de Rua")
    st.write(f"Líder da Viatura: **{st.session_state['nome_usuario']}**")
    st.info("🚧 Módulo em Construção: Aqui entrará a Trava Logística e Seleção de Equipe.")
    if st.button("Encerrar Sessão (Check-out)"):
        st.session_state.clear()
        st.rerun()

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
