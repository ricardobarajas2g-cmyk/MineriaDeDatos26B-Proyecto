# Notas de implementación

## Datos y etiquetas

Archivo proporcionado por el usuario: `rym_spotify_con_generos.csv`, 618 filas, 23 columnas. `favorito_9_10`: 611 valores etiquetados (320 ceros, 291 unos), 7 sin calificación. Se excluyen `rating_rym`, identificadores, `canciones_me_gusta`, `proporcion_me_gusta` de X.

## Reproducibilidad

El script fija `random_state=42`, split estratificado de test 20%, validación cruzada estratificada de 5 folds en entrenamiento. Conserva la evaluación sin mezclar el test en selección de parámetros. Guarda SHA-256 del CSV en resultados y un prefijo en MLflow. `CountVectorizer(token_pattern=r"[^|]+")` reconoce una frase completa de género por token.

## Revisión de calidad

Ejecutar `python -m pytest -q` y `python -m src.train --sin-mlflow` antes de la práctica. Para revisar el registro real MLflow es necesario instalar el paquete, iniciar servidor y ejecutar los tres runs en el equipo Windows del alumno/docente.

## Riesgo metodológico

Artistas, álbumes y selecciones personales pueden presentar sesgo de selección; no generalizar rendimiento. El popularidad de Spotify puede cambiar entre exportaciones; para aplicaciones futuras es conveniente controlar el momento de extracción.
