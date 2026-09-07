CAPÍTULO III. METODOLOGÍA (MATERIALES Y MÉTODOS)

3.1 Enfoque y diseño de investigación

La investigación adopta un enfoque mixto: cuantitativo en la evaluación del desempeño de los modelos de IA y de la arquitectura sensorial, y cualitativo en la evaluación de usabilidad. El diseño es experimental-aplicado, orientado al desarrollo y validación de un sistema tecnológico en condiciones reales.

| **Tipo** | **Enfoque** | **Diseño** |
| --- | --- | --- |
| Experimental-aplicado | Mixto (cuantitativo + cualitativo) | Experimental en módulos IA y sensores · No experimental en fase cualitativa |

**Tabla 3.1 **Diseño general de la investigación.

3.2 Arquitectura sensorial heterogénea con rangos complementarios

Una contribución de diseño original de esta tesis es la arquitectura sensorial heterogénea, que supera la arquitectura homogénea del artículo de referencia en tres dimensiones: fabricante distinto, principio físico distinto y rango de medición complementario. El principio que la fundamenta es que un sensor electrónico no mide directamente la magnitud física de interés, sino un fenómeno eléctrico secundario —variación de capacitancia, resistencia o voltaje— que convierte a la magnitud deseada mediante una función de calibración con limitaciones físicas conocidas (saturación, histéresis, deriva, sensibilidad al rango).

| **Parámetro** | **Sensor** | **Principio físico** | **Rango óptimo** | **Limitación conocida** |
| --- | --- | --- | --- | --- |
| Temp + HR (bajo-medio) | DHT22 | Capacitivo higroscópico | 0–80% HR · −40–80 °C | Saturación >85% HR · histéresis |
| Temp + HR (completo) | SHT31 | Capacitivo de película polimérica | 0–100% HR · ±2% HR | Mayor costo · requiere I²C |
| Sonido aéreo | INMP441 | MEMS capacitivo | 50–10,000 Hz | No capta vibración <50 Hz |
| Vibración estructural | MPU6050 | Acelerómetro MEMS | 1–50 Hz | Requiere contacto con madera |

**Tabla 3.2 **Arquitectura sensorial heterogénea: fabricante, principio físico, rango y limitación por sensor.

3.2.1 Fundamento físico del DHT22 y por qué se satura

El DHT22 contiene internamente dos placas conductoras muy delgadas separadas por un material higroscópico que absorbe vapor de agua del aire. Cuando la humedad aumenta, el material absorbe más agua, cambia su constante dieléctrica y modifica la capacitancia entre las placas. El circuito mide esa capacitancia y la convierte a porcentaje de HR mediante una tabla de calibración interna. Lo que el sensor mide realmente es una diferencia de carga eléctrica entre dos placas, no humedad directamente.

Por encima de ~85% HR, el material higroscópico se satura —está tan húmedo que ya no puede absorber más vapor de agua. El sensor pierde sensibilidad y reporta valores estables aunque la HR real siga aumentando. En temporada de lluvias en Campeche (mayo–octubre), la HR exterior frecuentemente supera el 85%, y dentro de una colmena de M. beecheii activa puede acercarse al 95%. Este es precisamente el rango donde el artículo de referencia operaba con un único DHT22 sin respaldo.

Adicionalmente, el DHT22 presenta histéresis: absorbe vapor de agua rápido pero lo libera lento. Si la HR sube de 60% a 90% en 10 minutos y luego baja a 60%, el sensor puede reportar valores elevados durante varios minutos adicionales porque el material aún no liberó toda la humedad absorbida. En el contexto del clima tropical de Campeche, con cambios abruptos de HR durante aguaceros, esto introduce lecturas que no reflejan la realidad actual de la colmena.

3.2.2 Fundamento físico del INMP441 y el MPU6050 como sensores complementarios

El INMP441 es un micrófono MEMS (Micro-Electro-Mechanical System). Contiene una membrana muy delgada que vibra con las variaciones de presión del aire (sonido aéreo). Esa vibración modifica la capacitancia entre la membrana y una placa fija, y el circuito convierte esa variación en voltaje. Su rango frecuencial efectivo es aproximadamente 50–10,000 Hz, lo que lo hace adecuado para las señales acústicas de comunicación de las abejas pero insensible a las vibraciones estructurales del nido en el rango de 1–50 Hz.

