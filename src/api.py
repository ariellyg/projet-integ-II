from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.main import carregar_prompt, gerar_receita_com_groq_json
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Gerador de Receitas com IA")

# Libera o CORS para frontend local ou hospedado
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Coloque aqui o domínio do seu frontend em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class IngredientesRequest(BaseModel):
    ingredientes: str

@app.post("/gerar-receita")
async def gerar_receita(req: IngredientesRequest):
    ingredientes = req.ingredientes
    ingredientes_lista = [i.strip() for i in ingredientes.split(",") if i.strip()]

    if len(ingredientes_lista) < 2:
        raise HTTPException(status_code=400, detail="Insira pelo menos 2 ingredientes.")
    if len(ingredientes_lista) > 15:
        raise HTTPException(status_code=400, detail="Insira no máximo 15 ingredientes.")

    try:
        prompt_base = carregar_prompt("prompt.txt")
        ingredientes_formatados = ", ".join(ingredientes_lista)
        receita = gerar_receita_com_groq_json(ingredientes_formatados, prompt_base)
        return {"receita": receita}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar receita: {str(e)}")

# Execução local (opcional)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
