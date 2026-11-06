from pathlib import Path

import numpy as np
import plotly.express as px
import pysd
import streamlit as st


ROOT_DIR = Path(__file__).resolve().parent
COLOR_PALETTE = [
    "#0B3C5D",
    "#145DA0",
    "#00A6D6",
    "#3CC8E8",
    "#7AE7FF",
    "#B8F2FF",
]

MODELS = {
    " [<] Modelo 1: Publicidad y SaaS": {
        "title": "Modelo 1: Adopción SaaS y Publicidad",
        "model_path": ROOT_DIR / "Modelos" / "Prob01-Publicidad.mdl",
        "causal_image": ROOT_DIR / "static" / "Causales" / "Prob01-Publicidad.bmp",
        "forrester_image": ROOT_DIR / "static" / "Forrester" / "Prob01F-Publicidad.png",
        "stocks": {
            "Usuarios Potenciales": "Usuario Potenciales",
            "Usuarios Activos": "Usuarios Activos",
            "Usuarios Inactivos": "UsuariosInactivos",
        },
        "variables": [
            (
                "Usuarios Potenciales",
                "Mercado objetivo que aún no ha adquirido el servicio.",
                "Valor Inicial: 100000",
            ),
            (
                "Usuarios Activos",
                "Personas que actualmente utilizan y pagan por el servicio.",
                "Valor Inicial: 0",
            ),
            (
                "Usuarios Inactivos",
                "Ex-clientes que cancelaron la suscripción pero pueden ser recuperados.",
                "Valor Inicial: 0",
            ),
            (
                "Adquisicion por Marketing",
                "Nuevos usuarios mensuales logrados mediante publicidad.",
                "Valor: 500",
            ),
            (
                "Tasa de Contacto",
                "Interacciones de un usuario activo al mes.",
                "Valor: 5",
            ),
            (
                "Fraccion de Adopcion Viral",
                "Probabilidad de conversión por recomendación.",
                "Valor: 0.02",
            ),
            (
                "Tiempo Medio de Retencion",
                "Meses promedio que un cliente se queda antes de cancelar.",
                "Valor: 12",
            ),
            (
                "Efectividad de Remarketing",
                "Porcentaje de ex-clientes recuperados al mes.",
                "Valor: 0.05",
            ),
        ],
    },
    " [>] Modelo 2: Gestión de Inventario": {
        "title": "Modelo 2: Gestión de Inventario",
        "model_path": ROOT_DIR / "Modelos" / "Prob02-Inventario.mdl",
        "causal_image": ROOT_DIR / "static" / "Causales" / "Prob02-Inventario.jpg",
        "forrester_image": ROOT_DIR / "static" / "Forrester" / "Prob02F-Inventario.png",
        "stocks": {
            "Ordenes en Transito": "Ordenes en transito",
            "Inventario en Almacen": "Inventario en Almacen",
            "Mercaderia Entregada": "Mercaderia Entregada",
        },
        "variables": [
            (
                "Ordenes en Transito",
                "Mercadería que ya se pidió al proveedor pero que viaja en los camiones.",
                "Valor Inicial: 0",
            ),
            (
                "Inventario en Almacen",
                "Mercadería física lista para ser vendida.",
                "Valor Inicial: 500",
            ),
            (
                "Mercaderia Entregada",
                "Nivel que acumula todo el histórico de ventas despachadas.",
                "Valor Inicial: 0",
            ),
            (
                "Capacidad Deseada",
                "Nivel de stock físico objetivo que se busca mantener.",
                "Valor: 600",
            ),
            (
                "Tiempo de Ajuste",
                "Días que tarda administración en procesar órdenes.",
                "Valor: 2",
            ),
            (
                "Tiempo de Proveedor",
                "Retraso logístico (lead time) en días.",
                "Valor: 5",
            ),
            (
                "Demanda de Clientes",
                "Cajas diarias solicitadas por el mercado.",
                "Valor: 40",
            ),
            (
                "Tiempo Minimo de Despacho",
                "Restricción física de salida en días.",
                "Valor: 1",
            ),
        ],
    },
}


@st.cache_data(show_spinner="Ejecutando simulación...")
def run_simulation(model_path: str):
    """Carga un modelo Vensim y devuelve sus resultados simulados."""
    model = pysd.read_vensim(model_path)
    return model.run()


def show_diagram(title: str, image_path: Path) -> None:
    with st.expander(title):
        if image_path.is_file():
            st.image(str(image_path), use_container_width=True)
        else:
            st.warning(f"No se encontró la imagen: {image_path}")


def show_variable_dictionary(variables: list[tuple[str, str, str]]) -> None:
    with st.expander("Diccionario de Variables"):
        markdown = "\n".join(
            f"- **{name}:** {description} ({value})."
            for name, description, value in variables
        )
        st.markdown(markdown)


def filter_integer_times(results):
    """Conserva las observaciones cuyo índice de tiempo es entero."""
    times = results.index.to_numpy(dtype=float)
    integer_time_mask = np.isclose(times, np.rint(times))
    return results.loc[integer_time_mask]


def main() -> None:
    st.set_page_config(page_title="Modelos de Dinámica de Sistemas", layout="wide")

    selected_model_name = st.sidebar.radio("Selecciona un modelo", list(MODELS))
    model_config = MODELS[selected_model_name]

    st.title(model_config["title"])
    show_diagram("Diagrama Causal", model_config["causal_image"])
    show_diagram("Diagrama de Forrester", model_config["forrester_image"])
    show_variable_dictionary(model_config["variables"])

    try:
        results = run_simulation(str(model_config["model_path"]))
    except Exception as error:
        st.error(f"No se pudo ejecutar el modelo Vensim: {error}")
        return

    integer_results = filter_integer_times(results)
    stock_names = list(model_config["stocks"])
    selected_stocks = st.multiselect(
        "Variables de nivel (stocks) para visualizar",
        options=stock_names,
        default=stock_names,
    )

    selected_columns = [
        model_config["stocks"][stock_name] for stock_name in selected_stocks
    ]
    display_data = integer_results[selected_columns].rename(
        columns={
            model_config["stocks"][stock_name]: stock_name
            for stock_name in selected_stocks
        }
    )
    display_data.index.name = "Tiempo"
    display_data = display_data.reset_index()

    if selected_stocks:
        fig = px.line(
            display_data,
            x="Tiempo",
            y=selected_stocks,
            title=f"Simulación: {model_config['title']}",
            labels={"Tiempo": "Tiempo", "value": "Unidades", "variable": "Variable"},
            color_discrete_sequence=COLOR_PALETTE,
            template="plotly_dark",
        )
        fig.update_layout(showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Selecciona al menos una variable de nivel para mostrar el gráfico.")

    st.subheader("Datos de la simulación (DT = 1)")
    st.dataframe(display_data, use_container_width=True)


if __name__ == "__main__":
    main()
