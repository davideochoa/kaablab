#ifndef SENSORES_H
#define SENSORES_H

#include <Arduino.h>

// Estructura de una lectura ambiental+tráfico instantánea (sin procesar)
struct LecturaInstantanea {
  float dht_T;
  float dht_RH;
  float sht_T;
  float sht_RH;
  uint32_t trafico_entradas;   // acumulado desde la última ventana
  uint32_t trafico_salidas;
  uint32_t timestamp_unix;     // desde el DS3231
};

// Inicializa todos los sensores y el RTC. Devuelve false si algo crítico falla.
bool sensores_iniciar();

// Lee DHT22 + SHT31 + contadores IR (y los reinicia) + hora del RTC.
LecturaInstantanea sensores_leer_instantanea();

// Captura una ventana de audio cruda (bloqueante ~1s). Escribe N_MUESTRAS_AUDIO
// muestras int16 en 'buffer'. 'buffer' debe tener espacio para N_MUESTRAS_AUDIO.
void sensores_capturar_audio(int16_t *buffer);

// Captura una ventana de vibración cruda (bloqueante ~2s), 3 ejes, desde el
// MPU6500 (librería MPU9250_WE, clase MPU6500_WE). Valores int16 en mg.
// 'buffer' debe tener espacio para N_MUESTRAS_VIB * 3 (formato intercalado x,y,z,x,y,z,...)
void sensores_capturar_vibracion(int16_t *buffer);

// Handlers de interrupción para los 2 pares de haces IR (llamar desde attachInterrupt)
void IRAM_ATTR isr_ir_a();
void IRAM_ATTR isr_ir_b();

#endif
