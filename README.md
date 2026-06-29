# Simulador NK OA–RPM

Mini laboratorio interactivo para trabajar con el modelo Nuevo Keynesiano simple en el plano inflación–brecha del producto.

Incluye dos reglas de política monetaria:

- Regla de Taylor
- Regla Monetaria Óptima (RMO)

## Archivos

- `app.py`: aplicación principal en Streamlit.
- `requirements.txt`: dependencias para Streamlit Cloud.

## Cómo correr localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Cómo publicar en Streamlit Cloud

1. Crear un repositorio en GitHub.
2. Subir `app.py`, `requirements.txt` y este `README.md`.
3. Entrar a Streamlit Community Cloud.
4. Elegir el repositorio.
5. Main file path: `app.py`.
6. Deploy.

## Ecuaciones usadas

Oferta agregada:

```math
\pi = \pi^e + \theta x + \varepsilon
```

con `x = y - \bar y`.

RPM derivada de Taylor:

```math
\pi - \bar\pi = -\frac{1+b\phi}{(a-1)\phi}x + \frac{\mu}{(a-1)\phi}
```

Tasa bajo Taylor:

```math
i - \bar i = a(\pi-\bar\pi)+bx
```

Regla Monetaria Óptima:

```math
\pi - \bar\pi = -\frac{\lambda}{\theta}x
```

Brecha del producto bajo RMO:

```math
x = \frac{\theta}{\theta^2+\lambda}(\bar\pi - \pi^e - \varepsilon)
```

Tasa bajo RMO:

```math
i - \bar i = \left(1+\frac{\theta}{\phi(\theta^2+\lambda)}\right)(\pi^e-\bar\pi)
+\frac{\theta}{\phi(\theta^2+\lambda)}\varepsilon
+\frac{1}{\phi}\mu
```
