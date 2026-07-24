const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, ImageRun, PageBreak,
  TableOfContents, LevelFormat, ShadingType, BorderStyle, convertInchesToTwip,
} = require("docx");

const DOCS = "/home/claude/fitcore/docs/";
const DATA = "/home/claude/fitcore/data/";
const img = (p) => fs.readFileSync(p);

const AZUL = "2E86AB", GRISOSC = "333333";

// ----------------------------------------------------------- helpers
const H1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 320, after: 160 }, children: [new TextRun({ text: t, color: AZUL })] });
const H2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 240, after: 120 }, children: [new TextRun({ text: t, color: GRISOSC })] });
const P = (t, opts = {}) => new Paragraph({
  alignment: AlignmentType.JUSTIFIED, spacing: { after: 120, line: 276 },
  children: [new TextRun({ text: t, size: 22, ...opts })],
});
const Prich = (runs) => new Paragraph({
  alignment: AlignmentType.JUSTIFIED, spacing: { after: 120, line: 276 },
  children: runs.map(([t, o]) => new TextRun({ text: t, size: 22, ...(o || {}) })),
});
const BULLET = (t, bold0) => new Paragraph({
  numbering: { reference: "vinetas", level: 0 }, spacing: { after: 80, line: 276 },
  children: bold0
    ? [new TextRun({ text: bold0, bold: true, size: 22 }), new TextRun({ text: t, size: 22 })]
    : [new TextRun({ text: t, size: 22 })],
});
const IMG = (ruta, wPx, hPx, caption) => [
  new Paragraph({
    alignment: AlignmentType.CENTER, spacing: { before: 120, after: 40 },
    children: [new ImageRun({ type: "png", data: img(ruta), transformation: { width: wPx, height: hPx } })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER, spacing: { after: 200 },
    children: [new TextRun({ text: caption, italics: true, size: 18, color: "666666" })],
  }),
];
const salto = () => new Paragraph({ children: [new PageBreak()] });

function tabla(encabezados, filas, anchos) {
  const total = anchos.reduce((a, b) => a + b, 0);
  const celda = (texto, esEnc) => new TableCell({
    width: { size: 0, type: WidthType.AUTO },
    shading: esEnc ? { type: ShadingType.CLEAR, fill: AZUL } : undefined,
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    children: [new Paragraph({
      children: [new TextRun({ text: String(texto), bold: esEnc, size: 20, color: esEnc ? "FFFFFF" : "000000" })],
    })],
  });
  const filaEnc = new TableRow({ children: encabezados.map((h, i) => {
    const c = celda(h, true); c.options ??= {}; return c; }) });
  return new Table({
    width: { size: total, type: WidthType.DXA },
    columnWidths: anchos,
    rows: [
      new TableRow({ children: encabezados.map((h, i) => new TableCell({
        width: { size: anchos[i], type: WidthType.DXA },
        shading: { type: ShadingType.CLEAR, fill: AZUL },
        margins: { top: 60, bottom: 60, left: 100, right: 100 },
        children: [new Paragraph({ children: [new TextRun({ text: String(h), bold: true, size: 20, color: "FFFFFF" })] })],
      })) }),
      ...filas.map((f) => new TableRow({ children: f.map((v, i) => new TableCell({
        width: { size: anchos[i], type: WidthType.DXA },
        margins: { top: 60, bottom: 60, left: 100, right: 100 },
        children: [new Paragraph({ children: [new TextRun({ text: String(v), size: 20 })] })],
      })) })),
    ],
  });
}

// ============================================================= PORTADA
const portada = [
  new Paragraph({ spacing: { before: 1600 } }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "ESCUELA POLITÉCNICA NACIONAL", bold: true, size: 32 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 }, children: [new TextRun({ text: "Facultad de Ingeniería de Sistemas", size: 26 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 500 }, children: [new TextRun({ text: "ISID223 — Introducción a los Sistemas de Información (2025-B)", size: 24 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 }, children: [new TextRun({ text: "PROYECTO FINAL", bold: true, size: 40, color: AZUL })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 }, children: [new TextRun({ text: "Transformación Digital Empresarial", size: 32 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 600 }, children: [new TextRun({ text: "FitCore Gym: Ecosistema Integrado de Sistemas de Información\npara la digitalización de una PYME de servicios deportivos", italics: true, size: 26 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 }, children: [new TextRun({ text: "Firma consultora: NEXUS Consulting Group", bold: true, size: 24 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 }, children: [new TextRun({ text: "Integrantes: [NOMBRE INTEGRANTE 1] — [NOMBRE INTEGRANTE 2]", size: 24 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 }, children: [new TextRun({ text: "Profesor: Iván Carrera", size: 24 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "Quito, 24 de julio de 2026", size: 24 })] }),
  salto(),
  new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: "Contenido", color: AZUL })] }),
  new TableOfContents("Contenido", { hyperlink: true, headingStyleRange: "1-2" }),
  salto(),
];

// ======================================================= 1. RESUMEN EJECUTIVO
const resumen = [
  H1("1. Resumen Ejecutivo"),
  P("FitCore Gym es un gimnasio de barrio con 350 socios que operaba de forma completamente manual: registro de socios en hojas de cálculo aisladas, cobros sin historial, compras a proveedores por intuición y ninguna capacidad para detectar cuándo un socio abandona. El resultado: silos de información, quiebres de stock recurrentes y una tasa de deserción del 26 % que la gerencia solo percibía cuando ya era irreversible."),
  P("Nuestra firma consultora diseñó y construyó un ecosistema integrado de sistemas de información desarrollado en Python con persistencia en SQLite: un Sistema Core (punto de venta de membresías, clases y productos) conectado mediante un bus de eventos a tres módulos satélite — ERP (contabilidad automática), SCM (reabastecimiento automático) y CRM (alertas de deserción) — culminando en un tablero de control gerencial que se actualiza con cada transacción."),
  P("El valor es inmediato y medible: cada venta genera su asiento contable sin intervención humana; cuando el stock de un producto cae bajo el mínimo, el sistema emite la orden de compra al proveedor por sí solo; y el módulo CRM identificó 137 socios en riesgo de deserción que hoy son invisibles para el negocio. La segmentación RFM reveló además que 57 clientes VIP (16 % de la base) concentran un gasto promedio de USD 831, un segmento que la empresa ni siquiera sabía que existía. Con esta plataforma, FitCore Gym pasa de administrar un cuaderno a dirigir el negocio con datos."),
];

// ======================================================= 2. DISEÑO ESTRATÉGICO
const porterFilas = [
  ["Rivalidad entre competidores", "ALTA", "Múltiples gimnasios y cadenas low-cost en el sector; competencia por precio.", "El SI diferencia por servicio: atención personalizada basada en datos (RFM/CRM), retención proactiva y disponibilidad de productos."],
  ["Amenaza de nuevos entrantes", "MEDIA-ALTA", "Barreras de entrada bajas (un local y equipos básicos).", "La base histórica de clientes y la analítica generan una ventaja difícil de replicar por un entrante sin datos."],
  ["Productos sustitutos", "ALTA", "Apps de fitness, entrenamiento en casa, parques públicos.", "Las clases dirigidas y el seguimiento CRM crean comunidad y vínculo que un sustituto digital no ofrece."],
  ["Poder de negociación de clientes", "ALTA", "Costo de cambio casi nulo; el socio puede irse a otro gimnasio.", "El CRM detecta la inactividad ANTES del abandono y permite campañas de recuperación dirigidas al segmento correcto."],
  ["Poder de negociación de proveedores", "MEDIA", "Pocos distribuidores de suplementos con precios estables.", "El SCM consolida órdenes de compra con datos reales de rotación, mejorando la posición negociadora de la PYME."],
];

const rf = [
  ["RF-01", "Registrar ventas de membresías, clases y productos asociadas a un socio."],
  ["RF-02", "Mantener el catálogo de productos con precio, costo, stock y stock mínimo."],
  ["RF-03", "Registrar y buscar socios (alta, consulta por nombre)."],
  ["RF-04", "Generar automáticamente el asiento contable de cada venta y de cada compra (ERP)."],
  ["RF-05", "Generar automáticamente una orden de compra al proveedor cuando el stock ≤ stock mínimo (SCM)."],
  ["RF-06", "Detectar mediante consulta automatizada a los socios sin compras en más de 30 días y emitir la alerta \u201cCliente en Riesgo de Deserción\u201d (CRM)."],
  ["RF-07", "Calcular la segmentación RFM de toda la base de clientes y asignar etiquetas estratégicas."],
  ["RF-08", "Generar el dashboard gerencial con ventas temporales, segmentos RFM, KPI financiero y alertas CRM."],
  ["RF-09", "Cerrar automáticamente la alerta de riesgo si el socio vuelve a comprar (recuperación)."],
];
const rnf = [
  ["RNF-01", "Rendimiento", "El registro de una venta y sus reacciones (ERP/SCM) debe completarse en < 2 segundos."],
  ["RNF-02", "Integridad", "Persistencia transaccional en SQLite con claves foráneas activas; sin pérdida de datos ante reinicio."],
  ["RNF-03", "Mantenibilidad", "Arquitectura modular desacoplada: los módulos se comunican solo mediante el bus de eventos."],
  ["RNF-04", "Usabilidad", "El personal debe poder registrar una venta en máximo 4 pasos desde el menú."],
  ["RNF-05", "Portabilidad", "Ejecución con Python 3.10+ y dependencias mínimas (pandas, matplotlib), sin instalación de servidores."],
  ["RNF-06", "Escalabilidad", "El diseño por eventos permite añadir nuevos módulos suscriptores sin modificar el Core."],
];

const estrategia = [
  H1("2. Diseño Estratégico"),
  H2("2.1 Análisis competitivo: las 5 Fuerzas de Porter"),
  P("Se analizó la industria de gimnasios de barrio en Quito para justificar cómo el sistema de información propuesto mejora la posición competitiva de FitCore Gym:"),
  tabla(["Fuerza", "Nivel", "Diagnóstico", "Cómo el SI mejora la posición"], porterFilas, [1900, 950, 2900, 3610]),
  P(""),
  P("Conclusión estratégica: FitCore opera en una industria de rivalidad alta donde competir por precio erosiona el margen. El SI reposiciona a la empresa hacia una estrategia de diferenciación por servicio e inteligencia de cliente (Porter): retener cuesta menos que adquirir, y ningún competidor del segmento posee capacidad analítica equivalente."),
  H2("2.2 Cadena de Valor: actual vs. propuesta"),
  P("El diagnóstico de la cadena de valor evidencia que los eslabones primarios operan desconectados. La propuesta introduce el SI en los eslabones donde agrega valor directo:"),
  ...IMG(DOCS + "cadena_valor.png", 620, 312, "Figura 1. Cadena de valor actual (manual) frente a la propuesta con el SI integrado."),
  P("Los eslabones de mayor impacto son Logística Interna (el SCM elimina los quiebres de stock), Marketing y Ventas (el RFM permite campañas por segmento) y Servicio Postventa (el CRM convierte la deserción, hoy invisible, en un evento gestionable)."),
  H2("2.3 Especificación de requerimientos (SDLC — Análisis)"),
  P("Requerimientos funcionales:"),
  tabla(["ID", "Requerimiento funcional"], rf, [900, 8460]),
  P(""),
  P("Requerimientos no funcionales:"),
  tabla(["ID", "Categoría", "Restricción"], rnf, [900, 1700, 6760]),
  H2("2.4 Integración empresarial: cómo se evitan los silos de información"),
  P("En una empresa tradicional, cada área mantiene sus propios registros (ventas en un cuaderno, contabilidad en Excel, compras en la memoria del dueño): eso es un silo de información. La teoría de integración empresarial propone que los sistemas transaccionales (TPS) alimenten automáticamente a los sistemas de gestión (ERP, SCM, CRM) compartiendo una única fuente de verdad."),
  P("Nuestra solución materializa ese principio con dos decisiones de diseño: (1) una base de datos única (SQLite) que actúa como repositorio central de clientes, ventas, inventario, contabilidad y alertas; y (2) un bus de eventos (patrón Observador) por el cual el Core publica hechos de negocio (\u201cventa_registrada\u201d, \u201cstock_bajo\u201d) y los módulos suscritos reaccionan sin acoplamiento. En un escenario real, este mismo diseño escala reemplazando el bus interno por middleware empresarial (colas de mensajes, APIs REST o un ESB) y los módulos por sistemas comerciales (SAP, Odoo, Salesforce), sin cambiar la lógica del Core."),
  H2("2.5 Diseño técnico: Diagrama Entidad-Relación"),
  ...IMG(DOCS + "diagrama_er.png", 620, 389, "Figura 2. Modelo de datos del ecosistema: 9 tablas que cubren Core, ERP, SCM, CRM y analítica."),
  P("El modelo cumple y supera el mínimo exigido (Clientes, Productos, Transacciones): la venta se descompone en cabecera (VENTAS) y detalle (DETALLE_VENTA) para soportar facturas multiproducto; PRODUCTOS distingue bienes físicos (con stock y proveedor) de servicios (membresías y clases, sin stock); y cada módulo satélite persiste sus propios hechos (ASIENTOS_CONTABLES, ORDENES_COMPRA, ALERTAS_CRM, SEGMENTOS_RFM) siempre enlazados por claves foráneas a las entidades del Core."),
  H2("2.6 Mockups de las interfaces principales"),
  ...IMG(DOCS + "mockup_pos.png", 480, 318, "Figura 3. Mockup del punto de venta (Core): búsqueda de socio, catálogo y carrito."),
  ...IMG(DOCS + "mockup_gerencial.png", 480, 320, "Figura 4. Mockup del panel gerencial: los cuatro cuadrantes del tablero de control."),
  salto(),
];

// ==================================================== 3. DOCUMENTACIÓN TÉCNICA
const clasesFilas = [
  ["Cliente", "core/modelos.py", "Socio del gimnasio; conserva los atributos del perfil (contrato, frecuencia, antigüedad) heredados del dataset."],
  ["Producto", "core/modelos.py", "Clase base de todo lo vendible. Encapsula el stock (atributo privado _stock) y expone descontar_stock(), que avisa si se cruzó el mínimo."],
  ["Membresia / ClaseDirigida", "core/modelos.py", "Subclases de Producto (herencia). Redefinen es_servicio() (polimorfismo): no manejan inventario."],
  ["Venta / DetalleVenta", "core/modelos.py", "Composición: la venta agrega líneas de detalle y calcula su total."],
  ["SistemaCore", "core/sistema_core.py", "Fachada del sistema principal: clientes, catálogo y registro de ventas. Publica los eventos de integración."],
  ["BusDeEventos", "events.py", "Implementa el patrón Observador: suscribir() y publicar(). Mantiene una bitácora como evidencia de integración."],
  ["ModuloERP", "modules/erp.py", "Suscrito a venta_registrada y orden_generada: crea asientos por partida doble y calcula el estado de caja."],
  ["ModuloSCM", "modules/scm.py", "Suscrito a stock_bajo: genera la orden de compra al proveedor (evitando duplicados) y publica orden_generada."],
  ["ModuloCRM", "modules/crm.py", "Consulta automatizada de inactividad (> 30 días) que genera alertas de deserción; suscrito a venta_registrada para cerrar alertas de socios recuperados."],
];

const tecnica = [
  H1("3. Documentación Técnica"),
  H2("3.1 Arquitectura y clases del sistema"),
  P("El sistema fue desarrollado en Python 3 con Programación Orientada a Objetos y persistencia en SQLite. La arquitectura separa el dominio (clases), la lógica del Core, los módulos satélite y la analítica:"),
  tabla(["Clase", "Archivo", "Responsabilidad"], clasesFilas, [2100, 1900, 5360]),
  P(""),
  P("Los cuatro pilares de la POO están presentes: encapsulamiento (el stock solo se modifica mediante métodos), herencia (Membresia y ClaseDirigida extienden Producto), polimorfismo (es_servicio() decide en tiempo de ejecución si corresponde descontar inventario) y composición (Venta contiene DetalleVenta)."),
  H2("3.2 Flujo de integración entre sistemas"),
  ...IMG(DOCS + "arquitectura_integracion.png", 600, 333, "Figura 5. Bus de eventos: el Core publica; ERP, SCM y CRM reaccionan sin intervención humana."),
  P("La cadena completa que se demuestra en vivo es la siguiente: al registrar una venta, el Core publica \u201cventa_registrada\u201d; el ERP reacciona creando el asiento contable (DEBE Caja / HABER Ingresos) y el CRM verifica si el socio tenía una alerta activa para cerrarla. Si además la venta dejó algún producto en o bajo su stock mínimo, el Core publica \u201cstock_bajo\u201d; el SCM reacciona generando la orden de compra al proveedor y publica a su vez \u201corden_generada\u201d, con la que el ERP registra el gasto (DEBE Inventario / HABER Caja). Tres sistemas se actualizan en cascada a partir de una única acción del usuario."),
  H2("3.3 Evidencia de funcionamiento"),
  P("Captura de la venta en vivo y la reacción en cascada de los módulos (salida real del sistema):"),
  ...IMG(DOCS + "captura_integracion.png", 620, 260, "Figura 6. Una venta dispara ERP (asiento), SCM (orden de compra) y nuevamente ERP (gasto)."),
  P("Captura del análisis automatizado del CRM sobre la base real de socios:"),
  ...IMG(DOCS + "captura_crm.png", 620, 160, "Figura 7. El CRM aísla a los socios inactivos y dispara las alertas de riesgo de deserción."),
  salto(),
];

// ================================================= 4. REPORTE DE INTELIGENCIA
const rfmFilas = [
  ["Perdido", "77", "22,0 %", "106,58", "Inactivos y de bajo valor histórico: no invertir en recuperación masiva; solo campañas de bajo costo (correo)."],
  ["Necesita Atención", "67", "19,1 %", "404,75", "Se están enfriando: recordatorios de clases y beneficios antes de que crucen el umbral de deserción."],
  ["Recuperable", "63", "18,0 %", "387,05", "Fueron buenos clientes y se alejaron: campaña dirigida con promoción de reactivación (prioridad del CRM)."],
  ["VIP", "57", "16,3 %", "831,69", "Máximo valor: trato preferencial, acceso anticipado a clases, programa de referidos."],
  ["Leal", "55", "15,7 %", "294,42", "Activos y constantes de ticket medio: venta cruzada de productos y clases premium."],
  ["Nuevo / Prometedor", "31", "8,9 %", "230,58", "Compraron hace poco: onboarding activo durante los primeros 90 días para consolidar el hábito."],
];

const cwv = [
  ["LCP (Largest Contentful Paint)", "≤ 2,5 s", "Renderizado del contenido principal; en el POS equivale a cargar catálogo y buscador al abrir."],
  ["INP (Interaction to Next Paint)", "≤ 200 ms", "Respuesta a cada interacción (agregar al carrito, registrar venta)."],
  ["CLS (Cumulative Layout Shift)", "≤ 0,1", "Estabilidad visual del dashboard al refrescar los gráficos."],
  ["Disponibilidad (uptime)", "≥ 99,5 %", "Medida con monitoreo externo; el POS es crítico en horario de atención (06h00–22h00)."],
  ["TTFB (Time to First Byte)", "≤ 0,8 s", "Latencia del servidor en la nube ante cada petición."],
];
const seguridad = [
  ["Cifrado en tránsito", "HTTPS/TLS 1.3 obligatorio en el 100 % de las páginas (candado y HSTS)."],
  ["Autenticación", "Contraseñas con hash (bcrypt) y roles diferenciados: cajero, gerente, administrador."],
  ["Protección de datos personales", "Cumplimiento de la LOPDP ecuatoriana: consentimiento, minimización y derecho de eliminación de datos de socios."],
  ["Inyección SQL", "Consultas 100 % parametrizadas (ya implementado en el código con placeholders de sqlite3)."],
  ["Respaldos", "Copia automática diaria de la base de datos con retención de 30 días y prueba de restauración mensual."],
  ["Auditoría de accesos", "Registro (log) de inicios de sesión y de operaciones sensibles: anulación de ventas, cambios de precios."],
];

const inteligencia = [
  H1("4. Reporte de Inteligencia de Negocios"),
  H2("4.1 Resultados de la segmentación RFM"),
  P("El algoritmo RFM se ejecutó sobre las 2.961 transacciones históricas de los 350 socios. Cada dimensión (Recencia, Frecuencia, Monetario) se puntuó de 1 a 5 por quintiles y la combinación de puntajes asignó la etiqueta estratégica:"),
  ...IMG(DOCS + "captura_rfm.png", 560, 200, "Figura 8. Salida real del cálculo RFM sobre la base de socios."),
  tabla(["Segmento", "Socios", "% base", "Gasto prom. (USD)", "Acción estratégica recomendada"], rfmFilas, [1750, 800, 800, 1300, 4710]),
  P(""),
  P("Lectura gerencial: el 16 % de los socios (VIP) genera un gasto promedio 7,8 veces mayor que el segmento Perdido, por lo que protegerlos es la prioridad número uno. El hallazgo más accionable es el segmento Recuperable (18 % de la base con gasto histórico alto): es exactamente la población sobre la que el módulo CRM dispara sus alertas, uniendo la analítica (RFM) con la operación (CRM) en un mismo ciclo de decisión."),
  H2("4.2 Auditoría web: KPIs de desempeño y seguridad para el despliegue en la nube"),
  P("Si el sistema se desplegara como aplicación web en la nube, se auditarían los siguientes indicadores de desempeño (Core Web Vitals de Google) con umbrales de la categoría \u201cbueno\u201d:"),
  tabla(["KPI de desempeño", "Umbral objetivo", "Aplicación en FitCore"], cwv, [2600, 1300, 5460]),
  P(""),
  P("Y los siguientes controles y KPIs de seguridad:"),
  tabla(["Control de seguridad", "Criterio de auditoría"], seguridad, [2600, 6760]),
  H2("4.3 Dashboard gerencial e interpretación"),
  ...IMG(DATA + "dashboard.png", 640, 384, "Figura 9. Tablero de control gerencial generado por el sistema (Matplotlib), actualizado tras la venta en vivo."),
  BULLET(" muestra el crecimiento sostenido de la facturación semanal conforme se incorporan socios, con picos regulares que coinciden con las renovaciones mensuales de membresías; la caída del extremo derecho corresponde a la semana en curso (incompleta).", "Panel 1 (Ventas):"),
  BULLET(" la base está balanceada pero con un 22 % de socios perdidos y un 18 % recuperables: casi 4 de cada 10 socios requieren acción de retención, lo que valida la inversión en el módulo CRM.", "Panel 2 (RFM):"),
  BULLET(" ingresos acumulados de USD 130.577 frente a gastos de reposición de USD 1.100 en el período; el indicador SCM muestra que la Proteína Whey es el producto más pedido a proveedores, información clave para negociar volumen.", "Panel 3 (ERP/SCM):"),
  BULLET(" los 137 socios en riesgo, ordenados por días de inactividad, dan a la gerencia una lista de trabajo priorizada para las campañas de recuperación.", "Panel 4 (CRM):"),
  salto(),
];

// ============================================ 5. CONCLUSIONES Y ANEXOS
const cierre = [
  H1("5. Conclusiones y Recomendaciones"),
  BULLET("La integración por bus de eventos demostró que una sola acción de negocio (una venta) puede actualizar contabilidad, abastecimiento y gestión de clientes sin intervención humana, eliminando los silos de información de la operación manual."),
  BULLET("La combinación RFM + CRM convierte la analítica en operación: los segmentos no se quedan en un gráfico, sino que alimentan alertas accionables con nombre y apellido."),
  BULLET("Se recomienda como siguiente fase: migrar la interfaz a web (Flask/Streamlit) manteniendo la misma capa de dominio, incorporar autenticación por roles y evolucionar el CRM hacia un modelo predictivo de churn entrenado con el histórico del propio sistema."),
  H1("6. Anexos"),
  Prich([["Repositorio de código fuente: ", { bold: true }], ["[ENLACE AL REPOSITORIO EN GITHUB]", { color: AZUL }]]),
  P("Instrucciones de ejecución: (1) instalar dependencias con pip install pandas matplotlib; (2) generar la base con python preparar_datos.py; (3) ejecutar la demo integral con python demo_integracion.py o el sistema interactivo con python main.py. El dashboard se genera en data/dashboard.png."),
  P("Dataset base de clientes: Gym Customers Features and Churn (Kaggle, adrianvinueza). Al describir perfiles y no transacciones, el histórico transaccional se simuló de forma coherente con cada perfil: la frecuencia de compra sigue la variable Avg_class_frequency_total y los socios con Churn = 1 interrumpen sus compras entre 45 y 180 días antes de la fecha actual, lo que permite que el CRM y el RFM detecten deserción real."),
];

// ============================================================= DOCUMENTO
const doc = new Document({
  numbering: {
    config: [{
      reference: "vinetas",
      levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022",
        style: { paragraph: { indent: { left: convertInchesToTwip(0.35), hanging: convertInchesToTwip(0.2) } } } }],
    }],
  },
  styles: {
    default: { document: { run: { font: "Calibri", size: 22 } } },
  },
  features: { updateFields: true },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1200, bottom: 1200, left: 1300, right: 1300 },
      },
    },
    children: [...portada, ...resumen, salto(), ...estrategia, ...tecnica, ...inteligencia, ...cierre],
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync("/home/claude/fitcore/docs/Informe_Final_FitCore.docx", buf);
  console.log("Informe generado.");
});
