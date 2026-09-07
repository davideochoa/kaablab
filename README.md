# KaabLab

Sistema de monitoreo IoT/IA no invasivo para colmenas de *Melipona beecheii* (abeja maya xunan kab), desarrollado como proyecto de tesis en ITESCAM.

## Estructura del repositorio

```
kaablab/
├── firmware/           # Firmware de los sensores y del microcontrolador (ESP32)
│   ├── inmp441/        # Micrófono I2S — sonido aéreo
│   ├── mpu6050/        # IMU — vibración estructural / comportamiento defensivo
│   ├── ir_counter/     # Sensor IR de doble haz — tráfico de piquera
│   └── esp32_main/     # Firmware principal de integración
├── software/
│   └── kaablab/        # Pipeline Python: preprocesamiento, extracción de
│                        # características, modelo XGBoost, ablación
├── thesis/              # Texto de la tesis (fuente versionada en Markdown)
│   ├── preliminares/
│   ├── capitulo-1-proposito-y-organizacion/
│   ├── capitulo-2-marco-teorico/
│   ├── capitulo-3-metodologia/
│   ├── capitulo-4-resultados-y-discusiones/
│   ├── capitulo-5-conclusiones-y-recomendaciones/
│   ├── figuras/
│   └── referencias.bib
├── data/
│   ├── raw/             # Datos crudos (no versionados)
│   └── samples/         # Muestras pequeñas de referencia (sí versionadas)
└── docs/                 # Bitácora de diseño, notas de asesor
```

## Estado del repositorio

> **Repositorio privado.** La titularidad de la propiedad intelectual (código y tesis) está pendiente de confirmación institucional con ITESCAM. No hay licencia de código abierto ni cesión de derechos definida todavía — ver [`LICENSE-PENDIENTE.md`](./LICENSE-PENDIENTE.md).
