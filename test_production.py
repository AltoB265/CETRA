import app


def test_single_pieces():
    hornos_estado = {
        'H1': [[{'pieza': 'LV', 'es_inicio': True}]],
        'H2A': [[{'pieza': 'TQ', 'es_inicio': True}]],
        'H2B': [[{'pieza': 'TQ', 'es_inicio': True}]],
        'H2C': [[{'pieza': 'TQ', 'es_inicio': True}]],
    }
    ciclos = {'H1': 159, 'H2': 141}
    carros = {'H1': 113, 'H2A': 113, 'H2B': 113, 'H2C': 113}
    result = app.calcular_produccion(hornos_estado, ciclos, carros)
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
    result = app.calcular_produccion(hornos_estado, ciclos, carros)
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
    resultado = app.auto_ubicar_piezas(estado, ciclos, carros)
    assert resultado['H1'][0][0]['pieza'] is not None
