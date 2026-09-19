#include "sensores.h"
#include "config.h"

#include <Wire.h>
#include <DHT.h>
#include <Adafruit_SHT31.h>
#include <Adafruit_Sensor.h> // sensors_event_t (antes llegaba vía Adafruit_MPU6050.h)
#include <MPU6500_WE.h>       // de la librería MPU9250_WE (Wolfgang Ewald)
#include <RTClib.h>
#include <driver/i2s.h>

static DHT dht(PIN_DHT22, DHT_TYPE);
static Adafruit_SHT31 sht31 = Adafruit_SHT31();
// MPU6500 (GY-6500): clase MPU6500_WE (WHO_AM_I = 0x70). MPU9250_WE espera 0x71
// y un magnetómetro AK8963 que el MPU6500 no tiene.
static const uint8_t MPU6500_WHO_AM_I = 0x70;
static MPU6500_WE imu(&Wire, MPU6050_ADDR);
static RTC_DS3231 rtc;

// Contadores de tráfico, incrementados por interrupción, leídos y reiniciados
// en sensores_leer_instantanea(). volatile por ser compartidos con ISR.
static volatile uint32_t contador_entradas_a = 0;
static volatile uint32_t contador_salidas_b  = 0;

void IRAM_ATTR isr_ir_a() {
  // Lógica simplificada: par A dispara primero -> se cuenta como "entrada"
  // si dentro de una ventana corta también dispara el par B (dirección),
  // pero aquí solo se incrementa el contador crudo; la dirección fina
  // (entrada vs salida real) se resuelve en el celular a partir del
  // orden temporal de A/B, no en el ISR (mantenerlo simple y rápido).
  contador_entradas_a++;
}

void IRAM_ATTR isr_ir_b() {
  contador_salidas_b++;
}

bool sensores_iniciar() {
  Wire.begin(PIN_SDA, PIN_SCL);
  Wire.setClock(400000); // I2C Fast Mode, igual que sensor-vibracion/*.ino: a 100 kHz una lectura del MPU6500 puede exceder el periodo de muestreo (~667 µs a FS_VIB = 1500 Hz)

  dht.begin();

  if (!sht31.begin(0x44)) {
    Serial.println("ERROR: SHT31 no detectado");
    return false;
  }

  // init() ya compara WHO_AM_I contra 0x70; whoAmI() se verifica de forma explícita
  // para poder reportar el valor leído.
  if (!imu.init() || imu.whoAmI() != MPU6500_WHO_AM_I) {
    Serial.printf("ERROR: MPU6500 no detectado en 0x%02X (WHO_AM_I=0x%02X, esperado 0x%02X; verificar AD0)\n",
                  MPU6050_ADDR, imu.whoAmI(), MPU6500_WHO_AM_I);
    return false;
  }
  imu.setAccRange(MPU6500_ACC_RANGE_8G);
  // Tras el reset el filtro digital del acelerómetro queda activo (DLPF programable de
  // 5 a 260 Hz, datasheet MPU-6500 Rev 1.1, Tabla 2), lo que atenuaría la banda objetivo
  // 300–600 Hz. Se desactiva (ancho de banda ~1046 Hz),
  // equivalente al MPU6050_BAND_260_HZ anterior; el muestreo a FS_VIB se hace por polling.
  imu.enableAccDLPF(false);

  if (!rtc.begin()) {
    Serial.println("ERROR: DS3231 no detectado");
    return false;
  }

  // Configuración I2S para INMP441 (micrófono digital, formato estándar)
  i2s_config_t i2s_cfg = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = FS_AUDIO,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_STAND_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 4,
    .dma_buf_len = 1024,
    .use_apll = false
  };
  i2s_pin_config_t pin_cfg = {
    .bck_io_num = PIN_I2S_SCK,
    .ws_io_num = PIN_I2S_WS,
    .data_out_num = I2S_PIN_NO_CHANGE,
    .data_in_num = PIN_I2S_SD
  };
  i2s_driver_install(I2S_NUM_0, &i2s_cfg, 0, NULL);
  i2s_set_pin(I2S_NUM_0, &pin_cfg);

  // Pines IR como entrada con interrupción por flanco de bajada
  // (los módulos FC-51/KY-033 salen en LOW al detectar bloqueo del haz)
  pinMode(PIN_IR_A1, INPUT);
  pinMode(PIN_IR_A2, INPUT);
  pinMode(PIN_IR_B1, INPUT);
  pinMode(PIN_IR_B2, INPUT);
  attachInterrupt(digitalPinToInterrupt(PIN_IR_A1), isr_ir_a, FALLING);
  attachInterrupt(digitalPinToInterrupt(PIN_IR_B1), isr_ir_b, FALLING);
  // Nota: A2/B2 son el segundo módulo de cada par enfrentado; según el
  // arreglo confirmado (2 pares FC-51/KY-033 enfrentados), la lógica de
  // qué par cuenta como "entrada" vs "salida" definitiva se resuelve con
  // el orden temporal en el celular, no aquí.

  return true;
}

