# CAPÍTULO 1. PROPÓSITO Y ORGANIZACIÓN

## 1.1 Antecedentes

El artículo de Chin-Canché et al. (2026) validó el pipeline KAABLAB sobre datos públicos de *Apis mellifera* en California. El módulo bioacústico alcanzó F1 ponderado = 0.933 (clasificación multiclase del estado de salud) y AUC-ROC = 0.9945 (detección de ausencia de reina). El módulo de visión alcanzó AUC-ROC = 0.969 con YOLOv8s. Los pipelines bee_audio_analysis y varroa_vision están disponibles en GitHub (github.com/guillermochin/kaablab-bee-congress-2026-figures) y Zenodo (doi.org/10.5281/zenodo.19685877).

Es importante destacar que ambos módulos fueron evaluados exclusivamente sobre conjuntos de datos públicos recolectados por terceros —el BeeAudio Dataset de Anna Yang (Kaggle, 2022) y el VarroaDataset de Schurischuster y Kampel (Zenodo, 2020)—, sin instrumentación propia de colmenas ni validación en condiciones reales de campo. El artículo no recolectó ningún dato nuevo: su contribución es metodológica, no empírica. Esta distinción es la que justifica estructuralmente la presente tesis.

### 1.1.5 Brechas bibliográficas en los cinco parámetros de medición

La adaptación del pipeline a *Melipona beecheii* no solo enfrenta una brecha de regionalización climática, sino una ausencia casi total de literatura específica de la especie en los cinco parámetros que el sistema mide. Esta sección documenta explícitamente esas brechas, distinguiendo en cada caso lo que existe para congéneres del género Melipona de lo que existe —o no existe— para *M. beecheii*.

**(a) Frecuencia de sonido aéreo de *M. beecheii*.** No existe evidencia publicada que caracterice el espectro de sonido aéreo de *M. beecheii* ni de sus congéneres del género Melipona. Tampoco existe evidencia de que *M. beecheii* emita una señal acústica aérea de alarma: a diferencia de otras meliponinas, no se ha detectado 2-heptanol (la feromona química de alarma típica del grupo) en las glándulas mandibulares de *M. beecheii* (Cruz-López et al., 2005, citado en Quezada-Euán, 2018, p. 113), lo que sugiere un mecanismo de defensa distinto y poco documentado. Esta ausencia de evidencia no implica ausencia del fenómeno, sino una laguna bibliográfica: el nivel acústico aéreo de la colmena no ha sido caracterizado en la especie. El precedente más cercano de uso de un micrófono MEMS en un meliponino es Suárez Carvajal (2025).

<!-- REVISAR CON ASESOR: confirmar si existe alguna fuente de frecuencia específica de *M. beecheii* no identificada aún -->

**(b) Comparación de temperatura interna vs. externa.** *M. beecheii* es una especie termoconformadora, no termorreguladora activa: Moo-Valle et al. (2000), en cavidades naturales de Yucatán (citados en Quezada-Euán, 2018, p. 50), documentaron que la temperatura de la colonia fue más estable durante el día (9:00-20:00h) que durante la noche, cuando las obreras no generaron calor activamente para compensar el descenso ambiental, de modo que la temperatura interna nocturna siguió más de cerca la fluctuación externa. El mismo estudio reportó una temperatura media intranidal de 30.2°C, con un rango de 25.4-34.0°C (Moo-Valle et al., 2000, en Quezada-Euán, 2018, p. 49). Bajo exposición controlada a temperatura extrema, Macías-Macías et al. (2011, en Quezada-Euán, 2018, p. 52) documentaron 90% de mortalidad de pupas a 40°C y 100% de mortalidad de pupas a 5°C. Esto implica que la variable diagnósticamente relevante no es el valor absoluto de temperatura interna, sino el contraste entre la lectura interna y la externa. El gap identificado es la ausencia de un registro continuo en campo, en condiciones reales de Campeche, de este contraste interno-externo.

