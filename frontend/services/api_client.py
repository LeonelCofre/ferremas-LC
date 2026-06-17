"""Cliente HTTP hacia el Backend API. Aísla las llamadas REST del resto del front.
Si el backend no está disponible, devuelve (None, mensaje) para degradar la UI."""
import requests
from flask import current_app


def _url(path):
    return f"{current_app.config['BACKEND_URL']}{path}"


def _get(path, params=None):
    try:
        r = requests.get(_url(path), params=params, timeout=6)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.RequestException as e:
        return None, f"El servicio no está disponible ({e.__class__.__name__})"


def _post(path, payload):
    try:
        r = requests.post(_url(path), json=payload, timeout=8)
        data = r.json() if r.content else {}
        if r.status_code >= 400:
            return None, data.get("error", f"Error {r.status_code}")
        return data, None
    except requests.exceptions.RequestException as e:
        return None, f"El servicio no está disponible ({e.__class__.__name__})"


# --- atajos ---
def categorias():       return _get("/api/categorias")
def productos(cat=None): return _get("/api/productos", {"categoria_id": cat} if cat else None)
def producto(pid):      return _get(f"/api/productos/{pid}")
def login(usuario, pw): return _post("/api/auth/login", {"usuario": usuario, "password": pw})
def registrar(payload): return _post("/api/clientes", payload)
def suscribir(correo):  return _post("/api/suscripcion", {"correo": correo})
def cotizar(items):     return _post("/api/cotizar", {"items": items})
def crear_pedido(p):    return _post("/api/pedidos", p)
def webpay_iniciar(p):  return _post("/api/pagos/webpay/iniciar", p)
def webpay_confirmar(p):return _post("/api/pagos/webpay/confirmar", p)
def transferencia(p):   return _post("/api/pagos/transferencia", p)
def divisa(moneda, monto): return _get("/api/divisa", {"moneda": moneda, "monto": monto})
