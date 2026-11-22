FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /workspace
COPY requirements.txt ./requirements.txt
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY monitoring ./monitoring
# Los CSV personales, logs y reportes se montan en ejecución, no se hornean en la imagen.
CMD ["python", "-m", "monitoring.generar_reporte"]
