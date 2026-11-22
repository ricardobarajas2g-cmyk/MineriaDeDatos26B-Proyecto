# Notas del docente — Práctica 5

El ejemplo se limita a orquestación local y está diseñado para completar tareas individuales sin reescribir los modelos. El dataset original tiene 618 filas, de las cuales 611 se consideran etiquetadas (291 favoritas / 320 no favoritas). 

**Elementos a comprobar:** `rym_spotify_entrenamiento` con 5 tareas, éxito en todas, `RYM_Spotify_Favoritos` con 3 runs y modelo `RYMSpotifyClasificadorFavoritos` alias `champion`; informe `resultados/informe_airflow.md`.

La orquestación por peticiones HTTP a un worker separado evita instalar pandas, scikit-learn y MLflow dentro del contenedor Airflow. Airflow muestra exactamente las dependencias y registra los logs de éxito/fallo. `worker` está disponible solo en la red Docker.

El error simulado se implementa mediante `force_fail=True` en el DAG: retorna HTTP 422; los datos y código de entrenamiento permanecen intactos.

El Champion se elige por mayor F1 media de validación cruzada. El conjunto de prueba no sirve para elegir el modelo. Cada ejecución registra un nuevo grupo de runs en un MLflow independiente del de la clase 4; no es el mismo servidor localhost:5000 anterior.

**Comprobaciones hechas durante la preparación:** pruebas Python, entrenamiento local sin MLflow, parsing YAML, sintaxis Python y estructura ZIP. **Pendiente de comprobar en un equipo con Docker:** construcción de imágenes y ejecución extremo a extremo de los tres contenedores, DAG y registro remoto.
