"""
preparar_datos.py - Carga inicial de datos (ejecutar UNA sola vez)
==================================================================
Problema de diseño resuelto aquí (explicarlo en el informe):
El dataset de Kaggle (gym churn) describe PERFILES de clientes (edad,
contrato, frecuencia, churn) pero NO contiene transacciones con fecha y
monto, que son indispensables para RFM y para el dashboard temporal.

Solución: usamos Kaggle como BASE DE CLIENTES y, a partir de cada perfil,
SIMULAMOS su histórico transaccional de los últimos 12 meses de forma
coherente:
  - Frecuencia de compra proporcional a Avg_class_frequency_total.
  - Gasto adicional proporcional a Avg_additional_charges_total.
  - Si Churn = 1, el cliente dejó de comprar hace 45-180 días
    (así el CRM y el RFM detectan deserción REAL, no inventada al azar).

Uso:
    python preparar_datos.py            # busca data/gym_churn.csv; si no
                                        # existe, genera perfiles sintéticos
"""

import os
import random
from datetime import datetime, timedelta

import pandas as pd

from database import reiniciar_bd, obtener_conexion, RUTA_BD

random.seed(42)  # reproducibilidad de la demo

RUTA_CSV_KAGGLE = os.path.join(os.path.dirname(__file__), "data", "gym_churn.csv")
NUM_CLIENTES = 350          # subconjunto del dataset (suficiente y rápido)
HOY = datetime.now()

NOMBRES_F = ["María", "Andrea", "Valeria", "Camila", "Daniela", "Gabriela",
             "Paula", "Carla", "Sofía", "Verónica", "Lucía", "Diana",
             "Fernanda", "Karen", "Michelle", "Nicole", "Emilia", "Doménica"]
NOMBRES_M = ["Juan", "Carlos", "Andrés", "David", "José", "Luis", "Diego",
             "Santiago", "Sebastián", "Mateo", "Daniel", "Kevin", "Bryan",
             "Alejandro", "Ricardo", "Esteban", "Francisco", "Pablo"]
APELLIDOS = ["Pérez", "García", "Rodríguez", "López", "Martínez", "Sánchez",
             "Torres", "Flores", "Vargas", "Castro", "Morales", "Herrera",
             "Jiménez", "Rojas", "Mendoza", "Guerrero", "Salazar", "Cevallos",
             "Andrade", "Espinoza", "Villacís", "Paredes", "Zambrano", "Cárdenas"]


# ---------------------------------------------------------------------------
# 1. CATÁLOGO: proveedores y productos del gimnasio
# ---------------------------------------------------------------------------
def cargar_catalogo(conexion):
    proveedores = [
        ("NutriSport Ecuador", "ventas@nutrisport.ec", 3),
        ("Hidratación Andina", "pedidos@handina.com", 2),
        ("FitAccesorios Quito", "contacto@fitaccesorios.ec", 5),
    ]
    conexion.executemany(
        "INSERT INTO proveedores (nombre, contacto, dias_entrega) VALUES (?,?,?)",
        proveedores,
    )

    # (nombre, categoria, precio, costo, stock, stock_min, id_proveedor)
    productos = [
        # Servicios (sin stock): el core del gimnasio
        ("Membresía Mensual",        "Membresía", 45.00, 12.00, None, None, None),
        ("Membresía Trimestral",     "Membresía", 120.00, 30.00, None, None, None),
        ("Membresía Anual",          "Membresía", 420.00, 95.00, None, None, None),
        ("Clase de Spinning",        "Clase",      6.00,  2.00, None, None, None),
        ("Clase de CrossFit",        "Clase",      8.00,  2.50, None, None, None),
        ("Clase de Yoga",            "Clase",      5.00,  1.80, None, None, None),
        ("Entrenamiento Personal",   "Clase",     20.00,  8.00, None, None, None),
        # Productos físicos (con stock): disparan al SCM
        ("Proteína Whey 1kg",        "Producto",  38.00, 22.00,  60,   15, 1),
        ("Creatina 300g",            "Producto",  25.00, 14.00,  50,   12, 1),
        ("Barra Energética",         "Producto",   2.50,  1.10, 200,   50, 1),
        ("Bebida Isotónica",         "Producto",   1.80,  0.80, 250,   60, 2),
        ("Agua Embotellada",         "Producto",   1.00,  0.35, 300,   80, 2),
        ("Toalla Deportiva",         "Producto",  12.00,  6.00,  40,   10, 3),
        ("Guantes de Entrenamiento", "Producto",  15.00,  7.50,  35,   10, 3),
        ("Shaker FitCore",           "Producto",   8.00,  3.20,  45,   12, 3),
    ]
    conexion.executemany(
        """INSERT INTO productos
             (nombre, categoria, precio, costo, stock, stock_minimo, id_proveedor)
           VALUES (?,?,?,?,?,?,?)""",
        productos,
    )
    conexion.commit()


