# CAPÍTULO V. CONCLUSIONES

## 5.1 Conclusiones

El presente protocolo documenta la factibilidad científica y metodológica del proyecto KaabLab en su fase de adaptación a *Melipona beecheii*. Las conclusiones son las siguientes:

- El artículo de referencia (Chin-Canché et al., 2026a) valida los pipelines con métricas sólidas y código disponible, estableciendo un punto de partida técnico concreto y no especulativo.

- El análisis de transferibilidad (Tabla 3.1) confirma que, tras excluir el módulo de visión no transferible a *M. beecheii* (*Varroa destructor* no la parasita), cerca del 40% de los componentes restantes son directamente reutilizables (extracción MFCC, XGBoost/Gradient Boosting, optimizador de hiperparámetros). Las contribuciones originales esperadas de esta tesis son:

  1. El primer dataset multimodal documentado de *M. beecheii* (audio aéreo + vibración estructural + conteo IR de tráfico en piquera + variables ambientales interna/externa).
  2. La arquitectura sensorial heterogénea con rangos complementarios.
  3. El protocolo formal de preprocesamiento de señal en cinco etapas (filtro de media móvil, pre-énfasis, umbral RMS, normalización Z-score y fusión sensorial ponderada por confianza y contraste interno-externo).
  4. La caracterización explícita de las cinco brechas bibliográficas de la especie en sonido aéreo, contraste térmico interno-externo, humedad relativa intranidal, conteo IR direccional y vibración estructural (sección 1.1.5).
  5. El sistema KaabLab validado en campo en meliponarios mayas de Campeche.

- La arquitectura sensorial heterogénea (sensores interno y externo de temperatura/humedad + sensor de sonido aéreo + sensor de vibración estructural + sensor IR doble haz) responde a una limitación real del artículo de referencia: ningún sensor mide directamente la magnitud física de interés; todos miden un fenómeno eléctrico secundario con limitaciones de rango, histéresis y deriva. En el clima tropical de Campeche, con HR frecuentemente >85%, esta arquitectura se plantea como necesaria para garantizar la calidad del dataset (por validar en campo). El desdoblamiento interno/externo de la medición de humedad y temperatura, además, habilita el contraste diagnóstico propio de una especie termoconformadora como *M. beecheii*.

- El protocolo de preprocesamiento convierte una limitación del trabajo previo en una contribución metodológica concreta. Se espera que un modelo entrenado con datos de alta calidad supere a uno más sofisticado entrenado con datos ruidosos.

- El cronograma de cuatro semestres es realista porque los pipelines bioacústico y de optimización ya están implementados. El trabajo principal es la recolección de datos y el reentrenamiento, con la adición de la validación de la arquitectura sensorial y del sensor IR de conteo en el primer semestre.
