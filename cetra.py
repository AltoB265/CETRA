import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(page_title="Sistema experto CETRA", page_icon="🏭", layout="wide")

PIEZA_INFO = {
    'TZ': {'espacios': 1, 'peso': 17.03, 'color': '#FF5733', 'hornos': ['H1', 'H2A', 'H2B', 'H2C']},
    'LV': {'espacios': 1, 'peso': 9.10, 'color': '#33FF57', 'hornos': ['H1', 'H2A', 'H2B', 'H2C']},
    'LVS': {'espacios': 3, 'peso': 7.06, 'color': '#3357FF', 'hornos': ['H1', 'H2A', 'H2B', 'H2C']},
    'TQ': {'espacios': 1, 'peso': 12.00, 'color': '#FF33A8', 'hornos': ['H1', 'H2A', 'H2B', 'H2C']},
    'TZ OP': {'espacios': 2, 'peso': 31.08, 'color': '#33FFF6', 'hornos': ['H1', 'H2A', 'H2B', 'H2C']},
    'OP': {'espacios': 1.5, 'peso': 31.75, 'color': '#FFD700', 'hornos': ['H1', 'H2A', 'H2B', 'H2C']},
    'OR': {'espacios': 1, 'peso': 16.14, 'color': '#800080', 'hornos': ['H1', 'H2A', 'H2B', 'H2C']},
    'PD': {'espacios': 0, 'peso': 8.83, 'color': '#A52A2A', 'hornos': ['H1', 'H2A', 'H2B', 'H2C']},
    'X': {'espacios': 0.5, 'peso': 9.73, 'color': '#708090', 'hornos': ['H1', 'H2A', 'H2B', 'H2C']},
    'TQ:PD': {'espacios': 1, 'peso': 20.83, 'color': '#FFC0CB', 'hornos': ['H1', 'H2A', 'H2B', 'H2C']},
    'LV:PD': {'espacios': 1, 'peso': 17.93, 'color': '#00CED1', 'hornos': ['H1', 'H2A', 'H2B', 'H2C']},
    '2TQ': {'espacios': 1, 'peso': 24.00, 'color': '#8B0000', 'hornos': ['H1', 'H2A', 'H2B', 'H2C']},
    '2X': {'espacios': 0.5, 'peso': 19.46, 'color': '#4682B4', 'hornos': ['H1', 'H2A', 'H2B', 'H2C']},
    '2LVS': {'espacios': 5, 'peso': 18.00, 'color': '#00FF00', 'hornos': ['H1', 'H2A', 'H2B', 'H2C']},
    '3LVS': {'espacios': 7, 'peso': 21.18, 'color': '#FFFF00', 'hornos': ['H1', 'H2A', 'H2B', 'H2C']},
}

HORNOS = {
    'H1': {'filas': 2, 'columnas': 12, 'masa_muerta': 261.2},
    'H2A': {'filas': 2, 'columnas': 14, 'masa_muerta': 344.3},
    'H2B': {'filas': 2, 'columnas': 14, 'masa_muerta': 194.4},
    'H2C': {'filas': 2, 'columnas': 14, 'masa_muerta': 312.7}
}

DEMANDA_INICIAL = {
    'TZ': 2998, 'LV': 1249, 'LVS': 323, 'TQ': 2145, 'TZ OP': 80,
    'OP': 240, 'OR': 66, 'PD': 1096, 'X': 284
}

def inicializar_matriz_detallada(filas, columnas):
    return [[{"pieza": None, "es_inicio": False, "pieza_origen": None} for _ in range(columnas)] for _ in range(filas)]

def get_ocupacion_pieza(pieza):
    ocupacion = {
        "TZ OP": (1, 2), "LVS": (1, 3), "2LVS": (1, 5), "3LVS": (1, 7)
    }
    return ocupacion.get(pieza, (1, 1))

def colocar_pieza_con_ocupacion(matriz, fila_inicio, col_inicio, pieza, filas_ocupadas, cols_ocupadas):
    for f in range(filas_ocupadas):
        for c in range(cols_ocupadas):
            if 0 <= fila_inicio + f < len(matriz) and 0 <= col_inicio + c < len(matriz[0]):
                if f == 0 and c == 0:
                    matriz[fila_inicio][col_inicio] = {"pieza": pieza, "es_inicio": True, "pieza_origen": (fila_inicio, col_inicio)}
                else:
                    matriz[fila_inicio + f][col_inicio + c] = {"pieza": pieza, "es_inicio": False, "pieza_origen": (fila_inicio, col_inicio)}

