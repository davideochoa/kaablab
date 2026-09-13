/*
 * MPU6050 — Ruta B (OPCIONAL): interrupcion data-ready + FIFO interno
 * KaabLab — vibración estructural, banda objetivo 300-600 Hz (Hrncir et al. 2006)
 *
 * IMPLEMENTAR SOLO SI la Ruta A (mpu6050_polling.ino) muestra perdida de
 * muestras en la prueba de banco (ver README.md sección 5). No es la ruta
 * recomendada para la primera prueba.
 *
 * Objetivo: evitar que el ESP32 bloquee el procesador con polling continuo.
 * El MPU6050 avisa por el pin INT cuando hay una muestra nueva y acumula
 * los datos en su FIFO interno; el ESP32 los retira en bloque cuando puede,
 * sin necesidad de sondear el bus I2C constantemente.
 *
 * Librería: I2Cdevlib MPU6050 (Jeff Rowberg)
 *   https://github.com/jrowberg/i2cdevlib
 *
 * Pin mapping confirmado del proyecto:
 *   SDA = GPIO21
 *   SCL = GPIO22
 * Pin INT sugerido (NO CONFIRMADO contra el mapeo global de pines del
 * proyecto en firmware/esp32_main): GPIO4. Verificar que no choque con
 * otro sensor (IR doble haz usa GPIO25/32/33; INMP441 usa pines I2S,
 * ver conflicto pendiente de GPIO14 en CLAUDE.md) antes de cablear.
 */

#include <Wire.h>
#include <MPU6050.h>

MPU6050 mpu;

const uint8_t SDA_PIN = 21;
const uint8_t SCL_PIN = 22;
const uint8_t INT_PIN = 4; // ver advertencia arriba: confirmar antes de cablear

const uint8_t SMPLRT_DIV_TARGET = 2; // ver README.md sección 2.1: ~2667 Hz, Nyquist ~1333 Hz
const uint8_t PACKET_SIZE = 6;       // accel X/Y/Z, 2 bytes cada eje

volatile bool mpuDataReady = false;

void IRAM_ATTR onMPUDataReady() {
  mpuDataReady = true;
}

void setup() {
  Serial.begin(115200);
  while (!Serial) { /* espera puerto serie en placas con USB nativo */ }

  Wire.begin(SDA_PIN, SCL_PIN);
  Wire.setClock(400000); // I2C Fast Mode: límite físico del bus del MPU6050

  pinMode(INT_PIN, INPUT);

  mpu.initialize();
  if (!mpu.testConnection()) {
    Serial.println("ERROR: MPU6050 no responde en el bus I2C (verificar cableado/direccion)");
    while (1) { delay(1000); } // fallo de inicializacion, no de muestreo
  }

  mpu.setDLPFMode(MPU6050_DLPF_BW_256); // DLPF_CFG=0 (ver README.md sección 2.2 para la limitación del ADC del acelerómetro)
  mpu.setRate(SMPLRT_DIV_TARGET);
  mpu.setFullScaleAccelRange(MPU6050_ACCEL_FS_4);

  // Habilitar solo el acelerómetro en el FIFO (no giroscopio/temperatura,
  // para mantener el tamaño de paquete en 6 bytes y simplificar el parseo).
  mpu.setAccelFIFOEnabled(true);
  mpu.setXGyroFIFOEnabled(false);
  mpu.setYGyroFIFOEnabled(false);
  mpu.setZGyroFIFOEnabled(false);

  mpu.setIntDataReadyEnabled(true); // pulso en INT en cada muestra nueva
  mpu.setFIFOEnabled(true);
  mpu.resetFIFO();

  attachInterrupt(digitalPinToInterrupt(INT_PIN), onMPUDataReady, RISING);

  Serial.println("timestamp_us,ax,ay,az");
}

void loop() {
  if (!mpuDataReady) {
    return; // sin bloquear: el procesador queda libre para otras tareas
  }
  mpuDataReady = false;

  uint16_t fifoCount = mpu.getFIFOCount();

  // Si el FIFO se desbordo (buffer lleno antes de ser leido), se pierde
  // la referencia de alineacion de paquetes: reiniciar y descartar el lote.
  uint8_t intStatus = mpu.getIntStatus();
  if (intStatus & 0x10) { // bit FIFO_OFLOW_INT (ver Register Map, Registro 58)
    mpu.resetFIFO();
    Serial.println("AVISO: FIFO overflow, buffer reiniciado (revisar tasa de vaciado)");
    return;
  }

  while (fifoCount >= PACKET_SIZE) {
    uint8_t buffer[PACKET_SIZE];
    mpu.getFIFOBytes(buffer, PACKET_SIZE);

    int16_t ax = (int16_t)((buffer[0] << 8) | buffer[1]);
    int16_t ay = (int16_t)((buffer[2] << 8) | buffer[3]);
    int16_t az = (int16_t)((buffer[4] << 8) | buffer[5]);

    Serial.print(micros());
    Serial.print(',');
    Serial.print(ax);
    Serial.print(',');
    Serial.print(ay);
    Serial.print(',');
    Serial.println(az);

    fifoCount -= PACKET_SIZE;
  }
}