Las meliponinas, incluida M. beecheii, expresan parte de su comportamiento defensivo y de comunicación mediante vibración del sustrato del nido —vibraciones que se transmiten por la madera de la colmena y no como ondas de presión aérea. Estas señales caen precisamente en el rango de 1–50 Hz que el INMP441 no capta. El MPU6050 es un acelerómetro MEMS de 6 ejes (3 de aceleración + 3 de giroscopio), montado en contacto directo con la madera de la colmena, que captura exactamente ese rango de vibración estructural. Los dos sensores son físicamente complementarios: el INMP441 captura lo que el MPU6050 no puede, y viceversa.

3.2.3 Fusión sensorial ponderada por confianza

La fusión sensorial ponderada por confianza asigna a cada sensor un peso dinámico que depende de si la lectura actual está dentro de su rango de máxima precisión. El algoritmo opera en tres pasos:

- **Paso 1 — Detección de rango: **para cada lectura ambiental, se determina si está dentro del rango óptimo del sensor. Si la lectura del DHT22 supera 82% HR (umbral de aproximación a la saturación), su peso se reduce progresivamente y el peso del SHT31 aumenta proporcionalmente.

- **Paso 2 — Detección de ****outliers****: **si la diferencia entre DHT22 y SHT31 supera un umbral de tolerancia (±5% HR o ±1.5 °C), la lectura que se desvía más de la media histórica de las últimas 5 muestras se descarta como outlier y se usa únicamente la lectura del sensor restante.

- **Paso 3 — Promedio ponderado: **el valor final es el promedio ponderado de las lecturas válidas, con pesos determinados por el rango de operación actual. Este valor es el que se concatena al vector de características antes de entrar al modelo.

Para la señal acústica, las características extraídas del INMP441 (MFCCs, ZCR, centroide espectral) y del MPU6050 (energía de vibración por bandas de frecuencia, pico de vibración, varianza de aceleración) se concatenan como bloques separados del vector de características, permitiendo al modelo aprender la contribución independiente de cada fuente.

3.3 Instrumentación y flujo de adquisición de datos (IoT)

El subsistema IoT cumple una función central: convertir el estado físico de la colmena en registros digitales fiables y entregarlos al subsistema de IA como un dataset estructurado. Se describe en tres bloques: la conexión de los sensores al nodo de cómputo, su disposición física en la colmena, y el flujo del dato desde la captura hasta el almacenamiento.

3.3.1 Conexión de los sensores

Todos los sensores convergen en un único nodo de borde (ESP32-CAM), que concentra la adquisición y la primera etapa de transmisión. La heterogeneidad de la arquitectura obliga a convivir tres protocolos distintos en el mismo microcontrolador: 1-Wire para el DHT22, I²C para el SHT31 y el MPU6050 (que comparten bus con direcciones 0x44 y 0x68 sin conflicto), e I²S para el micrófono digital INMP441. La cámara OV2640 va integrada al propio ESP32-CAM por bus paralelo DVP. Resistencias pull-up de 10 kΩ estabilizan la línea de datos del DHT22 y el bus I²C. La Figura 3.1 resume la conexión y la Tabla 3.3 detalla los protocolos y pines.

**Figura 3.1 **Conexión de los sensores al nodo de borde.

| **Sensor** | **Protocolo** | **Pines ESP32-CAM** | **Dirección I²C** |
| --- | --- | --- | --- |
| DHT22 | 1-Wire | GPIO 13 | N/A |
| SHT31 | I²C | SDA: GPIO 14 / SCL: GPIO 15 | 0x44 o 0x45 |
| INMP441 | I²S | SD: GPIO 2 / WS: GPIO 4 / SCK: GPIO 14 | N/A |
| MPU6050 | I²C | SDA: GPIO 14 / SCL: GPIO 15 | 0x68 o 0x69 |
| OV2640 | DVP | Integrada en ESP32-CAM | N/A |

**Tabla 3.3 **Protocolos de comunicación y pines por sensor.

3.3.2 Disposición física en la colmena

