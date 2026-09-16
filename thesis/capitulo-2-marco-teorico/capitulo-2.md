# CAPÍTULO 2. ESTADO DEL ARTE O MARCO TEÓRICO

## 2.1 La meliponicultura maya y *Melipona beecheii*

*M. beecheii* es criada por comunidades mayas desde épocas prehispánicas. Su miel posee propiedades antioxidantes (Cauich Kumul et al., 2015) y antimicrobianas (Ramírez-Miranda et al., 2023) documentadas. La especie se encuentra en declive severo atribuido a deforestación, expansión agrícola y plaguicidas (Villanueva-Gutiérrez et al., 2013). Sus características biológicas difieren profundamente de *Apis mellifera*: colonias de 300–2,000 individuos, piquera tipo tubo de cerumen de 5–15 mm, repertorio acústico propio de los meliponinos, y termoconformidad en rangos tropicales de 25.4-34.0°C, con media de 30.2°C (Moo-Valle et al., 2000).

**Tabla 2.1** Parámetros documentados vs. no documentados para *M. beecheii*

| Parámetro | Valor/rango en *M. beecheii* | Fuente (específica o congénere) | ¿Existe registro para la especie? | Relevancia para la tesis |
| --- | --- | --- | --- | --- |
| Sonido aéreo | Sin caracterización publicada | Ni siquiera hay dato de congéneres del género Melipona | No | Gap total; además, ausencia de 2-heptanol (feromona de alarma típica del grupo) no detectada en *M. beecheii* (Cruz-López et al., 2005) sugiere mecanismo de defensa distinto, sin documentar |
| Temperatura interna | 25.4–34.0°C, media 30.2°C; 90% mortalidad de pupas a 40°C, 100% a 5°C | Específica de *M. beecheii* (Moo-Valle et al., 2000; Macías-Macías et al., 2011) | Sí | Dato específico existe, pero nunca fue tomado mediante monitoreo continuo automatizado (ver Tabla 2.2) |
| Humedad relativa intranidal | Sin rango caracterizado | Ni siquiera hay dato de congéneres — "the dynamics of water balance has not been studied in stingless bees" (Roubik, 2006) | No | Gap total para todas las meliponinas, no solo *M. beecheii* |
| Conteo de tráfico (IR, piquera) | Sin rango de referencia | Parcial en congénere: Justino y Hartfelder (2024) registraron actividad en *M. quadrifasciata* sin diferenciar dirección | No (para conteo direccional) | Gap específico: ningún precedente de conteo IR bidireccional en meliponinos |
| Vibración estructural | Componentes de vuelo 180-250Hz; forrajeo 300-600Hz fundamental | Congénere (Hrncir et al., 2000/2006/2008); otro meliponino no congénere: dos Santos et al. (2025), en *Scaptotrigona* aff. *depilis* | No | Gap total para la especie; sin precedente de acelerómetro en meliponinos |

**Tabla 2.2** Registros previos de *M. beecheii*: manuales vs. monitoreo continuo automatizado

| Estudio | Tipo de registro | Parámetro | Duración/método | ¿Continuo y automatizado? |
| --- | --- | --- | --- | --- |
| Moo-Valle et al. (2000) | Estudio formal de campo | Temperatura intranidal | Cavidades naturales en Yucatán (el más riguroso encontrado para la especie); temperatura más estable de día (9:00-20:00h) que de noche | No — sondas manuales, periodo acotado |
| Macías-Macías et al. (2011) | Estudio formal de laboratorio | Mortalidad bajo temperatura extrema | Exposición controlada a 40°C y 5°C por 24h, comparando *M. beecheii*, *M. colimana* y *Scaptotrigona hellwegeri* | No — puntual |
| Quezada-Euán (2018) | Observación personal no sistemática | Comportamiento térmico/defensivo | "Pers. obs.", sin protocolo formal | No |
| Medina-Medina et al. (2014) | Observación conductual sistemática | Manejo de desechos | Observación directa, no basada en sensores | No |

Ninguno de los estudios revisados usó monitoreo continuo automatizado; todos fueron manuales, puntuales o de corta duración (días a semanas), sin uso de sensores IoT para registro continuo de meses. Este hallazgo es el argumento central del vacío bibliográfico de la sección 1.1.5.

## 2.2 Limitaciones del artículo de referencia

El artículo de referencia presenta tres limitaciones metodológicas que esta tesis identifica explícitamente y propone superar:

- **Ausencia de regionalización. **Los datos provienen de California, 2022, en clima mediterráneo. Las condiciones de Campeche —temperatura 28–40 °C, HR frecuentemente >85% en temporada de lluvias, ciclos circadianos tropicales distintos— no están representadas. Los umbrales de decisión aprendidos por los modelos, los patrones circadianos documentados y las correlaciones entre variables ambientales y estado de salud no son directamente transferibles a *M. beecheii* en Yucatán.

- **Ausencia de preprocesamiento de señal documentado. **Las variables ambientales —temperatura, humedad, presión— se concatenan directamente al vector de características sin filtrado previo. Las características acústicas se extraen sin pre-énfasis ni eliminación de segmentos silenciosos. Librosa aplica implícitamente una ventana de Hamming y banco de filtros Mel, pero no constituyen un protocolo de acondicionamiento de señal explícito.

- **Arquitectura sensorial homogénea. **Un solo sensor por parámetro (un sensor básico de temperatura/humedad, un micrófono MEMS estándar para audio). No hay redundancia ni cobertura de los rangos donde cada sensor pierde precisión. El sensor de temperatura/humedad básico se satura por encima de ~85% HR, rango frecuente en Campeche. El micrófono MEMS estándar no capta vibraciones estructurales del nido en el rango de 1–50 Hz donde parte del comportamiento comunicativo de las meliponinas ocurre.

## 2.3 Hallazgos metodológicos clave del artículo de referencia

El análisis de importancia de características reveló que las variables no acústicas dominan: la variable frames concentró el 27.5% de la importancia relativa en XGBoost. La correlación negativa más fuerte con el estado de salud fue la humedad interna (ρ = −0.378). Esto confirma la importancia crítica de medir correctamente la humedad —y por tanto, la necesidad de una arquitectura sensorial robusta que no pierda precisión en los rangos de alta HR del clima tropical.

## 2.4 Amenazas bióticas en colmenas de *M. beecheii*

Los principales agentes de intrusión documentados en meliponarios mayas de Campeche son la hormiga arriera (Eciton burchelli parvispinum, "xuulá" en maya) y la mosca parasitaria nenem (Pseudohypocera kerteszi, familia Phoridae), reportadas por el 47% y el 20% de los meliponicultores encuestados respectivamente, con mayor incidencia de la hormiga durante la temporada de lluvias (junio-septiembre) (Pat Fernández et al., 2018). Estos eventos pueden provocar el abandono del nido o la muerte de la colmena en períodos cortos.

<!-- REVISAR: avispas y lagartos como depredadores de M. beecheii no encontraron respaldo académico verificable; se retiraron de esta versión. Si se cuenta con fuente primaria, reincorporar con cita específica. -->