# atrón diagonal para TZ
def inicializar_h1():
    matriz = inicializar_matriz_detallada(2, 12)
    posiciones = [(0, 0), (1, 1), (0, 2), (1, 3), (0, 4), (1, 5), (0, 6), (1, 7), (0, 8), (1, 9), (0, 10), (1, 11)]
    for fila, col in posiciones:
        matriz[fila][col] = {"pieza": "TZ", "es_inicio": True, "pieza_origen": (fila, col)}
    return matriz

def inicializar_h2a():
    matriz = inicializar_matriz_detallada(2, 14)
    posiciones = [(0, 0), (1, 1), (0, 2), (1, 3), (0, 4), (1, 5), (0, 6), (1, 7), (0, 8), (1, 9), (0, 10), (1, 11), (0, 12), (1, 13)]
    for fila, col in posiciones:
        matriz[fila][col] = {"pieza": "TZ", "es_inicio": True, "pieza_origen": (fila, col)}
    return matriz

def inicializar_h2b():
    matriz = inicializar_matriz_detallada(2, 14)
    #TZ OP, OP y OR diseño predefinido
    colocar_pieza_con_ocupacion(matriz, 0, 0, "TZ OP", 1, 2)
    colocar_pieza_con_ocupacion(matriz, 0, 6, "TZ OP", 1, 2)
    colocar_pieza_con_ocupacion(matriz, 1, 2, "TZ OP", 1, 2)
    
    for i, j in [(0, 3), (0, 5), (0, 9), (0, 11), (1, 0), (1, 5), (1, 7)]:
        matriz[i][j] = {"pieza": "OP", "es_inicio": True, "pieza_origen": (i, j)}
    
    matriz[1][9] = {"pieza": "OR", "es_inicio": True, "pieza_origen": (1, 9)}
    matriz[1][11] = {"pieza": "OR", "es_inicio": True, "pieza_origen": (1, 11)}
    return matriz

def inicializar_h2c():
    return inicializar_h2a()  # Mismo patrón que H2A

# verificar posición cumple con las restricciones
def es_posicion_valida(horno_id, matriz, fila, col, pieza):
    filas_matriz, cols_matriz = len(matriz), len(matriz[0])
    filas_ocupadas, cols_ocupadas = get_ocupacion_pieza(pieza)
    
    if fila + filas_ocupadas > filas_matriz or col + cols_ocupadas > cols_matriz:
        return False
    
    for f in range(filas_ocupadas):
        for c in range(cols_ocupadas):
            if matriz[fila + f][col + c]["pieza"] is not None:
                return False
    # Restricción específica para TZ
    if pieza == 'TZ':
        for df, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            f, c = fila + df, col + dc
            if 0 <= f < filas_matriz and 0 <= c < cols_matriz:
                if matriz[f][c]["pieza"] == 'TZ':
                    return False
                
    if pieza not in [p for p in PIEZA_INFO if horno_id in PIEZA_INFO[p]['hornos']]:
        return False

    if pieza == '2TQ':
        return (fila == 0 and col == 0) or (fila == 0 and col == cols_matriz-1) or \
               (fila == filas_matriz-1 and col == 0) or (fila == filas_matriz-1 and col == cols_matriz-1)
    
    return True


def calcular_mv_mm(horno_id, matriz):
    masa_viva = 0
    for fila in range(len(matriz)):
        for col in range(len(matriz[0])):
            celda = matriz[fila][col]
            if celda["pieza"] is not None and celda["es_inicio"]:
                masa_viva += PIEZA_INFO[celda["pieza"]]['peso']
    
    masa_muerta = HORNOS[horno_id]['masa_muerta']
    return masa_viva, (masa_viva / masa_muerta if masa_muerta else 0)

def contar_piezas(matriz):
    conteo = {pieza: 0 for pieza in PIEZA_INFO}
    for fila in matriz:
        for celda in fila:
            if celda["pieza"] in conteo and celda["es_inicio"]:
                conteo[celda["pieza"]] += 1
    return conteo