El principio de instalación es no invasivo: solo las sondas de los sensores penetran la cavidad; la electrónica de cómputo, alimentación y comunicación permanece en el exterior dentro de una caja IP65. El DHT22 y la sonda encapsulada SHT31 se introducen al interior para medir el microclima del nido; el INMP441 capta el sonido aéreo dentro de la cavidad; el MPU6050 se fija en contacto directo con la madera para registrar la vibración estructural; y la cámara OV2640 se monta en la piquera apuntando a la entrada. Se respeta un período de aclimatación de 2–4 semanas antes de iniciar el etiquetado, y el barniz conformal protege la placa salvo el elemento sensor del DHT22 y el orificio del micrófono (Figura 3.2).

**Figura 3.2 **Disposición física de la instrumentación en la colmena.

3.3.3 Flujo del dato: de la captura al dataset

El ESP32 opera en muestreo periódico (5 minutos activo / 55 dormido) para preservar autonomía. Cada ciclo escribe las lecturas en un buffer local en microSD y, cuando hay enlace disponible, las transmite de forma inalámbrica. Conviene una precisión de ingeniería: el audio y las imágenes solo pueden viajar por WiFi, que ofrece ancho de banda suficiente; LoRa queda reservado para telemetría ambiental ligera en sitios remotos sin cobertura. Por ello el diseño es inalámbrico con respaldo local: si no hay enlace, el dato espera en la microSD y se sincroniza de forma diferida. En el servidor, el meliponicultor etiqueta los registros por observación directa y se consolidan en el dataset (audio en Parquet; imágenes en PNG con anotaciones YOLO/COCO), publicado finalmente en Zenodo (Figura 3.3).

**Figura 3.3 **Flujo del dato desde la captura hasta el dataset.

3.4 Protocolo de preprocesamiento de señal

El artículo de referencia no documentó ningún protocolo de preprocesamiento de señal antes de la extracción de características. Esta tesis introduce un protocolo formal, justificado por la naturaleza indirecta de las mediciones sensoriales y las condiciones climáticas tropicales de Campeche.

3.4.1 Filtro de media móvil sobre variables ambientales

Antes de concatenar las variables ambientales al vector de características, se aplica un filtro de media móvil de ventana de 5 muestras sobre temperatura y HR. Este filtro suaviza los picos espurios causados por la histéresis del DHT22, el ruido eléctrico de la batería y las variaciones abruptas de HR durante aguaceros. La ventana de 5 muestras equivale a 5 minutos de lecturas (una muestra por minuto), suficiente para suavizar picos transitorios sin introducir latencia significativa en la detección de cambios reales del estado de la colmena.

3.4.2 Pre-énfasis sobre la señal de audio

Antes de la extracción de MFCCs, se aplica un filtro de pre-énfasis de primer orden sobre la señal de audio cruda: y[n] = x[n] − 0.97 · x[n−1]. Este filtro amplifica las frecuencias altas relativas a las bajas, compensando la tendencia natural del micrófono INMP441 a captar con mayor energía las frecuencias graves. El pre-énfasis mejora la discriminabilidad de los coeficientes MFCC de orden alto, que capturan información sobre los armónicos y la textura fina de la señal acústica de la colmena.

3.4.3 Umbral de energía RMS para descarte de segmentos silenciosos

No todos los segmentos de 60 segundos contienen señal de colmena útil. Durante períodos de baja actividad nocturna, o si el micrófono se desconecta momentáneamente, el segmento puede contener principalmente ruido de fondo. Se calcula la energía RMS (Root Mean Square) de cada segmento y se descarta si cae por debajo de un umbral empírico determinado durante la fase de calibración inicial en cada meliponario. Los segmentos descartados se registran como datos faltantes y no se usan para entrenamiento ni inferencia.

3.4.4 Normalización Z-score del vector de características

Antes de entrenar los modelos, el vector de características completo —MFCCs, ZCR, centroide espectral, variables ambientales fusionadas y características de vibración del MPU6050— se normaliza mediante Z-score por colmena: a cada valor se le resta la media y se divide entre la desviación estándar calculada sobre el conjunto de entrenamiento de esa colmena. Esto garantiza que las variables de diferentes escalas tengan contribuciones comparables al modelo, sin que ninguna domine por su magnitud absoluta. El artículo de referencia no documentó esta normalización, lo que puede haber favorecido a variables de mayor escala en los modelos sensibles a la escala (SVM).

3.4.5 Conversión de humedad relativa a humedad absoluta

