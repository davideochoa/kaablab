/*
 * MPU6500 — Ruta B (OPCIONAL): interrupcion data-ready + FIFO interno
 * KaabLab — vibración estructural, banda objetivo 300-600 Hz (Hrncir et al., 2000, 2006a)
 *
 * IMPLEMENTAR SOLO SI la Ruta A (mpu6500_polling.ino) muestra perdida de
 * muestras en la prueba de banco (ver README.md sección 5). No es la ruta
 * recomendada para la primera prueba.
 *
 * Objetivo: evitar que el ESP32 bloquee el procesador con polling continuo.
 * El MPU6500 avisa por el pin INT cuando hay una muestra nueva y acumula
 * los datos en su FIFO interno; el ESP32 los retira en bloque cuando puede,
 * sin necesidad de sondear el bus I2C constantemente.
 *
 * Tasa: con el DLPF del acelerómetro desactivado el FIFO se llena a 4 kHz y
 * SMPLRT_DIV no lo divide (README.md sección 2.2). El sketch diezma ese flujo
 * a FS_VIB = 1500 Hz con un acumulador de fase (1500 de cada 4000 muestras).
 *
 * Librería: MPU9250_WE (Wolfgang Ewald) — clase MPU6500_WE
 *   https://github.com/wollewald/MPU9250_WE
 *   Mismo patrón que software/nodo_kaablab/sensores.cpp: imu.init() +
 *   whoAmI() == 0x70. No se usa I2Cdevlib (su testConnection() no es
 *   compatible con el MPU6500).
 *
 * Pin mapping confirmado del proyecto:
 *   SDA = GPIO21
 *   SCL = GPIO22
 *   INT = GPIO13 (Ruta B, opcional) — confirmado en
 *   thesis/capitulo-2-materiales-y-metodos/capitulo-2.md, Tabla 2.3.
 *   Reasignado desde GPIO4 para evitar el choque con el DATA del DHT22
 *   (GPIO4, 1-Wire).
 *   AD0 del MPU6500 a 3.3 V -> dirección I2C 0x69 (0x68 choca con el DS3231)
 */

#include <Wire.h>
#include <MPU6500_WE.h>

const uint8_t MPU6500_ADDR = 0x69;
const uint8_t MPU6500_WHO_AM_I = 0x70;

MPU6500_WE mpu(&Wire, MPU6500_ADDR);

const uint8_t SDA_PIN = 21;
const uint8_t SCL_PIN = 22;
const uint8_t INT_PIN = 13; // Ruta B, opcional — ver Tabla 2.3

// Criterio: Nyquist >= 600 Hz con margen ~1.25x -> FS_VIB = 1500 Hz (README 2.1).
const uint16_t FS_VIB = 1500;
const uint16_t FS_INTERNA_HZ = 4000; // salida del acelerómetro con DLPF desactivado

volatile bool mpuDataReady = false;

void IRAM_ATTR onMPUDataReady() {
  mpuDataReady = true;
}

void setup() {
  // 921600 baudios: a 1500 lineas/s de CSV, 115200 baudios no alcanzan.
  Serial.begin(921600);
  while (!Serial) { /* espera puerto serie en placas con USB nativo */ }

  Wire.begin(SDA_PIN, SCL_PIN);
  Wire.setClock(400000); // I2C Fast Mode: límite físico del bus del MPU6500

  pinMode(INT_PIN, INPUT);

  if (!mpu.init() || mpu.whoAmI() != MPU6500_WHO_AM_I) {
    Serial.printf("ERROR: MPU6500 no detectado en 0x%02X (WHO_AM_I=0x%02X, esperado 0x%02X; verificar cableado y AD0)\n",
                  MPU6500_ADDR, mpu.whoAmI(), MPU6500_WHO_AM_I);
    while (1) { delay(1000); } // fallo de inicializacion, no de muestreo
  }

  mpu.setAccRange(MPU6500_ACC_RANGE_4G);
  mpu.enableAccDLPF(false); // README.md sección 2.2: sin DLPF la salida corre a 4 kHz

  mpu.enableInterrupt(MPU6500_DATA_READY);  // pulso en INT en cada muestra nueva
  mpu.setIntPinPolarity(MPU6500_ACT_HIGH);
  mpu.enableFifo(true);
  mpu.startFifo(MPU6500_FIFO_ACC);          // solo acelerómetro: paquete de 6 bytes (x,y,z)
  mpu.resetFifo();                          // arranca alineado a paquetes de 6 bytes

  attachInterrupt(digitalPinToInterrupt(INT_PIN), onMPUDataReady, RISING);

  Serial.print("Sample Rate configurado: ");
  Serial.print(FS_VIB);
  Serial.println(" Hz (diezmado desde 4000 Hz)");
  Serial.println("timestamp_us,ax_mg,ay_mg,az_mg");
}

void loop() {
  static uint16_t fase = 0; // acumulador de fase del diezmado 4000 -> FS_VIB

  if (!mpuDataReady) {
    return; // sin bloquear: el procesador queda libre para otras tareas
  }
  mpuDataReady = false;

  // Si el FIFO se desbordo (buffer lleno antes de ser leido), se pierde
  // la referencia de alineacion de paquetes: reiniciar y descartar el lote.
  // Leer INT_STATUS tambien limpia las banderas de interrupcion.
  uint8_t intStatus = mpu.readAndClearInterrupts();
  if (mpu.checkInterrupt(intStatus, MPU6500_FIFO_OVF)) {
    mpu.resetFifo();
    fase = 0;
    Serial.println("AVISO: FIFO overflow, buffer reiniciado (revisar tasa de vaciado)");
    return;
  }

  int paquetes = mpu.getNumberOfFifoDataSets(); // paquetes completos de 6 bytes en el FIFO
  for (int i = 0; i < paquetes; i++) {
    xyzFloat g = mpu.getGValuesFromFifo(); // aceleración en g

    // Diezmado 4000 -> FS_VIB: se conservan FS_VIB de cada 4000 muestras.
    fase += FS_VIB;
    if (fase < FS_INTERNA_HZ) continue;
    fase -= FS_INTERNA_HZ;

    Serial.print(micros());
    Serial.print(',');
    Serial.print((int16_t)(g.x * 1000.0f)); // a mg, igual que nodo_kaablab
    Serial.print(',');
    Serial.print((int16_t)(g.y * 1000.0f));
    Serial.print(',');
    Serial.println((int16_t)(g.z * 1000.0f));
  }
}
