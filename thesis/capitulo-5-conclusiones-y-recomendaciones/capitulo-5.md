# CAPÍTULO 5. CONCLUSIONES Y RECOMENDACIONES

## 5.1 Conclusiones

El presente protocolo documenta la factibilidad científica y metodológica del proyecto KaabLab en su fase de adaptación a *Melipona beecheii*. Las conclusiones son las siguientes:

- El artículo de referencia (Chin-Canché et al., 2026) valida los pipelines con métricas sólidas y código disponible, estableciendo un punto de partida técnico concreto y no especulativo.

- El análisis de transferibilidad (Tabla 4.1) confirma que, tras excluir el módulo de visión no transferible a *M. beecheii* (*Varroa destructor* no la parasita), cerca del 40% de los componentes restantes son directamente reutilizables (extracción MFCC, XGBoost/Gradient Boosting, optimizador de hiperparámetros). Las contribuciones originales centrales de esta tesis son:

  1. El primer dataset multimodal documentado de *M. beecheii* (audio aéreo + vibración estructural + conteo IR de tráfico en piquera + variables ambientales interna/externa).
  2. La arquitectura sensorial heterogénea con rangos complementarios.
  3. El protocolo formal de preprocesamiento de señal en cinco etapas (filtro de media móvil, pre-énfasis, umbral RMS, normalización Z-score y fusión sensorial ponderada por confianza y contraste interno-externo).
  4. La caracterización explícita de las cuatro brechas bibliográficas de la especie en sonido aéreo, contraste térmico interno-externo, conteo IR y vibración estructural (sección 1.1.5).
  5. El sistema KaabLab validado en campo en meliponarios mayas de Campeche.

- La arquitectura sensorial heterogénea (SHT31 interno primario + DHT22 externo secundario + INMP441 + MPU6050 + sensor IR doble haz) responde a una limitación real del artículo de referencia: ningún sensor mide directamente la magnitud física de interés; todos miden un fenómeno eléctrico secundario con limitaciones de rango, histéresis y deriva. En el clima tropical de Campeche, con HR frecuentemente >85%, esta arquitectura no es opcional sino necesaria para garantizar la calidad del dataset. El desdoblamiento interno/externo de la medición de humedad y temperatura, además, habilita el contraste diagnóstico propio de una especie termoconformadora como *M. beecheii*.

- El protocolo de preprocesamiento convierte una limitación del trabajo previo en una contribución metodológica concreta. Un modelo entrenado con datos de alta calidad siempre supera a un modelo más sofisticado entrenado con datos ruidosos.

- El cronograma de cuatro semestres es realista porque los pipelines bioacústico y de optimización ya están implementados. El trabajo principal es la recolección de datos y el reentrenamiento, con la adición de la validación de la arquitectura sensorial y del sensor IR de conteo en el primer semestre.

## 5.2 Recomendaciones

- Confirmar tempranamente la cobertura de conectividad en cada meliponario para decidir entre transmisión WiFi y respaldo local con sincronización diferida; de optarse por LoRa para telemetría, incorporar el módulo de radio y el gateway correspondientes al presupuesto.

- Iniciar la fase de aclimatación e instrumentación con suficiente antelación al etiquetado, dado el período de adaptación de 2–4 semanas de la colonia (sección 3.6).

- Documentar desde el inicio la divergencia entre el SHT31 interno y el DHT22 externo —más allá del desfase térmico esperado de 5–6 h— como indicador de posible contaminación por propóleos del sensor interno, para anticipar el mantenimiento de sensores.

- Resolver el conflicto de asignación del GPIO14 (compartido entre el bus I²C de SHT31/MPU6050 y el SCK del bus I²S del INMP441) antes del cableado final del prototipo (sección 3.3.1).

- Extender, una vez validado el sistema, la metodología a otras especies del género Melipona, reutilizando el pipeline, el protocolo de preprocesamiento y el diseño del sensor IR de conteo.
