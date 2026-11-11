#include "captura.h"
#include "config.h"
#include "sensores.h"

#include <SD.h>
#include <SPI.h>
#include <ArduinoJson.h>
#include <esp_rom_crc.h>

static SPIClass spi_sd(VSPI);
static uint32_t ciclo_num = 0;
static long ciclo_activo = -1;

long captura_ciclo_activo() { return ciclo_activo; }

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

// Mayor número de carpeta /ciclo_* existente + 1 (1 si no hay ninguna).
static uint32_t siguiente_ciclo_en_sd() {
  uint32_t mayor = 0;
  File root = SD.open("/");
  for (File e = root.openNextFile(); e; e = root.openNextFile()) {
    String nombre = String(e.name());
    int p = nombre.indexOf("ciclo_");
    if (e.isDirectory() && p >= 0) mayor = max(mayor, (uint32_t)nombre.substring(p + 6).toInt());
  }
  return mayor + 1;
}

String captura_crear_ciclo() {
  uint32_t n = max(leer_o_iniciar_contador_ciclo(), siguiente_ciclo_en_sd());
  char nombre[32];
  snprintf(nombre, sizeof(nombre), "/ciclo_%05lu", (unsigned long)n);
  SD.mkdir(nombre);
  guardar_contador_ciclo(n + 1);
  ciclo_num = n;
  ciclo_activo = n;
  return String(nombre);
}

void captura_ejecutar_ventana(const String &carpeta_ciclo, int n) {
  char sufijo[3];
  snprintf(sufijo, sizeof(sufijo), "%02d", n);

  // --- 1. Captura cruda (usa buffers en el stack/heap, liberados al salir) ---
  static int16_t buf_audio[N_MUESTRAS_AUDIO];               // ~32 KB
  static int16_t buf_vib[N_MUESTRAS_VIB * 3];                // 3000 muestras x 3 ejes x 2 bytes ≈ 18 KB
  // 'static' evita fragmentar el heap; se sobrescribe en cada llamada.

  size_t audio_leidos = sensores_capturar_audio(buf_audio);
  uint32_t vib_tardias = sensores_capturar_vibracion(buf_vib);
  LecturaInstantanea lect = sensores_leer_instantanea();

  // --- 2. Escritura binaria directa; bytes y CRC-32 sobre lo realmente escrito ---
  size_t audio_bytes = 0, vib_bytes = 0;
  String ruta_audio = carpeta_ciclo + "/audio_" + sufijo + ".pcm";
  File f_audio = SD.open(ruta_audio, FILE_WRITE);
  if (f_audio) {
    audio_bytes = f_audio.write((uint8_t *)buf_audio, audio_leidos);
    f_audio.close();
  } else {
    Serial.println("ERROR escribiendo " + ruta_audio);
  }

  String ruta_vib = carpeta_ciclo + "/vib_" + sufijo + ".raw";
  File f_vib = SD.open(ruta_vib, FILE_WRITE);
  if (f_vib) {
    vib_bytes = f_vib.write((uint8_t *)buf_vib, N_MUESTRAS_VIB * 3 * sizeof(int16_t));
    f_vib.close();
  } else {
    Serial.println("ERROR escribiendo " + ruta_vib);
  }

  // --- 3. Metadatos en JSON, al final: su presencia confirma la ventana ---
  StaticJsonDocument<1536> doc;
  doc["schema_version"] = "1.0";
  doc["nodo_id"] = NODO_ID;
  doc["ciclo"] = ciclo_num;
  doc["ventana"] = n;
  doc["ts"] = lect.timestamp_unix;
  doc["audio_file"] = "audio_" + String(sufijo) + ".pcm";
  doc["audio_fs"] = FS_AUDIO;
  doc["audio_n"] = audio_leidos / sizeof(int16_t);
  doc["audio_fmt"] = "int16_mono";
  doc["audio_bytes"] = audio_bytes;
  doc["audio_crc"] = esp_rom_crc32_le(0, (const uint8_t *)buf_audio, audio_bytes);
  doc["vib_file"] = "vib_" + String(sufijo) + ".raw";
  doc["vib_ejes"] = "xyz_intercalado_int16_mg";
  doc["vib_fs"] = FS_VIB;
  doc["vib_n"] = N_MUESTRAS_VIB;
  doc["vib_unidad"] = "mg";
  doc["vib_rango_g"] = VIB_RANGO_G;
  doc["vib_tardias"] = vib_tardias;
  doc["vib_bytes"] = vib_bytes;
  doc["vib_crc"] = esp_rom_crc32_le(0, (const uint8_t *)buf_vib, vib_bytes);
  const char *claves[] = {"dht_T", "dht_RH", "sht_T", "sht_RH"};
  const float valores[] = {lect.dht_T, lect.dht_RH, lect.sht_T, lect.sht_RH};
  for (int i = 0; i < 4; i++) {
    if (isnan(valores[i])) doc[claves[i]] = nullptr;
    else doc[claves[i]] = valores[i];
  }
  doc["trafico_entradas"] = lect.trafico_entradas;
  doc["trafico_salidas"] = lect.trafico_salidas;

  String ruta_meta = carpeta_ciclo + "/meta_" + sufijo + ".json";
  File f_meta = doc.overflowed() ? File() : SD.open(ruta_meta, FILE_WRITE);
  if (f_meta) {
    serializeJson(doc, f_meta);
    f_meta.close();
  } else {
    Serial.println("ERROR escribiendo " + ruta_meta);
  }
  if (n >= VENTANAS_POR_CICLO - 1) ciclo_activo = -1;

  Serial.println("Ventana " + String(sufijo) + " guardada en " + carpeta_ciclo);
}
