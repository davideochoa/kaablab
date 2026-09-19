#include "config.h"
#include "sensores.h"
#include "captura.h"
#include "servidor_http.h"

RTC_DATA_ATTR int contador_ventanas_boot = 0; // sobrevive al deep sleep (no al power-cycle)

void entrar_deep_sleep() {
  Serial.println("Entrando a deep sleep por " + String(TIEMPO_DORMIDO_US / 1000000ULL) + "s");
  Serial.flush();
  esp_sleep_enable_timer_wakeup(TIEMPO_DORMIDO_US);
  esp_deep_sleep_start();
}

void setup() {
  Serial.begin(115200);
  delay(200);
  Serial.println("\n=== KaabLab nodo despierto ===");

  if (!captura_iniciar_sd()) {
    Serial.println("FALLO CRÍTICO: sin SD, no se puede continuar este ciclo");
    entrar_deep_sleep();
    return;
  }

  if (!sensores_iniciar()) {
    Serial.println("FALLO CRÍTICO: sensor no detectado, no se puede continuar este ciclo");
    entrar_deep_sleep();
    return;
  }

  servidor_iniciar();

  String carpeta_ciclo = captura_crear_ciclo();
  Serial.println("Ciclo activo: " + carpeta_ciclo);

  unsigned long inicio_activo = millis();
  int ventana = 0;
  unsigned long ultima_captura = 0;

  // Bucle de la ventana activa: captura periódica + atención HTTP intercalada
  while (millis() - inicio_activo < TIEMPO_ACTIVO_MS) {
    servidor_atender(); // permite que el celular descargue en cualquier momento

    if (ventana < VENTANAS_POR_CICLO &&
        (millis() - ultima_captura >= INTERVALO_VENTANA_MS || ventana == 0)) {
      captura_ejecutar_ventana(carpeta_ciclo, ventana);
      ventana++;
      ultima_captura = millis();
    }

    delay(10); // cede tiempo al stack de WiFi/HTTP sin saturar el loop
  }

  Serial.println("Fin de ventana activa (" + String(ventana) + " capturas)");
  servidor_detener();
  entrar_deep_sleep();
}

void loop() {
  // No se usa: toda la lógica corre una vez por despertar, dentro de setup().
  // Al volver del deep sleep, el ESP32 reinicia y vuelve a ejecutar setup().
}
