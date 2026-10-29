import os
import asyncio
import edge_tts
import re
from google import genai
from google.genai import types

# ... (CARREGAR CHAVE E ANALISAR MAQUINA CONTINUAM IGUAIS) ...
if os.path.exists(".env"):
    with open(".env", "r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if linha.startswith("GEMINI_API_KEY="):
                os.environ["GEMINI_API_KEY"] = linha.split("=", 1)[1].strip().strip('"').strip("'")
                break

client = genai.Client()

def analisar_maquina(caminho_imagem: str) -> str:
    # ... (código igual ao anterior) ...
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
            contents=[types.Part.from_bytes(data=imagem_bytes, mime_type='image/jpeg'), prompt]
        )
        return resposta.text
    except Exception as e:
        return f"Erro ao analisar a imagem: {e}"


# --- NOVA FUNÇÃO PARA LIMPAR O TEXTO ---
def limpar_texto_para_audio(texto: str) -> str:
    """Remove Markdown e símbolos que o robô leria errado."""
    # Remove asteriscos (negrito/itálico)
    texto = texto.replace("*", "")
    # Remove cerquilhas (títulos)
    texto = texto.replace("#", "")
    # Substitui múltiplos espaços e quebras de linha por espaço único
    texto = re.sub(r'\s+', ' ', texto)
    return texto.strip()


def gerar_audio_ficha(texto_treino: str, nome_arquivo: str = "ficha_treino.mp3"):
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
        print(f"❌ Erro ao gerar áudio: {e}")
        return False

# Função gerar_audio_maquina também pode usar o limpar_texto_para_audio se quiser