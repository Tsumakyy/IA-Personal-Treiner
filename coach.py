import os
import asyncio
import re
import edge_tts
from google import genai
from google.genai import types

# ==========================================
# 1. CARREGAR A CHAVE (PC e Nuvem)
# ==========================================
# Tenta carregar do Streamlit Secrets (se estiver na nuvem)
try:
    import streamlit as st
    if "GEMINI_API_KEY" in st.secrets:
        os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass # Se não for Streamlit, ignora e segue para o .env

# Se não achou na nuvem, tenta carregar do arquivo .env (no PC)
if not os.getenv("GEMINI_API_KEY"):
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()
                if linha.startswith("GEMINI_API_KEY="):
                    chave = linha.split("=", 1)[1].strip().strip('"').strip("'")
                    os.environ["GEMINI_API_KEY"] = chave
                    break

if not os.getenv("GEMINI_API_KEY"):
    print("⚠️  AVISO: GEMINI_API_KEY não encontrada!")

client = genai.Client()


# ==========================================
# 2. ANALISAR A FOTO DA MÁQUINA
# ==========================================
def analisar_maquina(caminho_imagem: str) -> str:
    """Lê a imagem da máquina e usa o Gemini para explicar como usar."""
    
    if not os.path.exists(caminho_imagem):
        return "❌ Erro: Arquivo de imagem não encontrado no caminho informado."

    with open(caminho_imagem, "rb") as img:
        imagem_bytes = img.read()

    prompt = """Você é um personal trainer experiente ajudando um senhor na academia.
Ele tirou uma foto desta máquina e não sabe como usar.
Identifique a máquina na imagem e explique de forma simples e direta:
1. O nome do aparelho.
2. Como se posicionar (regulagem de banco, altura, pegada).
3. Como executar o movimento (respiração e postura).
4. Cuidados principais (o que não fazer).
Responda em tópicos, com linguagem amigável e sem termos técnicos complicados."""

    try:
        resposta = client.models.generate_content(
            model='gemini-3.6-flash',
            contents=[
                types.Part.from_bytes(data=imagem_bytes, mime_type='image/jpeg'),
                prompt
            ]
        )
        return resposta.text
    except Exception as e:
        return f"Erro ao analisar a imagem: {e}"


# ==========================================
# 3. LIMPAR TEXTO PARA ÁUDIO
# ==========================================
def limpar_texto_para_audio(texto: str) -> str:
    """Remove Markdown e símbolos que o robô leria errado (como asteriscos e cerquilhas)."""
    texto = texto.replace("*", "")
    texto = texto.replace("#", "")
    texto = re.sub(r'\s+', ' ', texto) # Substitui múltiplos espaços/quebras por um único espaço
    return texto.strip()


# ==========================================
# 4. GERAR ÁUDIO DA FICHA DE TREINO
# ==========================================
def gerar_audio_ficha(texto_treino: str, nome_arquivo: str = "ficha_treino.mp3"):
    """Transforma o texto do treino em um áudio amigável para o pai."""
    
    prompt_audio = f"""
    Você é um personal trainer falando com um senhor idoso na academia.
    Transforme as informações de treino abaixo em um texto para ser falado em voz alta.
    Seja direto, amigável e não use termos técnicos. 
    Comece com uma saudação, diga o nome do exercício, quantas repetições ele deve fazer e dê 1 ou 2 dicas essenciais de como usar a máquina.
    NÃO use asteriscos, cerquilhas ou formatação de texto. Fale como se estivesse conversando.
    
    Informações do Treino: {texto_treino}
    """
    
    try:
        resposta_ia = client.models.generate_content(model='gemini-3.6-flash', contents=prompt_audio)
        roteiro = resposta_ia.text
        
        # Limpa o texto antes de gerar o áudio
        roteiro_limpo = limpar_texto_para_audio(roteiro)
        
        async def _gerar():
            voz = "pt-BR-AntonioNeural"
            communicate = edge_tts.Communicate(roteiro_limpo, voz, rate="-10%")
            await communicate.save(nome_arquivo)
        
        asyncio.run(_gerar())
        return True
    except Exception as e:
        print(f"❌ Erro ao gerar áudio da ficha: {e}")
        return False


# ==========================================
# 5. GERAR ÁUDIO DA MÁQUINA (OPCIONAL)
# ==========================================
def gerar_audio_maquina(texto_maquina: str, nome_arquivo: str = "instrucao_maquina.mp3"):
    """Transforma as instruções da máquina em um áudio curto e direto."""
    
    prompt_audio = f"""
    Você é um personal trainer ajudando um senhor na academia.
    Resuma as instruções abaixo em um áudio de no máximo 30 segundos.
    Fale apenas o essencial: nome do aparelho, como sentar/segurar e o movimento principal.
    Não use asteriscos ou formatação de texto.
    
    Instruções: {texto_maquina}
    """
    
    try:
        resposta_ia = client.models.generate_content(model='gemini-3.6-flash', contents=prompt_audio)
        roteiro = resposta_ia.text
        
        roteiro_limpo = limpar_texto_para_audio(roteiro)
        
        async def _gerar():
            voz = "pt-BR-AntonioNeural"
            communicate = edge_tts.Communicate(roteiro_limpo, voz, rate="-5%")
            await communicate.save(nome_arquivo)
        
        asyncio.run(_gerar())
        return True
    except Exception as e:
        print(f"❌ Erro ao gerar áudio da máquina: {e}")
        return False