from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Literal
import re

class Ingredientes(BaseModel):
    principais: List[str] = Field(description="Ingredientes principais da receita")
    condimentos: List[str] = Field(description="Temperos e condimentos usados")

class Receita(BaseModel):
    descricao: str = Field(alias="Descrição", description="Breve descrição da receita")
    ingredientes: Ingredientes = Field(alias="Ingredientes", description="Ingredientes divididos por tipo")
    modo_de_preparo: Dict[str, str] = Field(alias="Modo de preparo", description="Passos numerados do preparo")
    tempo_de_preparo: str = Field(alias="Tempo de preparo", description="Tempo estimado de preparo")

    @field_validator("tempo_de_preparo")
    @classmethod
    def tempo_de_preparo_deve_ter_unidade(cls, v):
        if not isinstance(v, str):
            raise TypeError("O tempo de preparo deve ser uma string")
    
        if not re.search(r"\d+\s*(minutos|min|h|horas|dia|dias|minuto|hora|segundo|segundos)", v.lower()):
            raise ValueError("O tempo de preparo deve conter uma unidade, como 'minutos' ou 'horas'")
        return v

    @field_validator("modo_de_preparo")
    @classmethod
    def modo_de_preparo_deve_ter_ordem(cls, v):
        if not v:
            raise ValueError("O modo de preparo não pode estar vazio")
        
        try:
            passos = sorted(int(k) for k in v.keys())
            if passos != list(range(len(passos))):
                raise ValueError("As etapas do modo de preparo devem começar de 0 e ser sequenciais")
        except Exception:
            raise ValueError("As chaves do modo de preparo devem ser números sequenciais (0, 1, 2...)")
        return v

    class Config:
        populate_by_name = True  # permite usar alias nos dados JSON

class RespostaBinaria(BaseModel):
    content: Literal["SIM", "NÃO"]
