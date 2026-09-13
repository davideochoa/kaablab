/*
 * MPU6050 — Ruta A: polling con librería, alta tasa de muestreo
 * KaabLab — vibración estructural, banda objetivo 300-600 Hz (Hrncir et al. 2006)
 *
 * Ver README.md (secciones 2 y 3.1) para la justificación completa de esta
 * configuración antes de modificarla.
 *
 * Librería: I2Cdevlib MPU6050 (Jeff Rowberg)
 *   https://github.com/jrowberg/i2cdevlib
 *   Instalar vía Arduino Library Manager: "I2Cdevlib-MPU6050"
 *   (requiere también la librería base "I2Cdevlib-Core")
 *
 * Pin mapping confirmado del proyecto:
 *   SDA = GPIO21
 *   SCL = GPIO22
 */

#include <Wire.h>
#include <MPU6050.h>

MPU6050 mpu;

const uint8_t SDA_PIN = 21;
const uint8_t SCL_PIN = 22;

// --- Cálculo de sample rate (ver README.md sección 2.1) ---
// Con DLPF deshabilitado (DLPF_CFG=0), el reloj base del giroscopio es 8 kHz.
//   Sample Rate = 8000 / (1 + SMPLRT_DIV)
//   SMPLRT_DIV = 2  ->  8000 / 3 ≈ 2667 Hz  ->  Nyquist ≈ 1333 Hz (>= 1200 Hz requerido)
const uint8_t SMPLRT_DIV_TARGET = 2;
const float SAMPLE_RATE_HZ = 8000.0f / (1 + SMPLRT_DIV_TARGET);
const unsigned long SAMPLE_INTERVAL_US = (unsigned long)(1000000.0f / SAMPLE_RATE_HZ);

void setup() {
  Serial.begin(115200);
  while (!Serial) { /* espera puerto serie en placas con USB nativo */ }

  Wire.begin(SDA_PIN, SCL_PIN);
  Wire.setClock(400000); // I2C Fast Mode: límite físico del bus del MPU6050 (ver README 2.3)

  mpu.initialize();
  if (!mpu.testConnection()) {
    Serial.println("ERROR: MPU6050 no responde en el bus I2C (verificar cableado/direccion)");
    while (1) { delay(1000); } // fallo de inicializacion, no de muestreo: delay() aceptable aqui
  }

  // DLPF_CFG = 0 (MPU6050_DLPF_BW_256): deshabilita el filtro pasa-bajas interno.
  // ADVERTENCIA (README.md sección 2.2): el ADC del acelerómetro del MPU6050
  // sigue muestreando internamente a 1 kHz fijo sin importar este ajuste;
  // validar en banco antes de instalación en campo.
  mpu.setDLPFMode(MPU6050_DLPF_BW_256);
  mpu.setRate(SMPLRT_DIV_TARGET);

  mpu.setFullScaleAccelRange(MPU6050_ACCEL_FS_4); // +/-4g; ajustar segun amplitud esperada
  mpu.setFullScaleGyroRange(MPU6050_GYRO_FS_500);

  Serial.print("Sample Rate configurado: ");
  Serial.print(SAMPLE_RATE_HZ);
  Serial.println(" Hz");
  Serial.println("timestamp_us,ax,ay,az");
}

void loop() {
  static unsigned long lastSampleUs = 0;
  unsigned long nowUs = micros();

  // Temporizacion no bloqueante: NO se usa delay() en este bucle.
  // El polling bloqueante es el cuello de botella real, no el bus I2C
  // (ver README.md sección 2.3, "Nota explícita").
  if (nowUs - lastSampleUs >= SAMPLE_INTERVAL_US) {
    lastSampleUs = nowUs;

    int16_t ax, ay, az;
    mpu.getAcceleration(&ax, &ay, &az); // lectura de 6 bytes, burst read via repeated-start

    Serial.print(nowUs);
    Serial.print(',');
    Serial.print(ax);
    Serial.print(',');
    Serial.print(ay);
    Serial.print(',');
    Serial.println(az);
  }

  // Espacio para otras tareas no bloqueantes del ESP32 (WiFi, otros sensores).
  // No agregar delay() aqui: reduciria la tasa de muestreo efectiva por debajo
  // de la configurada y reintroduciria el problema de la sección 1.
}
