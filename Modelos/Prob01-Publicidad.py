"""
Python model 'Prob01-Publicidad.py'
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
    name="FINAL TIME", units="Month", comp_type="Constant", comp_subtype="Normal"
)
def final_time():
    """
    The final time for the simulation.
    """
    return __data["time"].final_time()


@component.add(
    name="INITIAL TIME", units="Month", comp_type="Constant", comp_subtype="Normal"
)
def initial_time():
    """
    The initial time for the simulation.
    """
    return __data["time"].initial_time()


@component.add(
    name="SAVEPER",
    units="Month",
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
    units="Month",
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


@component.add(
    name="Adquisicion por marketing", comp_type="Constant", comp_subtype="Normal"
)
def adquisicion_por_marketing():
    return 500


@component.add(
    name="Adquisicion Viral",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "usuarios_activos": 1,
        "tasa_de_contacto": 1,
        "fraccion_de_adopcion_viral": 1,
        "usuario_potenciales": 1,
        "poblacion_total_del_mercado": 1,
    },
)
def adquisicion_viral():
    return (
        usuarios_activos()
        * tasa_de_contacto()
        * fraccion_de_adopcion_viral()
        * (usuario_potenciales() / poblacion_total_del_mercado())
    )


@component.add(
    name="Efectividad de remarketing", comp_type="Constant", comp_subtype="Normal"
)
def efectividad_de_remarketing():
    return 0.05


@component.add(
    name="Flujo de Abandono",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"usuarios_activos": 1, "tiempo_medio_de_retencion": 1},
)
def flujo_de_abandono():
    return usuarios_activos() / tiempo_medio_de_retencion()


@component.add(
    name="Flujo de Adquisicion",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"adquisicion_por_marketing": 1, "adquisicion_viral": 1},
)
def flujo_de_adquisicion():
    return adquisicion_por_marketing() + adquisicion_viral()


@component.add(
    name="Flujo de Recuperacion",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={"usuariosinactivos": 1, "efectividad_de_remarketing": 1},
)
def flujo_de_recuperacion():
    return usuariosinactivos() * efectividad_de_remarketing()


@component.add(
    name="Fraccion de adopcion viral", comp_type="Constant", comp_subtype="Normal"
)
def fraccion_de_adopcion_viral():
    return 0.02


@component.add(
    name="Poblacion total del mercado",
    comp_type="Auxiliary",
    comp_subtype="Normal",
    depends_on={
        "usuario_potenciales": 1,
        "usuarios_activos": 1,
        "usuariosinactivos": 1,
    },
)
def poblacion_total_del_mercado():
    return usuario_potenciales() + usuarios_activos() + usuariosinactivos()


@component.add(name="Tasa de Contacto", comp_type="Constant", comp_subtype="Normal")
def tasa_de_contacto():
    return 5


@component.add(
    name="Tiempo medio de retencion", comp_type="Constant", comp_subtype="Normal"
)
def tiempo_medio_de_retencion():
    return 12


@component.add(
    name="Usuario Potenciales",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_usuario_potenciales": 1},
    other_deps={
        "_integ_usuario_potenciales": {
            "initial": {},
            "step": {"flujo_de_recuperacion": 1, "flujo_de_adquisicion": 1},
        }
    },
)
def usuario_potenciales():
    return _integ_usuario_potenciales()


_integ_usuario_potenciales = Integ(
    lambda: flujo_de_recuperacion() - flujo_de_adquisicion(),
    lambda: 100000,
    "_integ_usuario_potenciales",
)


@component.add(
    name="Usuarios Activos",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_usuarios_activos": 1},
    other_deps={
        "_integ_usuarios_activos": {
            "initial": {},
            "step": {"flujo_de_adquisicion": 1, "flujo_de_abandono": 1},
        }
    },
)
def usuarios_activos():
    return _integ_usuarios_activos()


_integ_usuarios_activos = Integ(
    lambda: flujo_de_adquisicion() - flujo_de_abandono(),
    lambda: 0,
    "_integ_usuarios_activos",
)


@component.add(
    name="UsuariosInactivos",
    comp_type="Stateful",
    comp_subtype="Integ",
    depends_on={"_integ_usuariosinactivos": 1},
    other_deps={
        "_integ_usuariosinactivos": {
            "initial": {},
            "step": {"flujo_de_abandono": 1, "flujo_de_recuperacion": 1},
        }
    },
)
def usuariosinactivos():
    return _integ_usuariosinactivos()


_integ_usuariosinactivos = Integ(
    lambda: flujo_de_abandono() - flujo_de_recuperacion(),
    lambda: 0,
    "_integ_usuariosinactivos",
)
