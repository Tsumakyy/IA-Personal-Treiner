# IA-Personal-Treiner

Coach de treino adaptativo em terminal. Registra sessões, calcula volume
e 1RM estimado, e usa um LLM (Ollama local ou Gemini free tier) para
sugerir a próxima sessão com base em regras de progressão.

## Uso
    python registrar.py --tipo push --ex "supino,3,8,80,8"
    python main.py

## Backends de LLM
- Ollama (padrão, local, grátis): `ollama pull llama3.1`
- Gemini free tier: `export LLM_BACKEND=gemini` e `export GEMINI_API_KEY=...`