#ifndef CONFIG_H
#define CONFIG_H

// ===================== IDENTIDAD DEL NODO =====================
#define NODO_ID "nodo1"           // cambiar por nodo2/nodo3 al flashear cada uno
#define WIFI_SSID "KaabLab-Nodo1" // idem
// Red abierta por decisión de diseño (sin password) — fase Semestre 1
#define WIFI_OPEN true

// ===================== PINES I2C (bus compartido) =====================
// SHT31, IMU MPU6500/GY-6500 (@0x69, NO 0x68 -> AD0 a 3.3V para evitar choque con DS3231),
// DS3231 (@0x68)
#define PIN_SDA 21
#define PIN_SCL 22
#define MPU6050_ADDR 0x69   // Dirección del MPU6500 (GY-6500), AD0 en alto; el nombre MPU6050_ADDR se conserva por compatibilidad
#define DS3231_ADDR  0x68

// ===================== PIN DHT22 (protocolo propio de un hilo, no 1-Wire) =====================
#define PIN_DHT22 4
#define DHT_TYPE DHT22

// ===================== PINES I2S (INMP441) =====================
#define PIN_I2S_SCK 14
#define PIN_I2S_WS  15
#define PIN_I2S_SD  32

// ===================== PINES IR DOBLE HAZ (4 módulos TCRT5000 reflectivos) =====================
// Módulos reflectivos (emisor + receptor en la misma placa). Solo los principales
// (GPIO26, GPIO27) se usan para el conteo direccional; los secundarios son señales
// de diagnóstico de banco (redundancia), configuradas como entrada pero no leídas.
// Alimentar los módulos a 3.3 V, no 5 V (D0 subiría a 5 V y el ESP32 no lo tolera);
// validar la sensibilidad en banco.
#define PIN_IR_A1 26   // Haz A, módulo principal — conteo (Tabla 2.3: GPIO26)
#define PIN_IR_A2 25   // Haz A, módulo secundario — diagnóstico de banco (Tabla 2.3: GPIO25)
#define PIN_IR_B1 27   // Haz B, módulo principal — conteo (Tabla 2.3: GPIO27)
#define PIN_IR_B2 33   // Haz B, módulo secundario — diagnóstico de banco (Tabla 2.3: GPIO33)

// ===================== PIN INTERRUPCIÓN OPCIONAL MPU6500 (Ruta B) =====================
#define PIN_MPU_INT 13   // Confirmado en Tabla 2.3, sin choque con DHT22 (GPIO4)

// ===================== PINES SPI MICROSD (bus VSPI por defecto) =====================
#define PIN_SD_CS   5
#define PIN_SD_MOSI 23
#define PIN_SD_MISO 19
#define PIN_SD_SCK  18

// ===================== PARÁMETROS DE CAPTURA =====================
#define FS_AUDIO 16000          // Hz, igual que config.py del pipeline
#define DUR_AUDIO_S 1.0f        // segundos por ventana
#define N_MUESTRAS_AUDIO ((int)(FS_AUDIO * DUR_AUDIO_S))   // 16000 muestras

#define FS_VIB 1500             // Hz. Elección de diseño dentro de la capacidad del MPU6500 (salida
                                // programable hasta 4000 Hz con el DLPF desactivado). Nyquist = 750 Hz:
                                // cubre la banda de forrajeo 300-600 Hz con margen de diseño 1.25x sobre
                                // el límite superior (600 Hz). Igual que FS_VIB del pipeline.
#define DUR_VIB_S 2.0f
#define N_MUESTRAS_VIB ((int)(FS_VIB * DUR_VIB_S))         // 3000 muestras x 3 ejes

#define VENTANAS_POR_CICLO 10
#define INTERVALO_VENTANA_MS 30000UL   // 30 s entre ventanas

#define TIEMPO_ACTIVO_MS   (5UL * 60UL * 1000UL)   // 5 min activo
#define TIEMPO_DORMIDO_US  (55ULL * 60ULL * 1000000ULL) // 55 min dormido (deep sleep, en microsegundos)

// ===================== SERVIDOR HTTP =====================
#define HTTP_PORT 80

#endif
