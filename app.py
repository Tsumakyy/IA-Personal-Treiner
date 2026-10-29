import streamlit as st
import os
from coach import analisar_maquina, gerar_audio_ficha
import uuid # Para gerar nomes únicos de arquivos

st.set_page_config(page_title="IA Personal Trainer", page_icon="🏋️‍♂️", layout="wide")

st.title("🏋️‍♂️ Ficha de Treino Inteligente")
st.markdown("Tire foto da máquina, adicione as informações e gere a ficha em áudio para o seu pai!")

# Inicializa a "memória" do app para guardar os exercícios adicionados
if "treino" not in st.session_state:
    st.session_state.treino = []

# Cria as abas A, B e C
abas = st.tabs(["Treino A", "Treino B", "Treino C"])

for i, aba in enumerate(abas):
    letra = ["A", "B", "C"][i]
    with aba:
        st.header(f"Ficha {letra}")
        
        # Formulário para adicionar um exercício
        with st.form(key=f"form_{letra}"):
            col1, col2 = st.columns(2)
            with col1:
                foto = st.file_uploader("Foto da máquina", type=["jpg", "jpeg", "png"], key=f"foto_{letra}")
            with col2:
                nome_ex = st.text_input("Nome do Exercício", key=f"nome_{letra}", placeholder="Ex: Supino Inclinado")
                reps = st.text_input("Séries e Repetições", key=f"reps_{letra}", placeholder="Ex: 3x10")
                obs = st.text_input("Observação (opcional)", key=f"obs_{letra}")
            
            botao_adicionar = st.form_submit_button("Adicionar Exercício")
            
            if botao_adicionar:
                if not foto or not nome_ex or not reps:
                    st.error("Preencha a foto, o nome e as repetições!")
                else:
                    # Salva a foto temporariamente para o Gemini ler
                    nome_arquivo_foto = f"temp_{uuid.uuid4().hex}.jpg"
                    with open(nome_arquivo_foto, "wb") as f:
                        f.write(foto.getbuffer())
                    
                    with st.spinner("Analisando a máquina com IA..."):
                        instrucoes = analisar_maquina(nome_arquivo_foto)
                    
                    # Guarda os dados no estado do app
                    st.session_state.treino.append({
                        "letra": letra,
                        "foto": foto,
                        "nome": nome_ex,
                        "reps": reps,
                        "obs": obs,
                        "instrucoes": instrucoes
                    })
                    
                    # Limpa o arquivo temporário
                    if os.path.exists(nome_arquivo_foto):
                        os.remove(nome_arquivo_foto)
                        
                    st.success(f"Exercício {nome_ex} adicionado à Ficha {letra}!")

# --- ÁREA DE EXIBIÇÃO DA FICHA E ÁUDIO ---
st.divider()
st.header("📋 Sua Ficha de Treino")

if not st.session_state.treino:
    st.info("Nenhum exercício adicionado ainda. Use as abas acima para montar seu treino.")
else:
    # Mostra os exercícios separados por Ficha (A, B, C)
    for letra in ["A", "B", "C"]:
        exercicios_da_letra = [ex for ex in st.session_state.treino if ex["letra"] == letra]
        
        if exercicios_da_letra:
            st.subheader(f"Ficha {letra}")
            
            # Cria colunas para mostrar os cards lado a lado
            colunas = st.columns(len(exercicios_da_letra))
            
            for idx, ex in enumerate(exercicios_da_letra):
                with colunas[idx]:
                    with st.container(border=True):
                        # Mostra a foto
                        if ex["foto"]:
                            st.image(ex["foto"], use_container_width=True)
                        st.markdown(f"**{ex['nome']}**")
                        st.markdown(f"Repetições: **{ex['reps']}**")
                        if ex["obs"]:
                            st.caption(f"Obs: {ex['obs']}")
                        
                        # Acordeão para ver as instruções da IA
                        with st.expander("Ver instruções da máquina"):
                            st.write(ex["instrucoes"])

    # --- GERAR ÁUDIO DA FICHA COMPLETA ---
    st.divider()
    st.subheader("🎙️ Gerar Áudio para o seu Pai")
    
    letra_audio = st.selectbox("Escolha qual ficha gerar o áudio:", ["A", "B", "C"])
    
    if st.button("Gerar Áudio da Ficha"):
        # Junta as informações de todos os exercícios da ficha escolhida
        texto_para_audio = ""
        exs_para_audio = [ex for ex in st.session_state.treino if ex["letra"] == letra_audio]
        
        if not exs_para_audio:
            st.warning(f"Não há exercícios na ficha {letra_audio} para gerar o áudio.")
        else:
            with st.spinner("A IA está preparando o áudio..."):
                for ex in exs_para_audio:
                    texto_para_audio += f"Exercício: {ex['nome']}. Repetições: {ex['reps']}. "
                    if ex["obs"]:
                        texto_para_audio += f"Observação: {ex['obs']}. "
                    # Pega só as instruções da máquina para a IA resumir no áudio
                    texto_para_audio += f"Instruções: {ex['instrucoes']}\n\n"
                
                nome_audio = f"ficha_{letra_audio}.mp3"
                sucesso = gerar_audio_ficha(texto_para_audio, nome_audio)
                
                if sucesso:
                    st.success("Áudio gerado com sucesso!")
                    # Player de áudio no navegador
                    audio_file = open(nome_audio, "rb")
                    st.audio(audio_file.read(), format="audio/mp3")