def calcular_produccion(hornos_estado, ciclos_horno, carros_distribucion, demanda):
    """Compute production using plain dictionaries (no Streamlit state)."""
    produccion_final = {pieza: 0 for pieza in demanda}

    for horno_id, matriz in hornos_estado.items():
        if matriz is None:
            continue

        conteo = contar_piezas(matriz)
        ciclos_diarios = ciclos_horno['H1' if horno_id == 'H1' else 'H2']
        carros = carros_distribucion[horno_id]
        factor_ciclos = ciclos_diarios / 113

        for pieza, cantidad in conteo.items():
            if cantidad == 0:
                continue

            if pieza == 'TQ:PD':
                produccion_final['TQ'] += int(cantidad * carros * factor_ciclos)
                produccion_final['PD'] += int(cantidad * carros * factor_ciclos)
            elif pieza == 'LV:PD':
                produccion_final['LV'] += int(cantidad * carros * factor_ciclos)
                produccion_final['PD'] += int(cantidad * carros * factor_ciclos)
            elif pieza == '2TQ':
                produccion_final['TQ'] += int(2 * cantidad * carros * factor_ciclos)
            elif pieza == '2X':
                produccion_final['X'] += int(2 * cantidad * carros * factor_ciclos)
            elif pieza == '2LVS':
                produccion_final['LVS'] += int(2 * cantidad * carros * factor_ciclos)
            elif pieza == '3LVS':
                produccion_final['LVS'] += int(3 * cantidad * carros * factor_ciclos)
            elif pieza in produccion_final:
                produccion_final[pieza] += int(cantidad * carros * factor_ciclos)

    return produccion_final


def auto_ubicar_piezas(hornos_estado, ciclos_horno, carros_distribucion, demanda):
    """Fill empty slots prioritizing pieces with highest unmet demand."""
    produccion_actual = calcular_produccion(hornos_estado, ciclos_horno, carros_distribucion, demanda)
    faltante = {
        p: demanda[p] - produccion_actual.get(p, 0)
        for p in demanda
    }

    def delta_produccion(horno_id: str, pieza: str) -> dict[str, float]:
        """Return the production increment if one slot is filled with ``pieza``."""
        factor = ciclos_horno['H1' if horno_id == 'H1' else 'H2'] / 113
        carros = carros_distribucion[horno_id]
        if pieza == 'TQ:PD':
            return {'TQ': carros * factor, 'PD': carros * factor}
        if pieza == 'LV:PD':
            return {'LV': carros * factor, 'PD': carros * factor}
        if pieza == '2TQ':
            return {'TQ': 2 * carros * factor}
        if pieza == '2X':
            return {'X': 2 * carros * factor}
        if pieza == '2LVS':
            return {'LVS': 2 * carros * factor}
        if pieza == '3LVS':
            return {'LVS': 3 * carros * factor}
        return {pieza: carros * factor}

    for horno_id, matriz in hornos_estado.items():
        for fila in range(len(matriz)):
            for col in range(len(matriz[0])):
                if matriz[fila][col]["pieza"] is not None:
                    continue

                candidatos = [p for p in PIEZA_INFO if horno_id in PIEZA_INFO[p]['hornos']]
                candidatos.sort(key=lambda p: faltante.get(p, 0), reverse=True)
                for pieza in candidatos:
                    if faltante.get(pieza, 0) <= 0:
                        continue
                    if es_posicion_valida(horno_id, matriz, fila, col, pieza):
                        f_occ, c_occ = get_ocupacion_pieza(pieza)
                        colocar_pieza_con_ocupacion(matriz, fila, col, pieza, f_occ, c_occ)
                        for p, inc in delta_produccion(horno_id, pieza).items():
                            faltante[p] = max(faltante.get(p, 0) - inc, 0)
                        break

    return hornos_estado


def auto_ubicar_piezas_state():
    """Wrapper to auto-place pieces using Streamlit session state."""
    st.session_state.hornos_estado = auto_ubicar_piezas(
        st.session_state.hornos_estado,
        st.session_state.ciclos_horno,
        st.session_state.carros_distribucion,
        st.session_state.demanda,
    )
    # trigger a rerun so production results refresh immediately
    if st.runtime.exists():
        st.experimental_rerun()


