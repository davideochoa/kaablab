/*
 * SHT31 — Lectura de temperatura y humedad relativa interna
 * KaabLab — sensor interno primario, arquitectura sensorial heterogénea
 * (ver README.md, secciones 0-2, para la justificación completa)
 *
 * Librería: "Adafruit SHT31 Library"
 *   Instalar vía Arduino Library Manager: "Adafruit SHT31 Library"
 *   (requiere también la dependencia "Adafruit Unified Sensor")
 *
 * Protocolo: I2C. Bus compartido con el MPU6050 (ver
 * ../sensor-vibracion/README.md) — sin conflicto de direcciones:
 * SHT31 en 0x44/0x45, MPU6050/6500 en 0x68/0x69.
 *
 * Pin mapping confirmado del proyecto:
 *   SDA = GPIO21
 *   SCL = GPIO22
 */

#include <Wire.h>
#include <Adafruit_SHT31.h>

Adafruit_SHT31 sht31 = Adafruit_SHT31();

const uint8_t SDA_PIN = 21;
const uint8_t SCL_PIN = 22;
const uint8_t SHT31_ADDR = 0x44; // ADDR a GND en este proyecto (ver diagrama_conexion.svg)

const unsigned long READ_INTERVAL_MS = 1000;

void setup() {
  Serial.begin(115200);
  while (!Serial) { /* espera puerto serie en placas con USB nativo */ }

  Wire.begin(SDA_PIN, SCL_PIN);

  if (!sht31.begin(SHT31_ADDR)) {
    Serial.println("ERROR: SHT31 no responde en el bus I2C (verificar direccion/cableado)");
    while (1) { delay(1000); } // fallo de inicializacion, no de muestreo: delay() aceptable aqui
  }

  Serial.println("timestamp_ms,temperatura_C,humedad_relativa_pct");
}

void loop() {
  static unsigned long lastReadMs = 0;
  unsigned long nowMs = millis();

  if (nowMs - lastReadMs >= READ_INTERVAL_MS) {
    lastReadMs = nowMs;

    // readTemperature()/readHumidity() disparan una medicion nueva en el
    // chip (CMOSens) y leen el resultado ya calibrado via I2C.
    float temperatura = sht31.readTemperature(); // Celsius
    float humedad = sht31.readHumidity();

    if (isnan(temperatura) || isnan(humedad)) {
      Serial.println("ERROR: lectura fallida del SHT31 (bus I2C o sensor no responde)");
      return;
    }

    // Nota (README.md sección 0): esta %HR ya viene calibrada de fabrica
    // a partir de la capacitancia de la pelicula polimerica interna, no
    // es una medicion directa de humedad.
    //
    // Nota (CLAUDE.md, "Decisiones de diseño confirmadas"): por encima de
    // ~80-85% HR el SHT31 entra en un ciclo de autocalibracion interna;
    // la capa de fusion del proyecto reduce el peso de esta lectura
    // durante ese evento (ver thesis/capitulo-3-metodologia/capitulo-3.md,
    // sección 3.2.4, Paso 1).
    Serial.print(nowMs);
    Serial.print(',');
    Serial.print(temperatura, 2);
    Serial.print(',');
    Serial.println(humedad, 2);

    // La conversion a humedad absoluta (formula de Magnus) y el
    // contraste con el DHT22 externo se calculan en la capa de fusion
    // del proyecto (thesis/capitulo-3-metodologia/capitulo-3.md,
    // secciones 3.2.1 y 3.4.5), no en este sketch de adquisicion.
  }

  // Espacio para otras tareas no bloqueantes del ESP32, incluida la
  // lectura del MPU6050 en el mismo bus I2C (ver ../sensor-vibracion/).
}
