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
    st.header("🌿 A Selva - Radar Digital (Influenciadores)")
    st.write(f"Influenciador(a) Atirador(a): **{st.session_state['nome_usuario']}**")
    st.markdown("---")

    st.info(
        "💡 **Regra de Ouro:** Monitore suas postagens. Quando achar que o post atingiu o pico de Alcance/Views, faça o registro. **Atenção:** Só é permitido um registro por link de publicação.")

    # Formulário de Registro de Engajamento
    with st.form("form_reporte_digital", clear_on_submit=True):
        st.subheader("📱 Registrar Desempenho de Postagem")

        col_d, col_t = st.columns(2)
        with col_d:
            data_acao = st.date_input("Data em que a ação/foto foi feita")
        with col_t:
            turno_acao = st.selectbox("Turno da Ação", ["Manhã", "Tarde", "Noite", "Integral"])

        link_post = st.text_input("Link da Publicação (Único e Obrigatório)",
                                  placeholder="Ex: https://instagram.com/p/...")

        col_v, col_a = st.columns(2)
        with col_v:
            views = st.number_input("Visualizações (Views)", min_value=0, step=100)
        with col_a:
            alcance = st.number_input("Alcance (Reach)", min_value=0, step=100)

        comprovante = st.file_uploader("Subir Print do Engajamento (Prova)", type=["png", "jpg", "jpeg"])

        btn_registrar = st.form_submit_button("🚀 Registrar Métrica e Distribuir Pontos")

        if btn_registrar:
            if not link_post.strip():
                st.error("🛑 O Link da publicação é obrigatório para evitar duplicidade!")
            elif views == 0 and alcance == 0:
                st.warning("⚠️ Você precisa ter pelo menos alguma view ou alcance para registrar.")
            else:
                try:
                    # 1. VERIFICAÇÃO DE DUPLICIDADE: Impede que o mesmo link seja cadastrado duas vezes
                    busca_link = supabase.table("registro_influencia_digital").select("id").eq("link_postagem",
                                                                                               link_post.strip()).execute()

                    if len(busca_link.data) > 0:
                        st.error(
                            "❌ Negado! Este link já foi registrado anteriormente. Não é possível atualizar as views de um post já validado.")
                    else:
                        # 2. INSERÇÃO DOS DADOS NO BANCO
                        # Pegamos apenas o nome do arquivo se ele subir um print
                        nome_arquivo = comprovante.name if comprovante else "Sem print"

                        supabase.table("registro_influencia_digital").insert({
                            "colaborador_id": st.session_state["usuario_id"],
                            "data_referencia": str(data_acao),
                            "turno_referencia": turno_acao,
                            "link_postagem": link_post.strip(),
                            "views": views,
                            "alcance": alcance,
                            "print_arquivo": nome_arquivo
                        }).execute()

                        st.success(
                            f"🔥 Animal! Postagem validada. Os pontos gerados foram distribuídos para toda a equipe que operou no turno da {turno_acao} do dia {data_acao.strftime('%d/%m/%Y')}!")
                        time.sleep(2)
                        st.rerun()
                except Exception as e:
                    st.error(
                        f"Erro no banco de dados (Verifique se a tabela 'registro_influencia_digital' existe). Detalhe: {e}")

    # Histórico de aprovações
    st.markdown("---")
    st.subheader("📜 Seu Histórico de Disparos")
    try:
        resp_historico = supabase.table("registro_influencia_digital").select(
            "data_referencia, link_postagem, views, alcance").eq("colaborador_id",
                                                                 st.session_state["usuario_id"]).order("id",
                                                                                                       ascending=False).limit(
            5).execute()
        if resp_historico.data:
            df_hist = pd.DataFrame(resp_historico.data)
            df_hist.columns = ["Data Ref.", "Link do Post", "Views", "Alcance"]
            st.dataframe(df_hist, use_container_width=True)
        else:
            st.info("Nenhuma postagem registrada ainda. Vá para as redes! 🦁")
    except:
        pass

    # --- HISTÓRICO RECENTE DO INFLUENCIADOR ---
    st.markdown("---")
    st.subheader("📜 Seus Últimos Reportes de Hoje")
    try:
        resp_historico = supabase.table("registro_influenciadores") \
            .select("created_at, local_referencia, adesivos_colados, panfletos_entregues") \
            .eq("colaborador_id", st.session_state["usuario_id"]) \
            .order("created_at", ascending=False) \
            .limit(5).execute()

        if resp_historico.data:
            df_hist = pd.DataFrame(resp_historico.data)
            # Organiza as colunas para exibição rápida
            df_hist.columns = ["Horário", "Local", "Adesivos", "Panfletos"]
            st.dataframe(df_hist, use_container_width=True)
        else:
            st.info("Você ainda não fez nenhum reporte hoje. Vá para cima deles! 🦁")
    except Exception:
        pass

# --- Script 3: O Olho da Leoa (Sala de Guerra) ---
def script_o_olho_da_leoa():
    st.title("👁️ O Olho da Leoa - Comando C3")
    st.write("A central de inteligência e controle de toda a operação.")
    st.markdown("---")

    aba1, aba2, aba3, aba4, aba5 = st.tabs([
        "👁️ Visão", "👑 Gamificação", "🔎 O Covil", "🐾 Despacho", "💰 O Tesouro (Controle de Turnos e AC)"
    ])

    with aba1: st.info("Gráficos Visuais")
    
    with aba2:
        st.header("👑 Gamificação e Metas da Operação")

        tab_ranking, tab_metas = st.tabs(["🏆 Ranking de Equipes", "⚙️ Configurar Metas e Multiplicadores"])

        with tab_ranking:
            st.info("O Ranking Geral será gerado aqui cruzando os dados da Rua (Manada) com os do Digital (Selva).")

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
                        # Como é um painel global, usamos uma tabela simples de configuração.
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

    with aba3: st.info("Auditoria")

    with aba4:
        st.header("🐾 Controle da Manada (Despacho)")

        # --- Sub-abas principais do despacho ---
        tab_rotas, tab_candidatos, tab_rh = st.tabs(["📍 Territórios de Caça", "🦁 Realeza", "🐺 Alcateia (RH)"])

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

        with tab_candidatos:
            st.subheader("Adicionar Nome à Realeza (Radar de Pesquisas)")
            with st.form("form_candidatos", clear_on_submit=True):
                nome_cand = st.text_input("Nome do Candidato ou Partido")
                if st.form_submit_button("Registrar no Sistema"):
                    if nome_cand:
                        try:
                            supabase.table("candidatos").insert({"nome": nome_cand.strip(), "ativo": True}).execute()
                            st.success(f"✅ {nome_cand} adicionado ao radar dos líderes de rua!")
                        except Exception as e:
                            st.error(f"Erro ao adicionar candidato: {e}")
                    else:
                        st.warning("⚠️ Digite um nome válido.")

            st.markdown("---")
            st.subheader("🦁 Realeza Atual (Candidatos Ativos na Rua)")
            try:
                resp_cand = supabase.table("candidatos").select("*").eq("ativo", True).execute()
                if resp_cand.data:
                    for c in resp_cand.data:
                        st.write(f"▪️ **{c['nome']}**")
                else:
                    st.info("Nenhum candidato cadastrado no momento.")
            except:
                pass

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
                        tag_colab = st.selectbox("Patente (Função)", ["Motorista", "Influenciador", "Apoio", "Coordenacao"])

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
                            patentes = ["Motorista", "Influenciador", "Apoio", "Coordenacao"]
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