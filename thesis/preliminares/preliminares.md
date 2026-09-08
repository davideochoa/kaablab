**INSTITUTO TECNOLÓGICO SUPERIOR DE CALKINÍ**

**SUBDIRECCIÓN ACADÉMICA DE INVESTIGACIÓN E INNOVACIÓN**

**MAESTRÍA EN INTELIGENCIA ARTIFICIAL**

**KAABLAB****: INNOVACIÓN PARA LA PROTECCIÓN DE LAS ABEJAS MAYAS MEDIANTE UN SISTEMA INTELIGENTE DE MONITOREO DE COLMENAS DE ****MELIPONA**** ****BEECHEII**** BASADO EN ****IoT**** E INTELIGENCIA ARTIFICIAL**

**TESIS**

Que para obtener el título de:

**MAESTRO EN INTELIGENCIA ARTIFICIAL**

Presenta:

**DAVID ENRIQUE OCHOA DIAZ**

Comité tutorial:

Director: Dra. Marlene Méndez Moreno

Codirector: Dr. Rogelio Alfredo Flores Haas

Asesor interno: Dr. Daniel Bolivar Moreno

Asesor externo: Dr. Henry Jesus Loeza Concha

Colegio de Posgraduados Campeche

Calkiní, Campeche, México — 2026

Oficio de liberación de tesis

Oficio de autorización del comité tutorial/claustro doctoral

Carta de reconocimiento del director(a) y del codirector(a) de tesis

Declaración de propiedad intelectual

Análisis anti-plagio

Dedicatoria

Agradecimientos

RESUMEN

El presente trabajo documenta el protocolo de investigación del proyecto KaabLab, cuyo objetivo es adaptar, reentrenar y validar en condiciones reales un sistema de monitoreo inteligente de colmenas de Melipona beecheii basado en el Internet de las Cosas (IoT) e Inteligencia Artificial (IA). El sistema integra un módulo de análisis bioacústico —basado en Coeficientes Cepstrales en Escala de Frecuencias Mel (MFCC), vibración estructural y variables ambientales— y un módulo de conteo infrarrojo de tráfico en la piquera como proxy de actividad de forrajeo y vitalidad de la colonia.

Una contribución de diseño original de esta tesis, que referencia al artículo (Chin-Canché et al., 2026), es la incorporación de una arquitectura sensorial heterogénea con rangos complementarios: dos sensores distintos para temperatura y humedad con roles diferenciados (SHT31 interno primario y DHT22 externo secundario), un micrófono INMP441 para nivel acústico y estado general de la colonia, un acelerómetro MPU6050 para vibración estructural del nido, y un sensor infrarrojo de doble haz para conteo direccional de tráfico. Esta arquitectura, inexistente en los sistemas de monitoreo de colmenas publicados hasta la fecha, elimina los modos de falla comunes, cubre los rangos de alta humedad relativa (>85% HR) frecuentes en el clima tropical de Campeche donde el DHT22 externo se degrada, habilita el contraste diagnóstico interno-externo propio de una especie termoconformadora como M. beecheii, y captura las vibraciones estructurales mediante las cuales las meliponinas expresan su comportamiento defensivo —un fenómeno que no es aéreo y por tanto no es detectable con un micrófono.

El artículo de referencia validó el pipeline sobre datos de Apis mellifera en California, alcanzando AUC-ROC = 0.991 en detección de ausencia de reina y F1 = 0.933 en clasificación del estado de salud; su módulo de visión computacional para detección de Varroa destructor (AUC-ROC = 0.969 con YOLOv8s) no es transferible a M. beecheii, especie que Varroa no parasita, y se excluye de esta tesis. Esta tesis cierra tres brechas del trabajo previo: ausencia de datos propios de M. beecheii, falta de regionalización al clima tropical de Campeche, y ausencia de preprocesamiento de señal documentado antes de la extracción de características; además, caracteriza explícitamente cuatro brechas bibliográficas de la especie en sus parámetros de medición (sección 1.1.5).