def calcular_produccion_diaria():
    """Wrapper over :func:`calcular_produccion` using Streamlit session state."""
    return calcular_produccion(
        st.session_state.hornos_estado,
        st.session_state.ciclos_horno,
        st.session_state.carros_distribucion,
        st.session_state.demanda,
    )

def calcular_cumplimiento_demanda(produccion, demanda):
    cumplimiento = {}
    insatisfaccion = {}
    
    for pieza, d in demanda.items():
        if d > 0:
            cumplimiento[pieza] = min(produccion.get(pieza, 0) / d * 100, 100)
            insatisfaccion[pieza] = max(d - produccion.get(pieza, 0), 0)
        else:
            cumplimiento[pieza] = 100
            insatisfaccion[pieza] = 0
    
    return cumplimiento, insatisfaccion


if 'hornos_estado' not in st.session_state:
    st.session_state.hornos_estado = {
        'H1': inicializar_h1(),
        'H2A': inicializar_h2a(),
        'H2B': inicializar_h2b(),
        'H2C': inicializar_h2c()
    }

if 'carros_distribucion' not in st.session_state:
    st.session_state.carros_distribucion = {'H1': 43, 'H2A': 30, 'H2B': 10, 'H2C': 30}

if 'ciclos_horno' not in st.session_state:
    st.session_state.ciclos_horno = {'H1': 159, 'H2': 141}

if 'demanda' not in st.session_state:
    st.session_state.demanda = DEMANDA_INICIAL.copy()

# config. de la pagina
st.title("🏭 Sistema CETRA")
st.markdown("""
El sistema experto CETRA mejora la distribución de piezas cerámicas en hornos túnel, 
maximizando la relación MV/MM y cumpliendo con las restricciones especificadas.
""")

with st.sidebar:
    st.header("Configuración")
    
    st.subheader("Ciclos de Horno")
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.ciclos_horno['H1'] = st.number_input("Ciclo H1", min_value=1, value=st.session_state.ciclos_horno['H1'])
    with col2:
        st.session_state.ciclos_horno['H2'] = st.number_input("Ciclo H2", min_value=1, value=st.session_state.ciclos_horno['H2'])
    
    st.subheader("Distribución de Carros")
    st.session_state.carros_distribucion['H1'] = st.number_input("Carros H1", min_value=0, max_value=113, value=st.session_state.carros_distribucion['H1'])
    
    st.subheader("Distribución de Carros H2 (Total: 113)")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state.carros_distribucion['H2A'] = st.number_input("H2A", min_value=0, value=st.session_state.carros_distribucion['H2A'])
    with col2:
        st.session_state.carros_distribucion['H2B'] = st.number_input("H2B", min_value=0, value=st.session_state.carros_distribucion['H2B'])
    with col3:
        st.session_state.carros_distribucion['H2C'] = st.number_input("H2C", min_value=0, value=st.session_state.carros_distribucion['H2C'])
    
    total_carros_h2 = sum([st.session_state.carros_distribucion[key] for key in ['H2A', 'H2B', 'H2C']])
    if total_carros_h2 != 113:
        st.error(f"El total de carros del Horno 2 debe ser 113. Actual: {total_carros_h2}")

    st.subheader("Demanda por Pieza")
    for pieza in st.session_state.demanda:
        st.session_state.demanda[pieza] = st.number_input(
            pieza,
            min_value=0,
            value=st.session_state.demanda[pieza],
            step=1,
        )

# reiniciar
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("Reiniciar H1"):
        st.session_state.hornos_estado['H1'] = inicializar_h1()

with col2:
    if st.button("Reiniciar H2A"):
        st.session_state.hornos_estado['H2A'] = inicializar_h2a()

with col3:
    if st.button("Reiniciar H2B"):
        st.session_state.hornos_estado['H2B'] = inicializar_h2b()

with col4:
    if st.button("Reiniciar H2C"):
        st.session_state.hornos_estado['H2C'] = inicializar_h2c()

