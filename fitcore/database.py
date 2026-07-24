"""
database.py - Capa de Persistencia (SQLite)
===========================================
Cumple el requisito 2.1: "persistencia de datos (archivos CSV o Base de Datos)".
Se eligió SQLite porque:
  1. Viene incluido en Python (cero instalación).
  2. Permite consultas SQL reales para RFM y CRM (ventaja frente a CSV).
  3. Un solo archivo (data/fitcore.db) = fácil de entregar y respaldar.

Modelo de datos (refleja el Diagrama ER del informe):
  clientes(1) --- (N)ventas(1) --- (N)detalle_venta(N) --- (1)productos
  productos(N) --- (1)proveedores            (vía ordenes_compra del SCM)
  ventas(1) --- (1)asientos_contables        (generados por el ERP)
  clientes(1) --- (N)alertas_crm             (generadas por el CRM)
"""

import sqlite3
import os

RUTA_BD = os.path.join(os.path.dirname(__file__), "data", "fitcore.db")


def obtener_conexion():
    """Devuelve una conexión a la BD con filas accesibles por nombre de columna."""
    conexion = sqlite3.connect(RUTA_BD)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion


def crear_tablas():
    """Crea el esquema completo del ecosistema (Core + ERP + SCM + CRM)."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # ---------------- SISTEMA CORE (negocio principal: gimnasio) -------------
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS clientes (
        id_cliente              INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre                  TEXT NOT NULL,
        genero                  TEXT,
        edad                    INTEGER,
        telefono                TEXT,
        vive_cerca              INTEGER DEFAULT 0,   -- Near_Location (Kaggle)
        empresa_convenio        INTEGER DEFAULT 0,   -- Partner (Kaggle)
        promo_amigos            INTEGER DEFAULT 0,   -- Promo_friends (Kaggle)
        meses_contrato          INTEGER DEFAULT 1,   -- Contract_period (Kaggle)
        clases_grupales         INTEGER DEFAULT 0,   -- Group_visits (Kaggle)
        frecuencia_semanal      REAL DEFAULT 0,      -- Avg_class_frequency (Kaggle)
        meses_antiguedad        INTEGER DEFAULT 0,   -- Lifetime (Kaggle)
        abandono_historico      INTEGER DEFAULT 0,   -- Churn (Kaggle, para CRM)
        fecha_registro          TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS productos (
        id_producto     INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre          TEXT NOT NULL,
        categoria       TEXT NOT NULL,      -- 'Membresía' | 'Clase' | 'Producto'
        precio          REAL NOT NULL,
        costo           REAL NOT NULL,      -- para el ERP (margen)
        stock           INTEGER,            -- NULL para servicios (membresías/clases)
        stock_minimo    INTEGER,            -- umbral que dispara al SCM
        id_proveedor    INTEGER REFERENCES proveedores(id_proveedor)
    );

    CREATE TABLE IF NOT EXISTS ventas (
        id_venta        INTEGER PRIMARY KEY AUTOINCREMENT,
        id_cliente      INTEGER NOT NULL REFERENCES clientes(id_cliente),
        fecha           TEXT NOT NULL,
        total           REAL NOT NULL
    );

    CREATE TABLE IF NOT EXISTS detalle_venta (
        id_detalle      INTEGER PRIMARY KEY AUTOINCREMENT,
        id_venta        INTEGER NOT NULL REFERENCES ventas(id_venta),
        id_producto     INTEGER NOT NULL REFERENCES productos(id_producto),
        cantidad        INTEGER NOT NULL,
        precio_unitario REAL NOT NULL,
        subtotal        REAL NOT NULL
    );

    -- ---------------- MÓDULO ERP (mini-financiero) --------------------------
    CREATE TABLE IF NOT EXISTS asientos_contables (
        id_asiento      INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha           TEXT NOT NULL,
        descripcion     TEXT NOT NULL,
        cuenta_debe     TEXT NOT NULL,
        cuenta_haber    TEXT NOT NULL,
        monto           REAL NOT NULL,
        id_venta        INTEGER REFERENCES ventas(id_venta),
        id_orden        INTEGER REFERENCES ordenes_compra(id_orden)
    );

    -- ---------------- MÓDULO SCM (inventario / proveedores) -----------------
    CREATE TABLE IF NOT EXISTS proveedores (
        id_proveedor    INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre          TEXT NOT NULL,
        contacto        TEXT,
        dias_entrega    INTEGER DEFAULT 3
    );

    CREATE TABLE IF NOT EXISTS ordenes_compra (
        id_orden        INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha           TEXT NOT NULL,
        id_proveedor    INTEGER NOT NULL REFERENCES proveedores(id_proveedor),
        id_producto     INTEGER NOT NULL REFERENCES productos(id_producto),
        cantidad        INTEGER NOT NULL,
        costo_total     REAL NOT NULL,
        estado          TEXT DEFAULT 'PENDIENTE'   -- PENDIENTE | RECIBIDA
    );

    -- ---------------- MÓDULO CRM (relación con el cliente) ------------------
    CREATE TABLE IF NOT EXISTS alertas_crm (
        id_alerta       INTEGER PRIMARY KEY AUTOINCREMENT,
        id_cliente      INTEGER NOT NULL REFERENCES clientes(id_cliente),
        fecha_alerta    TEXT NOT NULL,
        tipo            TEXT NOT NULL,      -- 'RIESGO_DESERCION'
        detalle         TEXT,
        dias_inactivo   INTEGER,
        atendida        INTEGER DEFAULT 0
    );

    -- ---------------- ANALÍTICA (resultados RFM persistidos) ----------------
    CREATE TABLE IF NOT EXISTS segmentos_rfm (
        id_cliente      INTEGER PRIMARY KEY REFERENCES clientes(id_cliente),
        recencia_dias   INTEGER,
        frecuencia      INTEGER,
        monetario       REAL,
        puntaje_r       INTEGER,
        puntaje_f       INTEGER,
        puntaje_m       INTEGER,
        segmento        TEXT,
        fecha_calculo   TEXT
    );
    """)
    conexion.commit()
    conexion.close()


def reiniciar_bd():
    """Borra la BD (útil para regenerar la demo desde cero)."""
    if os.path.exists(RUTA_BD):
        os.remove(RUTA_BD)
    crear_tablas()
