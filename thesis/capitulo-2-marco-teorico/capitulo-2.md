# CAPÍTULO 2. ESTADO DEL ARTE O MARCO TEÓRICO

## 2.1 La meliponicultura maya y *Melipona beecheii*

*M. beecheii* es criada por comunidades mayas desde épocas prehispánicas. Su miel posee propiedades antioxidantes y antimicrobianas documentadas (Ramírez-Miranda et al., 2023; Cauich Kumul et al., 2015). La especie se encuentra en declive severo atribuido a deforestación, expansión agrícola y plaguicidas (Villanueva-Gutiérrez et al., 2014). Sus características biológicas difieren profundamente de *Apis mellifera*: colonias de 300–2,000 individuos, piquera tipo tubo de cerumen de 5–15 mm, repertorio acústico propio de los meliponinos, y termorregulación en rangos tropicales de 26–32 °C.

Para precisar el alcance del vacío bibliográfico ya introducido en la sección 1.1.5, la Tabla 2.1 sistematiza, parámetro por parámetro, qué se sabe específicamente de *M. beecheii* frente a lo que solo puede inferirse de congéneres del género Melipona.

| Parámetro | Valor/rango en *M. beecheii* | Fuente (específica o congénere) | ¿Existe registro para la especie? | Relevancia para la tesis |
| --- | --- | --- | --- | --- |
| Temperatura | <28 °C alerta baja (límite de desarrollo de cría); 28–33 °C óptimo; 34–35 °C alerta temprana (LT50 de pupas); ≥38–40 °C crítico (mortalidad de obreras) | Roubik & Peralta (1983); Macías-Macías et al. (2011) | Sí (puntual/manual) | Dato específico existe, pero nunca como monitoreo continuo |
| Humedad relativa | Umbrales provisionales: <60% HR alerta baja; 60–90% funcional; >90% HR alerta alta | Congénere, sin dato intranidal publicado para *M. beecheii* (Quezada-Euán, 2018) | No | Vacío bibliográfico — contribución original de esta tesis |
| Sonido aéreo | Vuelo ~180–250 Hz; forrajeo ~300–600 Hz (frecuencia fundamental), armónicos hasta el orden de los kHz | Congénere (Hrncir et al., 2000, 2006, 2008) | No | Vacío bibliográfico — contribución original de esta tesis |
| Tráfico de piquera (conteo IR direccional) | Sin rango de referencia publicado | No existe ni para la especie ni para congéneres | No | Originalidad total — sin línea base externa de comparación |
| Vibración estructural (sustrato) | 300–600 Hz, señalización defensiva/de forrajeo, reportada a nivel género Melipona | Congénere (Hrncir et al., 2006) | No | Vacío de especie — sin antecedente de uso de acelerómetro en meliponinos |

**Tabla 2.1** Parámetros documentados vs. no documentados para *M. beecheii*.

Más allá de qué parámetros carecen de dato específico, es necesario distinguir también el *tipo* de registro que sí existe. La Tabla 2.2 muestra que, incluso para el único parámetro con dato específico de la especie —temperatura—, ningún estudio previo empleó monitoreo continuo automatizado.

| Estudio | Tipo de registro | Parámetro | Duración/método | ¿Continuo y automatizado? |
| --- | --- | --- | --- | --- |
| Moo-Valle et al. (2000) | Estudio formal de campo | Temperatura intranidal | Cavidades naturales en Yucatán (el estudio más riguroso encontrado para la especie); halló temperatura de cría más estable de día (9:00–20:00 h) que de noche | No — sondas manuales, periodo acotado |
| Macías-Macías et al. (2011) | Estudio formal de laboratorio | Mortalidad bajo temperatura extrema | 40 °C y 5 °C durante 24 h, comparando *M. beecheii*, *M. colimana* y *Scaptotrigona hellwegeri* | No — puntual |
| Quezada-Euán (2018) | Observación personal no sistemática ("pers. obs.") | Comportamiento térmico/defensivo | — | No |
| Medina-Medina et al. (2014) | Observación conductual sistemática | Manejo de desechos | No basada en sensores | No |

**Tabla 2.2** Registros previos de *M. beecheii*: manuales vs. monitoreo continuo automatizado.

Ninguno de los estudios revisados empleó monitoreo continuo automatizado: todos fueron manuales, puntuales o de corta duración (días a semanas), sin uso de sensores IoT para registro continuo durante meses. Este hallazgo es el argumento central del vacío bibliográfico documentado en la sección 1.1.5: la ausencia no es solo de dato específico de la especie en varios parámetros, sino de una metodología de registro continuo y automatizado incluso donde el dato puntual sí existe.

## 2.2 Limitaciones del artículo de referencia

El artículo de referencia presenta tres limitaciones metodológicas que esta tesis identifica explícitamente y propone superar:

- **Ausencia de regionalización. **Los datos provienen de California, 2022, en clima mediterráneo. Las condiciones de Campeche —temperatura 28–40 °C, HR frecuentemente >85% en temporada de lluvias, ciclos circadianos tropicales distintos— no están representadas. Los umbrales de decisión aprendidos por los modelos, los patrones circadianos documentados y las correlaciones entre variables ambientales y estado de salud no son directamente transferibles a *M. beecheii* en Yucatán.

- **Ausencia de preprocesamiento de señal documentado. **Las variables ambientales —temperatura, humedad, presión— se concatenan directamente al vector de características sin filtrado previo. Las características acústicas se extraen sin pre-énfasis ni eliminación de segmentos silenciosos. Librosa aplica implícitamente una ventana de Hamming y banco de filtros Mel, pero no constituyen un protocolo de acondicionamiento de señal explícito.

- **Arquitectura sensorial homogénea. **Un solo sensor por parámetro (DHT22 para temperatura/humedad, INMP441 para audio). No hay redundancia ni cobertura de los rangos donde cada sensor pierde precisión. El DHT22 se satura por encima de ~85% HR, rango frecuente en Campeche. El INMP441 no capta vibraciones estructurales del nido en el rango de 1–50 Hz donde parte del comportamiento comunicativo de las meliponinas ocurre.

## 2.3 Hallazgos metodológicos clave del artículo de referencia

El análisis de importancia de características reveló que las variables no acústicas dominan: la variable frames concentró el 27.5% de la importancia relativa en XGBoost. La correlación negativa más fuerte con el estado de salud fue la humedad interna (ρ = −0.378). Esto confirma la importancia crítica de medir correctamente la humedad —y por tanto, la necesidad de una arquitectura sensorial robusta que no pierda precisión en los rangos de alta HR del clima tropical.

## 2.4 Amenazas bióticas en colmenas de *M. beecheii*

Los principales agentes de intrusión documentados son hormigas de los géneros Atta, Solenopsis y Azteca; moscas cleptoparásitas de la familia Phoridae; avispas; lagartos; y otras especies de insectos (Lóriga Peña et al., 2015). Estos eventos pueden provocar el abandono del nido o la muerte de la colmena en períodos cortos.

