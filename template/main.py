from fastapi import FastAPI, HTTPException, status, Query, Depends
from datetime import date
from typing import List, Optional
from models import TaskCreate, TaskUpdate, TaskResponse, TaskFilter
from services import TaskManager

app = FastAPI(title="Task Management API", version="1.0.0")

def get_task_manager():
    with TaskManager() as manager:
        yield manager

@app.get("/")
def root():
    return {
        "message": "Task Management API",
        "version": "1.0.0",
        "endpoints": {
            "POST /tasks/": "Crear nueva tarea",
            "GET /tasks/{task_id}": "Obtener tarea por ID",
            "PUT /tasks/{task_id}/completar": "Marcar tarea como completada",
            "GET /tasks/caducadas": "Listar tareas caducadas",
            "GET /tasks": "Listar todas las tareas (con filtros)",
            "DELETE /tasks/{task_id}": "Eliminar tarea",
            "GET /tasks/estadisticas": "Obtener estadísticas"
        }
    }

@app.post("/tasks/", 
          response_model=TaskResponse, 
          status_code=status.HTTP_201_CREATED,
          summary="Crear una nueva tarea",
          description="Crea una nueva tarea con título, contenido y fecha de vencimiento")
def crear_tarea(task: TaskCreate, manager: TaskManager = Depends(get_task_manager)):
    try:
        return manager.crear_tarea(task)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.get("/tasks/caducadas", 
         response_model=List[TaskResponse],
         summary="Listar tareas caducadas")
def obtener_tareas_caducadas(manager: TaskManager = Depends(get_task_manager)):
    return manager.obtener_tareas_caducadas()

@app.get("/tasks/estadisticas", 
         summary="Obtener estadísticas de tareas")
def obtener_estadisticas(manager: TaskManager = Depends(get_task_manager)):
    return manager.obtener_estadisticas()

@app.get("/tasks/{task_id}", 
         response_model=TaskResponse,
         summary="Obtener tarea por ID",
         responses={404: {"description": "Tarea no encontrada"}})
def obtener_tarea(task_id: int, manager: TaskManager = Depends(get_task_manager)):
    task = manager.obtener_tarea(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tarea con ID {task_id} no encontrada"
        )
    return task

@app.put("/tasks/{task_id}/completar", 
         response_model=TaskResponse,
         summary="Marcar tarea como completada")
def marcar_completada(task_id: int, manager: TaskManager = Depends(get_task_manager)):
    task = manager.marcar_completada(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tarea con ID {task_id} no encontrada"
        )
    return task

@app.get("/tasks", 
         response_model=List[TaskResponse],
         summary="Listar todas las tareas con filtros")
def obtener_todas_tareas(
    completada: Optional[bool] = Query(None, description="Filtrar por estado de completado"),
    fecha_desde: Optional[date] = Query(None, description="Fecha de vencimiento desde"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha de vencimiento hasta"),
    manager: TaskManager = Depends(get_task_manager)):
    filtros = {}
    if completada is not None:
        filtros['completada'] = completada
    if fecha_desde:
        filtros['fecha_desde'] = fecha_desde
    if fecha_hasta:
        filtros['fecha_hasta'] = fecha_hasta
    
    return manager.obtener_todas_tareas(filtros)

@app.delete("/tasks/{task_id}", 
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Eliminar una tarea")
def eliminar_tarea(task_id: int, manager: TaskManager = Depends(get_task_manager)):
    eliminada = manager.eliminar_tarea(task_id)
    if not eliminada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tarea con ID {task_id} no encontrada"
        )
    return None


"""TO DO: realizar metodos de actualizacion de tareas"""
