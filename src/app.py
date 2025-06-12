import streamlit as st
import json
from main import carregar_prompt, gerar_receita_com_groq_json  # importa sua lógica

st.set_page_config(page_title="Gerador de Receitas Inteligente", layout="centered")

st.title("🍳 Gerador de Receitas com IA")
st.markdown("""
Digite os ingredientes disponíveis, separados por vírgula. 
A IA irá gerar uma receita segura e clara com base no que você tem em casa!
""")

ingredientes_input = st.text_input("🧺 Ingredientes (ex: arroz, cenoura, frango)", "")

if st.button("Gerar Receita"):
    if not ingredientes_input.strip():
        st.warning("Por favor, insira pelo menos um ingrediente.")
    else:
        with st.spinner("Gerando receita com IA..."):
            try:
                prompt_base = carregar_prompt("prompt.txt")
                receita = gerar_receita_com_groq_json(ingredientes_input, prompt_base)

                st.success("✅ Receita gerada com sucesso!")
                st.subheader("📖 Descrição")
                st.write(receita["Descrição"])

                st.subheader("🧂 Ingredientes")
                st.write("\n".join(f"- {ing}" for ing in receita["Ingredientes"]))

                st.subheader("👩‍🍳 Modo de preparo")
                for i, passo in enumerate(receita["Modo de preparo"], 1):
                    st.markdown(f"**{i}.** {passo}")

                st.subheader(f"⏱️ Tempo de preparo: {receita['Tempo de preparo']}")

                # Exibe também o JSON bruto se o usuário quiser
                with st.expander("📦 Ver JSON"):
                    st.json(receita)

            except Exception as e:
                st.error(f"Erro ao gerar a receita: {str(e)}")
