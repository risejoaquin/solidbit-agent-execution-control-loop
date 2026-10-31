# Manual de Operación y Capacitación: SolidBit EOP (Ecosystem Orchestration Platform)

## 1. ¿Qué es el SolidBit EOP?
El EOP no es un editor de código (IDE) ni una terminal tradicional. Es un **Plano de Control Visual** diseñado para gobernar un ecosistema de agentes de Inteligencia Artificial locales. Funciona bajo el principio de **Inversión de Control (IoC)**: el operador dicta la intención arquitectónica (el *qué*) y el motor de orquestación subyacente ejecuta la mutación y las pruebas (el *cómo*), entregando un paquete cerrado para revisión final en compuertas criptográficas.

### Principios de Diseño Innegociables:
- **Zero-Blocking UX:** Las operaciones asíncronas nunca congelan la pantalla. El sistema opera mediante el patrón CQRS; al enviar un comando, el sistema lo valida, lo encola en SQLite WAL y devuelve un ACK inmediato ($<100\,\text{ms}$).
- **Zero-Trust Security:** El frontend visual es estrictamente un consumidor de estado de solo lectura (*Read-Only State Consumer*). No manipula ni persiste tokens o contraseñas en el navegador; la seguridad y firmas residen exclusivamente en el entorno local del sistema operativo.
- **Soberanía de Código:** Los agentes jamás escriben directamente en la rama principal (main). Operan en entornos efímeros desechables (git worktree o ramas temporales gent/*).

---

## 2. Los 5 Módulos Centrales de la Interfaz

### 1. Context Boundary (Pantalla de Inicio)
Establece el perímetro de seguridad mandatorio antes de permitir cualquier interacción con el sistema.
- **Uso:** Presiona el botón `📁 Explorar Sistema (Nativo)` para invocar el explorador de carpetas del sistema operativo y seleccionar la raíz del repositorio local.
- **Seguridad:** Aísla a los agentes para que no puedan leer ni mutar archivos fuera del espacio de trabajo montado.

### 2. Command Hub (Chat de Orquestación)
Centro de mando CQRS donde se emiten las intenciones de campaña.
- **Uso:** No es un canal de conversación casual. Se utiliza para despachar payloads JSON estructurados o directivas de arquitectura con requerimientos explícitos.
- **Comportamiento:** Al despachar, el formulario se libera de inmediato con un ACK y la intención queda encolada en SQLite WAL.

### 3. Control Loop (Telemetría en Tiempo Real)
Panel de observabilidad reactivo conectado vía Server-Sent Events (SSE).
- **Visualización:** Cuadrícula de tarjetas de agentes (*AgentCards*) con renderizado (1)$ (React.memo) que representan los roles de **Atlas** (Coordinador), **Vega** (Datos), **Nova** (Calidad) y **Centinela** (Seguridad).
- **Métricas:** Muestra el proceso en ejecución, registros monoespaciados, micro-gráficos sparkline de latencia RTT y estado de memoria.

### 4. Skills Importer & Studio
Gestor central de habilidades y directivas para los agentes.
- **Uso:** Zona de Drag & Drop para subir especificaciones .json o archivos SKILL.md, acompañada de un **Skill Authoring Studio** interactivo en panel dividido para generar y compilar nuevas directivas con asistencia de IA y persistencia directa en .agents/skills/<id>/.

### 5. Panel GitHub (Gobernanza)
Observabilidad continua sobre el control de versiones sin exposición de credenciales.
- **Uso:** Monitorea en tiempo real la rama activa, estado de limpieza (*clean / dirty porcelain*), commits pendientes (*ahead / behind*) y Pull Requests abiertos, operando en modo de solo lectura.

---

## 3. El Flujo de Trabajo del Operador (Paso a Paso)

1. **Despacho (Inyección de Intención):** Abre el Command Hub, redacta o pega el payload CQRS (EXECUTE_WAVE) con los criterios de aceptación y presiona enviar.
2. **Observación (Aislamiento):** En el Control Loop, observa a Atlas aprovisionar el worktree efímero (gent/*) y coordinar las tareas hacia Vega y Nova.
3. **Auditoría Automática:** Centinela evalúa el código resultante contra la matriz de prohibiciones constitucionales y ejecuta las suites de pruebas automatizadas.
4. **Gate 5 (Compuerta Humana):** Cuando las pruebas alcanzan el 100% de aprobación, la tarjeta de campaña cambia a estado ámbar (APPROVAL_REQUIRED).
5. **Firma y Cierre:** Inspecciona el diff y el reporte de evidencias. Para autorizar la integración, inyecta la resolución firmada con tu HMAC en el Command Hub. El motor fusiona los cambios, destruye el entorno efímero (*Cascading Teardown*) y deja el espacio de trabajo en un estado limpio y reproducible.