La humedad relativa (HR) depende de la temperatura: la misma cantidad real de vapor de agua produce lecturas de HR completamente distintas si la temperatura cambia. Por ejemplo, 10 g/m³ de vapor de agua producen HR = 57.8% a 20 °C, HR = 32.9% a 30 °C y HR = 25.3% a 35 °C, sin que el contenido de vapor haya variado. Concatenar HR directamente al vector de características, como hace el artículo de referencia, introduce una covariancia artificial con la temperatura que puede confundir al modelo.

Antes de concatenar las variables ambientales, se convierte la humedad relativa a humedad absoluta (HA, en g/m³) mediante la aproximación de Magnus: HA = 6.112 × e^(17.67·T/(T+243.5)) × HR / (461.5 × (T+273.15)), donde T es la temperatura en grados Celsius y HR la humedad relativa en tanto por uno. El resultado es el contenido real de vapor de agua, físicamente relevante para el desarrollo de hongos, la ventilación colectiva de M. beecheii y las condiciones patológicas de la colmena. La conversión se aplica tanto al DHT22 como al SHT31 antes de la fusión ponderada, generando un único valor de humedad absoluta fusionado.

3.5 Arquitectura del sistema KaabLab completo

El sistema KaabLab para M. beecheii se organiza en cinco capas funcionales, que expanden las cuatro del artículo de referencia con la adición de la capa de preprocesamiento:

- **Capa ****IoT**** (instrumentación heterogénea): **DHT22 + SHT31 (temperatura/HR) + INMP441 (audio aéreo) + MPU6050 (vibración estructural) + cámara OV2640 en piquera + ESP32 o Raspberry Pi 4 como edge device + batería LiPo 5,000–10,000 mAh + panel solar 5–10 W.

- **Capa de preprocesamiento: **fusión sensorial ponderada por confianza (DHT22 + SHT31) → filtro de media móvil → pre-énfasis de audio (α = 0.97) → umbral RMS → normalización Z-score del vector completo.

- **Módulo ****bioacústico****: **extracción de MFCCs (n=13, media y desviación), ZCR, centroide y rolloff espectral del INMP441; energía de vibración por bandas, pico y varianza de aceleración del MPU6050; concatenación con variables ambientales fusionadas; clasificación con XGBoost, Gradient Boosting, RF y SVM; optimización en dos fases (búsqueda aleatoria 20 it. + bayesiana 15 it., 3-fold CV).

- **Módulo de visión computacional: **imágenes OV2640 a 1–5 FPS, 160×280 px; clases: actividad normal, hormigas, Phoridae, lagarto, avispa, piquera vacía; CNN ligera desde cero + YOLOv8 fine-tuning desde COCO; evaluación de mAP@0.5 y FPS en hardware objetivo.

- **Capa de alertas y evidencia: **umbral de confianza 0.7; registro de imagen/video + timestamp + clase + confianza en JSON local; sincronización diferida.

3.6 Pipeline de procesamiento y evaluación (IA)

El subsistema de IA toma el dataset crudo y lo transforma, etapa por etapa, en un diagnóstico de la condición de la colmena. Entran cuatro modalidades alineadas por timestamp: audio aéreo (INMP441), vibración estructural (MPU6050), variables ambientales (DHT22 + SHT31) e imágenes de piquera (OV2640). La limpieza aplica el protocolo de preprocesamiento descrito en la sección 3.4. La extracción de características produce, del audio, los MFCC, ZCR, centroide y rolloff espectral; del MPU6050, la energía de vibración por bandas, el pico y la varianza de aceleración; concatenados con la humedad absoluta fusionada. A partir de ahí, el pipeline se bifurca en dos rutas: la bioacústica, que clasifica el estado de salud con XGBoost / Gradient Boosting (objetivo AUC-ROC ≥ 0.85, F1 ≥ 0.80), y la de visión, que detecta intrusos en la piquera con YOLOv8 / CNN ligera (objetivo mAP@0.5 ≥ 0.80, ≥ 10 FPS). Ambas rutas convergen en el diagnóstico de la condición de la colmena —sana, anomalía bioacústica o evento de intrusión—, con registro de evidencia cuando la confianza supera 0.7 (Figura 3.4).

**Figura 3.4 **Pipeline de procesamiento y evaluación de IA.

3.7 Justificación técnica de las decisiones de diseño de IA

3.7.1 Número de coeficientes MFCC (n = 13)

