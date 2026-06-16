import streamlit as st

# 1. Configuração inicial da página (A fachada do nosso prédio)
st.set_page_config(page_title="O Olho da Leoa", page_icon="🦁", layout="centered")

# 2. Cabeçalho
st.title("🦁 O Olho da Leoa")
st.subheader("Painel de Acesso Seguro")
st.markdown("---")

# 3. Criando a catraca de acesso (Formulário de Login)
usuario = st.text_input("Usuário")
senha = st.text_input("Senha", type="password") # Oculta os caracteres da senha
botao_entrar = st.button("Entrar")

# 4. A Lógica do Guarda de Trânsito
if botao_entrar:
    # Vamos usar um usuário e senha simples por enquanto para testar a mecânica
    if usuario == "admin" and senha == "leoa2026":
        st.success("✅ Acesso liberado! Bem-vindo ao sistema.")
        st.info("No futuro, as suas outras telas e automações aparecerão aqui.")
    else:
        st.error("❌ Acesso negado. Usuário ou senha incorretos.")