**Palabras clave: **meliponicultura maya, Melipona beecheii, monitoreo inteligente de colmenas, arquitectura sensorial heterogénea, redundancia sensorial, preprocesamiento de señal, fusión sensorial ponderada, bioacústica, vibración estructural, conteo infrarrojo de tráfico, IoT, XGBoost.

ABSTRACT

**DAVID ENRIQUE OCHOA DIAZ**

This document presents the research protocol for the KaabLab project, which aims to adapt, retrain, and validate under real conditions an intelligent beehive monitoring system for Melipona beecheii colonies based on the Internet of Things (IoT) and Artificial Intelligence. An original design contribution of this thesis, which surpasses the reference article (Chin-Canché et al., 2026), is the incorporation of a heterogeneous sensor architecture with complementary measurement ranges: two different manufacturers for temperature and humidity with differentiated roles (SHT31 by Sensirion as the internal primary sensor and DHT22 by Aosong as the external secondary sensor), an INMP441 microphone for acoustic level and overall colony vitality, an MPU6050 accelerometer for structural vibration of the nest, and a dual-beam infrared sensor for directional traffic counting at the hive entrance. This architecture eliminates common failure modes, covers high relative humidity ranges (>85% RH) frequent in the tropical climate of Campeche where the external DHT22 degrades, enables the internal-external diagnostic contrast proper to a thermoconforming species such as M. beecheii, and captures structural vibrations through which stingless bees express defensive behavior — a phenomenon that is not airborne and therefore not detectable with a microphone. The reference article's computer-vision module for Varroa destructor detection is not transferable to M. beecheii, a species Varroa does not parasitize, and is excluded from this thesis.

**Keywords: **Mayan beekeeping, Melipona beecheii, intelligent hive monitoring, heterogeneous sensor architecture, sensor redundancy, signal preprocessing, weighted sensor fusion, bioacoustics, structural vibration, infrared traffic counting, IoT, XGBoost.

ÍNDICE

	RESUMEN	ii

	ABSTRACT	iii

	ÍNDICE	iv

	ÍNDICE DE FIGURAS	viii

	ÍNDICE DE TABLAS	ix

	INTRODUCCIÓN	1

	CAPÍTULO 1. PROPÓSITO Y ORGANIZACIÓN	2

	1.1 Antecedentes	2

	1.1.5 Brechas bibliográficas en los cuatro parámetros de medición	2

	1.2 Planteamiento del problema	2

	1.3 Pregunta de investigación	2

	1.4 Hipótesis	2

	1.5 Objetivos	3

	1.5.1 Objetivo general	3

	1.5.2 Objetivos específicos	4

	1.6 Justificación	4

	1.6.1 Conveniencia, relevancia social e implicaciones prácticas	4

	1.7 Alcances y limitaciones	5

	1.8 Estrategia experimental	5

	1.9 Planeación: recursos, cronograma y presupuesto	5

	CAPÍTULO 2. ESTADO DEL ARTE O MARCO TEÓRICO	8

	2.1 La meliponicultura maya y Melipona beecheii	8

	2.2 Limitaciones del artículo de referencia	8

	2.3 Hallazgos metodológicos clave del artículo de referencia	8

	2.4 Amenazas bióticas en colmenas de M. beecheii	9

	CAPÍTULO 3. METODOLOGÍA (MATERIALES Y MÉTODOS)	10

	3.1 Enfoque y diseño de investigación	10

	3.2 Arquitectura sensorial heterogénea con rangos complementarios	10

	3.2.1 Fundamento físico de la humedad: SHT31 interno primario y DHT22 externo secundario	10

	3.2.2 Fundamento físico del INMP441 y el MPU6050 como sensores complementarios	11

	3.2.3 Sensor IR doble haz — conteo de tráfico en piquera	11

	3.2.4 Fusión sensorial ponderada por confianza	11

	3.3 Instrumentación y flujo de adquisición de datos (IoT)	12

	3.3.1 Conexión de los sensores	12

	3.3.2 Disposición física en la colmena	13

	3.3.3 Flujo del dato: de la captura al dataset	14

	3.4 Protocolo de preprocesamiento de señal	15

	3.4.1 Filtro de media móvil sobre variables ambientales	15

	3.4.2 Pre-énfasis sobre la señal de audio	15

	3.4.3 Umbral de energía RMS para descarte de segmentos silenciosos	16

	3.4.4 Normalización Z-score del vector de características	16

	3.4.5 Conversión de humedad relativa a humedad absoluta	16

	3.5 Arquitectura del sistema KaabLab completo	17

	3.6 Consideraciones de interferencia del hardware IoT en M. beecheii	17

	3.7 Pipeline de procesamiento y evaluación (IA)	17

	3.8 Justificación técnica de las decisiones de diseño de IA	18

	3.8.1 Número de coeficientes MFCC (n = 13)	18

	3.8.2 Validación cruzada de 3 pliegues	18

	3.8.3 XGBoost y Gradient Boosting	18

	3.9 Protocolo de construcción del dataset	19

	3.9.1 Recolección de datos bioacústicos, de vibración y ambientales	19

	3.9.2 Recolección de datos de conteo IR en piquera	19

	3.9.3 Manejo del desbalance de clases	19

	3.9.4 Partición y almacenamiento del dataset	19

	3.10 Métricas de evaluación	19

	CAPÍTULO 4. RESULTADOS Y DISCUSIONES	21

	4.1 Estado actual del proyecto: evidencia técnica disponible	21

	4.1.1 Baseline validado: pipeline completo para Apis mellifera	21

	4.1.2 Repositorios públicos con código y datos	21

	4.1.3 Análisis de transferibilidad del pipeline	21

	4.1.4 Problemas técnicos identificados y estrategias de mitigación	22

	4.1.5 Validación de arquitectura con datos sintéticos	22

	4.2 Contribuciones originales esperadas	24

	4.3 Discusión	24

	CAPÍTULO 5. CONCLUSIONES Y RECOMENDACIONES	25

	5.1 Conclusiones	25

	5.2 Recomendaciones	25

	REFERENCIAS	27

	ANEXOS	29

	Anexo A. Lista de hardware y costos	29

	Anexo B. Formatos institucionales	29

