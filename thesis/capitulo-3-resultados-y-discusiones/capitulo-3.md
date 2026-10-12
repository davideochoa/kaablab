# CAPÍTULO III. RESULTADOS Y DISCUSIONES

## 3.1 Estado actual del proyecto: evidencia técnica disponible

El proyecto cuenta con una base técnica concreta y verificable que distingue esta investigación de una propuesta especulativa. Los avances se organizan en cuatro niveles de evidencia. Por tratarse de un protocolo en fase de Seminario II, los resultados se presentan como evidencia preliminar y resultados esperados.

### 3.1.1 Baseline validado: pipeline completo para *Apis mellifera*

El artículo de referencia (Chin-Canché et al., 2026) es evidencia de código ejecutado, modelos entrenados y métricas publicadas en revista arbitrada. Los pipelines bee_audio_analysis y varroa_vision están disponibles públicamente. Los hiperparámetros óptimos documentados son: SVM kernel RBF con C = 34.22, γ = scale (CV F1 = 0.94 en clasificación de salud); Gradient Boosting con learning rate = 0.03, max_depth = 8, 436 estimadores, subsample = 0.836 (CV F1 = 0.9823 en detección de ausencia de reina). La ganancia de la fase bayesiana sobre la búsqueda aleatoria fue de apenas 0.0005 F1.

### 3.1.2 Repositorios públicos con código y datos

- **GitHub: **github.com/guillermochin/kaablab-bee-congress-2026-figures

- **Zenodo****: **doi.org/10.5281/zenodo.19685877

- **VarroaDataset****: **doi.org/10.5281/zenodo.4085044 (CC BY 4.0)

- **BeeAudio**** Dataset: **kaggle.com — annajyang/beehive-sounds

### 3.1.3 Análisis de transferibilidad del pipeline

| **Componente** | **Estado** | **Acción requerida** |
| --- | --- | --- |
| Extracción MFCC (librosa) | Reutilizable | Agregar pre-énfasis α=0.97 y umbral RMS |
| XGBoost / Gradient Boosting | Reutilizable | Reentrenar con datos de *M. beecheii* |
| Optimizador de hiperparámetros | Reutilizable | Ninguna — mismo protocolo |
| Dataset de audio (BeeAudio) | No transferible | Recolección propia de *M. beecheii* |
| Arquitectura sensorial (DHT22+INMP441) | Parcial | Agregar SHT31 interno primario, MPU6500 y sensor IR |
| Preprocesamiento de señal | No existe | Diseño e implementación completos |
| Sensor IR doble haz | No existe en artículo de referencia | Diseño original de esta tesis |

**Tabla 3.1 **Análisis de transferibilidad del pipeline KAABLAB al dominio de *Melipona beecheii*.

El artículo de referencia incluye además un módulo de visión computacional (CNN ligera y YOLOv8 sobre imágenes OV2640, entrenado con el VarroaDataset) orientado a la detección de *Varroa destructor*. Dado que *Varroa* no parasita a *M. beecheii*, este componente no es transferible al dominio de esta tesis y se excluye del pipeline activo; se menciona aquí únicamente como contexto histórico del artículo de referencia y no forma parte de la Tabla 3.1.

### 3.1.4 Problemas técnicos identificados y estrategias de mitigación

- **Desajuste acústico de dominio. ***M. beecheii* no produce tooting/quacking y los patrones circadianos de California no aplican. Los umbrales deben aprenderse desde cero con datos propios.

- **Degradación del DHT22 externo en condiciones tropicales. **La HR exterior frecuentemente supera el 85% en temporada de lluvias, y el DHT22 no se recupera del evento de saturación. Mitigación: el SHT31 interno, de mayor precisión y con autocalibración por encima de 80–85% HR, actúa como sensor primario; el DHT22 se conserva como referencia externa secundaria y como insumo del contraste interno-externo (sección 2.2.1).

- **Deriva por contaminación de propóleos en el SHT31 interno. **El material higroscópico del SHT31, al estar dentro de la cavidad, puede absorber resinas y partículas propias del microclima del nido, alterando su constante dieléctrica. Mitigación: dado que el DHT22 externo no está expuesto a propóleos, una divergencia creciente entre ambos que se aparte del patrón día/noche esperado de termoconformidad (sección 2.2.1) sirve como indicador automático de posible contaminación del sensor interno.

- **Vibración estructural no capturada. **Los congéneres del género Melipona usan vibración del sustrato en 180–600 Hz (vuelo ~180–250 Hz, forrajeo ~300–600 Hz); el INMP441 capta su componente aéreo, pero no la vibración de sustrato en sí. Mitigación: MPU6500 en contacto directo con la colmena.

- **Tamaño reducido del dataset inicial. **Mitigación: curvas de aprendizaje, data augmentation extensivo y reentrenamiento incremental.

- **Autonomía energética. **Ciclos de 5 min activo / 55 min en deep sleep; autonomía por validar en banco. Mitigación: muestreo periódico, detección de movimiento y panel solar 10–20 W.

### 3.1.5 Validación de arquitectura con datos sintéticos

Como cuarto nivel de evidencia, se implementó un prototipo ejecutable de extremo a extremo del pipeline de KaabLab, alimentado con un conjunto de datos sintéticos generados programáticamente. Su propósito es validar que la arquitectura de procesamiento es correcta y funcional antes de iniciar la recolección en campo, evitando comprometer recursos en una infraestructura cuyo flujo no haya sido verificado.

 

