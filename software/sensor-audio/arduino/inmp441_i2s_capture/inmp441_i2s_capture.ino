/*
 * INMP441 — Captura de audio I2S, lectura no bloqueante
 * KaabLab — nivel acústico / vitalidad de la colonia (Melipona beecheii)
 *
 * Bandas de interés documentadas (ver README.md sección 1):
 *   - Comunicación acústica:        200-2,000 Hz (rango óptimo del sensor)
 *   - Actividad de vuelo en piquera: 200-500 Hz
 *   - Alarma / intrusos:            hasta 5,000-8,000 Hz
 *
 * Ver README.md (secciones 2 y 3) para la justificación completa de esta
 * configuración antes de modificarla.
 *
 * Pin mapping confirmado del proyecto (CLAUDE.md, thesis/capitulo-2-materiales-y-metodos/capitulo-2.md Tabla 2.3):
 *   SCK (bit clock)           = GPIO14
 *   WS  (word select / LRCLK) = GPIO15
 *   SD  (datos)               = GPIO32
 *   L/R                       = GND  (selecciona canal izquierdo -> mono)
 *
 * Driver: API clásica ESP-IDF I2S (driver/i2s.h), incluida en el core
 * Arduino-ESP32 2.x. Si el proyecto usa el core 3.x (ESP-IDF v5), esta API
 * está marcada "legacy" — ver nota de migración al final de este archivo.
 */

#include <driver/i2s.h>

const i2s_port_t I2S_PORT = I2S_NUM_0;

const int I2S_SCK_PIN = 14;
const int I2S_WS_PIN  = 15;
const int I2S_SD_PIN  = 32;

// --- Configuración objetivo (ver README.md sección 2.1) ---
// Nyquist = SAMPLE_RATE_HZ / 2 >= 8,000 Hz cubre sin aliasing el extremo
// superior de la banda de alarma documentada (hasta 8,000 Hz), con margen.
const uint32_t SAMPLE_RATE_HZ = 16000;

const int DMA_BUF_COUNT = 8;
const int DMA_BUF_LEN   = 256; // muestras por buffer DMA

// Buffer de lectura: 32 bits por muestra (24 bits válidos dentro de la
// trama de 32, ver README.md sección 2.3 — protocolo I2S estándar, no PDM).
const size_t READ_BUF_SAMPLES = 256;
int32_t readBuffer[READ_BUF_SAMPLES];

void setup() {
  Serial.begin(115200);
  while (!Serial) { /* espera puerto serie en placas con USB nativo */ }

  i2s_config_t i2sConfig = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = SAMPLE_RATE_HZ,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,      // trama de 32 bits (24 bits validos, README 2.3)
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,       // L/R=GND -> canal izquierdo, mono (README 2.4)
    .communication_format = I2S_COMM_FORMAT_STAND_I2S, // I2S estandar, NO PDM
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = DMA_BUF_COUNT,
    .dma_buf_len = DMA_BUF_LEN,
    .use_apll = false,
    .tx_desc_auto_clear = false,
    .fixed_mclk = 0
  };

  i2s_pin_config_t pinConfig = {
    .bck_io_num = I2S_SCK_PIN,
    .ws_io_num = I2S_WS_PIN,
    .data_out_num = I2S_PIN_NO_CHANGE, // no se usa TX (solo captura)
    .data_in_num = I2S_SD_PIN
  };

  esp_err_t err = i2s_driver_install(I2S_PORT, &i2sConfig, 0, NULL);
  if (err != ESP_OK) {
    Serial.printf("ERROR: i2s_driver_install fallo (codigo %d)\n", err);
    while (1) { delay(1000); } // fallo de inicializacion, no de muestreo: delay() aceptable aqui
  }

  err = i2s_set_pin(I2S_PORT, &pinConfig);
  if (err != ESP_OK) {
    Serial.printf("ERROR: i2s_set_pin fallo (codigo %d)\n", err);
    while (1) { delay(1000); }
  }

  i2s_zero_dma_buffer(I2S_PORT);

  Serial.print("I2S configurado: ");
  Serial.print(SAMPLE_RATE_HZ);
  Serial.println(" Hz, mono, trama de 32 bits (24 bits validos)");
  Serial.println("timestamp_us,sample_24bit");
}

void loop() {
  size_t bytesRead = 0;

  // Lectura no bloqueante: ticks_to_wait=0 retorna de inmediato con lo que
  // ya esta disponible en el buffer DMA interno del periferico I2S, sin
  // detener el bucle principal (analogo a la nota de la seccion 2.3 del
  // README de sensor-vibracion: evitar bloquear otras tareas del ESP32 -
  // WiFi, otros sensores - mientras se espera al sensor).
  esp_err_t result = i2s_read(I2S_PORT, readBuffer, sizeof(readBuffer),
                               &bytesRead, 0);

  if (result == ESP_OK && bytesRead > 0) {
    unsigned long nowUs = micros();
    size_t samplesRead = bytesRead / sizeof(int32_t);

    for (size_t i = 0; i < samplesRead; i++) {
      // El INMP441 entrega 24 bits validos alineados a la izquierda dentro
      // de la trama de 32 bits transmitida por I2S. Desplazar >>8 extrae
      // esos 24 bits como valor con signo.
      //
      // NOTA DE VALIDACION (README.md seccion 5): el periferico I2S del
      // ESP32 tiene un corrimiento de bit conocido en algunas versiones de
      // core Arduino-ESP32, que en la practica requiere >>11 en vez de >>8
      // para obtener la escala esperada. Confirmar en banco con un tono
      // conocido antes de asumir que >>8 es correcto para el hardware y
      // version de core especificos del proyecto.
      int32_t sample24 = readBuffer[i] >> 8;

      Serial.print(nowUs);
      Serial.print(',');
      Serial.println(sample24);
    }
  }

  // Espacio para otras tareas no bloqueantes del ESP32 (WiFi, otros
  // sensores). No agregar delay() aqui: reduciria el throughput de lectura
  // del buffer DMA y podria acumular retraso frente a la tasa de llegada
  // de datos configurada (16 kHz).
}

/*
 * Nota sobre migracion a Arduino-ESP32 core 3.x (ESP-IDF v5):
 * La API driver/i2s.h usada arriba esta marcada "legacy" (deprecated) en
 * ESP-IDF v5. La API nueva es i2s_std (driver/i2s_std.h), con funciones
 * i2s_new_channel(), i2s_channel_init_std_mode() e i2s_channel_read().
 * El mapeo de pines, sample rate y formato de datos documentados en
 * README.md aplican igual; solo cambian los nombres de funcion/struct.
 * Confirmar que version de core Arduino-ESP32 esta instalada antes de
 * copiar este codigo a un proyecto nuevo.
 */
