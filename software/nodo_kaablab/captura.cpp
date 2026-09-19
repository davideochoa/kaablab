#include "captura.h"
#include "config.h"
#include "sensores.h"

#include <SD.h>
#include <SPI.h>
#include <ArduinoJson.h>

static SPIClass spi_sd(VSPI);

bool captura_iniciar_sd() {
  spi_sd.begin(PIN_SD_SCK, PIN_SD_MISO, PIN_SD_MOSI, PIN_SD_CS);
  if (!SD.begin(PIN_SD_CS, spi_sd)) {
    Serial.println("ERROR: microSD no detectada");
    return false;
  }
  return true;
}

static uint32_t leer_o_iniciar_contador_ciclo() {
  uint32_t contador = 1;
  if (SD.exists("/contador_ciclo.txt")) {
    File f = SD.open("/contador_ciclo.txt", FILE_READ);
    if (f) {
      contador = f.parseInt();
      f.close();
    }
  }
  return contador;
}

static void guardar_contador_ciclo(uint32_t contador) {
  File f = SD.open("/contador_ciclo.txt", FILE_WRITE);
  if (f) {
    f.print(contador);
    f.close();
  }
}

String captura_crear_ciclo() {
  uint32_t n = leer_o_iniciar_contador_ciclo();
  char nombre[32];
  snprintf(nombre, sizeof(nombre), "/ciclo_%05lu", (unsigned long)n);
  SD.mkdir(nombre);
  guardar_contador_ciclo(n + 1);
  return String(nombre);
}

void captura_ejecutar_ventana(const String &carpeta_ciclo, int n) {
  char sufijo[3];
  snprintf(sufijo, sizeof(sufijo), "%02d", n);

  // --- 1. Captura cruda (usa buffers en el stack/heap, liberados al salir) ---
  static int16_t buf_audio[N_MUESTRAS_AUDIO];               // ~32 KB
  static int16_t buf_vib[N_MUESTRAS_VIB * 3];                // 3000 muestras x 3 ejes x 2 bytes ≈ 18 KB
  // 'static' aquí evita fragmentar el heap entre ventanas sucesivas;
  // el contenido se sobrescribe en cada llamada, nunca se acumula.

  sensores_capturar_audio(buf_audio);
  sensores_capturar_vibracion(buf_vib);
  LecturaInstantanea lect = sensores_leer_instantanea();

  // --- 2. Escritura binaria directa (sin pasar por JSON) ---
  String ruta_audio = carpeta_ciclo + "/audio_" + sufijo + ".pcm";
  File f_audio = SD.open(ruta_audio, FILE_WRITE);
  if (f_audio) {
    f_audio.write((uint8_t *)buf_audio, N_MUESTRAS_AUDIO * sizeof(int16_t));
    f_audio.close();
  } else {
    Serial.println("ERROR escribiendo " + ruta_audio);
  }

  String ruta_vib = carpeta_ciclo + "/vib_" + sufijo + ".raw";
  File f_vib = SD.open(ruta_vib, FILE_WRITE);
  if (f_vib) {
    f_vib.write((uint8_t *)buf_vib, N_MUESTRAS_VIB * 3 * sizeof(int16_t));
    f_vib.close();
  } else {
    Serial.println("ERROR escribiendo " + ruta_vib);
  }

  // --- 3. Metadatos en JSON (pequeño, sin arrays de muestras) ---
  StaticJsonDocument<512> doc;
  doc["ts"] = lect.timestamp_unix;
  doc["audio_file"] = "audio_" + String(sufijo) + ".pcm";
  doc["vib_file"] = "vib_" + String(sufijo) + ".raw";
  doc["vib_ejes"] = "xyz_intercalado_int16_mg"; // formato explícito, para el parser Kotlin
  doc["dht_T"] = lect.dht_T;
  doc["dht_RH"] = lect.dht_RH;
  doc["sht_T"] = lect.sht_T;
  doc["sht_RH"] = lect.sht_RH;
  doc["trafico_entradas"] = lect.trafico_entradas;
  doc["trafico_salidas"] = lect.trafico_salidas;

  String ruta_meta = carpeta_ciclo + "/meta_" + sufijo + ".json";
  File f_meta = SD.open(ruta_meta, FILE_WRITE);
  if (f_meta) {
    serializeJson(doc, f_meta);
    f_meta.close();
  } else {
    Serial.println("ERROR escribiendo " + ruta_meta);
  }

  Serial.println("Ventana " + String(sufijo) + " guardada en " + carpeta_ciclo);
}
