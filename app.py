import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# ------------------------
# 🔗 CONEXIÓN GOOGLE SHEETS
# ------------------------
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

SHEET_NAME = "control_pedidos"
sheet = client.open(SHEET_NAME)

pedidos_ws = sheet.worksheet("pedidos")
recepciones_ws = sheet.worksheet("recepciones")
entregas_ws = sheet.worksheet("entregas")


def get_data(ws):
    data = ws.get_all_records()
    return pd.DataFrame(data)


# ------------------------
# 📊 FUNCIONES LÓGICAS
# ------------------------
def calcular_estado(df_pedidos, df_rec, df_ent):
    estados = []

    for _, row in df_pedidos.iterrows():
        pid = row["id"]
        solicitado = row["cantidad"]

        recibido = df_rec[df_rec["id_pedido"] == pid]["cantidad"].sum()
        entregado = df_ent[df_ent["id_pedido"] == pid]["cantidad"].sum()

        disponible = recibido - entregado
        faltante = solicitado - recibido

        if recibido == 0:
            estado = "Pendiente"
        elif faltante > 0:
            estado = "Parcial"
        else:
            estado = "Completo"

        estados.append({
            "id": pid,
            "producto": row["producto"],
            "solicitado": solicitado,
            "recibido": recibido,
            "entregado": entregado,
            "disponible": disponible,
            "estado": estado
        })

    return pd.DataFrame(estados)


# ------------------------
# 🧭 UI
# ------------------------
st.title("📦 Control de Pedidos")

menu = st.sidebar.selectbox("Menú", [
    "Crear Pedido",
    "Registrar Recepción",
    "Registrar Entrega",
    "Dashboard"
])

df_pedidos = get_data(pedidos_ws)
df_rec = get_data(recepciones_ws)
df_ent = get_data(entregas_ws)

# ------------------------
# 🧾 CREAR PEDIDO
# ------------------------
if menu == "Crear Pedido":
    st.header("🧾 Nuevo Pedido")

    producto = st.text_input("Producto")
    cantidad = st.number_input("Cantidad", min_value=1)
    proveedor = st.text_input("Proveedor")
    solicitante = st.text_input("Solicitante")

    if st.button("Guardar"):
        new_id = f"PED-{len(df_pedidos)+1:03d}"

        pedidos_ws.append_row([
            new_id,
            producto,
            cantidad,
            proveedor,
            solicitante,
            datetime.now().strftime("%Y-%m-%d")
        ])

        st.success("Pedido creado")

# ------------------------
# 📥 RECEPCIÓN
# ------------------------
elif menu == "Registrar Recepción":
    st.header("📥 Registrar Recepción")

    if df_pedidos.empty:
        st.warning("No hay pedidos")
    else:
        pedido = st.selectbox("Pedido", df_pedidos["id"])
        cantidad = st.number_input("Cantidad recibida", min_value=1)

        if st.button("Registrar"):
            recepciones_ws.append_row([
                pedido,
                datetime.now().strftime("%Y-%m-%d"),
                cantidad
            ])
            st.success("Recepción registrada")

# ------------------------
# 📤 ENTREGA
# ------------------------
elif menu == "Registrar Entrega":
    st.header("📤 Registrar Entrega")

    if df_pedidos.empty:
        st.warning("No hay pedidos")
    else:
        pedido = st.selectbox("Pedido", df_pedidos["id"])
        cantidad = st.number_input("Cantidad a entregar", min_value=1)
        persona = st.text_input("Entregado a")
        sede = st.text_input("Sede / Área")
        destino = st.text_input("Destino")

        # calcular disponible
        recibido = df_rec[df_rec["id_pedido"] == pedido]["cantidad"].sum()
        entregado = df_ent[df_ent["id_pedido"] == pedido]["cantidad"].sum()
        disponible = recibido - entregado

        st.info(f"Disponible: {disponible}")

        if st.button("Registrar Entrega"):
            if cantidad > disponible:
                st.error("No hay suficiente inventario")
            else:
                entregas_ws.append_row([
                    pedido,
                    datetime.now().strftime("%Y-%m-%d"),
                    cantidad,
                    persona,
                    sede,
                    destino
                ])
                st.success("Entrega registrada")

# ------------------------
# 📊 DASHBOARD
# ------------------------
elif menu == "Dashboard":
    st.header("📊 Estado de Pedidos")

    if df_pedidos.empty:
        st.warning("No hay datos")
    else:
        df_estado = calcular_estado(df_pedidos, df_rec, df_ent)
        st.dataframe(df_estado)