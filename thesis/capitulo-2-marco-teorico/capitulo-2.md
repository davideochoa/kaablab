CAPÍTULO 2. ESTADO DEL ARTE O MARCO TEÓRICO

2.1 La meliponicultura maya y Melipona beecheii

M. beecheii es criada por comunidades mayas desde épocas prehispánicas. Su miel posee propiedades antioxidantes y antimicrobianas documentadas (Ramírez-Miranda et al., 2023; Cauich Kumul et al., 2015). La especie se encuentra en declive severo atribuido a deforestación, expansión agrícola y plaguicidas (Villanueva-Gutiérrez et al., 2014). Sus características biológicas difieren profundamente de Apis mellifera: colonias de 300–2,000 individuos, piquera tipo tubo de cerumen de 5–15 mm, repertorio acústico propio de los meliponinos, y termorregulación en rangos tropicales de 26–32 °C.

2.2 Limitaciones del artículo de referencia

El artículo de referencia presenta tres limitaciones metodológicas que esta tesis identifica explícitamente y propone superar:

- **Ausencia de regionalización. **Los datos provienen de California, 2022, en clima mediterráneo. Las condiciones de Campeche —temperatura 28–40 °C, HR frecuentemente >85% en temporada de lluvias, ciclos circadianos tropicales distintos— no están representadas. Los umbrales de decisión aprendidos por los modelos, los patrones circadianos documentados y las correlaciones entre variables ambientales y estado de salud no son directamente transferibles a M. beecheii en Yucatán.

- **Ausencia de preprocesamiento de señal documentado. **Las variables ambientales —temperatura, humedad, presión— se concatenan directamente al vector de características sin filtrado previo. Las características acústicas se extraen sin pre-énfasis ni eliminación de segmentos silenciosos. Librosa aplica implícitamente una ventana de Hamming y banco de filtros Mel, pero no constituyen un protocolo de acondicionamiento de señal explícito.

- **Arquitectura sensorial homogénea. **Un solo sensor por parámetro (DHT22 para temperatura/humedad, INMP441 para audio). No hay redundancia ni cobertura de los rangos donde cada sensor pierde precisión. El DHT22 se satura por encima de ~85% HR, rango frecuente en Campeche. El INMP441 no capta vibraciones estructurales del nido en el rango de 1–50 Hz donde parte del comportamiento comunicativo de las meliponinas ocurre.

2.3 Hallazgos metodológicos clave del artículo de referencia

El análisis de importancia de características reveló que las variables no acústicas dominan: la variable frames concentró el 27.5% de la importancia relativa en XGBoost. La correlación negativa más fuerte con el estado de salud fue la humedad interna (ρ = −0.378). Esto confirma la importancia crítica de medir correctamente la humedad —y por tanto, la necesidad de una arquitectura sensorial robusta que no pierda precisión en los rangos de alta HR del clima tropical.

2.4 Amenazas bióticas en colmenas de M. beecheii

Los principales agentes de intrusión documentados son hormigas de los géneros Atta, Solenopsis y Azteca; moscas cleptoparásitas de la familia Phoridae; avispas; lagartos; y otras especies de insectos (Lóriga Peña et al., 2015). Estos eventos pueden provocar el abandono del nido o la muerte de la colmena en períodos cortos.

