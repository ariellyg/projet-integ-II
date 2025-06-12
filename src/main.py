from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableLambda, RunnableSequence
from dotenv import load_dotenv
import json
import re

load_dotenv()

# 1. Carrega o prompt base de um arquivo .txt
def carregar_prompt(caminho: str) -> str:
    with open(caminho, 'r', encoding='utf-8') as arquivo:
        return arquivo.read()

# 2. Tenta extrair o primeiro JSON válido de um texto bruto
def extrair_json_fallback(texto: str) -> dict:
    try:
        match = re.search(r'{.*}', texto, re.DOTALL)
        if match:
            return json.loads(match.group())
    except json.JSONDecodeError:
        pass
    return None

# 3. Valida se o JSON contém os campos esperados
def validar_campos_esperados(receita: dict) -> bool:
    campos = {"Descrição", "Ingredientes", "Modo de preparo", "Tempo de preparo"}
    return isinstance(receita, dict) and campos.issubset(set(receita.keys()))

# 4. Gera a receita com Groq e aplica fallback e validação
def gerar_receita_com_groq_json(ingredientes: str, prompt_base: str) -> dict:
    # Formata o prompt
    prompt_formatado = prompt_base.replace("{{ingredientes}}", ingredientes)
    prompt_formatado += "\n\nPor favor, responda apenas no formato JSON válido."

    # Inicializa modelo e parser
    llm = ChatGroq(model="gemma2-9b-it", temperature=0.7, max_retries=2)
    parser = JsonOutputParser()

    # Define a cadeia de execução
    chain = (
        RunnableLambda(lambda _: prompt_formatado)
        | llm
        | parser
    )

    try:
        resultado = chain.invoke({})
        if validar_campos_esperados(resultado):
            return resultado
        else:
            raise ValueError("JSON não contém os campos esperados.")
    except Exception as e:
        print("⚠️ Falha na análise direta como JSON. Tentando fallback...")
        # fallback: executa modelo bruto e tenta regex manual
        resposta_bruta = llm.invoke(prompt_formatado)
        receita_fallback = extrair_json_fallback(resposta_bruta)
        if receita_fallback and validar_campos_esperados(receita_fallback):
            print("✅ Fallback foi bem-sucedido.")
            return receita_fallback
        else:
            raise RuntimeError("Falha completa ao obter JSON válido.")

# 5. Execução principal
if __name__ == "__main__":
    caminho_prompt = "prompt.txt"
    ingredientes_usuario = input("Digite os ingredientes separados por vírgula: ")

    prompt_base = carregar_prompt(caminho_prompt)

    try:
        receita_json = gerar_receita_com_groq_json(ingredientes_usuario, prompt_base)
        print("\n🍽️ Receita Gerada (JSON):\n")
        print(json.dumps(receita_json, indent=2, ensure_ascii=False))

    except Exception as e:
        print("\n❌ Erro ao gerar ou interpretar a receita:")
        print(str(e))