ÍNDICE DE FIGURAS

**Figura ****3.1  **Conexión de los sensores al nodo de borde.

**Figura ****3.2  **Disposición física de la instrumentación en la colmena.

**Figura ****3.3  **Flujo del dato desde la captura hasta el dataset.

**Figura ****3.4  **Pipeline de procesamiento y evaluación de IA.

ÍNDICE DE TABLAS

**Tabla ****1.1  **Cronograma de actividades con hitos y planes de contingencia.

**Tabla ****1.2  **Presupuesto del proyecto por nodo y total.

**Tabla ****3.1  **Diseño general de la investigación.

**Tabla ****3.2  **Arquitectura sensorial heterogénea: fabricante, principio físico, rango, rol y limitación por sensor.

**Tabla ****3.3  **Protocolos de comunicación y pines por sensor.

**Tabla ****3.4  **Métricas de evaluación con umbrales objetivo y benchmarks de referencia.

**Tabla ****4.1  **Análisis de transferibilidad del pipeline KAABLAB al dominio de M. beecheii.

INTRODUCCIÓN

La meliponicultura maya —el cultivo de Melipona beecheii (Bennett, 1831), la abeja señora o xunan kab— es una práctica biocultural de más de dos milenios en la Península de Yucatán. Sus colonias enfrentan declive acelerado por pérdida de hábitat, agroquímicos y ausencia de herramientas tecnológicas adaptadas. El Laboratorio de Ambientes Inteligentes del ITESCAM publicó KAABLAB (Chin-Canché et al., 2026), un sistema AIoT de monitoreo inteligente validado sobre datos de Apis mellifera. Esta tesis constituye la etapa de adaptación del sistema a M. beecheii, incorporando además tres mejoras metodológicas que el artículo de referencia no contempló: regionalización al clima tropical de Campeche, preprocesamiento formal de señal de sensores, y arquitectura sensorial heterogénea con rangos complementarios.

