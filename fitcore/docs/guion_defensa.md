# Guion de Defensa — FitCore Gym (11:00, duración sugerida: 10-12 min)

## Antes de entrar (checklist)
- [ ] Laptop con el proyecto probado: `python preparar_datos.py` YA ejecutado
- [ ] Terminal abierta en la carpeta del proyecto, letra grande (Ctrl + "+")
- [ ] `data/dashboard.png` abierto en el visor de imágenes
- [ ] Informe PDF abierto en otra pestaña
- [ ] Nombres de integrantes y enlace al repo YA reemplazados en el informe

## Reparto sugerido (Persona A = estrategia, Persona B = técnica)

### 1) Apertura — Persona A (1 min)
"Somos NEXUS Consulting. Nuestro cliente, FitCore Gym, operaba con cuadernos
y Excel: no sabía qué socio estaba por abandonar ni cuándo pedir mercadería.
Construimos un ecosistema integrado: un punto de venta conectado por un bus
de eventos a un ERP, un SCM y un CRM, con un tablero gerencial que se
actualiza con cada transacción."

### 2) Estrategia — Persona A (2 min, con el informe en pantalla)
- Porter: rivalidad alta + clientes con costo de cambio nulo → estrategia de
  DIFERENCIACIÓN por inteligencia de cliente, no por precio.
- Cadena de valor: el SI entra en logística interna (SCM), ventas (RFM) y
  postventa (CRM).
- Mostrar el diagrama ER 10 segundos: "9 tablas, una sola fuente de verdad".

### 3) DEMO EN VIVO — Persona B (4-5 min) ⭐ lo más importante
Opción segura: `python demo_integracion.py` y narrar cada sección.
Opción con más impacto (si hay tiempo): `python main.py` y hacerlo manual:
  1. Opción 5 → RFM ("clasificamos 350 socios en 6 segmentos")
  2. Opción 4 → CRM ("la consulta automatizada aísla 137 socios en riesgo")
  3. Opción 7 → abrir dashboard.png ("estado ANTES de la venta")
  4. Opción 1 → registrar venta: buscar un socio, vender 2 Proteína Whey
     + 1 Membresía Mensual
     → SEÑALAR EN LA CONSOLA: "miren: el ERP creó el asiento, el SCM generó
       la orden de compra y el ERP registró el gasto. Nadie tocó nada."
  5. Opción 7 de nuevo → reabrir dashboard.png ("y el tablero ya cambió")

NOTA: para garantizar que la venta dispare al SCM, antes de la defensa dejen
el stock de la Proteína Whey al límite (la demo automática ya lo hace sola;
en el menú manual pueden vender varias unidades hasta cruzar el mínimo de 15).

### 4) Inteligencia — Persona A (2 min)
- RFM: "el 16% de los socios (VIP) gasta en promedio USD 831 — 7,8 veces más
  que un socio perdido. Protegerlos es la prioridad."
- CRM + RFM juntos: "el segmento Recuperable es exactamente el que recibe
  las alertas: la analítica se vuelve operación."
- Dashboard: leer los 4 paneles (están interpretados en el informe, sec. 4.3).

### 5) Cierre — Persona B (30 s)
"Con esto FitCore pasa de administrar un cuaderno a dirigir con datos.
Siguiente fase: interfaz web y modelo predictivo de churn."

## Preguntas probables del profesor (y respuestas)

**¿Cómo demuestran que la integración es automática?**
El Core no llama al ERP ni al SCM: publica eventos en el bus (events.py,
patrón Observador). Los módulos se suscriben al arrancar (main.py). La
bitácora del bus registra cada notificación.

**¿Por qué SQLite y no CSV?**
Cumple persistencia con transacciones y claves foráneas, y permite las
consultas SQL del RFM y del CRM (julianday para calcular inactividad).
CSV habría requerido reimplementar todo eso a mano.

**¿De dónde salen las transacciones si el dataset de Kaggle no las tiene?**
Kaggle aporta los PERFILES (350 socios reales: contrato, frecuencia, churn).
El histórico se simula coherente con cada perfil: la frecuencia de compra
sigue Avg_class_frequency_total y los socios con Churn=1 dejan de comprar
45-180 días atrás. Por eso el CRM detecta deserción real, no aleatoria.

**¿Cómo funciona el puntaje RFM?**
Recencia, Frecuencia y Monetario se calculan con una consulta SQL por
cliente; cada dimensión se divide en quintiles (pandas.qcut) con puntaje
1-5 (la recencia invertida: menos días = más puntos) y reglas de negocio
traducen la combinación a etiquetas (analytics/rfm.py).

**¿Qué es la partida doble del ERP?**
Cada hecho económico afecta dos cuentas: una venta es DEBE Caja / HABER
Ingresos; una compra es DEBE Inventario / HABER Caja. El estado de caja
sale de sumar los movimientos de la cuenta Caja.

**¿Qué pasa si dos ventas seguidas dejan el mismo producto bajo mínimo?**
El SCM verifica si ya existe una orden PENDIENTE de ese producto y no la
duplica (modules/scm.py). Al "recibirla" (opción 6) el stock se repone.

**¿Cómo escalaría esto en una empresa real?**
Misma arquitectura: el bus interno se reemplaza por colas de mensajes o
APIs REST, y los módulos por sistemas comerciales (Odoo, SAP, Salesforce).
El Core no cambiaría.

## IMPORTANTE antes de entregar
1. Reemplazar [NOMBRE INTEGRANTE 1/2] y [ENLACE AL REPOSITORIO] en el docx.
2. Abrir el docx en Word → clic derecho en la tabla de contenido →
   "Actualizar campos" → guardar y EXPORTAR EL PDF desde Word
   (el índice se llena en ese momento).
3. Subir el código a GitHub y pegar el enlace real en Anexos.
