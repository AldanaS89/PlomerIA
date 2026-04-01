from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def inicio():
    return {
        "estado": "¡Funcionando desde San José City!",
        "proyecto": "PlomerIA - Grupo 3",
        "mensaje": "Si ves esto, Aldana, el setup fue un éxito total"
    }