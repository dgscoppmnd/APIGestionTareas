from datetime import datetime, date
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
import re
from database import SessionLocal, TaskModel
from models import TaskCreate, TaskUpdate, TaskResponse

class TextProcessor:
    """Simulación logica de negocio"""
    def __init__(self):
        self._palabras_prohibidas = {
            'gilipollas', 'capullo', 'capulla', 'null'
        }
    
    def _censurar_palabras(self, texto: str) -> str:
        palabras = texto.split()
        palabras_censuradas = []
        
        for palabra in palabras:
            palabra_lower = palabra.lower().strip('.,!?;:')
            if palabra_lower in self._palabras_prohibidas:
                palabras_censuradas.append('*' * len(palabra))
            else:
                palabras_censuradas.append(palabra)
        
        return ' '.join(palabras_censuradas)
    
    def limpiar_texto(self, texto: str) -> str:
        if not texto:
            return texto
        
        texto = self._censurar_palabras(texto)
        return texto


class DateValidator:
    """Gestor de fechas"""
    @staticmethod
    def es_fecha_valida(fecha: date) -> bool:
        hoy = date.today()
        diferencia = (fecha - hoy).days
        return diferencia <= 365 
    
    @staticmethod
    def esta_caducada(fecha: date) -> bool:
        return fecha < date.today()
    
    @staticmethod
    def dias_restantes(fecha: date) -> int:
        return (fecha - date.today()).days

class TaskManager:  
    """Logica endPoints""" 
    def __init__(self):
        self._text_processor = TextProcessor()
        self._date_validator = DateValidator()
        self._db: Optional[Session] = None
    
    def _get_db(self) -> Session:
        if not self._db:
            self._db = SessionLocal()
        return self._db
    
    def _cerrar_db(self):
        if self._db:
            self._db.close()
            self._db = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cerrar_db()
    
    def crear_tarea(self, task_data: TaskCreate) -> TaskResponse:
        db = self._get_db()
        
        titulo_limpio = self._text_processor.limpiar_texto(task_data.titulo)
        contenido_limpio = self._text_processor.limpiar_texto(task_data.contenido)
        
        if not self._date_validator.es_fecha_valida(task_data.deadline):
            raise ValueError("La fecha de vencimiento debe ser dentro del próximo año")
        
        db_task = TaskModel(
            titulo=titulo_limpio,
            contenido=contenido_limpio,
            deadline=task_data.deadline,
            completada=False
        )
        
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        
        return TaskResponse.model_validate(db_task)
    
    def obtener_tarea(self, task_id: int) -> Optional[TaskResponse]:
        db = self._get_db()
        task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
        
        if task:
            return TaskResponse.model_validate(task)
        return None
    
    def marcar_completada(self, task_id: int) -> Optional[TaskResponse]:
        db = self._get_db()
        task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
        
        if not task:
            return None
        
        task.completada = True
        task.fecha_actualizacion = datetime.now()
        db.commit()
        db.refresh(task)
        
        return TaskResponse.model_validate(task)
    
    def obtener_tareas_caducadas(self) -> List[TaskResponse]:
        db = self._get_db()
        hoy = date.today()
        
        tasks = db.query(TaskModel).filter(
            TaskModel.deadline < hoy,
            TaskModel.completada == False
        ).all()
        
        return [TaskResponse.model_validate(task) for task in tasks]
    
    def obtener_todas_tareas(self, filtros: Optional[Dict] = None) -> List[TaskResponse]:
        db = self._get_db()
        query = db.query(TaskModel)
        
        if filtros:
            if filtros.get('completada') is not None:
                query = query.filter(TaskModel.completada == filtros['completada'])
            if filtros.get('fecha_desde'):
                query = query.filter(TaskModel.deadline >= filtros['fecha_desde'])
            if filtros.get('fecha_hasta'):
                query = query.filter(TaskModel.deadline <= filtros['fecha_hasta'])
        
        tasks = query.order_by(TaskModel.deadline).all()
        return [TaskResponse.model_validate(task) for task in tasks]
    
    def eliminar_tarea(self, task_id: int) -> bool:
        db = self._get_db()
        task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
        
        if not task:
            return False
        
        db.delete(task)
        db.commit()
        return True
    
    def obtener_estadisticas(self) -> Dict:
        db = self._get_db()
        hoy = date.today()
        
        total = db.query(TaskModel).count()
        completadas = db.query(TaskModel).filter(TaskModel.completada == True).count()
        pendientes = total - completadas
        caducadas = db.query(TaskModel).filter(
            TaskModel.deadline < hoy,
            TaskModel.completada == False
        ).count()
        
        fecha_limite = date.fromordinal(hoy.toordinal() + 7)
        proximas = db.query(TaskModel).filter(
            TaskModel.deadline >= hoy,
            TaskModel.deadline <= fecha_limite,
            TaskModel.completada == False
        ).count()
        
        return {
            "total": total,
            "completadas": completadas,
            "pendientes": pendientes,
            "caducadas": caducadas,
            "proximas_a_vencer": proximas
        }