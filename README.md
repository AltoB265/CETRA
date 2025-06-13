# CETRA

Sistema experto para optimizar la carga de piezas cerámicas en hornos túnel.

## Requisitos
- Python 3.10+
- Paquetes: streamlit, pandas, plotly

## Uso de la aplicación

Instale las dependencias y ejecute la app con:

```bash
pip install streamlit pandas plotly
streamlit run cetra.py
```

En la barra lateral podrá configurar ciclos de horno, distribución de carros y la demanda por tipo de pieza. Use el botón **Auto Ubicar Piezas** para llenar los espacios vacíos. La función tiene en cuenta la producción diaria que generará cada pieza para aproximarse a la demanda establecida.

## Pruebas

Para ejecutar la suite de pruebas:

```bash
pip install pytest
pytest -q
```