with col5:
    if st.button("Reiniciar Todos"):
        st.session_state.hornos_estado['H1'] = inicializar_h1()
        st.session_state.hornos_estado['H2A'] = inicializar_h2a()
        st.session_state.hornos_estado['H2B'] = inicializar_h2b()
        st.session_state.hornos_estado['H2C'] = inicializar_h2c()

st.sidebar.button("Auto Ubicar Piezas", on_click=auto_ubicar_piezas_state)

# cuadrícula del horno
def generar_cuadricula_horno(horno_id, matriz):
    filas, columnas = len(matriz), len(matriz[0])
    st.subheader(f"Horno {horno_id[1:]} - Diseño {horno_id[-1] if horno_id != 'H1' else 'A'}")
    
    masa_viva, ratio_mv_mm = calcular_mv_mm(horno_id, matriz)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Masa Viva (kg)", f"{masa_viva:.2f}")
    with col2:
        st.metric("Masa Muerta (kg)", f"{HORNOS[horno_id]['masa_muerta']:.2f}")
    with col3:
        st.metric("Ratio MV/MM", f"{ratio_mv_mm:.2f}", 
                 delta="Bueno" if ratio_mv_mm > 1 else "Mejorar",
                 delta_color="normal" if ratio_mv_mm > 1 else "inverse")
    
    cols = st.columns(columnas)
    
    for idx, col in enumerate(cols):
        col.markdown(f"<div style='text-align:center; font-weight:bold;'>{idx+1}</div>", unsafe_allow_html=True)

    for fila in range(filas):
        cols = st.columns(columnas)
        
        for col in range(columnas):
            with cols[col]:
                celda = matriz[fila][col]
                pieza_actual = celda["pieza"]
                es_inicio = celda["es_inicio"]
            
                if pieza_actual:
                    color = PIEZA_INFO[pieza_actual]['color']
                    if es_inicio:
                        st.markdown(
                            f"""<div style='background-color: {color}; border: 1px solid black; text-align: center; 
                                padding: 10px 0; margin: 2px; font-weight: bold; color: white; text-shadow: 1px 1px 2px black;'>{pieza_actual}</div>""", 
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f"""<div style='background-color: {color}; border: 1px solid black; text-align: center; 
                                padding: 10px 0; margin: 2px; color: {color};'>.</div>""", 
                            unsafe_allow_html=True
                        )
                else:
                    st.markdown(
                        """<div style='background-color: #f0f0f0; border: 1px solid #ddd; text-align: center; 
                            padding: 10px 0; margin: 2px;'>-</div>""", 
                        unsafe_allow_html=True
                    )
                if not (pieza_actual and not es_inicio):

                    opciones = [None] + [p for p in PIEZA_INFO if horno_id in PIEZA_INFO[p]['hornos']]
                    pieza_seleccionada = st.selectbox(
                        label=" ",
                        options=opciones, 
                        index=0 if pieza_actual is None else opciones.index(pieza_actual),
                        key=f"{horno_id}-{fila}-{col}",
                        label_visibility="collapsed" 
                    )

                    if pieza_seleccionada != pieza_actual:
                        if pieza_seleccionada is None:
                            if pieza_actual and es_inicio:
                                filas_ocupadas, cols_ocupadas = get_ocupacion_pieza(pieza_actual)
                                for f in range(filas_ocupadas):
                                    for c in range(cols_ocupadas):
                                        if fila + f < len(matriz) and col + c < len(matriz[0]):
                                            if matriz[fila + f][col + c]["pieza_origen"] == (fila, col):
                                                matriz[fila + f][col + c] = {"pieza": None, "es_inicio": False, "pieza_origen": None}
                            matriz[fila][col] = {"pieza": None, "es_inicio": False, "pieza_origen": None}
                        elif es_posicion_valida(horno_id, matriz, fila, col, pieza_seleccionada):
                            filas_ocupadas, cols_ocupadas = get_ocupacion_pieza(pieza_seleccionada)
                            colocar_pieza_con_ocupacion(matriz, fila, col, pieza_seleccionada, filas_ocupadas, cols_ocupadas)
                        else:
                            st.error(f"No se puede colocar {pieza_seleccionada} en esta posición")

tab1, tab2, tab3, tab4 = st.tabs(["Horno 1 (A)", "Horno 2 (A)", "Horno 2 (B)", "Horno 2 (C)"])

