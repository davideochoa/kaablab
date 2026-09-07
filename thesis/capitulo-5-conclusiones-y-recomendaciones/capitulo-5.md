CAPÍTULO V. CONCLUSIONES Y RECOMENDACIONES

5.1 Conclusiones

El presente protocolo documenta la factibilidad científica y metodológica del proyecto KaabLab en su fase de adaptación a Melipona beecheii. Las conclusiones son las siguientes:

- El artículo de referencia (Chin-Canché et al., 2026) valida los pipelines con métricas sólidas y código disponible, estableciendo un punto de partida técnico concreto y no especulativo.

- El análisis de transferibilidad confirma que cerca del 60% de los componentes son reutilizables. Las contribuciones originales centrales son el dataset de M. beecheii, la arquitectura sensorial heterogénea y el protocolo de preprocesamiento.

- La arquitectura sensorial heterogénea (DHT22 + SHT31 + INMP441 + MPU6050) responde a una limitación real del artículo de referencia: ningún sensor mide directamente la magnitud física de interés; todos miden un fenómeno eléctrico secundario con limitaciones de rango, histéresis y deriva. En el clima tropical de Campeche, con HR frecuentemente >85%, esta arquitectura no es opcional sino necesaria para garantizar la calidad del dataset.

- El protocolo de preprocesamiento convierte una limitación del trabajo previo en una contribución metodológica concreta. Un modelo entrenado con datos de alta calidad siempre supera a un modelo más sofisticado entrenado con datos ruidosos.

- El cronograma de cuatro semestres es realista porque los pipelines ya están implementados. El trabajo principal es la recolección de datos y el reentrenamiento, con la adición de la validación de la arquitectura sensorial en el primer semestre.

5.2 Recomendaciones

- Confirmar tempranamente la cobertura de conectividad en cada meliponario para decidir entre transmisión WiFi y respaldo local con sincronización diferida; de optarse por LoRa para telemetría, incorporar el módulo de radio y el gateway correspondientes al presupuesto.

- Iniciar la fase de aclimatación e instrumentación con suficiente antelación al etiquetado, dado el período de adaptación de 2–4 semanas de la colonia.

- Documentar desde el inicio la divergencia entre DHT22 y SHT31 como indicador de contaminación por propóleos, para anticipar el mantenimiento de sensores.

- Extender, una vez validado el sistema, la metodología a otras especies del género Melipona, reutilizando el pipeline y el protocolo de preprocesamiento.

