import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json

# ------------------------
# 🔗 CONEXIÓN GOOGLE SHEETS
# ------------------------
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

if "gcp_service_account" in st.secrets:
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
else:
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)

client = gspread.authorize(creds)

SHEET_ID = "18qN6miXJOTj46FZfRKxQ4Lpcx3BB-MXg-aNJvc96kLc"
sheet = client.open_by_key(SHEET_ID)

pedidos_ws = sheet.worksheet("PEDIDOS")
recepciones_ws = sheet.worksheet("RECEPCIONES")
entregas_ws = sheet.worksheet("ENTREGA")

# ------------------------
# 📊 FUNCIONES DE DATOS
def get_data(ws):
    # Leemos todo el contenido de la hoja
    raw_data = ws.get_all_values()
    if len(raw_data) < 4:
        return pd.DataFrame()
    
    # La fila 4 (índice 3 en Python) tiene los encabezados
    headers = [header.strip() for header in raw_data[3]]
    # Los datos reales empiezan en la fila 5 (índice 4)
    data = raw_data[4:]
    
    df = pd.DataFrame(data, columns=headers)
    
    # Limpieza: eliminar filas vacías y convertir cantidades a números
    df = df[df[headers[0]] != ""] # Filtra si la primera columna está vacía
    for col in df.columns:
        if "CANTIDAD" in col.upper():
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df


# ------------------------
# 📊 FUNCIONES LÓGICAS
# ------------------------
def calcular_estado(df_pedidos, df_rec, df_ent):

    estados = []

    df_pedidos.columns = [c.strip() for c in df_pedidos.columns]
    df_rec.columns = [c.strip() for c in df_rec.columns]
    df_ent.columns = [c.strip() for c in df_ent.columns]

    for _, row in df_pedidos.iterrows():
        pid = row["ID"]
        solicitado = row["CANTIDAD"]
        producto = row.get("PRODUCTO", "N/A")

        recibido = df_rec[df_rec["ID_PEDIDO"] == pid]["CANTIDAD"].sum() if "ID_PEDIDO" in df_rec.columns else 0 
        entregado = df_ent[df_ent["ID_PEDIDOS"] == pid]["CANTIDAD"].sum() if "ID_PEDIDOS" in df_ent.columns else 0

        disponible = recibido - entregado
        faltante = solicitado - recibido

        if recibido == 0:
            estado = "🔴 Pendiente"
        elif faltante > 0:
            estado = "🟡 Parcial"
        else:
            estado = "🟢 Completo"

        estados.append({
            "ID": pid,
            "PRODUCTO": producto,
            "SOLICITADO": solicitado,
            "RECIBIDO": recibido,
            "ENTREGADO": entregado,
            "DISPONIBLE": disponible,
            "ESTADO": estado
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
        pedido = st.selectbox("Pedido", df_pedidos["ID"])
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
        pedido = st.selectbox("Pedido", df_pedidos["ID"])
        cantidad = st.number_input("Cantidad a entregar", min_value=1)
        persona = st.text_input("Entregado a")
        sede = st.text_input("Sede / Área")
        destino = st.text_input("Destino")

        # calcular disponible
        recibido = df_rec[df_rec["ID_PEDIDO"] == pedido]["CANTIDAD"].sum()
        entregado = df_ent[df_ent["ID_PEDIDOS"] == pedido]["CANTIDAD"].sum()
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
        st.warning("No hay pedidos registrados en la hoja de Excel (Fila 5 en adelante).")
    else:
        # Llamamos a la función y mostramos el resultado
        with st.spinner('Calculando inventario...'):
            df_estado = calcular_estado(df_pedidos, df_rec, df_ent)
            
            # Mostramos métricas rápidas arriba
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Pedidos", len(df_estado))
            c2.metric("En Stock", int(df_estado["DISPONIBLE"].sum()))
            c3.metric("Por Recibir", int(df_estado["SOLICITADO"].sum() - df_estado["RECIBIDO"].sum()))

            # Mostramos la tabla principal
            st.dataframe(df_estado, use_container_width=True)
