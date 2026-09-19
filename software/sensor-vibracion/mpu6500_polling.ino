/*
 * MPU6500 — Ruta A: polling con librería, muestreo a FS_VIB = 1500 Hz
 * KaabLab — vibración estructural, banda objetivo 300-600 Hz (Hrncir et al. 2006)
 *
 * Ver README.md (secciones 2 y 3.1) para la justificación completa de esta
 * configuración antes de modificarla.
 *
 * Librería: MPU9250_WE (Wolfgang Ewald) — clase MPU6500_WE
 *   https://github.com/wollewald/MPU9250_WE
 *   Instalar vía Arduino Library Manager: "MPU9250_WE"
 *   Mismo patrón que software/nodo_kaablab/sensores.cpp: imu.init() +
 *   whoAmI() == 0x70. No se usa I2Cdevlib: su testConnection() valida el
 *   WHO_AM_I del MPU6050 y no es compatible con el MPU6500.
 *
 * Pin mapping confirmado del proyecto:
 *   SDA = GPIO21
 *   SCL = GPIO22
 *   AD0 del MPU6500 a 3.3 V -> dirección I2C 0x69 (0x68 choca con el DS3231)
 */

#include <Wire.h>
#include <MPU6500_WE.h>

const uint8_t MPU6500_ADDR = 0x69;
const uint8_t MPU6500_WHO_AM_I = 0x70;

MPU6500_WE mpu(&Wire, MPU6500_ADDR);

const uint8_t SDA_PIN = 21;
const uint8_t SCL_PIN = 22;

// --- Tasa de muestreo (ver README.md sección 2) ---
// Criterio: Nyquist >= 600 Hz con margen de diseño ~1.25x -> FS_VIB = 1500 Hz
// (Nyquist = 750 Hz). Igual que FS_VIB en nodo_kaablab/config.h.
// Con el DLPF del acelerómetro desactivado la salida corre a 4 kHz y SMPLRT_DIV
// no la divide: la tasa se impone aquí por temporización (polling con micros()).
const uint16_t FS_VIB = 1500;
const unsigned long SAMPLE_INTERVAL_US = 1000000UL / FS_VIB; // ~666 us

void setup() {
  // 921600 baudios: a 1500 lineas/s de CSV, 115200 baudios no alcanzan y el
  // Serial.print() bloquearia el bucle de muestreo.
  Serial.begin(921600);
  while (!Serial) { /* espera puerto serie en placas con USB nativo */ }

  Wire.begin(SDA_PIN, SCL_PIN);
  Wire.setClock(400000); // I2C Fast Mode: límite físico del bus del MPU6500 (ver README 2.3)

  // init() ya compara WHO_AM_I contra 0x70; whoAmI() se verifica de forma
  // explícita para poder reportar el valor leído.
  if (!mpu.init() || mpu.whoAmI() != MPU6500_WHO_AM_I) {
    Serial.printf("ERROR: MPU6500 no detectado en 0x%02X (WHO_AM_I=0x%02X, esperado 0x%02X; verificar cableado y AD0)\n",
                  MPU6500_ADDR, mpu.whoAmI(), MPU6500_WHO_AM_I);
    while (1) { delay(1000); } // fallo de inicializacion, no de muestreo: delay() aceptable aqui
  }

  mpu.setAccRange(MPU6500_ACC_RANGE_4G); // +/-4g; ajustar segun amplitud esperada

  // Tras el reset el DLPF del acelerómetro queda activo (5-260 Hz, datasheet
  // MPU-6500 Rev 1.1, Tabla 2) y atenuaría la banda 300-600 Hz. Se desactiva
  // (ACCEL_CONFIG2, accel_fchoice_b = 1): salida a 4 kHz, ancho de banda ~1046 Hz.
  mpu.enableAccDLPF(false);

  Serial.print("Sample Rate configurado: ");
  Serial.print(FS_VIB);
  Serial.println(" Hz");
  Serial.println("timestamp_us,ax_mg,ay_mg,az_mg");
}

void loop() {
  static unsigned long lastSampleUs = 0;
  unsigned long nowUs = micros();

  // Temporizacion no bloqueante: NO se usa delay() en este bucle.
  // El polling bloqueante es el cuello de botella real, no el bus I2C
  // (ver README.md sección 2.3, "Nota explícita").
  if (nowUs - lastSampleUs >= SAMPLE_INTERVAL_US) {
    lastSampleUs = nowUs;

    xyzFloat g = mpu.getGValues(); // aceleración en g; lectura de 6 bytes por I2C

    Serial.print(nowUs);
    Serial.print(',');
    Serial.print((int16_t)(g.x * 1000.0f)); // a mg, igual que nodo_kaablab
    Serial.print(',');
    Serial.print((int16_t)(g.y * 1000.0f));
    Serial.print(',');
    Serial.println((int16_t)(g.z * 1000.0f));
  }

  // Espacio para otras tareas no bloqueantes del ESP32 (WiFi, otros sensores).
  // No agregar delay() aqui: reduciria la tasa de muestreo efectiva por debajo
  // de la configurada y reintroduciria el problema de la sección 1.
}