El generador sintético produce, para cada unidad de observación, tres señales con fundamento físico y diferencias deliberadas entre clases (colmena sana, ausencia de reina y estrés): (i) una señal acústica con armónicos en el rango de los meliponinos, en la que la clase de ausencia de reina desplaza el centroide espectral y modifica la energía por bandas; (ii) series ambientales que reproducen el ciclo diurno del trópico húmedo de Campeche, incluyendo la saturación del DHT22 por encima del 85% de HR; y (iii) una señal de vibración estructural con componentes en 220 Hz (vuelo, dentro de 180–250 Hz) y 380 Hz (forrajeo, dentro de 300–600 Hz), con un armónico adicional a 460 Hz que se intensifica en la clase de estrés.

 

Sobre estos datos se ejecuta el protocolo completo: las cinco etapas de preprocesamiento descritas en el Capítulo II, la extracción del vector de características enriquecido (13 MFCC, ZCR, centroide y rolloff espectral, descriptores de vibración del MPU6500 y variables ambientales interna/externa con su contraste) y el entrenamiento del clasificador Gradient Boosting, implementado con XGBoost. El prototipo se organiza de forma modular —generación de datos, preprocesamiento, extracción de características, modelo y evaluación— de modo que, al disponer de datos reales, únicamente se sustituye el módulo de generación por el de carga, conservando intacto el resto del flujo.

La evaluación contrasta las métricas obtenidas con los umbrales definidos en la hipótesis (AUC-ROC ≥ 0.85 y F1 ≥ 0.80) e incorpora dos experimentos de ablación: con y sin la fusión de variables ambientales, para cuantificar el aporte de la arquitectura sensorial heterogénea (H1b); y con y sin los descriptores de vibración, para cuantificar el aporte del MPU6500 (H1a).

La ejecución del pipeline sobre los datos sintéticos generados arrojó AUC-ROC = 1.000 y F1 macro = 1.000 para el modelo completo, superando ampliamente los umbrales de la hipótesis (AUC-ROC ≥ 0.85, F1 ≥ 0.80). Los experimentos de ablación mostraron que remover la fusión de variables ambientales reduce el F1 a 0.807 (aporte de +19.3 pp, H1b), y remover los descriptores de vibración lo reduce a 0.949 (aporte de +5.1 pp, H1a). Ambos aportes son positivos y no triviales, lo que indica que, bajo el diseño de separabilidad de clases sintéticas empleado, cada modalidad sensorial contribuye información no redundante a la clasificación.

Es necesario delimitar el alcance de esta validación con precisión metodológica. Dado que las etiquetas de clase se asignan por construcción durante la generación, las métricas obtenidas verifican que la arquitectura del pipeline es correcta y capaz de aprender cuando existe señal discriminativa, pero no constituyen un resultado biológico ni evidencia sobre el comportamiento real de *M. beecheii*; por la misma razón, la magnitud exacta de las cifras anteriores depende del diseño de los generadores sintéticos y no de datos de campo. La generación de datos empíricos de campo de la especie permanece como la contribución central de la tesis (sección 3.2).

## 3.2 Contribuciones originales esperadas

- **Primer dataset multimodal de *M. beecheii*. **Audio aéreo + vibración estructural + conteo IR de tráfico en piquera + variables ambientales interna/externa, etiquetados por estado de salud. Publicación en Zenodo CC BY 4.0.

- **Arquitectura sensorial heterogénea para monitoreo de colmenas. **Primera implementación documentada de redundancia sensorial con fabricantes distintos, roles interno/externo diferenciados y rangos complementarios aplicada al monitoreo de colmenas de abejas nativas.

- **Protocolo formal de preprocesamiento de señal. **Filtro de media móvil, pre-énfasis, umbral RMS, normalización Z-score y fusión sensorial ponderada por confianza y contraste interno-externo.

- **Caracterización de brechas bibliográficas. **Documentación explícita de los cinco gaps de literatura específica de *M. beecheii* en sonido aéreo, contraste térmico interno-externo, humedad relativa intranidal, conteo IR direccional y vibración estructural (sección 1.1.5).

- **Modelos especializados con ****benchmarks**** comparables. **Resultados de clasificación bioacústica en el dominio de *M. beecheii*, comparables directamente con el artículo de referencia.

- **Sistema ****KaabLab**** validado en campo. **Prototipo IoT de bajo costo desplegado en meliponarios mayas con métricas documentadas.

- **Metodología transferible. **Pipeline reproducible extensible a otras especies del género Melipona.

## 3.3 Discusión

Los resultados esperados se apoyan en una base técnica verificable: un pipeline ya validado en *Apis mellifera* y un análisis de transferibilidad (Tabla 3.1) que, tras excluir el módulo de visión no transferible a *M. beecheii*, estima reutilizable directamente cerca del 40% de los componentes restantes (extracción MFCC, XGBoost/Gradient Boosting y el optimizador de hiperparámetros), con otro componente parcialmente reutilizable (arquitectura sensorial) y dos completamente nuevos (preprocesamiento de señal y sensor IR). La discusión central es que la calidad del dato —garantizada por la arquitectura sensorial heterogénea y el protocolo de preprocesamiento— es el factor determinante del desempeño en el clima tropical de Campeche, por encima de la sofisticación del modelo. La validación de campo del Semestre 1 permitirá contrastar empíricamente las hipótesis H1e (superioridad de la arquitectura heterogénea) y H1b (aporte de la fusión sensorial), que son las contribuciones más novedosas del trabajo.

