# SolidBit Agent Execution Control Loop (SACL V1)

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![UI Theme](https://img.shields.io/badge/UI-OLED%20Pitch%20Black%20%23000000-black.svg)](file:///C:/Users/Lucilfer/Documents/Stable-Ecommerce-Orchestrator/SACL_IMPLEMENTATION_CAMPAIGN_v1/runs/impl-20261007-203727-e69378/worktrees/integration/src/sacl/ui)
[![Tests Status](https://img.shields.io/badge/tests-29%2F29%20PASS-brightgreen.svg)](file:///C:/Users/Lucilfer/Documents/Stable-Ecommerce-Orchestrator/SACL_IMPLEMENTATION_CAMPAIGN_v1/runs/impl-20261007-203727-e69378/worktrees/integration/tests/ui)
[![Invariants Policy](https://img.shields.io/badge/policy-Hard%20Deny%20Supremacy-red.svg)](file:///C:/Users/Lucilfer/Documents/Stable-Ecommerce-Orchestrator/SACL_IMPLEMENTATION_CAMPAIGN_v1/runs/impl-20261007-203727-e69378/worktrees/integration/docs/SECURITY_MODEL.md)
[![Engine](https://img.shields.io/badge/engine-Antigravity%20AGY%20v1.4.5-orange.svg)](file:///C:/Users/Lucilfer/Documents/Stable-Ecommerce-Orchestrator/SACL_IMPLEMENTATION_CAMPAIGN_v1/runs/impl-20261007-203727-e69378/src/sacl/ui/modules/chat.py)
[![Author](https://img.shields.io/badge/Author-LUCILFER%20%2F%20%40risejoaquin-emerald.svg)](https://github.com/risejoaquin)

> **Autor Soberano:** `LUCILFER / risejoaquin` ([@risejoaquin](https://github.com/risejoaquin))  
> **Estándar:** SolidBit SACL Standard 2026 · Cero Bypass & Zero-Smoke Policy  
> **Modo de Seguridad:** Fail-Closed Staging / Aislamiento por Git Worktrees / SQLite WAL Crash-Consistent  

---

## 1. Resumen Ejecutivo

El **SolidBit Agent Execution Control Loop (SACL V1)** es una plataforma de orquestación, supervisión y gobernanza multi-agente diseñada para gobernar la ejecución de agentes de inteligencia artificial (Antigravity `agy.exe`, Claude 3.7 Sonnet, Gemini 3.8 Flash) en estaciones de trabajo y entornos de despliegue controlado.

SACL resuelve el problema fundamental de la autonomía descontrolada: **garantizar matemáticamente y por diseño que ningún agente pueda ejecutar operaciones con efectos secundarios indebidos, incluso ante fallos, interrupciones abruptas o estados de concurrencia.**

### Principios Fundamentales del Sistema
1. **Soberanía Humana (HITL - Human-in-the-Loop):** Toda mutación destructiva, merge de ramas o despliegue a producción requiere un token firmado HMAC-SHA256 con TTL emitido por el operador principal (`Joaquín / LUCILFER`).
2. **Hard Deny Supremacy:** Política de denegación por defecto (*DENY by default*). Si una operación no tiene preflights verificados y permiso expreso en la matriz de políticas, se bloquea antes de tocar el filesystem o la red.
3. **Persistencia Crash-Consistent:** Almacenamiento operacional en **SQLite WAL (`sacl_ops.db`)** con transacciones `IMMEDIATE`, versionado Compare-And-Swap (CAS), reconciliación de runs huérfanos y zero-loss ante cierres inesperados.
4. **Aislamiento por Git Worktrees:** Los agentes operan confinados en worktrees efímeros independientes (`wt-*`), preservando el árbol raíz (`Local Dirty-Root Rule`) y prohibiendo terminantemente escrituras directas sobre `main`.
5. **Cero Mocks / Cero Humo:** Todas las integraciones son directas contra herramientas instaladas en el sistema anfitrión (Git, GitHub CLI, Railway, Supabase, Resend, Python, Node.js y Antigravity CLI).

---

## 2. Arquitectura de Módulos (SACL V12)

```
                                  [ OPERADOR SOBERANO ]
                                 (LUCILFER / risejoaquin)
                                            │
                      ┌─────────────────────┴─────────────────────┐
                      │                                           │
             [ Consola Web OLED HUD ]                    [ Gateway de Correo ]
              (http://127.0.0.1:8765)                   (Resend API / Inbound)
                      │                                           │
         ┌────────────┼───────────────────────────┐               │
         ▼            ▼                           ▼               ▼
   [ Selector     [ Dossier de             [ Explorador &   [ Webhook Inbound ]
   Ecosistema ]   Gobernanza HITL ]        Visor Código ]   (Tokens Svix HMAC)
         │            │                           │               │
         └────────────┼───────────────────────────┴───────────────┘
                      ▼
         [ Motor Orquestador SACL ] ◄──────► [ SQLite WAL Store ]
         (Políticas & Lock Supervisor)        (sacl_ops.db - 14 Tablas)
                      │
         ┌────────────┼───────────────────────────┐
         ▼            ▼                           ▼
   [ Agente Fase 1 ] [ Agente Fase 2 ]     [ Agente Fase 3 ]     [ Agente Fase 4 ]
   Architect Agent    Senior Coder AGY      Independent QA        Deployment Sentinel
   (spec-enforcer)    (worktree-coder)      (zero-bypass-qa)      (hitl-sentinel)
```

---

## 3. Capacidades de la Interfaz Web (Executive HUD)

La interfaz web de SACL está construida bajo una estética **OLED Pure Black (`#000000`)** de alto contraste con tipografía blanca pura (`#FFFFFF`), eliminando el ruido visual y optimizando la toma de decisiones:

- **Selector Multi-Proyecto del Ecosistema:** Alternancia instantánea entre los 4 proyectos clave (`Stable-Ecommerce`, `FULL-METAL-CASH`, `SolidPOS` y `SACL Core Engine`), reindexando el árbol de archivos en caliente vía `POST /api/fs/open-folder`.
- **Barra de Flujo Multi-Agente 2026:** Supervisión visual del ciclo de vida del DAG en 4 fases (`spec-enforcer` -> `worktree-coder` -> `zero-bypass-qa` -> `hitl-sentinel`).
- **Explorador de Archivos y Visor de Código:** Árbol de navegación jerárquico interactivo en disco con lectura de código con numeración de líneas y metadata de tamaño.
- **Decision Dossier & Compuertas de Aprobación:** Visualización de radio de impacto, diff git interactivo, TTL restante y botones de decisión (`Autorizar Despliegue` / `Rechazar`) con persistencia en la tabla SQLite `approvals`.
- **Base de Datos SQLite WAL & PRAGMA:** Tablas operacionales en vivo (`approvals`, `runs`, `events`, `errors`, `leases`, `jobs`) con herramienta de auditoría física `PRAGMA integrity_check`.
- **Consola Chat REPL & Motor de Inferencia:** Terminal interactiva conectada directamente al binario local `agy.exe` (v1.4.5) con selector de modelos (`gemini-3.8-flash-high`, `claude-3-7-sonnet`, `gemini-2-flash`).
- **Drawer de Terminal Monospace en Vivo:** Salida streaming de eventos del supervisor y pipelines SDLC sin recarga de página.

---

## 4. Matriz de Conexiones Reales (Lattice Tecnológico)

SACL se comunica de manera nativa con las herramientas de la estación de trabajo:

| Tecnología | Rol en el Sistema | Modo de Integración |
| :--- | :--- | :--- |
| **Git Core** | Aislamiento de código | Worktrees efímeros, SHA locking, dirty-root guard |
| **GitHub CLI (`gh`)** | SCM Remoto seguro | Creación de PRs autenticados bajo identidad `risejoaquin` |
| **Railway CLI** | Despliegue de Staging | Aprovisionamiento de entornos efímeros para preview |
| **Supabase CLI** | Base de Datos Cloud | Migraciones y réplicas PostgreSQL WAL (CLI v2.122.0) |
| **Resend CLI & API** | Gateway de Notificaciones | Envío y recepción de decisiones soberanas vía email |
| **Antigravity (`agy`)**| Motor de Inferencia | Ejecución local sandboxed del CLI v1.4.5 |
| **Python Runtime** | Backend & Scripts | Python 3.11.9 con suite de tests Pytest (29 tests) |
| **SQLite WAL** | Almacén de Estado Local | Base de datos relacional ACID con PRAGMA foreign_keys |

---

## 5. Invariantes de Negocio Auditadas (Hard Deny)

El orquestador incluye validadores deterministas para los contratos inmutables de la plataforma:

- **`DR-INV-001` (Sellable Unit Invariant):** Prohíbe cualquier decremento de inventario sin un registro transaccional idempotente asociado.
- **`DR-PAY-001` (Double-Entry Balance):** Garantiza que todo cobro o reembolso mantenga balance cero en la partida doble del ledger antes de confirmar cualquier transacción.
- **`DR-IDEM-001` (Idempotency Key Guard):** Rechaza llamadas duplicadas con el mismo identificador dentro de una ventana de tiempo configurable.
- **`DR-REC-001` (Crash-Safe Reconciliation):** Garantiza que cualquier proceso abortado por fallo eléctrico o cierre forzado sea clasificado como `INTERRUPTED` y requiera validación antes de reanudar efectos externos.

---

## 6. Instalación y Puesta en Marcha

### Prerrequisitos
- Windows 10/11 o Linux.
- Python 3.11+.
- Git 2.40+.
- Binario de Antigravity CLI (`agy.exe`) en `PATH` o `AppData\Local\agy\bin`.

### 1. Clonar el Repositorio
```bash
git clone https://github.com/risejoaquin/solidbit-agent-execution-control-loop.git
cd solidbit-agent-execution-control-loop
```

### 2. Configurar el Entorno
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
pip install pytest requests selenium
```

### 3. Ejecutar la Suite de Pruebas
```powershell
$env:PYTHONPATH = "src"
pytest tests/ui -v
```
*Garantía: 29 de 29 tests pasando exitosamente.*

### 4. Iniciar la Consola Web del Orquestador
```powershell
$env:PYTHONPATH = "src"
python -m sacl.cli ui --port 8765
```
Acceso en tu navegador local:
👉 **`http://127.0.0.1:8765`**

---

## 7. Modelo Canónico de Autoridad (4 Niveles)

Toda decisión arquitectónica o de código en SACL sigue rigurosamente el modelo de precedencia:

```
+==================================================================================================+
|                               SACL CANONICAL PRECEDENCE HIERARCHY                                |
+==================================================================================================+
|  TIER 1: Decisiones Explícitas de Joaquín (LUCILFER / @risejoaquin)                              |
|          Línea base inviolable codificada directamente por el arquitecto soberano.               |
+--------------------------------------------------------------------------------------------------+
|  TIER 2: Comportamiento Probado del Orquestador en Producción                                    |
|          Regla Local Dirty-Root, Aislamiento por Worktrees, Timeouts no destructivos.            |
+--------------------------------------------------------------------------------------------------+
|  TIER 3: Gobernanza y Contratos Congelados                                                       |
|          Invariantes DR-INV-001, DR-PAY-001, esquemas JSON y cabeceras de máquina.              |
+--------------------------------------------------------------------------------------------------+
|  TIER 4: Estándares de la Industria (RFCs, POSIX, Windows APIs)                                  |
|          Convenciones técnicas para resolver vacíos no especificados.                           |
+==================================================================================================+
```

---

## 8. Estructura del Repositorio

```
.
├── docs/                           # Documentación técnica, ADRs y modelos de amenaza
│   ├── ARCHITECTURE.md             # Arquitectura modular integral
│   ├── AUTHORITY_MODEL.md          # Especificación del modelo de gobernanza humana
│   ├── SECURITY_MODEL.md           # Políticas de Hard Deny y análisis STRIDE
│   ├── SQLITE_DATA_MODEL.md        # Esquema relacional y transacciones WAL
│   └── adr/                        # Architectural Decision Records (ADR-001 a ADR-014)
├── src/sacl/                       # Código fuente del orquestador soberano
│   ├── cli/                        # Comandos de consola (sacl ui, sacl verify, sacl audit)
│   ├── ui/                         # Motor de UIX Web y Executive HUD V12
│   │   ├── server.py               # Servidor HTTP ligero, enrutador y manejador SSE
│   │   ├── templates.py            # Dashboard OLED #000000, componentes visuales y cliente JS
│   │   └── modules/                # Módulos especializados de UIX y backend
│   │       ├── chat.py             # Integración con Antigravity AGY CLI y telemetría
│   │       ├── connections.py      # Matriz de detección de herramientas locales
│   │       ├── email_gateway.py    # Gateway Resend con soporte bi-direccional
│   │       ├── fs_explorer.py      # Explorador recursivo de archivos y lector de código
│   │       ├── gates.py            # Compuertas de decisión y firmas HMAC
│   │       ├── models.py           # Catálogo de modelos de IA soportados
│   │       └── state.py            # Adaptador persistente a SQLite WAL
│   └── ...                         # Motores de políticas, workspaces y supervisor
├── tests/                          # Suite de pruebas unitarias, integración y UI
│   ├── ui/                         # Tests del servidor HTTP, rutas API y módulos (29 tests)
│   └── ...
├── pyproject.toml                  # Configuración de paquete Python y dependencias
└── README.md                       # Documentación principal de la plataforma
```

---

## 9. Autoría y Licencia

Desarrollado y gobernado por **LUCILFER / risejoaquin** ([@risejoaquin](https://github.com/risejoaquin)).  
Todos los derechos reservados bajo la arquitectura de gobernanza soberana **SolidBit SACL Standard 2026**.
