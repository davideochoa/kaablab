# KaabLab

Sistema de monitoreo IoT/IA no invasivo para colmenas de *Melipona beecheii* (abeja maya xunan kab), desarrollado como proyecto de tesis en ITESCAM.

## Estructura del repositorio

```
kaablab/
├── software/
│   ├── kaablab_pipeline/ # Pipeline Python: preprocesamiento, extracción de
│   │                    # características, modelo XGBoost, ablación
│   ├── nodo_kaablab/   # Firmware integrado del nodo ESP32 DevKit V1 (5 sensores)
│   └── sensor-*/       # Un sensor por carpeta: README + arduino/<sketch>/<sketch>.ino
│                        # (ESP32) + raspberry/ (Python, opcional)
├── thesis/              # Texto de la tesis (fuente versionada en Markdown)
│   ├── preliminares/
│   ├── capitulo-1-antecedentes-planteamiento-objetivos/
│   ├── capitulo-2-materiales-y-metodos/
│   ├── capitulo-3-resultados-y-discusiones/
│   ├── capitulo-4-recomendaciones/
│   ├── capitulo-5-conclusiones/
│   ├── figuras/
│   └── referencias.bib
├── data/
│   ├── raw/             # Datos crudos (no versionados)
│   └── samples/         # Muestras pequeñas de referencia (sí versionadas)
└── docs/                 # Bitácora de diseño, notas de asesor
```

## Estado del repositorio

> **Repositorio privado.** La titularidad de la propiedad intelectual (código y tesis) está pendiente de confirmación institucional con ITESCAM. No hay licencia de código abierto ni cesión de derechos definida todavía — ver [`LICENSE-PENDIENTE.md`](./LICENSE-PENDIENTE.md).