with tab1:
    generar_cuadricula_horno('H1', st.session_state.hornos_estado['H1'])

with tab2:
    generar_cuadricula_horno('H2A', st.session_state.hornos_estado['H2A'])

with tab3:
    generar_cuadricula_horno('H2B', st.session_state.hornos_estado['H2B'])

with tab4:
    generar_cuadricula_horno('H2C', st.session_state.hornos_estado['H2C'])

st.header("Resultados de Producción")

produccion = calcular_produccion_diaria()
cumplimiento, insatisfaccion = calcular_cumplimiento_demanda(
    produccion,
    st.session_state.demanda,
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Cumplimiento de Demanda")
    df_resultados = pd.DataFrame({
        'Pieza': list(st.session_state.demanda.keys()),
        'Demanda': [st.session_state.demanda[p] for p in st.session_state.demanda],
        'Producción': [produccion[p] for p in st.session_state.demanda],
        'Cumplimiento (%)': [cumplimiento[p] for p in st.session_state.demanda],
        'Insatisfecha': [insatisfaccion[p] for p in st.session_state.demanda]
    })
    
    st.dataframe(df_resultados.style.format({
        'Producción': '{:.2f}',
        'Cumplimiento (%)': '{:.2f}',
        'Insatisfecha': '{:.2f}'
    }))
    
    cumplimiento_promedio = sum(cumplimiento.values()) / len(cumplimiento)
    st.metric("Cumplimiento Promedio", f"{cumplimiento_promedio:.2f}%")

with col2:
    st.subheader("Masa Total")
    peso_programado = sum(
        st.session_state.demanda[p] * PIEZA_INFO[p]['peso']
        for p in st.session_state.demanda
    )
    peso_cargado = sum(
        produccion[p] * PIEZA_INFO[p]['peso']
        for p in st.session_state.demanda
    )
    
    st.metric("Peso Programado (kg)", f"{peso_programado:.2f}")
    st.metric("Peso Cargado (kg)", f"{peso_cargado:.2f}")
    st.metric("Relación Cargado/Programado", f"{(peso_cargado/peso_programado*100):.2f}%")

st.subheader("Gráfico de Cumplimiento de Demanda")
fig = px.bar(
    df_resultados, 
    x='Pieza', 
    y=['Demanda', 'Producción'], 
    barmode='group',
    title='Demanda vs Producción por Tipo de Pieza'
)
st.plotly_chart(fig, use_container_width=True)

fig2 = px.bar(
    df_resultados, 
    x='Pieza', 
    y='Cumplimiento (%)',
    title='Porcentaje de Cumplimiento por Tipo de Pieza'
)
fig2.add_hline(y=100, line_dash="dash", line_color="green", annotation_text="Objetivo")
st.plotly_chart(fig2, use_container_width=True)

with st.expander("Reglas del Sistema"):
    st.markdown("""
    ### Reglas:
    
    - Las TZ no pueden ir juntas de manera vertical ni horizontal. Se inicializan en patrón diagonal.
    - Los TQ cuando están en las esquinas, se puede llevar 2 unidades (2TQ), máximo 1 vez por columna esquinera.
    - La categoría LVS puede colocar de forma conjunta sus piezas:
      - 1 LVS = 3 espacios
      - 2 LVS = 5 espacios
      - 3 LVS = 7 espacios
    - Se pueden llevar PD en el mismo espacio que LV o TQ (LV:PD o TQ:PD)
    - Las piezas X pueden ir 2 unidades en un solo espacio (2X)
    - El carro B inicia siempre 3 TZ OP, 7 OP y 2 OR
    - El horno 1 solo permite llevar LV, TZ, X, TQ, TQ:PD y LV:PD
    """)

st.sidebar.markdown("---")
st.sidebar.info("Sistema CETRA - v6.0")
st.markdown("---")
st.markdown("#### 📝 Sistema CETRA: Carga Eficiente Trazada")
st.markdown("""
Este sistema experto utiliza reglas heurísticas para optimizar la distribución de piezas cerámicas en hornos túnel.
El objetivo es maximizar la eficiencia cargando la mayor cantidad posible de piezas favoreciendo la relación MV/MM.
""")

#             
