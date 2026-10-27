# SolidBit SACL — Agent Execution Control Loop

> **Control Plane Determinista, Telemetría de Procesos del SO y Gobernanza Soberana para Flotas de Agentes de IA Autónomos**  
> *Diseñado e implementado por **Joaquín Vallejo** ([@risejoaquin](https://github.com/risejoaquin)) bajo la metodología **SolidBit SDLC (`SB-ENG-HB-001 v1.0`)**.*

[![CI/CD Status](https://img.shields.io/github/actions/workflow/status/risejoaquin/solidbit-agent-execution-control-loop/ci.yml?branch=main&style=flat-square&logo=githubactions&logoColor=white&label=GitHub%20Actions%20CI)](https://github.com/risejoaquin/solidbit-agent-execution-control-loop/actions)
[![Test Suite](https://img.shields.io/badge/Pytest-698%2F698%20PASSED%20(100%25)-10b981?style=flat-square&logo=pytest&logoColor=white)](https://github.com/risejoaquin/solidbit-agent-execution-control-loop/actions)
[![Linter](https://img.shields.io/badge/Ruff-0%20errors%20%7C%20clean-blue?style=flat-square&logo=python&logoColor=white)](https://github.com/astral-sh/ruff)
[![Persistence](https://img.shields.io/badge/Storage-SQLite%20V1%20WAL%20(ACID)-003B57?style=flat-square&logo=sqlite&logoColor=white)](#3-capa-de-persistencia-local-soberana-sqlite-wal)
[![Frontend](https://img.shields.io/badge/Frontend-Vite%20%2B%20React%2019%20%2B%20Tailwind-61DAFB?style=flat-square&logo=react&logoColor=black)](#6-interfaz-unificada-de-misión-dual-spa-react--cli)
[![Security Policy](https://img.shields.io/badge/Security-Hard%20Deny%20Supremacy-red?style=flat-square&logo=securityscorecard&logoColor=white)](#5-compuertas-soberanas-hitl-con-firmas-criptográficas-hmac)

---

## 1. Por qué creé SACL: El problema real en producción

Cuando comencé a operar múltiples agentes de codificación autónomos (como Claude 3.7 Sonnet, Gemini 2.0/3.8 o Antigravity CLI) en repositorios complejos de comercio electrónico y microservicios, me encontré rápidamente con los límites del estado del arte:

1. **Colisiones destructivas en Git:** Múltiples agentes trabajando sobre el mismo directorio raíz sobreescriben archivos ajenos, ensucian el árbol de trabajo (`dirty root`) e introducen merge commits imposibles de auditar.
2. **"Activity Theater" y quema de tokens en bucles vacíos:** Los agentes suelen simular actividad continua consumiendo miles de tokens innecesarios sin producir un solo cambio verificable en disco ni ejecutar pruebas reales.
3. **Pérdida de invariantes de negocio:** Ningún LLM garantiza por sí solo que contratos críticos de inventario, stock concurrente o pasarelas de pago no sean modificados de forma silenciosa.
4. **Falta de compuertas de detención soberana:** Si un agente falla una prueba o toma un camino erróneo, la mayoría de los frameworks continúan ejecutando tareas posteriores en cascada, multiplicando el daño.

Construí **SACL (SolidBit Agent Execution Control Loop)** para resolver esto desde la ingeniería de sistemas: un plano de control **fail-closed**, determinista y soberano que trata a los agentes de IA no como generadores mágicos de código, sino como **procesos del sistema operativo sujetos a límites estrictos, aislamiento de espacio de trabajo, verificación criptográfica y compuertas de aprobación humana (HITL)**.

---

## 2. Arquitectura del Sistema

SACL opera como un kernel orquestador local desacoplado de dependencias en la nube:

```text
 ┌────────────────────────────────────────────────────────────────────────┐
 │                      OPERADOR HUMANO SOBERANO                          │
 │            (UI Web React 19 / Terminal CLI / Email Gateway)            │
 └───────────────────────────────────┬────────────────────────────────────┘
                                     │ HMAC-SHA256 Token / HITL Decision
                                     ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │                     SACL CONTROL PLANE (KERNEL)                        │
 │  ┌──────────────────────────────────────────────────────────────────┐  │
 │  │        Planificador DAG de Kahn & Particionado en Oleadas        │  │
 │  └──────────────────────────────┬───────────────────────────────────┘  │
 │                                 │                                      │
 │   ┌─────────────────────────────┼──────────────────────────────┐       │
 │   ▼                             ▼                              ▼       │
 │ ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐     │
 │ │  Worker Worktree │   │  Worker Worktree │   │  Worker Worktree │     │
 │ │  (Oleada 1: Cód) │   │  (Oleada 2: Tests)│  │ (Oleada 3: Docs) │     │
 │ └─────────┬────────┘   └─────────┬────────┘   └─────────┬────────┘     │
 │           └─────────────────────┼──────────────────────┘              │
 │                                 ▼                                      │
 │  ┌──────────────────────────────────────────────────────────────────┐  │
 │  │        Reconciliación Forense en 4 Puntos & Validación Invariante│  │
 │  │             (DR-INV-001, DR-PAY-001, DR-IDEM-001)                │  │
 │  └──────────────────────────────┬───────────────────────────────────┘  │
 └─────────────────────────────────┼──────────────────────────────────────┘
                                   │
                                   ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │            PERSISTENCIA LOCAL SOBERANA (SQLite V1 en modo WAL)         │
 │   Jobs (3) │ Runs (26) │ Eventos (26) │ Leases │ Auditoría Inmutable   │
 └────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Capacidades y Módulos Fundamentales

### A. Planificador de DAG Topológico (Algoritmo de Kahn)
* Resuelve dependencias entre tareas técnicas de forma determinista y sin ciclos.
* Divide las ejecuciones en **Oleadas Concurrentes Seguras**: dos tareas que tocan dominios independientes corren en paralelo; tareas con dependencias se detienen ante la primera falla (*fail-closed*).
* Si un nodo devuelve un código de salida diferente de `0`, todo el sub-árbol dependiente entra en estado de contención inmediata.

### B. Persistencia Soberana en Disco (SQLite V1 en Modo WAL)
* **Cero fuga de metadatos:** Toda la auditoría transaccional vive en el disco local (`control_loop.db` y `sacl_ops.db`), sin enviar logs, esquemas ni credenciales a servidores cloud.
* **Durabilidad ACID estricta:** Opera bajo **Write-Ahead Logging (WAL)** con control de concurrencia optimista (*CAS - Compare-And-Swap*), garantizando integridad absoluta en caso de reinicio de la máquina.
* **Inspección en tiempo real:** Registra cada `Job`, cada `Run`, salidas estándar (`stdout`/`stderr`), errores capturados y el historial de eventos forenses.

### C. Aislamiento Físico en Git Worktrees & La Regla "Dirty-Root"
* Los agentes de IA tienen **estrictamente prohibido** operar sobre la raíz del repositorio de trabajo.
* SACL aprovisiona automáticamente **worktrees efímeros independientes** en carpetas dedicadas para cada oleada.
* **Protocolo de Reconciliación en 4 Puntos:** Antes de admitir cualquier commit en la rama de integración, el sistema verifica:
  1. Ausencia de colisiones de archivos no rastreados.
  2. Compilación limpia y suites de tests unitarios (exit code 0).
  3. Integridad total de contratos congelados (`DR-INV-001`, `DR-PAY-001`, `DR-IDEM-001`).
  4. Generación de entregables físicos auditables en disco.

### D. Compuertas Soberanas HITL (Human-in-the-Loop)
* Ninguna acción crítica (modificación de infraestructura, despliegue o fusión de código a producción) se ejecuta sin intervención del operador.
* Las compuertas generan un identificador de solicitud único (ej. `REQ-20261026-743941E4`) y exigen una **firma criptográfica HMAC-SHA256**.
* Si el operador rechaza o la compuerta expira, el DAG aborta de forma segura revirtiendo el worktree efímero.

### E. Email Gateway & Automatización Bidireccional
* Integrado de forma nativa con **Resend** para notificaciones salientes y comandos entrantes.
* **Reportes de Micro-Decisión:** Al finalizar una oleada o bloquearse una compuerta, el sistema envía un informe estructurado al operador (`lawlieeet@outlook.es`) desde la cuenta autorizada (`lucilfer@selfcaresinners.com`).
* **Inbound Webhook Autenticado:** Permite disparar DAGs de manera remota mediante correos firmados validados por tokens criptográficos y firmas Svix.

### F. Selector Universal de Modelos de IA
* Interfaz de inferencia multi-proveedor que permite al operador alternar en caliente el motor de razonamiento según el tipo de tarea:
  - **Claude 3.7 Sonnet (via AGY):** Razonamiento híbrido profundo para arquitectura de código e invariantes estrictas.
  - **Gemini 3.8 Flash (High Reasoning):** Inferencia sub-segundo nativa de Antigravity para análisis de contratos y ejecución rápida de DAGs.
  - **Claude Sonnet 5.5 / Opus 5.5:** Especialistas en síntesis y pruebas de estrés de seguridad.
  - **GPT-4o:** Validación de esquemas multimodales y documentación.
  - **GPT-OSS 120B:** Modelo soberano desconectado (*air-gapped*) para auditorías confidenciales.

### G. Filosofía "Zero-Token Idle" (Cero Teatro)
* SACL no maquilla el frontend con gráficos inventados ni procesos simulados en bucle.
* Cuando no hay agentes ejecutándose, la consola reporta con honestidad: **`0 Procesos Activos`** y **`0 Tokens Consumidos`**.
* Solo se muestran métricas y eventos reales provenientes de los procesos del sistema operativo.

---

## 4. Resultados Empíricos y Verificación de Calidad

Los estándares de ingeniería del proyecto se verifican de manera continua y hermética tanto en entornos locales (Windows y Linux) como en GitHub Actions CI/CD:

```text
============================= Resumen de Validación =============================
Platform:              Windows 11 & Ubuntu 24.04 (Cross-platform hermetic)
Python:                3.11.9
Pytest Suite:          698 PASSED (100% verde) en 106.88s
Ruff Linting:          0 errores | Todas las reglas estrictas cumplidas
Vite React 19 Build:   0 errores | Bundle de producción generado en 639 ms
Contratos Congelados:  DR-INV-001 (Inventario), DR-PAY-001 (Pagos) blindados
Pull Requests:         PRs #3, #7, #8, #9 con checks pasando en GitHub
==================================================================================
```

---

## 5. Estructura del Repositorio

El proyecto está organizado en una arquitectura modular desacoplada:

```text
solidbit-agent-execution-control-loop/
├── apps/
│   └── web/                   # Frontend Vite + React 19 + Tailwind CSS
│       ├── src/
│       │   ├── components/    # Tablero principal, terminal de logs y modales
│       │   │   └── sections/  # Secciones: Email Gateway, Chat IA, Auth Hub, etc.
│       │   ├── utils/         # Formateador contextual de fechas (dateFormat.ts)
│       │   └── types/         # Tipos TypeScript para contratos y telemetría
│       └── dist/              # Build optimizado para producción
├── src/
│   └── sacl/                  # Núcleo del control plane (Python)
│       ├── approval/          # Gestor de compuertas HITL y validación HMAC
│       ├── cli/               # Comandos de consola y servidor local UI
│       ├── contracts/         # Contratos congelados e interfaces inmutables
│       ├── dag/               # Algoritmo de Kahn, particionado y barreras
│       ├── observability/     # Emisión de eventos y telemetría forense
│       ├── policy/            # Lattice de permisos y hard policies
│       ├── recovery/          # Detección de caída y reconciliación de worktree
│       ├── results/           # Colección y empaquetado de entregables
│       ├── state/             # Motor SQLite WAL, migraciones y repositorios
│       ├── ui/                # Servidor HTTP/SSE nativo y templates soberanos
│       └── worker/            # Supervisión de procesos de agentes y timeouts
├── tests/                     # 698 pruebas unitarias, de integración y seguridad
│   ├── integration/           # Concurrencia de DAG, supervisor y pasarelas
│   ├── security/              # Modelo de amenazas STRIDE y guardas de acceso
│   ├── ui/                    # Pruebas de equivalencia de API y servidor UI
│   └── unit/                  # Validación exhaustiva de contratos e invariantes
└── pyproject.toml             # Configuración central de Python, Pytest y Ruff
```

---

## 6. Guía Rápida de Inicio

### Requisitos Previos
* **Python:** 3.11 o superior.
* **Node.js:** v20 o superior (con npm).
* **Git:** 2.40 o superior con soporte de worktrees.

### 1. Clonar e Instalar Dependencias
```bash
git clone https://github.com/risejoaquin/solidbit-agent-execution-control-loop.git
cd solidbit-agent-execution-control-loop

# Entorno virtual de Python
python -m venv .venv
# En Windows:
.venv\Scripts\activate
# En Linux/macOS:
source .venv/bin/activate

pip install -e .[dev]
```

### 2. Ejecutar la Suite de Pruebas Automatizadas
```bash
# Ejecutar los 698 tests unitarios y de integración
pytest tests/ -v

# Verificar estilo y tipado con Ruff
ruff check src/ tests/
```

### 3. Compilar el Frontend React 19
```bash
cd apps/web
npm install
npm run build
cd ../..
```

### 4. Iniciar el Servidor de Misión Control (UI Soberana)
```bash
# Inicia el backend en puerto 8765 y sirve la telemetría en tiempo real
python -m sacl.cli ui --port 8765
```

Abre tu navegador en `http://localhost:8765` para acceder a la consola conversacional, el centro de compuertas HITL y la gestión de flotas.

---

## 7. Metodología de Ingeniería: SolidBit RISEHANDBOOK

Este proyecto sigue estrictamente el estándar de calidad **SolidBit SDLC (`SB-ENG-HB-001 v1.0`)**:

* **Principio de Verdad Absoluta:** Ninguna interfaz de usuario puede proyectar un estado inventado o simular ejecuciones que no existen en el sistema operativo.
* **Contratos Inmutables:** Los esquemas y modelos de datos críticos no se refactorizan sin una prueba formal de equivalencia.
* **Durabilidad Forense:** Toda falla técnica debe quedar registrada con su stacktrace y contexto completo en la base de datos transaccional SQLite WAL para auditoría post-mortem.

---

## 8. Licencia y Créditos

Desarrollado y mantenido por **Joaquín Vallejo** ([@risejoaquin](https://github.com/risejoaquin)).  
Distribuido bajo la licencia [Apache 2.0](LICENSE).
