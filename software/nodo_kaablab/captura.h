#ifndef CAPTURA_H
#define CAPTURA_H

#include <Arduino.h>

// Inicializa la microSD. Devuelve false si no se detecta/monta.
bool captura_iniciar_sd();

// Crea una nueva carpeta de ciclo (ciclo_00001, ciclo_00002, ...) y devuelve
// su nombre. El número de ciclo se persiste en un archivo contador en la SD
// para sobrevivir a reinicios/deep sleep.
String captura_crear_ciclo();

// Ejecuta UNA ventana de captura (audio + vibración + instantánea) y la
// escribe en la carpeta del ciclo dado, con índice 'n' (00-09):
//   /<ciclo>/meta_0n.json
//   /<ciclo>/audio_0n.pcm
//   /<ciclo>/vib_0n.raw
// Libera toda la RAM usada antes de retornar (no acumula buffers entre
// llamadas), por diseño: nunca más de 1 captura en memoria a la vez.
void captura_ejecutar_ventana(const String &carpeta_ciclo, int n);

#endif
