import requests
import json
from datetime import datetime, date, timedelta
import time

BASE_URL = "http://localhost:8000"

def print_result(test_name, status_code, expected, response_data=None):
    print(f"{test_name}: Status {status_code} (esperado {expected})")
    if response_data and status_code == expected:
        print(f"   Respuesta: {json.dumps(response_data, indent=2, default=str)[:200]}...")

def test_crear_tarea_valida():
    print("\nProbando POST /tasks/ (Datos válidos)")
    
    # Datos válidos (deadline = mañana)
    manana = (date.today() + timedelta(days=1)).isoformat()
    tarea_valida = {
        "titulo": "Comprar regalo de cumpleaños",
        "contenido": "Recordar comprar un regalo para mamá, #importante #familia",
        "deadline": manana
    }
    
    response = requests.post(f"{BASE_URL}/tasks/", json=tarea_valida)
    print_result("Crear tarea válida", response.status_code, 201, response.json() if response.status_code == 201 else None)
    
    if response.status_code == 201:
        return response.json()["id"]
    return None

def test_crear_tarea_invalida():
    print("\nProbando POST /tasks/ (Datos inválidos - fecha pasada)")
    
    # Datos inválidos (deadline ayer)
    ayer = (date.today() - timedelta(days=1)).isoformat()
    tarea_invalida = {
        "titulo": "Tarea con fecha pasada",
        "contenido": "Esta tarea tiene fecha de ayer",
        "deadline": ayer
    }
    
    response = requests.post(f"{BASE_URL}/tasks/", json=tarea_invalida)
    print_result("Crear tarea inválida", response.status_code, 422, response.json() if response.status_code >= 400 else None)

def test_obtener_tarea(task_id):
    print(f"\nProbando GET /tasks/{task_id}")
    
    response = requests.get(f"{BASE_URL}/tasks/{task_id}")
    print_result("Obtener tarea existente", response.status_code, 200, response.json() if response.status_code == 200 else None)
    
    if response.status_code == 200:
        tarea = response.json()
        print(f"   Título: {tarea['titulo']}")
        print(f"   Completada: {tarea['completada']}")

def test_obtener_tarea_inexistente():
    print("\nProbando GET /tasks/99999 (ID inexistente)")
    
    response = requests.get(f"{BASE_URL}/tasks/99999")
    print_result("Obtener tarea inexistente", response.status_code, 404, response.json() if response.status_code == 404 else None)

def test_marcar_completada(task_id):
    print(f"\nProbando PUT /tasks/{task_id}/completar")
    
    response = requests.put(f"{BASE_URL}/tasks/{task_id}/completar")
    print_result("Marcar como completada", response.status_code, 200, response.json() if response.status_code == 200 else None)

def test_obtener_tareas_caducadas():
    print("\nProbando GET /tasks/caducadas")
    
    response = requests.get(f"{BASE_URL}/tasks/caducadas")
    print_result("Obtener tareas caducadas", response.status_code, 200, response.json() if response.status_code == 200 else None)
    
    if response.status_code == 200:
        print(f"   Total tareas caducadas: {len(response.json())}")

def test_obtener_todas_tareas():
    print("\nProbando GET /tasks?completada=false")
    
    response = requests.get(f"{BASE_URL}/tasks", params={"completada": "false"})
    print_result("Obtener tareas pendientes", response.status_code, 200, response.json() if response.status_code == 200 else None)
    
    if response.status_code == 200:
        print(f"   Total tareas pendientes: {len(response.json())}")

def test_obtener_estadisticas():

    """Solucionado 422 moviendo declaracion end point de main por encima de tasks/1... Buscar info"""

    print("\nProbando GET /tasks/estadisticas")
    
    response = requests.get(f"{BASE_URL}/tasks/estadisticas")
    print_result("Obtener estadísticas", response.status_code, 200, response.json() if response.status_code == 200 else None)
    
    if response.status_code == 200:
        stats = response.json()
        print(f"   Total: {stats['total']}, Completadas: {stats['completadas']}, Pendientes: {stats['pendientes']}")

def test_eliminar_tarea(task_id):
    print(f"\nProbando DELETE /tasks/{task_id}")
    
    response = requests.delete(f"{BASE_URL}/tasks/{task_id}")
    print_result("Eliminar tarea", response.status_code, 204)
    
    # Verificar que ya no existe
    if response.status_code == 204:
        response_get = requests.get(f"{BASE_URL}/tasks/{task_id}")
        if response_get.status_code == 404:
            print("Verificacion: Tarea eliminada correctamente (404 Not Found al intentar obtenerla)")

def run_all_tests():
    print("=" * 60)
    print("INICIANDO PRUEBAS")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Servidor conectado: {response.json()['message']}")
    except requests.exceptions.ConnectionError:
        print("Error: No se puede conectar al servidor")
        print("Debe Ejecutar: uvicorn main:app --reload")
        return
    
    test_crear_tarea_invalida()
    
    task_id = test_crear_tarea_valida()
    
    if task_id:
        test_obtener_tarea(task_id)
        test_marcar_completada(task_id)
        test_obtener_tarea(task_id)
        test_obtener_tareas_caducadas()
        test_obtener_todas_tareas()
        test_obtener_estadisticas()
        test_eliminar_tarea(task_id)
    
    test_obtener_tarea_inexistente()
    
    print("\n" + "=" * 60)
    print("PRUEBAS COMPLETADAS")
    print("=" * 60)

if __name__ == "__main__":
    run_all_tests()