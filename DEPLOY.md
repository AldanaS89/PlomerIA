# 🚀 Deploy de PlomerIA (servidor propio + Cloudflare Tunnel)

Guía para publicar **backend (FastAPI) + frontend (React)** en tu Ubuntu Server
usando Docker y un **Cloudflare Tunnel** (sin abrir puertos en el router, sin
exponer tu IP de casa, con HTTPS automático).

> Las apps móviles (`app_cliente`, `app_plomero`) **no** entran en este deploy:
> son plantillas Expo y se distribuyen aparte (Expo Go / EAS).

## Arquitectura

```
Internet → Cloudflare (HTTPS) → cloudflared (en tu server) ──┐
                                                             │ red interna Docker
                                          frontend (nginx) ──┘
                                          ├─ /            → estáticos del build React
                                          └─ /api/*       → backend (FastAPI :8000)
                                                             └─ SQLite en volumen Docker
```

Todo corre como un stack de Docker Compose **independiente** de tu nginx/gitea
del host. No publica ningún puerto en el host: cloudflared llega al frontend por
la red interna de Docker.

---

## 0. Requisitos en el server (una sola vez)

```bash
docker --version          # si falta: https://docs.docker.com/engine/install/ubuntu/
docker compose version    # viene con docker-ce reciente
```

Tu dominio ya tiene que estar en Cloudflare (nameservers apuntando a Cloudflare).

---

## 1. Traer el código al server

Desde tu gitea (o donde tengas el repo):

```bash
git clone http://TU-GITEA/usuario/PlomerIA.git
cd PlomerIA
```

---

## 2. Variables de entorno del backend

```bash
cp Backend/.env.example Backend/.env
nano Backend/.env
```

Completar:

- `SECRET_KEY` → una cadena larga y aleatoria (firma los JWT). Generala con:
  ```bash
  python3 -c "import secrets; print(secrets.token_urlsafe(48))"
  ```
- `GEMINI_API_KEY` → tu key de https://aistudio.google.com/apikey
  (si la dejás vacía, la IA funciona con el fallback por keywords).

---

## 3. Crear el túnel en Cloudflare

En el panel de Cloudflare:

1. **Zero Trust** → **Networks** → **Tunnels** → **Create a tunnel**.
2. Tipo **Cloudflared** → nombre, por ej. `plomeria` → **Save**.
3. En la pantalla "Install connector" vas a ver un comando con un **token**
   largo (empieza con `ey...`). **Copiá solo ese token** (no hace falta correr
   el comando, lo levanta el compose).
4. Pestaña **Public Hostnames** → **Add a public hostname**:
   - **Subdomain**: `plomeria` (o el que quieras)
   - **Domain**: tu dominio
   - **Type**: `HTTP`
   - **URL**: `frontend:80`  ← nombre del servicio del compose
   - **Save**. El registro DNS lo crea Cloudflare solo.

> Cloudflare termina el HTTPS en su borde y el túnel ya va cifrado, por eso el
> origen es HTTP (`frontend:80`). Dejá SSL/TLS en **Full** si te lo pregunta.

---

## 4. Token del túnel para el compose

```bash
cp .env.example .env
nano .env
```

Pegar el token del paso 3:

```
CLOUDFLARE_TUNNEL_TOKEN=eyJ...
```

---

## 5. Levantar todo

```bash
docker compose up -d --build
```

Esto compila el backend y el frontend, levanta nginx y conecta el túnel.
Verificar:

```bash
docker compose ps          # los 3 servicios "Up"
docker compose logs -f cloudflared   # buscar "Registered tunnel connection"
```

Abrí `https://plomeria.tudominio.com` 🎉

---

## 6. (Opcional) Cargar plomeros de prueba

```bash
docker compose exec backend python data/cargar_plomeros.py
```

Quedan persistidos en el volumen, no se borran al reconstruir.

---

## 7. Actualizar a una versión nueva

```bash
git pull
docker compose up -d --build
```

La base de datos vive en el volumen `plomeria_db` y **sobrevive** a los rebuilds.

---

## Operación

| Acción | Comando |
|--------|---------|
| Ver logs del backend | `docker compose logs -f backend` |
| Reiniciar | `docker compose restart` |
| Bajar todo | `docker compose down` (la DB se conserva) |
| Backup de la DB | `docker compose cp backend:/data/plomeria.db ./backup-$(date +%F).db` |
| Borrar TODO incl. DB | `docker compose down -v` ⚠️ |

---

## Notas de seguridad / producción

- **CORS** está en `allow_origins=["*"]`. Como el frontend pega a `/api` en el
  mismo origen, no hace falta, pero conviene restringirlo en `Backend/main.py`
  al dominio real antes de algo serio.
- `Backend/.env` y `.env` están en `.gitignore`: **no se commitean**. Verificá.
- SQLite + un único contenedor está perfecto para esta escala/demo. Si más
  adelante necesitás concurrencia alta, migrar a Postgres (cambiar `DATABASE_URL`).
- Cloudflare te da el firewall/WAF y oculta la IP de tu casa. No abras puertos
  en el router: el túnel es saliente.