La selección de n = 13 coeficientes MFCC sigue el estándar de la literatura de bioacústica de colmenas (Uthoff et al., 2023) y fue validada en el artículo de referencia: CV F1 = 0.9336 ± 0.0085 con XGBoost. Con n = 13, cada coeficiente se representa con media y desviación estándar, generando 26 valores acústicos por segmento. Valores mayores incrementan la dimensionalidad sin aportar información discriminativa adicional y elevan el riesgo de sobreajuste con datasets pequeños.

3.7.2 Validación cruzada de 3 pliegues

Con datasets estimados de 2,000–5,000 registros, la diferencia en el balance sesgo-varianza entre 3-fold y 5-fold CV es mínima. El artículo de referencia lo demostró: desviaciones estándar de F1 de 0.0085 con 3-fold CV y 7,100 registros. La ganancia de la fase bayesiana sobre la búsqueda aleatoria fue de 0.0005 F1, confirmando que 20 iteraciones de búsqueda aleatoria identifican adecuadamente las regiones óptimas del espacio de hiperparámetros.

3.7.3 XGBoost y Gradient Boosting

Su superioridad sobre redes neuronales profundas para datos tabulares con datasets pequeños se explica por tres razones: la regularización L1+L2 reduce el sobreajuste; el boosting secuencial reduce sesgo y varianza simultáneamente; y no requieren normalización estricta. Superaron a Regresión Logística y KNN por 5–14 pp de F1 en el artículo de referencia.

3.7.4 CNN ligera y YOLOv8 sobre Transfer Learning

El Transfer Learning desde ImageNet produjo recall < 43% en la clase positiva en el artículo de referencia, atribuido al desajuste de dominio entre fotografías de objetos cotidianos en alta resolución e imágenes de insectos de 1–2 mm en 160×280 px. La CNN ligera y YOLOv8s especializados alcanzaron AUC de 0.968 y 0.969 respectivamente. Esta decisión se revalidará con datos de M. beecheii.

3.8 Protocolo de construcción del dataset

3.8.1 Recolección de datos bioacústicos y ambientales

Segmentos de 60 segundos a 22,050 Hz (INMP441) y datos de vibración estructural simultáneos (MPU6050 a 100 Hz), con variables ambientales fusionadas (DHT22 + SHT31). Seis clases de estado de salud siguiendo la taxonomía del artículo de referencia. Etiquetado por observación directa del meliponicultor. Meta: ≥ 1,000 registros de M. beecheii en el primer semestre.

3.8.2 Recolección de imágenes de piquera

Cámara OV2640 a 5–10 cm de la piquera, 2 FPS, iluminación IR nocturna. Seis clases de intrusos. Etiquetado con Roboflow, ≥ 2 revisores por imagen. Meta: ≥ 3,000 imágenes.

3.8.3 Manejo del desbalance de clases

AUC-ROC como métrica principal, funciones de pérdida ponderadas, data augmentation extensivo y SMOTE si el desbalance supera 1:10.

3.8.4 Partición y almacenamiento del dataset

División 70/15/15 con estratificación por clase. Formato Parquet (audio), PNG + YOLO/COCO (imágenes). Publicación en Zenodo CC BY 4.0 al concluir.

3.9 Métricas de evaluación

| **Módulo** | **Métrica** | **Umbral objetivo** | **Ref. Apis ****mellifera** |
| --- | --- | --- | --- |
| Arquitectura sensorial — HR <85% | CV DHT22 vs SHT31 | Diferencia < ±3% HR | N/A (nuevo) |
| Arquitectura sensorial — HR >85% | Precisión SHT31 vs DHT22 | DHT22 <±8% · SHT31 <±3% | N/A (nuevo) |
| Bioacústico — estado de salud | F1 ponderado | ≥ 0.80 | 0.933 (XGBoost) |
| Bioacústico — ausencia de reina | AUC-ROC | ≥ 0.85 | 0.991 (XGBoost) |
| Visión — detección de intrusos | mAP@0.5 | ≥ 0.80 | 0.969 (YOLOv8s) |
| Visión — inferencia | FPS en hardware objetivo | ≥ 10 FPS | N/A |
| Sistema — autonomía IoT | Horas de operación | ≥ 72 h | N/A |
| Sistema — latencia de alerta | Detección a alerta | < 60 s | N/A |

**Tabla 3.4 **Métricas de evaluación con umbrales objetivo y benchmarks de referencia.

