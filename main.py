import os
from coach import analisar_maquina, gerar_audio_ficha

def modo_treino():
    print("\n📸 MODO GRAVAR TREINO")
    
    # 1. Pede as informações
    caminho_foto = input("Caminho da foto da máquina: ").strip()
    nome_exercicio = input("Nome do exercício (ex: Supino Inclinado): ").strip()
    repeticoes = input("Séries e repetições (ex: 3x10): ").strip()
    descricao = input("Descrição/observação (opcional, aperte Enter para pular): ").strip()
    
    # 2. Analisa a foto com a IA (usando a função que já criamos)
    print("\n🧠 Analisando a máquina...")
    instrucoes_maquina = analisar_maquina(caminho_foto)
    
    if "Erro" in instrucoes_maquina:
        print(f"❌ Falha na análise: {instrucoes_maquina}")
        return

    # 3. Monta o texto completo para a IA gerar o áudio
    texto_treino = f"""
    Exercício: {nome_exercicio}
    Repetições: {repeticoes}
    Instruções da máquina: {instrucoes_maquina}
    """
    
    if descricao:
        texto_treino += f"\nObservação: {descricao}"
        
    # 4. Gera o áudio com o roteiro
    print("\n🎙️ Gerando áudio para o seu pai...")
    sucesso = gerar_audio_ficha(texto_treino, "ficha_treino_hoje.mp3")
    
    if sucesso:
        print("\n✅ Tudo pronto! O áudio 'ficha_treino_hoje.mp3' foi gerado.")
        print("Mande esse arquivo para o seu pai ou dê play nele!")


def main():
    while True:
        print("\n" + "="*40)
        print("🏋️‍♂️  IA PERSONAL TRAINER  🏋️‍♂️")
        print("="*40)
        print("1. Gravar Treino (Foto + Áudio)")
        print("2. Sair")
        
        opcao = input("\nEscolha uma opção: ").strip()
        
        if opcao == "1":
            modo_treino()
        elif opcao == "2":
            print("Bom treino! 👋")
            break
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    main()