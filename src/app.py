import streamlit as st
import json
from main import carregar_prompt, gerar_receita_com_groq_json

st.set_page_config(page_title="Gerador de Receitas Inteligente", layout="centered")

st.title("🍳 Gerador de Receitas com IA")
st.markdown("""
Digite os ingredientes disponíveis, separados por vírgula.  
A IA irá gerar uma receita segura e clara com base no que você tem em casa!
""")

ingredientes_input = st.text_input("🧺 Ingredientes (ex: arroz, cenoura, frango)", "")

# Lista de ingredientes tratados
ingredientes_lista = [i.strip() for i in ingredientes_input.split(",") if i.strip()]
qtd_ingredientes = len(ingredientes_lista)

# Mostra contador dinâmico
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
                receita = gerar_receita_com_groq_json(ingredientes_formatados, prompt_base)

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

                # Exibe também o JSON bruto se o usuário quiser
                # with st.expander("📦 Ver JSON"):
                #     st.json(receita)

            except Exception as e:
                st.error(f"❌ Erro ao gerar a receita: {str(e)}")
