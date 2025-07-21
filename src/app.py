import streamlit as st
import json
from main import carregar_prompt, gerar_receita_com_groq_json, buscar_receitas_na_web

st.set_page_config(page_title="Gerador de Receitas Inteligente", layout="centered")

st.title("🍳 Gerador de Receitas com IA")
st.markdown("""
Digite os ingredientes disponíveis, separados por vírgula.  
A IA irá gerar uma receita segura e clara com base no que você tem em casa!
""")

ingredientes_input = st.text_input("🧺 Ingredientes (ex: arroz, cenoura, frango)", "")
ingredientes_lista = [i.strip() for i in ingredientes_input.split(",") if i.strip()]
qtd_ingredientes = len(ingredientes_lista)
st.session_state["ingredientes_originais"] = ingredientes_lista

estados = ["", "Maranhão",  "Piauí", "Ceará", "Rio Grande do Norte", "Paraíba",
            "Pernambuco", "Alagoas",  "Sergipe", "Bahia"]

estado_escolhido = st.selectbox("🌍 Deseja focar em um estado brasileiro?", estados)

if "receitas" not in st.session_state:
    st.session_state.receitas = []
if "resultados_web" not in st.session_state:
    st.session_state.resultados_web = None

if ingredientes_input.strip():
    if qtd_ingredientes < 2:
        st.markdown(f"🔴 Ingredientes inseridos: **{qtd_ingredientes}** (mínimo: 2)")
    elif qtd_ingredientes > 15:
        st.markdown(f"🔴 Ingredientes inseridos: **{qtd_ingredientes}** (máximo: 15)")
    elif 2 <= qtd_ingredientes <= 4:
        st.markdown(f"🟡 Ingredientes inseridos: **{qtd_ingredientes}** (poucos, mas aceitáveis)")
    else:
        st.markdown(f"🟢 Ingredientes inseridos: **{qtd_ingredientes}** ✅")

if st.button("Gerar Receita"):
    if not ingredientes_lista:
        st.warning("Por favor, insira pelo menos um ingrediente.")
    elif qtd_ingredientes < 2:
        st.warning("Insira pelo menos **2 ingredientes**.")
    elif qtd_ingredientes > 15:
        st.warning("Insira no máximo **15 ingredientes**.")
    else:
        with st.spinner("Gerando receita com IA..."):
            try:
                prompt_base = carregar_prompt("prompt.txt")
                ingredientes_formatados = ", ".join(ingredientes_lista)

                if estado_escolhido:
                    prompt_base += f"\n\nCrie uma nova receita típica ou criativa do estado: {estado_escolhido}."

                # Busca na web uma única vez
                if st.session_state.resultados_web is None:
                    st.session_state.resultados_web = buscar_receitas_na_web(ingredientes_formatados, estado_escolhido)

                receita = gerar_receita_com_groq_json(
                    ingredientes_formatados,
                    prompt_base.replace("{{resultados_web}}", st.session_state.resultados_web)
                )

                st.session_state.receitas.append(receita)

            except Exception as e:
                st.error(f"❌ Erro ao gerar a receita: {str(e)}")

if st.session_state.receitas:
    receita = st.session_state.receitas[-1]

    st.success("✅ Receita gerada com sucesso!")
    st.subheader("📖 Descrição")
    st.write(receita["Descrição"])

    st.subheader("🧂 Ingredientes")
    principais = receita["Ingredientes"]["principais"]
    condimentos = receita["Ingredientes"]["condimentos"]

    st.markdown("**Principais:**")
    st.write("\n".join(f"- {ing}" for ing in principais))

    st.markdown("**Condimentos:**")
    st.write("\n".join(f"- {ing}" for ing in condimentos))

    st.subheader("👩‍🍳 Modo de preparo")
    passos_dict = receita["Modo de preparo"]
    for i in sorted(passos_dict.keys(), key=lambda x: int(x)):
        st.markdown(f"**{int(i) + 1}.** {passos_dict[i]}")

    st.subheader(f"⏱️ Tempo de preparo")
    st.write(receita["Tempo de preparo"])

    if st.button("🔄 Gerar outra receita com os mesmos ingredientes"):
        with st.spinner("Gerando nova receita..."):
            try:
                prompt_base = carregar_prompt("prompt.txt")
                if estado_escolhido:
                    prompt_base += f"\n\nCrie uma nova receita típica ou criativa do estado {estado_escolhido}."

                novo_prompt = prompt_base + f"\n Tente criar uma receita diferente dessa: {receita}\n Mas com base nos mesmos ingredientes."
                nova_receita = gerar_receita_com_groq_json(
                    ", ".join(ingredientes_lista),
                    novo_prompt.replace("{{resultados_web}}", st.session_state.resultados_web)
                )
                st.session_state.receitas.append(nova_receita)
            except Exception as e:
                st.error(f"❌ Erro ao gerar nova receita: {str(e)}")

st.subheader("🔁 Trocar Ingrediente")

ingrediente_para_trocar = st.selectbox(
    "Escolha um ingrediente para substituir:",
    st.session_state["ingredientes_originais"]
)

novo_ingrediente = st.text_input("Digite o novo ingrediente que deseja usar:")

if st.button("♻️ Substituir ingrediente e gerar nova receita"):
    nova_lista = [
        novo_ingrediente if ing == ingrediente_para_trocar else ing
        for ing in st.session_state["ingredientes_originais"]
    ]

    with st.spinner("Gerando nova receita com ingrediente substituído..."):
        try:
            prompt_base = carregar_prompt("prompt.txt")

            if estado_escolhido:
                prompt_base += f"\n\nCrie uma nova receita típica ou criativa do estado {estado_escolhido}."

            ingredientes_novos = ", ".join(nova_lista)
            nova_receita = gerar_receita_com_groq_json(
                ingredientes_novos,
                prompt_base.replace("{{resultados_web}}", st.session_state.resultados_web)
            )

            st.session_state.receitas.append(nova_receita)
            st.session_state["ingredientes_originais"] = nova_lista

        except Exception as e:
            st.error(f"❌ Erro ao gerar nova receita com ingrediente substituído: {str(e)}")