**(c) Humedad relativa intranidal.** No existe ningún estudio publicado sobre la dinámica del balance hídrico en abejas sin aguijón: "the dynamics of water balance has not been studied in stingless bees" (Roubik, 2006, citado en Quezada-Euán, 2018, p. 51), quien únicamente señala que la humedad relativa suele ser alta en zonas tropicales y que ocurre condensación de agua dentro de las colonias. El gap es total, no solo para *M. beecheii* sino para el conjunto de las meliponinas: ningún estudio ha caracterizado los rangos de humedad intranidal de ninguna especie del grupo.

**(d) Conteo de individuos por el opérculo.** No existe precedente publicado de un sensor infrarrojo aplicado específicamente a *M. beecheii* para el conteo de tráfico en la piquera. Para congéneres del género Melipona existe el precedente de Justino y Hartfelder (2024), quienes registraron actividad continua en el túnel de entrada de *M. quadrifasciata* con un detector IR simple, sin diferenciar direccionalidad (entrada vs. salida). El gap total que llena esta tesis es específicamente el conteo automatizado **direccional** (bidireccional, con doble haz) en meliponinas nativas de la región — no reportado ni para *M. beecheii* ni para ningún congénere.

**(e) Vibración estructural del nido.** La vibración de sustrato —transmitida por la estructura del nido, no por el aire— está documentada para congéneres del género Melipona: componentes de vuelo en 180-250Hz y de reclutamiento de forrajeo con frecuencia fundamental de 300-600Hz, con armónicos que se extienden hasta el orden de los kHz (Hrncir et al., 2000/2006/2008, citado en Quezada-Euán, 2018, sección 5.6). No existe registro publicado con acelerómetro del comportamiento vibracional del nido de *M. beecheii* específicamente. Las referencias disponibles son de otros meliponinos: dos Santos et al. (2025), en un estudio exploratorio sobre *Scaptotrigona* aff. *depilis* con sensor piezoeléctrico de contacto, y Hrncir et al. (2006, 2008), congéneres del género Melipona. El gap es total para la especie.

Estas cinco brechas son la justificación empírica directa de que el dataset multimodal construido en esta tesis —audio aéreo, vibración estructural, conteo IR de tráfico y variables ambientales de *M. beecheii*— constituye una contribución original y no una simple repetición metodológica del artículo de referencia. Cabe precisar el tipo de contribución de esta tesis: consistente con su título, la protección de *M. beecheii* que busca el sistema KaabLab deriva de la integración de tres elementos —arquitectura IoT, análisis mediante inteligencia artificial, y datos propios de la especie registrados de forma continua y automatizada por primera vez—. Esta protección no puede lograrse sin dicho registro continuo, el cual, como efecto necesario, genera nuevo conocimiento sobre la especie en los cinco parámetros documentados en esta sección. El aporte científico-técnico de la investigación reside en la integración IoT+IA+datos y en la arquitectura sensorial que la hace posible; el conocimiento biológico nuevo que resulta del registro continuo es una consecuencia necesaria de esa integración, no el objetivo de investigación en sí mismo. La caracterización biológica existente se usa como marco justificativo y fuente de umbrales de diseño, mientras que los datos originales que el sistema captura son el insumo que permite entrenar, validar y, en última instancia, proteger a la colonia.

## 1.2 Planteamiento del problema

El problema central es la inexistencia de un sistema de monitoreo inteligente regionalizado, con preprocesamiento de señal robusto y arquitectura sensorial heterogénea, adaptado y validado para colonias de *Melipona beecheii* en el contexto de la meliponicultura maya, a pesar de que las herramientas metodológicas para desarrollarlo existen y han sido validadas para *Apis mellifera* por el mismo equipo de investigación. La situación ideal —un sistema autónomo de bajo costo que detecte anomalías de salud e intrusiones en condiciones tropicales reales— contrasta con la situación observada, en la que solo existe un pipeline validado en otra especie, otro clima y sobre datos de terceros.

