#include "servidor_http.h"
#include "config.h"

#include <WiFi.h>
#include <WebServer.h>
#include <SD.h>
#include <ArduinoJson.h>

static WebServer servidor(HTTP_PORT);

// --- GET /ciclos : lista las carpetas ciclo_* pendientes en la SD ---
static void handle_listar_ciclos() {
  StaticJsonDocument<1024> doc;
  JsonArray arr = doc.to<JsonArray>();

  File root = SD.open("/");
  File entrada = root.openNextFile();
  while (entrada) {
    if (entrada.isDirectory()) {
      String nombre = String(entrada.name());
      if (nombre.startsWith("/ciclo_") || nombre.startsWith("ciclo_")) {
        arr.add(nombre);
      }
    }
    entrada = root.openNextFile();
  }

  String salida;
  serializeJson(doc, salida);
  servidor.send(200, "application/json", salida);
}

// --- GET /ciclos/{nombre} : lista los archivos meta_*.json de ese ciclo ---
static void handle_listar_capturas() {
  String uri = servidor.uri();  // /ciclos/ciclo_00001
  String carpeta = uri.substring(String("/ciclos/").length());
  String ruta = "/" + carpeta;

  if (!SD.exists(ruta)) {
    servidor.send(404, "application/json", "{\"error\":\"ciclo no encontrado\"}");
    return;
  }

  StaticJsonDocument<1024> doc;
  JsonArray arr = doc.to<JsonArray>();
  File dir = SD.open(ruta);
  File entrada = dir.openNextFile();
  while (entrada) {
    String nombre = String(entrada.name());
    if (nombre.indexOf("meta_") >= 0) {
      arr.add(nombre);
    }
    entrada = dir.openNextFile();
  }

  String salida;
  serializeJson(doc, salida);
  servidor.send(200, "application/json", salida);
}

// --- GET /ciclos/{nombre}/{archivo} : sirve el archivo crudo (json/pcm/raw) ---
static void handle_obtener_archivo() {
  String uri = servidor.uri();
  String ruta = uri.substring(String("/ciclos/").length() - 1); // conserva "/"

  if (!SD.exists(ruta)) {
    servidor.send(404, "text/plain", "archivo no encontrado");
    return;
  }

  File f = SD.open(ruta, FILE_READ);
  String tipo = "application/octet-stream";
  if (ruta.endsWith(".json")) tipo = "application/json";

  servidor.streamFile(f, tipo);
  f.close();
}

// --- DELETE /ciclos/{nombre} : borra la carpeta completa tras confirmación ---
static void borrar_carpeta_recursiva(const String &ruta) {
  File dir = SD.open(ruta);
  File entrada = dir.openNextFile();
  while (entrada) {
    String ruta_hijo = ruta + "/" + String(entrada.name());
    if (entrada.isDirectory()) {
      borrar_carpeta_recursiva(ruta_hijo);
      SD.rmdir(ruta_hijo);
    } else {
      SD.remove(ruta_hijo);
    }
    entrada = dir.openNextFile();
  }
  SD.rmdir(ruta);
}

static void handle_borrar_ciclo() {
  String uri = servidor.uri();
  String carpeta = uri.substring(String("/ciclos/").length());
  String ruta = "/" + carpeta;

  if (!SD.exists(ruta)) {
    servidor.send(404, "application/json", "{\"error\":\"ciclo no encontrado\"}");
    return;
  }

  borrar_carpeta_recursiva(ruta);
  servidor.send(200, "application/json", "{\"ok\":true}");
}

void servidor_iniciar() {
  if (WIFI_OPEN) {
    WiFi.softAP(WIFI_SSID);
  } else {
    // Reservado para fase con contraseña: WiFi.softAP(WIFI_SSID, "password");
    WiFi.softAP(WIFI_SSID);
  }

  servidor.on("/ciclos", HTTP_GET, handle_listar_ciclos);
  // Rutas con parámetro en el path: WebServer no soporta patrones nativos,
  // se resuelve inspeccionando servidor.uri() dentro del handler con onNotFound.
  servidor.onNotFound([]() {
    String uri = servidor.uri();
    HTTPMethod metodo = servidor.method();

    if (uri.startsWith("/ciclos/")) {
      // Determinar si es /ciclos/{n} o /ciclos/{n}/{archivo}
      String resto = uri.substring(String("/ciclos/").length());
      int slash = resto.indexOf('/');

      if (metodo == HTTP_DELETE && slash < 0) {
        handle_borrar_ciclo();
      } else if (slash < 0) {
        handle_listar_capturas();
      } else {
        handle_obtener_archivo();
      }
      return;
    }
    servidor.send(404, "text/plain", "ruta no encontrada");
  });

  servidor.begin();
  Serial.println("Servidor HTTP iniciado. AP: " + String(WIFI_SSID));
}

void servidor_atender() {
  servidor.handleClient();
}

void servidor_detener() {
  servidor.close();
  WiFi.softAPdisconnect(true);
}
