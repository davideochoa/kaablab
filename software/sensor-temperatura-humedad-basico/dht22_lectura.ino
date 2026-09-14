/*
 * DHT22 (AM2302) — Lectura de temperatura y humedad relativa externa
 * KaabLab — sensor externo secundario, arquitectura sensorial heterogénea
 * (ver README.md, secciones 0-2, para la justificación completa)
 *
 * Librería: "DHT sensor library" (Adafruit)
 *   Instalar vía Arduino Library Manager: "DHT sensor library" de Adafruit
 *   (requiere también la dependencia "Adafruit Unified Sensor")
 *
 * Protocolo: digital propietario de un solo hilo, NO I2C, NO 1-Wire
 * estándar Dallas. El timing de los pulsos lo maneja la librería
 * internamente (bit-banging con micros()); no requiere configuración
 * manual de temporización en este sketch.
 *
 * Pin mapping confirmado del proyecto:
 *   DATA = GPIO4
 *
 * Limitación de tasa: el DHT22 solo admite ~0.5 Hz (una lectura cada
 * 2 segundos como mínimo). Leer más rápido devuelve NAN o datos
 * repetidos del ciclo de conversión anterior del sensor.
 */

#include <DHT.h>

#define DHTPIN 4
#define DHTTYPE DHT22

DHT dht(DHTPIN, DHTTYPE);

const unsigned long READ_INTERVAL_MS = 2500; // margen sobre el minimo de 2000 ms del sensor

void setup() {
  Serial.begin(115200);
  while (!Serial) { /* espera puerto serie en placas con USB nativo */ }

  dht.begin();

  Serial.println("timestamp_ms,temperatura_C,humedad_relativa_pct");
}

void loop() {
  static unsigned long lastReadMs = 0;
  unsigned long nowMs = millis();

  // Temporizacion no bloqueante: se respeta el limite de tasa del sensor
  // sin usar delay() largo, dejando espacio para otras tareas del ESP32.
  if (nowMs - lastReadMs >= READ_INTERVAL_MS) {
    lastReadMs = nowMs;

    // readHumidity()/readTemperature() bloquean brevemente (~250 ms)
    // mientras la libreria hace bit-banging del protocolo del sensor.
    float humedad = dht.readHumidity();
    float temperatura = dht.readTemperature(); // Celsius por defecto

    if (isnan(humedad) || isnan(temperatura)) {
      Serial.println("ERROR: lectura fallida del DHT22 (timing de protocolo o cableado)");
      return;
    }

    // Nota (README.md sección 0): esta %HR ya viene calibrada de fabrica
    // a partir de la capacitancia interna del sensor, no es una medicion
    // directa de humedad.
    Serial.print(nowMs);
    Serial.print(',');
    Serial.print(temperatura, 1);
    Serial.print(',');
    Serial.println(humedad, 1);

    // La conversion a humedad absoluta (formula de Magnus) y el
    // contraste con el SHT31 interno se calculan en la capa de fusion
    // del proyecto (thesis/capitulo-3-metodologia/capitulo-3.md,
    // secciones 3.2.1 y 3.4.5), no en este sketch de adquisicion.
  }

  // Espacio para otras tareas no bloqueantes del ESP32 (WiFi, otros sensores).
}