# ---------------------------------------------------------------------------
# 2. CLIENTES: desde el CSV de Kaggle (o sintéticos con el mismo esquema)
# ---------------------------------------------------------------------------
def cargar_clientes(conexion) -> pd.DataFrame:
    if os.path.exists(RUTA_CSV_KAGGLE):
        print(f"Usando dataset real de Kaggle: {RUTA_CSV_KAGGLE}")
        df = pd.read_csv(RUTA_CSV_KAGGLE)
        # Normalizar nombres de columnas (el CSV de Kaggle usa esta convención)
        df.columns = [c.strip() for c in df.columns]
        df = df.sample(n=min(NUM_CLIENTES, len(df)), random_state=42).reset_index(drop=True)
    else:
        print("AVISO: no se encontró data/gym_churn.csv; generando perfiles sintéticos "
              "con el mismo esquema (reemplazar por el CSV real y volver a ejecutar).")
        df = _perfiles_sinteticos(NUM_CLIENTES)

    filas = []
    for i, p in df.iterrows():
        genero = "M" if int(p.get("gender", random.randint(0, 1))) == 1 else "F"
        nombre = (random.choice(NOMBRES_M if genero == "M" else NOMBRES_F)
                  + " " + random.choice(APELLIDOS))
        antiguedad = int(p.get("Lifetime", 6))
        fecha_registro = (HOY - timedelta(days=30 * max(antiguedad, 1)
                                          + random.randint(0, 29))).strftime("%Y-%m-%d")
        filas.append((
            nombre, genero, int(p.get("Age", 30)),
            f"09{random.randint(10000000, 99999999)}",
            int(p.get("Near_Location", 1)), int(p.get("Partner", 0)),
            int(p.get("Promo_friends", 0)), int(p.get("Contract_period", 1)),
            int(p.get("Group_visits", 0)),
            round(float(p.get("Avg_class_frequency_total", 2.0)), 2),
            antiguedad, int(p.get("Churn", 0)), fecha_registro,
        ))
    conexion.executemany(
        """INSERT INTO clientes
             (nombre, genero, edad, telefono, vive_cerca, empresa_convenio,
              promo_amigos, meses_contrato, clases_grupales, frecuencia_semanal,
              meses_antiguedad, abandono_historico, fecha_registro)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        filas,
    )
    conexion.commit()
    return df


def _perfiles_sinteticos(n: int) -> pd.DataFrame:
    """Genera perfiles con la MISMA estructura estadística del dataset Kaggle."""
    filas = []
    for _ in range(n):
        churn = 1 if random.random() < 0.27 else 0          # ~27% churn (como Kaggle)
        filas.append({
            "gender": random.randint(0, 1),
            "Near_Location": 1 if random.random() < 0.85 else 0,
            "Partner": random.randint(0, 1),
            "Promo_friends": 1 if random.random() < 0.3 else 0,
            "Contract_period": random.choice([1, 1, 1, 6, 12]),
            "Group_visits": random.randint(0, 1),
            "Age": random.randint(18, 41),
            "Avg_additional_charges_total": round(random.uniform(10, 280), 2),
            "Lifetime": random.randint(1, 24) if not churn else random.randint(1, 9),
            "Avg_class_frequency_total": round(random.uniform(0.5, 5.0), 2),
            "Churn": churn,
        })
    return pd.DataFrame(filas)


# ---------------------------------------------------------------------------
# 3. HISTÓRICO TRANSACCIONAL simulado coherente con cada perfil
# ---------------------------------------------------------------------------
def generar_historico(conexion, perfiles: pd.DataFrame):
    clientes = conexion.execute("SELECT * FROM clientes").fetchall()
    productos = conexion.execute("SELECT * FROM productos").fetchall()
    membresias = [p for p in productos if p["categoria"] == "Membresía"]
    clases = [p for p in productos if p["categoria"] == "Clase"]
    fisicos = [p for p in productos if p["categoria"] == "Producto"]

    ventas, detalles = [], []
    id_venta = 0

    for c in clientes:
        # ¿Hasta cuándo compró este cliente?
        if c["abandono_historico"] == 1:
            # Cliente que desertó: su última actividad fue hace 45-180 días
            fin_actividad = HOY - timedelta(days=random.randint(45, 180))
        else:
            # Cliente activo: compró hace poco (0-20 días)
            fin_actividad = HOY - timedelta(days=random.randint(0, 20))

        inicio_actividad = HOY - timedelta(days=30 * max(c["meses_antiguedad"], 1))
        if inicio_actividad >= fin_actividad:
            inicio_actividad = fin_actividad - timedelta(days=30)

        # Membresías: una por período de contrato (1, 6 o 12 meses)
        paso_membresia = {1: 30, 6: 180, 12: 360}.get(c["meses_contrato"], 30)
        memb = {1: membresias[0], 6: membresias[1], 12: membresias[2]}
        producto_memb = memb.get(c["meses_contrato"], membresias[0])
        fecha = inicio_actividad
        while fecha <= fin_actividad:
            id_venta += 1
            f = fecha.strftime("%Y-%m-%d %H:%M:%S")
            ventas.append((id_venta, c["id_cliente"], f, producto_memb["precio"]))
            detalles.append((id_venta, producto_memb["id_producto"], 1,
                             producto_memb["precio"], producto_memb["precio"]))
            fecha += timedelta(days=paso_membresia + random.randint(-3, 3))

        # Compras adicionales (clases sueltas y productos):
        # proporcionales a la frecuencia semanal del perfil Kaggle
        dias_activos = max((fin_actividad - inicio_actividad).days, 15)
        n_compras = max(1, int(dias_activos / 30 * c["frecuencia_semanal"] * 0.9))
        for _ in range(n_compras):
            id_venta += 1
            fecha_v = inicio_actividad + timedelta(
                days=random.randint(0, dias_activos),
                hours=random.randint(6, 21), minutes=random.randint(0, 59))
            f = fecha_v.strftime("%Y-%m-%d %H:%M:%S")
            items = random.sample(
                clases + fisicos, k=random.choices([1, 2, 3], weights=[60, 30, 10])[0])
            total = 0.0
            for item in items:
                cantidad = random.randint(1, 2)
                subtotal = round(item["precio"] * cantidad, 2)
                total += subtotal
                detalles.append((id_venta, item["id_producto"], cantidad,
                                 item["precio"], subtotal))
            ventas.append((id_venta, c["id_cliente"], f, round(total, 2)))

    conexion.executemany(
        "INSERT INTO ventas (id_venta, id_cliente, fecha, total) VALUES (?,?,?,?)",
        ventas,
    )
    conexion.executemany(
        """INSERT INTO detalle_venta
             (id_venta, id_producto, cantidad, precio_unitario, subtotal)
           VALUES (?,?,?,?,?)""",
        detalles,
    )

    # El histórico también genera sus asientos contables (ingresos pasados),
    # para que el KPI financiero del dashboard tenga datos desde el día 1.
    conexion.execute(
        """INSERT INTO asientos_contables
             (fecha, descripcion, cuenta_debe, cuenta_haber, monto, id_venta)
           SELECT fecha, 'Venta histórica #' || id_venta, 'Caja',
                  'Ingresos por Ventas', total, id_venta
           FROM ventas""",
    )
    conexion.commit()
    print(f"Histórico generado: {len(ventas)} ventas, {len(detalles)} líneas de detalle.")


if __name__ == "__main__":
    print("Reiniciando base de datos...")
    reiniciar_bd()
    conexion = obtener_conexion()
    cargar_catalogo(conexion)
    perfiles = cargar_clientes(conexion)
    generar_historico(conexion, perfiles)
    n = conexion.execute("SELECT COUNT(*) c FROM clientes").fetchone()["c"]
    v = conexion.execute("SELECT COUNT(*) c FROM ventas").fetchone()["c"]
    conexion.close()
    print(f"Listo: {n} clientes y {v} ventas en {RUTA_BD}")
