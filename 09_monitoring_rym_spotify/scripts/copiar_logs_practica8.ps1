param(
  [string]$Contenedor = "",
  [switch]$Forzar
)
$ErrorActionPreference = "Stop"
$raiz = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$destino = Join-Path $raiz "logs\predicciones.jsonl"
if ((Test-Path $destino) -and -not $Forzar) {
    throw "Ya existe $destino. Use -Forzar si desea sobrescribirlo."
}
if ($Contenedor -ne "") {
    docker cp "${Contenedor}:/app/logs/predicciones.jsonl" $destino
    if ($LASTEXITCODE -ne 0) { throw "Falló docker cp. Verifique docker ps y nombre del contenedor." }
    Write-Host "Copiado desde contenedor $Contenedor a $destino"
    exit 0
}
foreach ($origen in @(
    (Join-Path $raiz "..\08_cicd_rym_spotify\logs\predicciones.jsonl"),
    (Join-Path $raiz "..\07_docker_rym_spotify\logs\predicciones.jsonl"),
    (Join-Path $raiz "..\06_fastapi_rym_spotify\logs\predicciones.jsonl")
)) {
    if (Test-Path $origen) {
        Copy-Item $origen $destino -Force
        Write-Host "Copiado desde $origen"
        exit 0
    }
}
throw "No se encontraron logs locales. Con contenedor Docker: .\scripts\copiar_logs_practica8.ps1 -Contenedor NOMBRE"
