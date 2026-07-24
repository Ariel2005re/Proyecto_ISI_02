# FitCore Gym — Ecosistema Integrado de Sistemas de Información

**Proyecto Final ISID223 — Transformación Digital Empresarial (EPN-FIS, 2025-B)**

Digitalización de una PYME (gimnasio) mediante un ecosistema integrado:
Sistema Core (POS de membresías, clases y productos) + módulos ERP, SCM y CRM
comunicados por un **bus de eventos** (patrón Observador), con segmentación
RFM y Dashboard gerencial.

## Estructura del proyecto

```
fitcore/
├── main.py               # Menú principal del sistema (punto de entrada)
├── demo_integracion.py   # Demo automática (guion de la defensa)
├── preparar_datos.py     # Carga clientes (Kaggle) + histórico transaccional
├── database.py           # Capa de persistencia SQLite (esquema completo)
├── events.py             # Bus de eventos (integración entre sistemas)
├── core/
│   ├── modelos.py        # Clases POO: Cliente, Producto, Membresía, Venta...
│   └── sistema_core.py   # Sistema principal (POS) — publica eventos
├── modules/
│   ├── erp.py            # ERP: asientos contables automáticos
│   ├── scm.py            # SCM: órdenes de compra automáticas por stock bajo
│   └── crm.py            # CRM: alertas de riesgo de deserción
├── analytics/
│   └── rfm.py            # Segmentación RFM (Fase 3)
├── dashboard/
│   └── tablero.py        # Dashboard gerencial 2x2 (Matplotlib)
└── data/
    ├── gym_churn.csv     # (colocar aquí el dataset de Kaggle)
    ├── fitcore.db        # Base de datos SQLite (se genera)
    └── dashboard.png     # Tablero de control (se genera)
```

## Requisitos

- Python 3.10+
- `pip install pandas matplotlib`

## Instalación y ejecución

```bash
# 1. Colocar gym_churn.csv (Kaggle) en data/  — opcional pero recomendado
# 2. Generar la base de datos con clientes e histórico:
python preparar_datos.py

# 3a. Demo automática (recomendada para la defensa):
python demo_integracion.py

# 3b. O sistema interactivo con menú:
python main.py
```

## Flujo de integración (requisito 2.3)

```
VENTA (Core) ──publica──> 'venta_registrada' ──> ERP crea asiento contable
     │                                       └─> CRM cierra alerta si el cliente estaba en riesgo
     └── stock <= mínimo ──> 'stock_bajo' ─────> SCM genera orden de compra
                                                      │
                                  'orden_generada' ───┘──> ERP registra el gasto
```

Ninguna de estas reacciones requiere intervención humana: los módulos se
suscriben al bus de eventos al iniciar el sistema.

## Dataset

Base de clientes construida a partir de
[Gym Customers Features and Churn (Kaggle)](https://www.kaggle.com/datasets/adrianvinueza/gym-customers-features-and-churn).
Como el dataset describe perfiles (no transacciones), el histórico de ventas
se simula de forma coherente con cada perfil: la frecuencia de compra sigue
`Avg_class_frequency_total` y los clientes con `Churn = 1` dejan de comprar
45–180 días atrás (lo que permite que el CRM y el RFM detecten deserción real).

## Autores

- [Integrante 1]
- [Integrante 2]
