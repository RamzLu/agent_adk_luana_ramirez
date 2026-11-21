import os
from ddgs import DDGS

# Ruta absoluta: la carpeta de apuntes queda siempre en la raíz del proyecto,
# sin importar desde dónde se ejecute `adk web`.
NOTES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "apuntes_guardados")


def _normalizar_nombre(titulo: str) -> str:
    """
    Convierte un título en un nombre de archivo seguro (sin extensión).
    Se usa tanto al guardar como al consultar, para que ambos coincidan.
    Devuelve "" si el título no contiene ningún carácter válido.
    """
    titulo = titulo.strip()
    if titulo.lower().endswith(".txt"):
        titulo = titulo[:-4]
    limpio = "".join(c for c in titulo if c.isalnum() or c in (" ", "_", "-"))
    return "_".join(limpio.split()).lower()


def buscar_en_web(query: str, max_results: int = 5) -> str:
    """
    Herramienta para realizar búsquedas en internet en tiempo real utilizando DuckDuckGo.

    Args:
        query: str -> La consulta o término que se desea investigar en internet.
        max_results: int -> Cantidad máxima de resultados a devolver (entre 1 y 10).
    """
    try:
        if not query or not str(query).strip():
            return "Error de validación: La consulta no puede estar vacía."

        try:
            limite = int(max_results) if max_results else 5
        except (TypeError, ValueError):
            limite = 5
        limite = max(1, min(limite, 10))

        results = DDGS().text(query=str(query).strip(), max_results=limite)

        if not results:
            return f"No se encontraron resultados en internet para: '{query}'."

        lineas = [f"Resultados de búsqueda para '{query}':"]
        for i, r in enumerate(results, start=1):
            lineas.append(
                f"{i}. {r.get('title', 'Sin título')}\n"
                f"   URL: {r.get('href', '')}\n"
                f"   {r.get('body', '')}"
            )
        return "\n".join(lineas)
    except Exception as e:
        print("Error interno al utilizar la herramienta:", e)
        return f"Error al buscar en la web: {str(e)}"


def guardar_apunte(titulo: str, contenido: str, sobrescribir: bool = False) -> str:
    """
    Herramienta para guardar un apunte, resumen o nota de estudio en un archivo de texto local.

    Args:
        titulo: str -> Nombre o título del apunte (ej. 'redes_neuronales').
        contenido: str -> El texto o información detallada que se desea guardar.
        sobrescribir: bool -> Si es True, reemplaza un apunte existente con el mismo título.
                              Por defecto es False y no se pisa un apunte existente.
    """
    try:
        if not titulo or not str(titulo).strip():
            return "Error de validación: El título del apunte no puede estar vacío."
        if not contenido or len(str(contenido).strip()) < 10:
            return "Error de validación: El contenido es demasiado corto o está vacío (mínimo 10 caracteres)."

        nombre = _normalizar_nombre(str(titulo))
        if not nombre:
            return "Error de validación: El título debe contener al menos una letra o número."

        os.makedirs(NOTES_DIR, exist_ok=True)
        nombre_archivo = nombre + ".txt"
        ruta_completa = os.path.join(NOTES_DIR, nombre_archivo)

        if os.path.exists(ruta_completa) and not sobrescribir:
            return (
                f"Aviso: Ya existe un apunte llamado '{nombre_archivo}'. "
                "No se modificó. Pregunta al usuario si desea reemplazarlo "
                "(sobrescribir=True) o usar otro título."
            )

        with open(ruta_completa, "w", encoding="utf-8") as f:
            f.write(str(contenido).strip())

        return f"Éxito: Apunte guardado correctamente como '{nombre_archivo}'."
    except Exception as e:
        return f"Error interno al guardar el apunte: {str(e)}"


def consultar_apuntes(titulo: str = "") -> str:
    """
    Herramienta para listar todos los apuntes guardados o leer el contenido de un apunte específico.

    Args:
        titulo: str -> (Opcional) Nombre del apunte a leer. Si se deja vacío (""), devuelve la lista de todos los apuntes disponibles.
    """
    try:
        if not os.path.exists(NOTES_DIR):
            return "Aún no existen apuntes guardados (el directorio no fue creado)."

        archivos = sorted(f for f in os.listdir(NOTES_DIR) if f.endswith(".txt"))

        if not archivos:
            return "No hay ningún apunte guardado actualmente."

        if not titulo or not str(titulo).strip():
            return f"Apuntes disponibles ({len(archivos)}): {', '.join(archivos)}"

        # La misma normalización que al guardar: evita rutas como '../' y
        # garantiza que el nombre coincida con el archivo guardado.
        nombre = _normalizar_nombre(str(titulo))
        if not nombre:
            return f"Error de validación: Título inválido. Los apuntes disponibles son: {', '.join(archivos)}"

        busqueda = nombre + ".txt"
        if busqueda not in archivos:
            return f"No se encontró el apunte '{busqueda}'. Los apuntes disponibles son: {', '.join(archivos)}"

        with open(os.path.join(NOTES_DIR, busqueda), "r", encoding="utf-8") as f:
            contenido = f.read()

        if not contenido.strip():
            return f"El apunte '{busqueda}' existe pero está vacío."

        return f"Contenido de '{busqueda}':\n{contenido}"
    except Exception as e:
        return f"Error interno al consultar apuntes: {str(e)}"


def calcular_estado_academico(notas: list[float], nota_aprobacion: float = 6.0) -> str:
    """
    Herramienta para calcular el promedio de calificaciones de un estudiante y determinar su estado académico.

    Args:
        notas: list[float] -> Lista de calificaciones numéricas (entre 1 y 10).
        nota_aprobacion: float -> Nota mínima requerida para aprobar (por defecto 6.0).
    """
    try:
        # Algunos modelos envían las notas como texto ("7, 8, 9"): se convierten a lista.
        if isinstance(notas, str):
            notas = [n for n in notas.replace(";", ",").split(",") if n.strip()]

        if not notas or not isinstance(notas, list):
            return "Error de validación: Debes proporcionar una lista con al menos una calificación."

        if isinstance(nota_aprobacion, bool):
            return "Error de validación: La nota de aprobación debe ser un número."
        nota_aprobacion = float(nota_aprobacion)
        if nota_aprobacion < 1 or nota_aprobacion > 10:
            return "Error de validación: La nota de aprobación debe estar entre 1 y 10."

        notas_validas = []
        for n in notas:
            if isinstance(n, bool):
                return f"Error de validación: '{n}' no es una calificación válida."
            valor = float(str(n).strip().replace(",", ".")) if isinstance(n, str) else float(n)
            if valor < 1 or valor > 10:
                return f"Error de validación: La calificación '{valor}' es inválida. Todas las notas deben estar entre 1 y 10."
            notas_validas.append(valor)

        promedio = round(sum(notas_validas) / len(notas_validas), 2)
        estado = "APROBADO" if promedio >= nota_aprobacion else "DESAPROBADO"

        return (
            f"Resultado del cálculo:\n"
            f"- Cantidad de evaluaciones: {len(notas_validas)}\n"
            f"- Calificaciones: {notas_validas}\n"
            f"- Nota mínima de aprobación: {nota_aprobacion}\n"
            f"- Promedio final: {promedio}\n"
            f"- Estado: {estado}"
        )
    except (TypeError, ValueError):
        return "Error de validación: Todos los elementos de la lista de notas deben ser números válidos."
    except Exception as e:
        return f"Error interno al calcular el promedio: {str(e)}"
