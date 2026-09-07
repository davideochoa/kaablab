CAPÍTULO IV. RESULTADOS Y DISCUSIONES

4.1 Estado actual del proyecto: evidencia técnica disponible

El proyecto cuenta con una base técnica concreta y verificable que distingue esta investigación de una propuesta especulativa. Los avances se organizan en cuatro niveles de evidencia. Por tratarse de un protocolo en fase de Seminario II, los resultados se presentan como evidencia preliminar y resultados esperados.

4.1.1 Baseline validado: pipeline completo para Apis mellifera

El artículo de referencia (Chin-Canché et al., 2026) es evidencia de código ejecutado, modelos entrenados y métricas publicadas en revista arbitrada. Los pipelines bee_audio_analysis y varroa_vision están disponibles públicamente. Los hiperparámetros óptimos documentados son: SVM kernel RBF con C = 34.22, γ = scale (CV F1 = 0.94 en clasificación de salud); Gradient Boosting con learning rate = 0.03, max_depth = 8, 436 estimadores, subsample = 0.836 (CV F1 = 0.9823 en detección de ausencia de reina). La ganancia de la fase bayesiana sobre la búsqueda aleatoria fue de apenas 0.0005 F1.

4.1.2 Repositorios públicos con código y datos

- **GitHub: **github.com/guillermochin/kaablab-bee-congress-2026-figures

- **Zenodo****: **doi.org/10.5281/zenodo.19685877

- **VarroaDataset****: **doi.org/10.5281/zenodo.4085044 (CC BY 4.0)

- **BeeAudio**** Dataset: **kaggle.com — annajyang/beehive-sounds

4.1.3 Análisis de transferibilidad del pipeline

| **Componente** | **Estado** | **Acción requerida** |
| --- | --- | --- |
| Extracción MFCC (librosa) | Reutilizable | Agregar pre-énfasis α=0.97 y umbral RMS |
| XGBoost / Gradient Boosting | Reutilizable | Reentrenar con datos de M. beecheii |
| Optimizador de hiperparámetros | Reutilizable | Ninguna — mismo protocolo |
| Dataset de audio (BeeAudio) | No transferible | Recolección propia de M. beecheii |
| CNN ligera | Reutilizable | Reentrenar con imágenes de piquera |
| YOLOv8 (pesos COCO) | Fine-tuning | Fine-tuning con dataset propio |
| VarroaDataset (A. mellifera) | No transferible | Dataset propio de intrusos |
| Arquitectura sensorial (DHT22+INMP441) | Parcial | Agregar SHT31 y MPU6050 |
| Preprocesamiento de señal | No existe | Diseño e implementación completos |

**Tabla 4.1 **Análisis de transferibilidad del pipeline KAABLAB al dominio de M. beecheii.

4.1.4 Problemas técnicos identificados y estrategias de mitigación

- **Desajuste acústico de dominio. **M. beecheii no produce tooting/quacking y los patrones circadianos de California no aplican. Los umbrales deben aprenderse desde cero con datos propios.

- **Saturación del DHT22 en condiciones tropicales. **La HR frecuentemente supera el 85% en temporada de lluvias. Mitigación: arquitectura sensorial heterogénea con SHT31 como respaldo de mayor precisión en ese rango.

- **Deriva por contaminación de propóleos. **El material higroscópico del DHT22 puede absorber resinas, alterando su constante dieléctrica. Mitigación: el SHT31, de tecnología distinta, es menos susceptible; la divergencia creciente entre ambos sirve como indicador automático de contaminación.

- **Vibración estructural no capturada. **M. beecheii usa vibración del sustrato en 1–50 Hz, no captable por el INMP441. Mitigación: MPU6050 en contacto directo con la colmena.

- **Tamaño reducido del dataset inicial. **Mitigación: curvas de aprendizaje, data augmentation extensivo y reentrenamiento incremental.

- **Autonomía energética. **RPi4 ~5 W → ~7.4 h con 10,000 mAh. Mitigación: muestreo periódico, detección de movimiento y panel solar 10–20 W.

4.1.5 Validación de arquitectura con datos sintéticos

