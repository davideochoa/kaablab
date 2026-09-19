#ifndef SERVIDOR_HTTP_H
#define SERVIDOR_HTTP_H

// Inicia el WiFi en modo Access Point (abierto) y el WebServer con las
// rutas /ciclos, /ciclos/{n}, /ciclos/{n}/{archivo}, y DELETE /ciclos/{n}.
void servidor_iniciar();

// Debe llamarse repetidamente dentro de la ventana activa (handleClient()).
void servidor_atender();

// Apaga el WebServer y el WiFi antes de entrar a deep sleep.
void servidor_detener();

#endif
