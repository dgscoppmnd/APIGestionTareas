from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date
from typing import Optional

class TaskCreate(BaseModel):
    titulo: str = Field(min_length=1, max_length=100, description="Título de la tarea")
    contenido: str = Field(min_length=1, max_length=1000, description="Contenido de la tarea")
    deadline: date = Field(description="Fecha de vencimiento")
    
    @field_validator('deadline')
    def validate_deadline(cls, v):
        if v < date.today():
            raise ValueError('El deadline no puede ser una fecha pasada')
        return v
    
    @field_validator('titulo')
    def validate_titulo(cls, v):
        if not v.strip():
            raise ValueError('El título no puede estar vacío')
        return v.strip()

class TaskUpdate(BaseModel):
    completada: bool = Field(description="Estado de completado")

class TaskResponse(BaseModel):
    id: int
    titulo: str
    contenido: str
    deadline: date
    completada: bool
    fecha_creacion: datetime
    
    class Config:
        from_attributes = True

class TaskFilter(BaseModel):
    completada: Optional[bool] = None
    fecha_desde: Optional[date] = None
    fecha_hasta: Optional[date] = None