## 1.3 Pregunta de investigación

¿Puede un sistema de monitoreo inteligente, adaptado a la abeja *Melipona beecheii* y a las condiciones del trópico húmedo de Campeche, detectar de forma automática y confiable las señales de problemas en la salud de la colmena, operando de manera autónoma en meliponarios mayas?

## 1.4 Hipótesis

**H1 (hipótesis general). **El sistema KAABLAB, adaptado con datos propios de *M. beecheii*, arquitectura sensorial heterogénea y preprocesamiento formal de señal, puede detectar anomalías en el estado de salud de la colonia con AUC-ROC ≥ 0.85 y F1 ≥ 0.80 en el módulo bioacústico, y operación autónoma ≥ 72 horas en meliponarios mayas.

- **H1a. **El sistema KAABLAB, adaptado con datos propios de *M. beecheii*, una arquitectura sensorial heterogénea regionalizada al clima tropical de Campeche y un protocolo formal de preprocesamiento de señal, detecta de forma confiable las anomalías en la salud de la colmena, entendiendo "confiable" como: AUC-ROC ≥ 0.85 y F1 ≥ 0.80 en el módulo bioacústico, y operación autónoma ≥ 72 horas en meliponarios mayas.

- **H1b. **La integración de variables ambientales IoT procesadas con fusión sensorial ponderada por confianza (SHT31 + DHT22) mejora la clasificación del estado de salud en ≥ 5 pp de F1 respecto al módulo acústico solo.

- **H1c. **El dispositivo IoT opera de forma autónoma ≥ 72 horas con batería LiPo y/o panel solar en meliponarios mayas.

- **H1d. **Los meliponicultores perciben el sistema como útil, comprensible y apropiado con tasa de adopción ≥ 70%.

- **H1e. **La arquitectura sensorial heterogénea (SHT31 + DHT22 + INMP441 + MPU6050) produce lecturas más fiables en condiciones de HR >85% y temperatura ≥34°C que la arquitectura homogénea del artículo de referencia, medido por la reducción del coeficiente de variación de las lecturas y la tasa de detección de outliers.

## 1.5 Objetivos

### 1.5.1 Objetivo general

Adaptar, reentrenar y validar en condiciones reales el sistema KAABLAB para colonias de *Melipona beecheii* en meliponarios mayas de Campeche, mediante la recolección de datos propios, una arquitectura sensorial heterogénea regionalizada al clima tropical, un protocolo formal de preprocesamiento de señal, y la evaluación del sistema en campo con participación activa de meliponicultores.

### 1.5.2 Objetivos específicos

- **OE1. **Construir el primer dataset multimodal etiquetado de registros de audio aéreo, vibración estructural, conteo IR de tráfico en piquera y variables ambientales (temperatura, humedad, nivel acústico) de colmenas de *M. beecheii*, clasificados por estado de salud.

- **OE2. **Diseñar e implementar la arquitectura sensorial heterogénea (SHT31 interno primario + DHT22 externo secundario para temperatura/HR; INMP441 para nivel acústico y estado general de la colonia; MPU6050 para vibración estructural y comportamiento defensivo; sensor IR doble haz para conteo de tráfico) y validar su superioridad respecto a la arquitectura homogénea del artículo de referencia en condiciones tropicales de Campeche.

- **OE3. **Implementar y validar el protocolo de preprocesamiento de señal: filtro de media móvil sobre variables ambientales, pre-énfasis sobre señal de audio, umbral de energía RMS para descarte de segmentos silenciosos, normalización Z-score y fusión sensorial ponderada por confianza.

- **OE4. **Adaptar y reentrenar el módulo bioacústico (XGBoost, Gradient Boosting, RF, SVM) sobre datos propios de *M. beecheii*; objetivo: AUC-ROC ≥ 0.85 y F1 ≥ 0.80.

- **OE5. **Evaluar el sistema completo en campo y medir usabilidad y adopción con meliponicultores mayas.

