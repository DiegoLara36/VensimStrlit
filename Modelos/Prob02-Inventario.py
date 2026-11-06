"""
Python model 'Prob02-Inventario.py'
Translated using PySD
"""

from pathlib import Path
import numpy as np

from pysd.py_backend.statefuls import Integ
from pysd import Component

__pysd_version__ = "3.14.3"

__data = {"scope": None, "time": lambda: 0}

_root = Path(__file__).parent


component = Component()

#######################################################################
#                          CONTROL VARIABLES                          #
#######################################################################

_control_vars = {
    "initial_time": lambda: 0,
    "final_time": lambda: 60,
    "time_step": lambda: 1,
    "saveper": lambda: time_step(),
}


def _init_outer_references(data):
    for key in data:
        __data[key] = data[key]


@component.add(name="Time")
def time():
    """
    Current time of the model.
    """
    return __data["time"]()


@component.add(
    name="FINAL TIME", units="Day", comp_type="Constant", comp_subtype="Normal"
)
def final_time():
    """
    The final time for the simulation.
    """
    return __data["time"].final_time()


@component.add(
    name="INITIAL TIME", units="Day", comp_type="Constant", comp_subtype="Normal"
)
def initial_time():
    """
    The initial time for the simulation.
    """
    return __data["time"].initial_time()


@component.add(
    name="SAVEPER",
    units="Day",
    limits=(0.0, np.nan),
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time_step": 1},
)
def saveper():
    """
    The frequency with which output is stored.
    """
    return __data["time"].saveper()


@component.add(
    name="TIME STEP",
    units="Day",
    limits=(0.0, np.nan),
    comp_type="Constant",
    comp_subtype="Normal",
)
def time_step():
    """
    The time step for the simulation.
    """
    return __data["time"].time_step()


#######################################################################
#                           MODEL VARIABLES                           #
#######################################################################


@component.add(name="Capacidad Deseada", comp_type="Constant", comp_subtype="Normal")
def capacidad_deseada():
    return 600


@component.add(
    name="Demanda de Clientes",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"time": 1},
)
def demanda_de_clientes():
    return float(np.random.uniform(15, 40, size=()))


@component.add(
    name="Inventario en Almacen",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_inventario_en_almacen": 1},
    other_deps={
        "_integ_inventario_en_almacen": {
            "initial": {},
            "step": {"tasa_de_recepcion": 1, "tasa_de_despacho": 1},
        }
    },
)
def inventario_en_almacen():
    return _integ_inventario_en_almacen()


_integ_inventario_en_almacen = Integ(
    lambda: tasa_de_recepcion() - tasa_de_despacho(),
    lambda: 500,
    "_integ_inventario_en_almacen",
)


@component.add(
    name="Mercaderia Entregada",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_mercaderia_entregada": 1},
    other_deps={
        "_integ_mercaderia_entregada": {"initial": {}, "step": {"tasa_de_despacho": 1}}
    },
)
def mercaderia_entregada():
    return _integ_mercaderia_entregada()


_integ_mercaderia_entregada = Integ(
    lambda: tasa_de_despacho(), lambda: 0, "_integ_mercaderia_entregada"
)


@component.add(
    name="Ordenes en transito",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_ordenes_en_transito": 1},
    other_deps={
        "_integ_ordenes_en_transito": {
            "initial": {},
            "step": {"tasa_de_pedidos": 1, "tasa_de_recepcion": 1},
        }
    },
)
def ordenes_en_transito():
    return _integ_ordenes_en_transito()


_integ_ordenes_en_transito = Integ(
    lambda: tasa_de_pedidos() - tasa_de_recepcion(),
    lambda: 0,
    "_integ_ordenes_en_transito",
)


@component.add(
    name="Posicion de Inventario",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"inventario_en_almacen": 1, "ordenes_en_transito": 1},
)
def posicion_de_inventario():
    return inventario_en_almacen() + ordenes_en_transito()


@component.add(
    name="Tasa de despacho",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "demanda_de_clientes": 1,
        "inventario_en_almacen": 1,
        "tiempo_minimo_de_despacho": 1,
    },
)
def tasa_de_despacho():
    return float(
        np.minimum(
            demanda_de_clientes(), inventario_en_almacen() / tiempo_minimo_de_despacho()
        )
    )


@component.add(
    name="Tasa de Pedidos",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "capacidad_deseada": 1,
        "posicion_de_inventario": 1,
        "tiempo_de_ajuste": 1,
    },
)
def tasa_de_pedidos():
    return float(
        np.maximum(
            0, (capacidad_deseada() - posicion_de_inventario()) / tiempo_de_ajuste()
        )
    )


@component.add(
    name="Tasa de recepcion",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"ordenes_en_transito": 1, "tiempo_de_proovedor": 1},
)
def tasa_de_recepcion():
    return ordenes_en_transito() / tiempo_de_proovedor()


@component.add(name="Tiempo de Ajuste", comp_type="Constant", comp_subtype="Normal")
def tiempo_de_ajuste():
    return 2


@component.add(name="Tiempo de Proovedor", comp_type="Constant", comp_subtype="Normal")
def tiempo_de_proovedor():
    return 5


@component.add(
    name="Tiempo minimo de despacho", comp_type="Constant", comp_subtype="Normal"
)
def tiempo_minimo_de_despacho():
    return 0.25
