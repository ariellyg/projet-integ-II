# Gerador de Receitas Nordestinas com LLMs

Este projeto implementa um sistema de recomendação de receitas nordestinas baseado em Modelos de Linguagem de Grande Escala (LLMs), utilizando tecnologias como **LangChain** e **Groq API**. A aplicação permite ao usuário inserir até 15 ingredientes e receber receitas completas e estruturadas, com:

- Ingredientes organizados por categoria
- Modo de preparo passo a passo
- Tempos estimados por etapa
- Suporte a variações criativas com os mesmos ingredientes

Além disso, o sistema conta com uma interface simplificada construída com **Streamlit**, e faz uso de *role-based prompting* para simular um chef especialista em culinária nordestina.

---

## ⚙️ Requisitos

- Python 3.11+
- Groq API Key
- TavilySearch API Key
- Dependências listadas em `requirements.txt`

---

## 🚀 Como Rodar

1. Clone o repositório:

```bash
git clone git@github.com:ariellyg/projet-integ-II.git
cd src
```

2. Crie e ative um ambiente virtual:

```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Execute a aplicação:

```bash
streamlit run app.py
```

---

📁 Estrutura do Projeto

```
- src/
    ├── structured_outputs/
    │   └── structured_outputs.py   # Processamento do output estruturado
    │
    ├── app.py                      # Interface com Streamlit
    ├── clean_dataset.py            # Limpeza e pré-processamento
- main.py                     # Lógica de inferência e orquestração
- prompt.txt                  # Prompt utilizado pelo modelo
- requirements.txt            # Bibliotecas necessárias
- .gitignore
- README.md
```

Este projeto está licenciado sob a Licença MIT – veja o arquivo LICENSE para mais detalhes.