## 1.6 Justificación

### 1.6.1 Conveniencia, relevancia social e implicaciones prácticas

La justificación descansa en cinco argumentos. Primero, por conveniencia y relevancia social, *M. beecheii* es un recurso biocultural en declive que requiere herramientas de monitoreo adaptadas a sus condiciones específicas. Segundo, el pipeline KAABLAB está validado para *Apis mellifera* con código disponible; su adaptación a *M. beecheii* es la etapa natural del proyecto. Tercero, no existe ningún dataset de señales de *M. beecheii*; su construcción es una contribución científica original. Cuarto, en cuanto a implicaciones prácticas, las restricciones del contexto rural maya justifican específicamente la orientación hacia modelos ligeros y edge computing de bajo costo. Quinto —y como contribución de diseño original de esta tesis—, la naturaleza indirecta de los sensores electrónicos (que miden fenómenos físicos secundarios y los convierten mediante funciones de calibración con limitaciones conocidas) justifica una arquitectura sensorial heterogénea con rangos complementarios, inexistente en los sistemas de monitoreo de colmenas publicados hasta la fecha.

## 1.7 Alcances y limitaciones

Es importante precisar el objeto de estudio de esta investigación: en línea con su título, esta tesis desarrolla un sistema de monitoreo inteligente cuya protección de *M. beecheii* deriva de la integración de arquitectura electrónica IoT, análisis de datos mediante inteligencia artificial, y datos propios de la especie capturados de forma continua por primera vez. Dicha protección no es posible sin ese registro continuo, que necesariamente genera nuevo conocimiento sobre la especie. El aporte de la investigación se concentra en la integración técnica que hace posible ese registro —no en el estudio biológico o entomológico de la especie como fin en sí mismo—; los datos biológicos recolectados en campo son tanto un insumo para entrenar y validar el sistema como, en sí mismos, un registro original que respalda las brechas bibliográficas documentadas en 1.1.5.

El alcance de esta investigación se delimita a la especie *Melipona beecheii* y a meliponarios ubicados en el estado de Campeche, con al menos tres sitios instrumentados. El sistema se concibe en fase de adaptación y validación de campo, no de despliegue comercial masivo. El módulo bioacústico se orienta a la clasificación del estado de salud y la detección de ausencia de reina; el módulo de conteo de tráfico en la piquera, mediante sensor IR de doble haz, se orienta a la estimación de la actividad de forrajeo como proxy adicional de vitalidad de la colonia. La instrumentación es no invasiva: solo las sondas de los sensores penetran la cavidad de la colmena.

Entre las limitaciones reconocidas se encuentran: el tamaño del dataset inicial (estimado en 1,000–2,000 registros de audio y vibración en el primer año), que condiciona la complejidad de los modelos y obliga a estrategias de aumento de datos; la dependencia del etiquetado por observación directa del meliponicultor, sujeto a disponibilidad y a la dificultad de observar ciertos estados; y la cobertura de conectividad en sitios rurales, que condiciona el esquema de transmisión inalámbrica y obliga a un respaldo local de los datos.

## 1.8 Estrategia experimental

La estrategia experimental organiza el trabajo en cuatro fases macro, distintas del detalle metodológico del Capítulo 3. La primera fase es de instrumentación: integración de la arquitectura sensorial heterogénea en las colmenas y validación comparativa de los sensores (SHT31 interno frente a DHT22 externo) en condiciones tropicales reales. La segunda fase es de recolección y construcción del dataset multimodal etiquetado, junto con la implementación del protocolo de preprocesamiento. La tercera fase es de adaptación y reentrenamiento del modelo bioacústico sobre los datos propios. La cuarta fase es de despliegue y validación en campo, con la medición cuantitativa del desempeño y la evaluación cualitativa de usabilidad y adopción con los meliponicultores.

## 1.9 Planeación: recursos, cronograma y presupuesto