LecturaInstantanea sensores_leer_instantanea() {
  LecturaInstantanea l;

  l.dht_T = dht.readTemperature();
  l.dht_RH = dht.readHumidity();

  sensors_event_t humidity, temp;
  // Adafruit_SHT31 expone getEvent() en versiones recientes; si tu versión
  // de librería solo tiene readTemperature()/readHumidity(), sustituir aquí.
  l.sht_T = sht31.readTemperature();
  l.sht_RH = sht31.readHumidity();

  // Snapshot atómico de los contadores (deshabilitar interrupciones brevemente)
  noInterrupts();
  l.trafico_entradas = contador_entradas_a;
  l.trafico_salidas = contador_salidas_b;
  contador_entradas_a = 0;
  contador_salidas_b = 0;
  interrupts();

  DateTime ahora = rtc.now();
  l.timestamp_unix = ahora.unixtime();

  return l;
}

void sensores_capturar_audio(int16_t *buffer) {
  size_t bytes_leidos = 0;
  size_t bytes_totales = N_MUESTRAS_AUDIO * sizeof(int16_t);
  i2s_read(I2S_NUM_0, (void *)buffer, bytes_totales, &bytes_leidos, portMAX_DELAY);
  // Si bytes_leidos < bytes_totales, el buffer queda parcialmente lleno;
  // el celular debe validar el tamaño real del archivo .pcm recibido.
}

void sensores_capturar_vibracion(int16_t *buffer) {
  // Muestreo por polling a FS_VIB (1500 Hz, periodo ~667 µs). No se usa la FIFO/interrupción
  // interna del MPU6500 (Ruta B, PIN_MPU_INT) en esta versión — polling
  // simple es suficiente dado que todo el procesamiento ocurre en el celular.
  const uint32_t periodo_us = 1000000UL / FS_VIB;

  // DIAGNÓSTICO: cuenta las iteraciones (lectura I2C + espera) cuya duración total excede
  // el periodo esperado más un 10 % de tolerancia; si la lectura tarda más que el periodo,
  // el muestreo se desfasa en silencio. Solo informa: no aborta ni altera la captura.
  // Revisar este contador en la primera prueba con hardware real antes de confiar en
  // FS_VIB = 1500 Hz para captura de campo (umbral de muestra tardía: ~733 µs).
  const uint32_t tolerancia_us = periodo_us + periodo_us / 10;
  uint32_t muestras_tardias = 0;

  for (int i = 0; i < N_MUESTRAS_VIB; i++) {
    uint32_t t0 = micros();
    // getGValues() devuelve la aceleración en g (ya corregida con los offsets,
    // que aquí son 0); a mg basta multiplicar por 1000. Con ±8 g el máximo es
    // ±8000 mg, muy por debajo del límite de int16 (±32767).
    xyzFloat g = imu.getGValues();
    buffer[i * 3 + 0] = (int16_t)(g.x * 1000.0f);
    buffer[i * 3 + 1] = (int16_t)(g.y * 1000.0f);
    buffer[i * 3 + 2] = (int16_t)(g.z * 1000.0f);

    // Espera activa hasta completar el periodo de muestreo
    while (micros() - t0 < periodo_us) { /* espera */ }

    if (micros() - t0 > tolerancia_us) muestras_tardias++;
  }

  if (muestras_tardias > 0) {
    Serial.printf("ADVERTENCIA: %lu/%d muestras de vibración excedieron el periodo esperado (%.1f%%)\n",
                  (unsigned long)muestras_tardias, N_MUESTRAS_VIB,
                  100.0f * muestras_tardias / N_MUESTRAS_VIB);
  }
}
