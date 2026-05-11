from pydantic import BaseModel, conint, constr, Field
from typing import Optional, List
from enum import Enum


class Categoria(str, Enum):
    coding = "coding"
    meeting = "meeting"
    estudo = "estudo"
    outros = "outros"


class RegistroIn(BaseModel):
    nivel_foco: conint(ge=1, le=5) = Field(..., description="Nível de foco de 1 (muito distraído) a 5 (flow)")
    tempo_minutos: conint(gt=0) = Field(..., description="Duração da sessão em minutos, inteiro positivo")
    comentario: constr(min_length=3, max_length=1000) = Field(..., description="Breve comentário sobre a sessão")
    categoria: Optional[Categoria] = Field(None, description="Categoria da sessão (coding, meeting, estudo, outros)")
    tags: Optional[List[constr(strip_whitespace=True, min_length=1)]] = Field(None, description="Lista opcional de tags")


class RegistroOut(BaseModel):
    id: int
    nivel_foco: int
    tempo_minutos: int
    comentario: str
    categoria: Optional[Categoria]
    tags: Optional[List[str]]
    created_at: str


class TopCategoria(BaseModel):
    categoria: str
    tempo_minutos: int


class DiagnosticoOut(BaseModel):
    media_nivel_foco: Optional[float]
    tempo_total_minutos: int
    registros: int
    mensagem: str
    top_categorias_por_tempo: List[TopCategoria] = []