El proyecto se ejecuta en cuatro semestres. Los recursos de cómputo en campo se basan en un edge device de bajo costo (ESP32-CAM para coordinación y almacenamiento y, a partir del tercer semestre, Raspberry Pi 4 para inferencia), alimentación autónoma mediante power bank, batería LiPo y panel solar, y una arquitectura sensorial heterogénea de cinco sensores (SHT31, DHT22, INMP441, MPU6050 e IR doble haz). La Tabla 1.1 presenta el cronograma con hitos de decisión y planes de contingencia; la Tabla 1.2 detalla el presupuesto por nodo y para los tres meliponarios instrumentados.

| **N°** | **Actividad** | **S1** | **S2** | **S3** | **S4** | **Hito / Entregable** | **Contingencia** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Revisión sistemática y análisis del artículo de referencia | ✓ |  |  |  | Marco teórico completo | N/A |
| 2 | Adquisición de hardware IoT | ✓ |  |  |  | Hardware disponible | ESP32-CAM si no hay RPi4 |
| 3 | Coordinación con meliponarios mayas de Campeche | ✓ |  |  |  | ≥ 3 meliponarios confirmados | Ampliar a Yucatán |
| 4 | Instrumentación en campo y validación de la arquitectura sensorial | ✓ | ✓ |  |  | Comparativa SHT31 vs DHT22 | Reducir a 2 colmenas |
| 5 | Recolección de datos y construcción del dataset | ✓ | ✓ |  |  | Dataset v1 | Aumento de datos |
| 6 | Implementación del protocolo de preprocesamiento | ✓ | ✓ |  |  | Reducción del CV de sensores | N/A |
| 7 | Caracterización bioacústica y de vibración |  | ✓ |  |  | Informe de patrones | N/A |
| 8 | Módulo bioacústico — reentrenamiento y evaluación |  | ✓ |  |  | F1 ≥ 0.75 mínimo | Reducir clases |
| 9 | Calibración y validación del sensor IR de conteo |  | ✓ | ✓ |  | Precisión de conteo definida | Ajustar separación de haces |
| 10 | Integración del dispositivo IoT de campo |  |  | ✓ |  | Autonomía ≥ 72 h | Muestreo cada 10 min |
| 11 | Despliegue y evaluación cuantitativa en campo |  |  | ✓ |  | AUC-ROC en campo | N/A |
| 12 | Evaluación cualitativa con meliponicultores |  |  | ✓ | ✓ | Adopción ≥ 60% mínimo | Rediseño de interfaz |
| 13 | Redacción de tesis y artículos |  |  | ✓ | ✓ | Tesis + ≥ 1 artículo | N/A |
| 14 | Defensa de tesis |  |  |  | ✓ | Tesis aprobada | N/A |

**Tabla 1.1 **Cronograma de actividades con hitos de decisión y planes de contingencia.

El presupuesto se calcula por nodo (una colmena instrumentada) y se escala a tres meliponarios. El costo por nodo completo es de aproximadamente $3,737 MXN; el total del proyecto, incluyendo herramientas compartidas, asciende a cerca de $11,561 MXN (~$578 USD).

| **Categoría** | **Semestre 1 (MXN)** | **Semestre 3 adicional (MXN)** |
| --- | --- | --- |
| Edge device | $250 | $1,210 (RPi4 + accesorios) |
| Sensores (5, incl. IR doble haz) | $407 | — |
| Almacenamiento | $120 | — |
| Alimentación | $650 | $500 (LiPo + DC5521) |
| Prototipado | $220 | — |
| Protección física | $380 | — |
| Subtotal por nodo | $2,027 | $1,710 |
| Total por nodo completo | ~$3,737 MXN (~$187 USD) |  |
| Hardware × 3 nodos | $11,211 | ~$561 USD |
| Herramientas (compartidas) | $350 | ~$18 USD |
| Total del proyecto | ~$11,561 MXN | ~$578 USD |

**Tabla 1.2 **Presupuesto del proyecto por nodo y total.