Como cuarto nivel de evidencia, se implementó un prototipo ejecutable de extremo a extremo del pipeline de KaabLab, alimentado con un conjunto de datos sintéticos generados programáticamente. Su propósito es validar que la arquitectura de procesamiento es correcta y funcional antes de iniciar la recolección en campo, evitando comprometer recursos en una infraestructura cuyo flujo no haya sido verificado.

 

El generador sintético produce, para cada unidad de observación, tres señales con fundamento físico y diferencias deliberadas entre clases (colmena sana, ausencia de reina y estrés): (i) una señal acústica con armónicos en el rango de los meliponinos, en la que la clase de ausencia de reina desplaza el centroide espectral y modifica la energía por bandas; (ii) series ambientales que reproducen el ciclo diurno del trópico húmedo de Campeche, incluyendo la saturación del DHT22 por encima del 85% de HR; y (iii) una señal de vibración estructural en el rango 1–50 Hz que se intensifica en la clase de estrés.

 

Sobre estos datos se ejecuta el protocolo completo: las cinco etapas de preprocesamiento descritas en el Capítulo III, la extracción del vector de características enriquecido (13 MFCC, ZCR, centroide y rolloff espectral, descriptores de vibración del MPU6050 y variables ambientales fusionadas) y el entrenamiento del clasificador Gradient Boosting, implementado con XGBoost. El prototipo se organiza de forma modular —generación de datos, preprocesamiento, extracción de características, modelo y evaluación— de modo que, al disponer de datos reales, únicamente se sustituye el módulo de generación por el de carga, conservando intacto el resto del flujo.

La evaluación contrasta las métricas obtenidas con los umbrales definidos en la hipótesis (AUC-ROC ≥ 0.85 y F1 ≥ 0.80) e incorpora dos experimentos de ablación: con y sin la fusión de variables ambientales, para cuantificar el aporte de la arquitectura sensorial heterogénea (H1b); y con y sin los descriptores de vibración, para cuantificar el aporte del MPU6050 (H1a).

Es necesario delimitar el alcance de esta validación con precisión metodológica. Dado que las etiquetas de clase se asignan por construcción durante la generación, las métricas obtenidas verifican que la arquitectura del pipeline es correcta y capaz de aprender cuando existe señal discriminativa, pero no constituyen un resultado biológico ni evidencia sobre el comportamiento real de M. beecheii. La generación de datos empíricos de campo de la especie permanece como la contribución central de la tesis (Sección 4.2).

4.2 Contribuciones originales esperadas

- **Primer dataset multimodal de M. ****beecheii****. **Audio aéreo + vibración estructural + imágenes de piquera + variables ambientales fusionadas, etiquetados por estado de salud. Publicación en Zenodo CC BY 4.0.

- **Arquitectura sensorial heterogénea para monitoreo de colmenas. **Primera implementación documentada de redundancia sensorial con fabricantes distintos y rangos complementarios aplicada al monitoreo de colmenas de abejas nativas.

- **Protocolo formal de preprocesamiento de señal. **Filtro de media móvil, pre-énfasis, umbral RMS, normalización Z-score y fusión sensorial ponderada por confianza.

- **Modelos especializados con ****benchmarks**** comparables. **Resultados de clasificación bioacústica y detección visual en el dominio de M. beecheii, comparables directamente con el artículo de referencia.

- **Sistema ****KaabLab**** validado en campo. **Prototipo IoT de bajo costo desplegado en meliponarios mayas con métricas documentadas.

- **Metodología transferible. **Pipeline reproducible extensible a otras especies del género Melipona.

4.3 Discusión

Los resultados esperados se apoyan en una base técnica verificable: un pipeline ya validado en Apis mellifera y un análisis de transferibilidad que estima reutilizable cerca del 60% de los componentes. La discusión central es que la calidad del dato —garantizada por la arquitectura sensorial heterogénea y el protocolo de preprocesamiento— es el factor determinante del desempeño en el clima tropical de Campeche, por encima de la sofisticación del modelo. La validación de campo del Semestre 1 permitirá contrastar empíricamente las hipótesis H1f (superioridad de la arquitectura heterogénea) y H1b (aporte de la fusión sensorial), que son las contribuciones más novedosas del trabajo.

