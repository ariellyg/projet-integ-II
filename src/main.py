from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv
from structured_outputs.structured_outputs import Receita
from pydantic import ValidationError
import json
import re

load_dotenv()

# 1. Carrega o prompt base de um arquivo .txt
def carregar_prompt(caminho: str) -> str:
    with open(caminho, 'r', encoding='utf-8') as arquivo:
        return arquivo.read()

# 2. Extrai JSON dentro de blocos markdown caso necessário
def extrair_json_fallback(texto: str) -> dict:
    try:
        if "```json" in texto:
            texto = texto.split("```json")[1].split("```")[0].strip()
        elif "```" in texto:
            texto = texto.split("```")[1].strip()

        match = re.search(r'{.*}', texto, re.DOTALL)
        if match:
            return json.loads(match.group())
    except json.JSONDecodeError:
        pass
    return None

# 3. Busca na web receitas com ingredientes dados
def buscar_receitas_na_web(ingredientes: str, k: int = 3) -> str:
    search = TavilySearchResults(max_results=k)
    resultados = search.run(f"Receitas do Nordeste do Brasil **apenas** com os ingredientes: {ingredientes}")

    if not resultados:
        return "Nenhum resultado encontrado."

    # Se for uma lista de strings
    if isinstance(resultados, list) and all(isinstance(r, str) for r in resultados):
        return "\n\n".join(resultados)

    # Se for lista de dicts (ex: com title/url/snippet)
    if isinstance(resultados, list) and isinstance(resultados[0], dict):
        linhas = []
        for r in resultados:
            titulo = r.get("title", "Sem título")
            snippet = r.get("snippet", "")
            url = r.get("url", "")
            linhas.append(f"**{titulo}**\n{snippet}\n🔗 {url}")
        return "\n\n".join(linhas)

    return str(resultados)  # fallback

# 4. Gera a receita com integração com web + Pydantic fallback robusto
def gerar_receita_com_groq_json(ingredientes: str, prompt_base: str) -> dict:
    web_results = buscar_receitas_na_web(ingredientes)

    prompt_formatado = (
        prompt_base
        .replace("{{resultados_web}}", web_results)
        .replace("{{ingredientes}}", ingredientes)
        + "\n\nPor favor, responda apenas no formato JSON válido conforme estrutura."
    )

    llm = ChatGroq(model="gemma2-9b-it", temperature=1.2, max_retries=2)
    parser = PydanticOutputParser(pydantic_object=Receita)

    chain = RunnableLambda(lambda _: prompt_formatado) | llm | parser

    try:
        resultado: Receita = chain.invoke({})
        return resultado.model_dump(by_alias=True)
    except ValidationError as ve:
        print("⚠️ Falha na validação do Pydantic direto. Tentando fallback...")
    except Exception as e:
        print(f"⚠️ Erro no chain.invoke(): {e}. Tentando fallback...")

    resposta_bruta = llm.invoke(prompt_formatado)
    texto = getattr(resposta_bruta, "content", str(resposta_bruta))
    receita_dict = extrair_json_fallback(texto)

    if receita_dict:
        try:
            receita = Receita(**receita_dict)
            print("✅ Fallback validado com sucesso!")
            return receita.model_dump(by_alias=True)
        except ValidationError as e:
            raise RuntimeError(f"❌ Fallback falhou na validação: {e}")
    else:
        raise RuntimeError("❌ Falha total: não foi possível extrair JSON.")

# 5. Execução direta
if __name__ == "__main__":
    caminho_prompt = "prompt.txt"
    ingredientes_usuario = input("Digite os ingredientes separados por vírgula: ")
    prompt_base = carregar_prompt(caminho_prompt)

    try:
        receita_json = gerar_receita_com_groq_json(ingredientes_usuario, prompt_base)
        print("\n🍽️ Receita Gerada (JSON):")
        print(json.dumps(receita_json, indent=2, ensure_ascii=False))
    except Exception as e:
        print("\n❌ Erro ao gerar a receita:")
        print(e)
