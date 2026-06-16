import streamlit as st

# --- 1. Configuração Inicial da Página ---
st.set_page_config(page_title="O Olho da Leoa", page_icon="🦁", layout="wide")

# --- 2. Inicialização do Estado da Sessão (Memória do Guarda de Trânsito) ---
if "logado" not in st.session_state:
    st.session_state["logado"] = False
if "perfil" not in st.session_state:
    st.session_state["perfil"] = None
if "nome_usuario" not in st.session_state:
    st.session_state["nome_usuario"] = None

# --- 3. Módulo de Login (A Catraca) ---
def tela_login():
    # Centralizando o login na tela
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🦁 O Olho da Leoa")
        st.subheader("Acesso Restrito")
        st.markdown("---")

        with st.form("form_login"):
            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            botao_entrar = st.form_submit_button("Entrar")

            if botao_entrar:
                # Dicionário temporário para testarmos o Roteamento Seguro
                usuarios_mock = {
                    "lider1": {"senha": "123", "perfil": "Lider_Rua", "nome": "João (Carro 1)"},
                    "influencer1": {"senha": "123", "perfil": "Influenciador", "nome": "Maria Insta"},
                    "coord": {"senha": "admin", "perfil": "Coordenacao", "nome": "Comando C3"}
                }

                if usuario in usuarios_mock and usuarios_mock[usuario]["senha"] == senha:
                    # Salva as credenciais na sessão
                    st.session_state["logado"] = True
                    st.session_state["perfil"] = usuarios_mock[usuario]["perfil"]
                    st.session_state["nome_usuario"] = usuarios_mock[usuario]["nome"]
                    st.rerun() # Atualiza a página instantaneamente
                else:
                    st.error("❌ Usuário ou senha incorretos.")

# --- 4. Estruturas Base dos 3 Scripts (Esqueletos) ---
def script_manada_de_leao():
    st.header(f"🚙 Manada de Leão - Tático de Rua")
    st.write(f"Bem-vindo, **{st.session_state['nome_usuario']}**. Turno pronto para iniciar.")
    st.info("🚧 Módulo em Construção: Aqui entrará a Trava Logística de Estoque, Seleção de Equipe, Rotas e Captação de WhatsApp.")
    if st.button("Encerrar Sessão (Check-out)"):
        st.session_state.clear()
        st.rerun()

def script_a_selva():
    st.header(f"📱 A Selva - Radar de Influenciadores")
    st.write(f"Bem-vindo, **{st.session_state['nome_usuario']}**.")
    st.info("🚧 Módulo em Construção: Aqui entrará o Cadastro de Postagens e a Geração de Código Criptográfico.")
    if st.button("Encerrar Sessão"):
        st.session_state.clear()
        st.rerun()

def script_o_olho_da_leoa():
    st.header(f"👁️ O Olho da Leoa - Sala de Guerra (C3)")
    st.write(f"Comandante logado: **{st.session_state['nome_usuario']}**.")
    st.info("🚧 Módulo em Construção: Aqui entrará o Despacho de Carros, Inside Sales, Auditoria de Fraudes e Coliseu de Dados (Dashboards).")
    if st.button("Encerrar Sessão"):
        st.session_state.clear()
        st.rerun()

# --- 5. O Roteador Principal (A Lógica que Oculta as Telas) ---
if not st.session_state["logado"]:
    tela_login()
else:
    # Se passou da catraca, o Guarda de Trânsito analisa a tag e libera APENAS a tela correta
    if st.session_state["perfil"] == "Lider_Rua":
        script_manada_de_leao()
    elif st.session_state["perfil"] == "Influenciador":
        script_a_selva()
    elif st.session_state["perfil"] == "Coordenacao":
        script_o_olho_da_leoa()