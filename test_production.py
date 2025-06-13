import cetra as app


def test_single_pieces():
    hornos_estado = {
        'H1': [[{'pieza': 'LV', 'es_inicio': True}]],
        'H2A': [[{'pieza': 'TQ', 'es_inicio': True}]],
        'H2B': [[{'pieza': 'TQ', 'es_inicio': True}]],
        'H2C': [[{'pieza': 'TQ', 'es_inicio': True}]],
    }
    ciclos = {'H1': 159, 'H2': 141}
    carros = {'H1': 113, 'H2A': 113, 'H2B': 113, 'H2C': 113}
    result = app.calcular_produccion(hornos_estado, ciclos, carros, app.DEMANDA_INICIAL)
    assert result['LV'] == 159
    assert result['TQ'] == 423


def test_special_pieces():
    hornos_estado = {
        'H1': [[{'pieza': '2TQ', 'es_inicio': True}]],
        'H2A': [[{'pieza': 'LV:PD', 'es_inicio': True}]],
        'H2B': [[{'pieza': 'TQ:PD', 'es_inicio': True}]],
        'H2C': [[{'pieza': '2X', 'es_inicio': True}]],
    }
    ciclos = {'H1': 159, 'H2': 141}
    carros = {'H1': 113, 'H2A': 113, 'H2B': 113, 'H2C': 113}
    result = app.calcular_produccion(hornos_estado, ciclos, carros, app.DEMANDA_INICIAL)
    expected_tq = int(2 * 113 * (159/113)) + int(113 * (141/113))  # 2TQ from H1 and TQ from TQ:PD
    expected_pd = int(113 * (141/113)) + int(113 * (141/113))  # PD from LV:PD and TQ:PD
    expected_lv = int(113 * (141/113))
    expected_x = int(2 * 113 * (141/113))
    assert result['TQ'] == expected_tq
    assert result['PD'] == expected_pd
    assert result['LV'] == expected_lv
    assert result['X'] == expected_x


def test_auto_ubicar():
    estado = {
        'H1': [[{'pieza': None, 'es_inicio': False, 'pieza_origen': None}]],
        'H2A': [[{'pieza': None, 'es_inicio': False, 'pieza_origen': None}]],
        'H2B': [[{'pieza': None, 'es_inicio': False, 'pieza_origen': None}]],
        'H2C': [[{'pieza': None, 'es_inicio': False, 'pieza_origen': None}]],
    }
    ciclos = {'H1': 159, 'H2': 141}
    carros = {'H1': 113, 'H2A': 113, 'H2B': 113, 'H2C': 113}
    resultado = app.auto_ubicar_piezas(estado, ciclos, carros, app.DEMANDA_INICIAL)
    assert resultado['H1'][0][0]['pieza'] is not None


def test_auto_ubicar_respects_demand():
    estado = {
        'H1': [[{'pieza': None, 'es_inicio': False, 'pieza_origen': None}]],
        'H2A': [[{'pieza': None, 'es_inicio': False, 'pieza_origen': None}]],
        'H2B': [[{'pieza': None, 'es_inicio': False, 'pieza_origen': None}]],
        'H2C': [[{'pieza': None, 'es_inicio': False, 'pieza_origen': None}]],
    }
    ciclos = {'H1': 159, 'H2': 141}
    carros = {'H1': 113, 'H2A': 113, 'H2B': 113, 'H2C': 113}
    demanda = {'LV': 160, 'TQ': 0, 'LVS': 0, 'TQ:PD': 0, 'LV:PD': 0,
               'TZ': 0, 'TZ OP': 0, 'OP': 0, 'OR': 0, 'PD': 0,
               'X': 0, '2TQ': 0, '2X': 0, '2LVS': 0, '3LVS': 0}
    resultado = app.auto_ubicar_piezas(estado, ciclos, carros, demanda)
    produccion = app.calcular_produccion(resultado, ciclos, carros, demanda)
    assert produccion['LV'] >= 159


def test_diferencia_calculation():
    prod = {'LV': 200}
    demanda = {'LV': 180}
    cumplimiento, diferencia = app.calcular_cumplimiento_demanda(prod, demanda)
    assert diferencia['LV'] == 20
    assert cumplimiento['LV'] == 100


def test_auto_ubicar_prioridad_tz_vs_lvs():
    estado = {
        'H1': [[{'pieza': None, 'es_inicio': False, 'pieza_origen': None}]],
        'H2A': [[{'pieza': None, 'es_inicio': False, 'pieza_origen': None}]],
        'H2B': [[{'pieza': None, 'es_inicio': False, 'pieza_origen': None}]],
        'H2C': [[{'pieza': None, 'es_inicio': False, 'pieza_origen': None}]],
    }
    ciclos = {'H1': 159, 'H2': 141}
    carros = {'H1': 113, 'H2A': 113, 'H2B': 113, 'H2C': 113}
    demanda = {'TZ': 1, 'LVS': 1000}
    resultado = app.auto_ubicar_piezas(estado, ciclos, carros, demanda)
    assert resultado['H1'][0][0]['pieza'] == 'TZ'


def test_editar_celda_remueve_completo():
    matriz = app.inicializar_matriz_detallada(2, 10)
    app.colocar_pieza_con_ocupacion(matriz, 0, 0, '2LVS', 1, 5)
    app.editar_celda(matriz, 'H1', 0, 2, None)
    assert all(c['pieza'] is None for fila in matriz for c in fila)


def test_editar_celda_restaura_si_invalido():
    matriz = app.inicializar_matriz_detallada(1, 2)
    matriz[0][0] = {'pieza': 'TZ', 'es_inicio': True, 'pieza_origen': (0, 0)}
    matriz[0][1] = {'pieza': 'LV', 'es_inicio': True, 'pieza_origen': (0, 1)}
    ok = app.editar_celda(matriz, 'H1', 0, 1, 'TZ')
    assert not ok
    assert matriz[0][1]['pieza'] == 'LV'
