# CAPÍTULO I. ANTECEDENTES, PLANTEAMIENTO Y OBJETIVOS DE LA INVESTIGACIÓN

## 1.1 Antecedentes

El artículo de Chin-Canché et al. (2026) validó el pipeline KAABLAB sobre datos públicos de *Apis mellifera* en California. El módulo bioacústico alcanzó F1 ponderado = 0.933 (clasificación multiclase del estado de salud) y AUC-ROC = 0.9945 (detección de ausencia de reina). El módulo de visión alcanzó AUC-ROC = 0.969 con YOLOv8s. Los pipelines bee_audio_analysis y varroa_vision están disponibles en GitHub y Zenodo (Chin-Canché, 2026; https://doi.org/10.5281/zenodo.19685877).

Es importante destacar que ambos módulos fueron evaluados exclusivamente sobre conjuntos de datos públicos recolectados por terceros —el BeeAudio Dataset de Anna Yang (Kaggle, 2022) y el VarroaDataset de Schurischuster y Kampel (Zenodo, 2020)—, sin instrumentación propia de colmenas ni validación en condiciones reales de campo. El artículo no recolectó ningún dato nuevo: su contribución es metodológica, no empírica. Esta distinción es la que justifica estructuralmente la presente tesis.

### 1.1.1 La meliponicultura maya y *Melipona beecheii*

*M. beecheii* es criada por comunidades mayas desde épocas prehispánicas. Su miel posee propiedades antioxidantes (Cauich Kumul et al., 2015) y antimicrobianas (Ramírez-Miranda et al., 2023) documentadas. La especie se encuentra en declive severo atribuido a deforestación, expansión agrícola y plaguicidas (Villanueva-Gutiérrez et al., 2013). Sus características biológicas difieren profundamente de *Apis mellifera*: colonias de 300–2,000 individuos, piquera tipo tubo de cerumen de 5–15 mm, repertorio acústico propio de los meliponinos, y termoconformidad en rangos tropicales de 25.4-34.0°C, con media de 30.2°C (Moo-Valle et al., 2000).

### 1.1.2 Limitaciones del artículo de referencia

El artículo de referencia presenta tres limitaciones metodológicas que esta tesis identifica explícitamente y propone superar:

- **Ausencia de regionalización. **Los datos provienen de California, 2022, en clima mediterráneo. Las condiciones de Campeche —temperatura 28–40 °C, HR frecuentemente >85% en temporada de lluvias, ciclos circadianos tropicales distintos— no están representadas. Los umbrales de decisión aprendidos por los modelos, los patrones circadianos documentados y las correlaciones entre variables ambientales y estado de salud no son directamente transferibles a *M. beecheii* en Yucatán.

- **Ausencia de preprocesamiento de señal documentado. **Las variables ambientales —temperatura, humedad, presión— se concatenan directamente al vector de características sin filtrado previo. Las características acústicas se extraen sin pre-énfasis ni eliminación de segmentos silenciosos. Librosa aplica implícitamente una ventana de Hamming y banco de filtros Mel, pero no constituyen un protocolo de acondicionamiento de señal explícito.

- **Arquitectura sensorial homogénea. **Un solo sensor por parámetro (un sensor básico de temperatura/humedad, un micrófono MEMS estándar para audio). No hay redundancia ni cobertura de los rangos donde cada sensor pierde precisión. El sensor de temperatura/humedad básico se satura por encima de ~85% HR, rango frecuente en Campeche. El micrófono MEMS estándar no capta la vibración de sustrato del nido (sí su componente de sonido aéreo) en el rango de 180–600 Hz (vuelo ~180 Hz, forrajeo ~300–600 Hz; un acelerómetro MEMS de contacto admite tasas de muestreo programables de hasta 4 kHz, es decir, un Nyquist efectivo muy superior a esta banda y sin necesidad de recorte) donde parte del comportamiento comunicativo de las meliponinas ocurre.

### 1.1.3 Hallazgos metodológicos clave del artículo de referencia

El análisis de importancia de características reveló que las variables no acústicas dominan: la variable frames concentró el 27.5% de la importancia relativa en XGBoost. La correlación negativa más fuerte con el estado de salud fue la humedad interna (ρ = −0.378). Esto confirma la importancia crítica de medir correctamente la humedad —y por tanto, la necesidad de una arquitectura sensorial robusta que no pierda precisión en los rangos de alta HR del clima tropical.

### 1.1.4 Amenazas bióticas en colmenas de *M. beecheii*

Los principales agentes de intrusión documentados en meliponarios mayas de Campeche son la hormiga arriera (Eciton burchelli parvispinum, "xuulá" en maya) y la mosca parasitaria nenem (Pseudohypocera kerteszi, familia Phoridae), reportadas por el 47% y el 20% de los meliponicultores encuestados respectivamente, con mayor incidencia de la hormiga durante la temporada de lluvias (junio-septiembre) (Pat Fernández et al., 2018). Estos eventos pueden provocar el abandono del nido o la muerte de la colmena en períodos cortos.

<!-- REVISAR: avispas y lagartos como depredadores de M. beecheii no encontraron respaldo académico verificable; se retiraron de esta versión. Si se cuenta con fuente primaria, reincorporar con cita específica. -->

### 1.1.5 Brechas bibliográficas en los cinco parámetros de medición

La adaptación del pipeline a *Melipona beecheii* no solo enfrenta una brecha de regionalización climática, sino una ausencia casi total de literatura específica de la especie en los cinco parámetros que el sistema mide. Esta sección documenta explícitamente esas brechas, distinguiendo en cada caso lo que existe para congéneres del género Melipona de lo que existe —o no existe— para *M. beecheii*.

**(a) Frecuencia de sonido aéreo de *M. beecheii*.** No existe caracterización publicada del sonido aéreo de *Melipona beecheii*. Sí existe para congéneres: en *Melipona scutellaris* y *Melipona quadrifasciata*, el sonido aéreo y la vibración de sustrato de las forrajeras comparten la misma frecuencia principal (350–520 Hz y 480–600 Hz, respectivamente; Hrncir et al., 2000), y el rango reportado para el género es de 300–600 Hz (Hrncir et al., 2006). Estos valores son de congéneres, no de *M. beecheii*, y se usan solo como referencia orientativa para el diseño del sistema de captura. Tampoco existe evidencia de que *M. beecheii* emita una señal acústica aérea de alarma: a diferencia de otras meliponinas, no se ha detectado 2-heptanol (la feromona química de alarma típica del grupo) en las glándulas mandibulares de *M. beecheii* (Cruz-López et al., 2005, citado en Quezada-Euán, 2018, p. 113), lo que sugiere un mecanismo de defensa distinto y poco documentado. Esta ausencia de evidencia no implica ausencia del fenómeno, sino una laguna bibliográfica: el nivel acústico aéreo de la colmena no ha sido caracterizado en la especie. El precedente más cercano de uso de un micrófono MEMS en un meliponino es Suárez Carvajal (2025), realizado en *Melipona eburnea* (Colombia); se trata, por tanto, de un precedente de un congénere, no de la especie de esta tesis.

<!-- REVISAR CON ASESOR: confirmar si existe alguna fuente de frecuencia específica de *M. beecheii* no identificada aún -->

**(b) Comparación de temperatura interna vs. externa.** *M. beecheii* es una especie termoconformadora, no termorreguladora activa: Moo-Valle et al. (2000), en cavidades naturales de Yucatán (citados en Quezada-Euán, 2018, p. 50), documentaron que la temperatura de la colonia fue más estable durante el día (9:00-20:00h) que durante la noche, cuando las obreras no generaron calor activamente para compensar el descenso ambiental, de modo que la temperatura interna nocturna siguió más de cerca la fluctuación externa. El mismo estudio reportó una temperatura media intranidal de 30.2°C, con un rango de 25.4-34.0°C (Moo-Valle et al., 2000, en Quezada-Euán, 2018, p. 49). Bajo exposición controlada a temperatura extrema, Macías-Macías et al. (2011, en Quezada-Euán, 2018, p. 52) documentaron 90% de mortalidad de pupas a 40°C y 100% de mortalidad de pupas a 5°C. Esto implica que la variable diagnósticamente relevante no es el valor absoluto de temperatura interna, sino el contraste entre la lectura interna y la externa. El gap identificado es la ausencia de un registro continuo en campo, en condiciones reales de Campeche, de este contraste interno-externo.

**(c) Humedad relativa intranidal.** No existe ningún estudio publicado sobre la dinámica del balance hídrico en abejas sin aguijón: "the dynamics of water balance has not been studied in stingless bees" (Roubik, 2006, citado en Quezada-Euán, 2018, p. 51), quien únicamente señala que la humedad relativa suele ser alta en zonas tropicales y que ocurre condensación de agua dentro de las colonias. El gap es total, no solo para *M. beecheii* sino para el conjunto de las meliponinas: ningún estudio ha caracterizado los rangos de humedad intranidal de ninguna especie del grupo.

**(d) Conteo de individuos por el opérculo.** No existe precedente publicado de un sensor infrarrojo aplicado específicamente a *M. beecheii* para el conteo de tráfico en la piquera. Para congéneres del género Melipona existe el precedente de Justino y Hartfelder (2024), quienes registraron actividad continua en el túnel de entrada de *M. quadrifasciata* con un detector IR simple, sin diferenciar direccionalidad (entrada vs. salida). El gap total que llena esta tesis es específicamente el conteo automatizado **direccional** (bidireccional, con doble haz) en meliponinas nativas de la región — no reportado ni para *M. beecheii* ni para ningún congénere.

**(e) Vibración estructural del nido.** La vibración de sustrato —transmitida por la estructura del nido, no por el aire— está documentada para congéneres del género Melipona: componentes de vuelo en ~180 Hz (Hrncir et al., 2008) y de reclutamiento de forrajeo con frecuencia fundamental de 300-600Hz, con armónicos que se extienden hasta el orden de los kHz (Hrncir et al., 2000, 2006, citado en Quezada-Euán, 2018, sección 5.6). No existe registro publicado con acelerómetro del comportamiento vibracional del nido de *M. beecheii* específicamente. Las referencias disponibles son de otros meliponinos: dos Santos et al. (2025), en un estudio exploratorio sobre *Scaptotrigona* aff. *depilis* con sensor piezoeléctrico de contacto, y Hrncir et al. (2006, 2008), congéneres del género Melipona. El gap es total para la especie.

Estas cinco brechas son la justificación empírica directa de que el dataset multimodal construido en esta tesis —audio aéreo, vibración estructural, conteo IR de tráfico y variables ambientales de *M. beecheii*— constituye una contribución original y no una simple repetición metodológica del artículo de referencia. Cabe precisar el tipo de contribución de esta tesis: consistente con su título, la protección de *M. beecheii* que busca el sistema KaabLab deriva de la integración de tres elementos —arquitectura IoT, análisis mediante inteligencia artificial, y datos propios de la especie registrados de forma continua y automatizada por primera vez—. Esta protección no puede lograrse sin dicho registro continuo, el cual, como efecto necesario, genera nuevo conocimiento sobre la especie en los cinco parámetros documentados en esta sección. El aporte científico-técnico de la investigación reside en la integración IoT+IA+datos y en la arquitectura sensorial que la hace posible; el conocimiento biológico nuevo que resulta del registro continuo es una consecuencia necesaria de esa integración, no el objetivo de investigación en sí mismo. La caracterización biológica existente se usa como marco justificativo y fuente de umbrales de diseño, mientras que los datos originales que el sistema captura son el insumo que permite entrenar, validar y, en última instancia, proteger a la colonia.

**Tabla 1.1** Parámetros documentados vs. no documentados para *M. beecheii*

| Parámetro | Valor/rango en *M. beecheii* | Fuente (específica o congénere) | ¿Existe registro para la especie? | Relevancia para la tesis |
| --- | --- | --- | --- | --- |
| Sonido aéreo | Congéneres: 350–520 Hz (*M. scutellaris*) y 480–600 Hz (*M. quadrifasciata*), frecuencia principal de las pulsaciones de forrajeo; sin dato de *M. beecheii* | Congénere (Hrncir et al., 2000, 2006) | No | Gap de especie, no de género; además, la ausencia de 2-heptanol en *M. beecheii* (Cruz-López et al., 2005) sugiere un mecanismo de defensa distinto, sin documentar |
| Temperatura interna | 25.4–34.0°C, media 30.2°C; 90% mortalidad de pupas a 40°C, 100% a 5°C | Específica de *M. beecheii* (Moo-Valle et al., 2000; Macías-Macías et al., 2011) | Sí | Dato específico existe, pero nunca fue tomado mediante monitoreo continuo automatizado (ver Tabla 1.2) |
| Humedad relativa intranidal | Sin rango caracterizado | Ni siquiera hay dato de congéneres — "the dynamics of water balance has not been studied in stingless bees" (Roubik, 2006) | No | Gap total para todas las meliponinas, no solo *M. beecheii* |
| Conteo de tráfico (IR, piquera) | Sin rango de referencia | Parcial en congénere: Justino y Hartfelder (2024) registraron actividad en *M. quadrifasciata* sin diferenciar dirección | No (para conteo direccional) | Gap específico: ningún precedente de conteo IR bidireccional en meliponinos |
| Vibración estructural | Componentes de vuelo ~180 Hz; forrajeo 300-600Hz fundamental | Congénere (vuelo: Hrncir et al., 2008; forrajeo: Hrncir et al., 2000, 2006); otro meliponino no congénere: dos Santos et al. (2025), en *Scaptotrigona* aff. *depilis* | No | Gap total para la especie; sin precedente de acelerómetro en meliponinos |

**Tabla 1.2** Registros previos de *M. beecheii*: manuales vs. monitoreo continuo automatizado

| Estudio | Tipo de registro | Parámetro | Duración/método | ¿Continuo y automatizado? |
| --- | --- | --- | --- | --- |
| Moo-Valle et al. (2000) | Estudio formal de campo | Temperatura intranidal | Cavidades naturales en Yucatán (el más riguroso encontrado para la especie); temperatura más estable de día (9:00-20:00h) que de noche | No — sondas manuales, periodo acotado |
| Macías-Macías et al. (2011) | Estudio formal de laboratorio | Mortalidad bajo temperatura extrema | Exposición controlada a 40°C y 5°C por 24h, comparando *M. beecheii*, *M. colimana* y *Scaptotrigona hellwegeri* | No — puntual |
| Quezada-Euán (2018) | Observación personal no sistemática | Comportamiento térmico/defensivo | "Pers. obs.", sin protocolo formal | No |
| Medina-Medina et al. (2014) | Observación conductual sistemática | Manejo de desechos | Observación directa, no basada en sensores | No |

Ninguno de los estudios revisados usó monitoreo continuo automatizado; todos fueron manuales, puntuales o de corta duración (días a semanas), sin uso de sensores IoT para registro continuo de meses. Este hallazgo es el argumento central del vacío bibliográfico de la sección 1.1.5.

## 1.2 Planteamiento del problema

El problema central es la inexistencia de un sistema de monitoreo inteligente regionalizado, con preprocesamiento de señal robusto y arquitectura sensorial heterogénea, adaptado y validado para colonias de *Melipona beecheii* en el contexto de la meliponicultura maya, a pesar de que las herramientas metodológicas para desarrollarlo existen y han sido validadas para *Apis mellifera* por el mismo equipo de investigación. La situación ideal —un sistema autónomo de bajo costo que detecte anomalías de salud e intrusiones en condiciones tropicales reales— contrasta con la situación observada, en la que solo existe un pipeline validado en otra especie, otro clima y sobre datos de terceros.

## 1.3 Pregunta de investigación

¿Puede un sistema de monitoreo inteligente, adaptado a la abeja *Melipona beecheii* y a las condiciones del trópico húmedo de Campeche, detectar de forma automática y confiable las señales de problemas en la salud de la colmena, operando de manera autónoma en meliponarios mayas?

## 1.4 Hipótesis

**H1 (hipótesis general). **El sistema KAABLAB, adaptado con datos propios de *M. beecheii*, arquitectura sensorial heterogénea y preprocesamiento formal de señal, puede detectar anomalías en el estado de salud de la colonia con AUC-ROC ≥ 0.85 y F1 ≥ 0.80 en el módulo bioacústico, y operación autónoma ≥ 72 horas en meliponarios mayas.

- **H1a. **El sistema KAABLAB, adaptado con datos propios de *M. beecheii*, una arquitectura sensorial heterogénea regionalizada al clima tropical de Campeche y un protocolo formal de preprocesamiento de señal, detecta de forma confiable las anomalías en la salud de la colmena, entendiendo "confiable" como: AUC-ROC ≥ 0.85 y F1 ≥ 0.80 en el módulo bioacústico, y operación autónoma ≥ 72 horas en meliponarios mayas.

- **H1b. **La integración de variables ambientales IoT procesadas con fusión sensorial ponderada por confianza (sensor interno y sensor externo de temperatura/humedad) mejora la clasificación del estado de salud en ≥ 5 pp de F1 respecto al módulo acústico solo.

- **H1c. **El dispositivo IoT opera de forma autónoma ≥ 72 horas con batería LiPo y/o panel solar en meliponarios mayas.

- **H1d. **Los meliponicultores perciben el sistema como útil, comprensible y apropiado con tasa de adopción ≥ 70%.

- **H1e. **La arquitectura sensorial heterogénea (sensores interno y externo de temperatura/humedad, sensor de sonido aéreo y sensor de vibración estructural) produce lecturas más fiables en condiciones de HR >85% y temperatura ≥34°C que la arquitectura homogénea del artículo de referencia, medido por la reducción del coeficiente de variación de las lecturas y la tasa de detección de outliers.

## 1.5 Objetivos

### 1.5.1 Objetivo general

Adaptar, reentrenar y validar en condiciones reales el sistema KAABLAB para colonias de *Melipona beecheii* en meliponarios mayas de Campeche, mediante la recolección de datos propios, una arquitectura sensorial heterogénea regionalizada al clima tropical, un protocolo formal de preprocesamiento de señal, y la evaluación del sistema en campo con participación activa de meliponicultores.

### 1.5.2 Objetivos específicos

- **OE1. **Construir el primer dataset multimodal etiquetado de registros de audio aéreo, vibración estructural, conteo IR de tráfico en piquera y variables ambientales (temperatura, humedad, nivel acústico) de colmenas de *M. beecheii*, clasificados por estado de salud.

- **OE2. **Diseñar e implementar la arquitectura sensorial heterogénea (sensor interno de alta precisión + sensor externo básico para temperatura/HR; sensor de sonido aéreo para nivel acústico y estado general de la colonia; sensor de vibración estructural para comportamiento defensivo; sensor IR doble haz para conteo de tráfico) y validar su superioridad respecto a la arquitectura homogénea del artículo de referencia en condiciones tropicales de Campeche.

- **OE3. **Implementar y validar el protocolo de preprocesamiento de señal: filtro de media móvil sobre variables ambientales, pre-énfasis sobre señal de audio, umbral de energía RMS para descarte de segmentos silenciosos, normalización Z-score y fusión sensorial ponderada por confianza.

- **OE4. **Adaptar y reentrenar el módulo bioacústico (XGBoost, Gradient Boosting, RF, SVM) sobre datos propios de *M. beecheii*; objetivo: AUC-ROC ≥ 0.85 y F1 ≥ 0.80.

- **OE5. **Evaluar el sistema completo en campo y medir usabilidad y adopción con meliponicultores mayas.

## 1.6 Justificación

### 1.6.1 Conveniencia, relevancia social e implicaciones prácticas

La justificación descansa en cinco argumentos. Primero, por conveniencia y relevancia social, *M. beecheii* es un recurso biocultural en declive que requiere herramientas de monitoreo adaptadas a sus condiciones específicas. Segundo, el pipeline KAABLAB está validado para *Apis mellifera* con código disponible; su adaptación a *M. beecheii* es la etapa natural del proyecto. Tercero, no existe ningún dataset de señales de *M. beecheii*; su construcción es una contribución científica original. Cuarto, en cuanto a implicaciones prácticas, las restricciones del contexto rural maya justifican específicamente la orientación hacia modelos ligeros y edge computing de bajo costo. Quinto —y como contribución de diseño original de esta tesis—, la naturaleza indirecta de los sensores electrónicos (que miden fenómenos físicos secundarios y los convierten mediante funciones de calibración con limitaciones conocidas) justifica una arquitectura sensorial heterogénea con rangos complementarios, inexistente en los sistemas de monitoreo de colmenas publicados hasta la fecha.

## 1.7 Alcances y limitaciones

En línea con su título, esta tesis desarrolla un sistema de monitoreo inteligente cuya protección de *M. beecheii* deriva de la integración de arquitectura electrónica IoT, análisis de datos mediante inteligencia artificial, y datos propios de la especie capturados de forma continua por primera vez. Dicha protección no es posible sin ese registro continuo, que necesariamente genera nuevo conocimiento sobre la especie. El aporte de la investigación se concentra en la integración técnica que hace posible ese registro —no en el estudio biológico o entomológico de la especie como fin en sí mismo—; los datos biológicos recolectados en campo son tanto un insumo para entrenar y validar el sistema como un registro original que respalda las brechas bibliográficas documentadas en 1.1.5.

El alcance de esta investigación se delimita a la especie *Melipona beecheii* y a meliponarios ubicados en el estado de Campeche, con al menos tres sitios instrumentados. El sistema se concibe en fase de adaptación y validación de campo, no de despliegue comercial masivo. El módulo bioacústico se orienta a la clasificación del estado de salud y la detección de ausencia de reina; el módulo de conteo de tráfico en la piquera, mediante sensor IR de doble haz, se orienta a la estimación de la actividad de forrajeo como proxy adicional de vitalidad de la colonia. La instrumentación es no invasiva: solo las sondas de los sensores penetran la cavidad de la colmena.

Entre las limitaciones reconocidas se encuentran: el tamaño del dataset inicial (estimado en al menos 1,000 registros en el cuarto semestre), que condiciona la complejidad de los modelos y obliga a estrategias de aumento de datos; la dependencia del etiquetado por observación directa del meliponicultor, sujeto a disponibilidad y a la dificultad de observar ciertos estados; la cobertura de conectividad en sitios rurales, que condiciona el esquema de transmisión inalámbrica y obliga a un respaldo local de los datos; y el firmware del nodo, el muestreo de vibración a 1.5 kHz, la autonomía y la aplicación móvil están diseñados, pero aún no validados en banco ni en campo.

## 1.8 Estrategia experimental

La estrategia experimental organiza el trabajo en cuatro fases macro, distintas del detalle metodológico del Capítulo II. La primera fase es de instrumentación: integración de la arquitectura sensorial heterogénea en las colmenas y validación comparativa de los sensores (sensor interno frente a sensor externo de temperatura/humedad) en condiciones tropicales reales. La segunda fase es de recolección y construcción del dataset multimodal etiquetado, junto con la implementación del protocolo de preprocesamiento. La tercera fase es de adaptación y reentrenamiento del modelo bioacústico sobre los datos propios. La cuarta fase es de despliegue y validación en campo, con la medición cuantitativa del desempeño y la evaluación cualitativa de usabilidad y adopción con los meliponicultores.

## 1.9 Planeación: recursos, cronograma y presupuesto

El proyecto se ejecuta en cuatro semestres —propuesta de tesis (S1), desarrollo (S2), integración de hardware y revisión (S3) e implementación (S4)— y se encuentra en el tercero. Los recursos de cómputo en campo se basan en un edge device de bajo costo (ESP32 DevKit V1 que captura y almacena en microSD; el procesamiento y la inferencia se harán en una aplicación Android), alimentación autónoma mediante power bank, batería LiPo y panel solar, y una arquitectura sensorial heterogénea de cinco sensores (temperatura/humedad interno, temperatura/humedad externo, sonido aéreo, vibración estructural e IR doble haz). La Tabla 1.3 presenta el cronograma con hitos de decisión y planes de contingencia; la Tabla 1.4 detalla el presupuesto por nodo y para los tres meliponarios instrumentados.

| **N°** | **Actividad** | **S1** | **S2** | **S3** | **S4** | **Hito / Entregable** | **Contingencia** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Revisión sistemática y análisis del artículo de referencia | ✓ | ✓ |  |  | Marco teórico completo | N/A |
| 2 | Adquisición de hardware IoT |  |  | ✓ |  | Hardware disponible | N/A |
| 3 | Coordinación con meliponarios mayas de Campeche |  |  | ✓ |  | ≥ 3 meliponarios confirmados | Ampliar a Yucatán |
| 4 | Instrumentación en campo y validación de la arquitectura sensorial |  |  |  | ✓ | Comparativa sensor interno vs. externo | Reducir a 2 colmenas |
| 5 | Recolección de datos y construcción del dataset |  |  |  | ✓ | Dataset v1 | Aumento de datos |
| 6 | Implementación del protocolo de preprocesamiento |  | ✓ | ✓ |  | Reducción del CV de sensores | N/A |
| 7 | Caracterización bioacústica y de vibración |  |  |  | ✓ | Informe de patrones | N/A |
| 8 | Módulo bioacústico — reentrenamiento y evaluación |  |  |  | ✓ | F1 ≥ 0.75 mínimo | Reducir clases |
| 9 | Calibración y validación del sensor IR de conteo |  |  | ✓ | ✓ | Precisión de conteo definida | Ajustar separación de haces |
| 10 | Integración del dispositivo IoT de campo |  |  | ✓ |  | Autonomía ≥ 72 h | Menos ventanas por ciclo |
| 11 | Despliegue y evaluación cuantitativa en campo |  |  |  | ✓ | AUC-ROC en campo | N/A |
| 12 | Evaluación cualitativa con meliponicultores |  |  |  | ✓ | Adopción ≥ 60% mínimo | Rediseño de interfaz |
| 13 | Redacción de tesis y artículos |  | ✓ | ✓ | ✓ | Tesis + ≥ 1 artículo | N/A |
| 14 | Defensa de tesis |  |  |  | ✓ | Tesis aprobada | N/A |

**Tabla 1.3 **Cronograma de actividades con hitos de decisión y planes de contingencia.

El presupuesto se calcula por nodo (una colmena instrumentada) y se escala a tres meliponarios. El costo por nodo completo es de aproximadamente $2,577 MXN; el total del proyecto, incluyendo herramientas compartidas, asciende a cerca de $8,081 MXN (~$404 USD).

| **Categoría** | **Semestre 3 (MXN)** | **Semestre 4 adicional (MXN)** |
| --- | --- | --- |
| Edge device | $250 | — |
| Sensores (5, incl. IR doble haz) | $407 | — |
| Almacenamiento | $120 | — |
| Reloj de tiempo real (DS3231) | $50 | — |
| Alimentación | $650 | $500 (LiPo + DC5521) |
| Prototipado | $220 | — |
| Protección física | $380 | — |
| Subtotal por nodo | $2,077 | $500 |
| Total por nodo completo | ~$2,577 MXN (~$129 USD) |  |
| Hardware × 3 nodos | $7,731 | ~$387 USD |
| Herramientas (compartidas) | $350 | ~$18 USD |
| Total del proyecto | ~$8,081 MXN | ~$404 USD |

**Tabla 1.4 **Presupuesto del proyecto por nodo y total.
