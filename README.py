p"] // 500) + 1
        with open(self.file, 'w') as f: json.dump(self.dados, f)
        return xp_ganho

# --- MOTOR DE LEITURA E PRIORIDADE ---
def processar_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    texto_completo = "\n".join([pagina.get_text() for pagina in doc])
    
    tarefas = []
    # Regex para capturar Data e Descrição (Ex: 12/05 - Prova de Matemática)
    padrao = r"(\d{2}/\d{2})\s*-\s*(.*)"
    matches = re.findall(padrao, texto_completo)
    
    for data_str, desc in matches:
        desc_lower = desc.lower()
        # Define Peso
        if any(w in desc_lower for w in ["prova", "avaliação", "exame"]): peso = 3
        elif any(w in desc_lower for w in ["teste", "simulado"]): peso = 2
        else: peso = 1
        
        data_dt = datetime.strptime(f"{data_str}/2026", "%d/%m/%Y")
        tarefas.append({"Data": data_dt, "Atividade": desc, "Tipo": peso, "Status": "Pendente"})
    
    return tarefas

# --- INTERFACE (DASHBOARD) ---
st.set_page_config(page_title="StudyFlow Sênior", layout="wide")
game = Gamificacao()

st.title("🛡️ StudyFlow: Seu RPG de Estudos")

# Sidebar com Status
st.sidebar.header(f"Nível {game.dados['nivel']}")
st.sidebar.progress(min((game.dados['xp'] % 500) / 500, 1.0))
st.sidebar.write(f"XP Total: {game.dados['xp']}")
st.sidebar.write(f"Missões Concluídas: {game.dados['concluidas']}")

arquivo = st.file_uploader("Suba seu roteiro semanal (PDF)", type="pdf")

if arquivo:
    if 'lista_tarefas' not in st.session_state:
        st.session_state.lista_tarefas = processar_pdf(arquivo)

    df = pd.DataFrame(st.session_state.lista_tarefas)
    df = df.sort_values(by=["Tipo", "Data"], ascending=[False, True])

    st.subheader("⚔️ Suas Missões da Semana")
    
    for i, row in df.iterrows():
        col1, col2, col3 = st.columns([1, 4, 1])
        emoji = {3: "🔴 PROVA", 2: "🟠 TESTE", 1: "🔵 TAREFA"}[row['Tipo']]
        
        col1.write(row['Data'].strftime('%d/%m'))
        col2.write(f"**{emoji}**: {row['Atividade']}")
        
        if col3.button("Concluir", key=f"btn_{i}"):
            xp = game.ganhar_xp(row['Tipo'])
            st.toast(f"Missão Cumprida! +{xp} XP")
            st.balloons()
            # Aqui poderíamos remover a tarefa da lista...
