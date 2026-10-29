/*
 * Contador IR doble haz (módulos TCRT5000 reflectivos) — lectura digital con
 * debounce por software y lógica de secuencia para conteo direccional
 * KaabLab — conteo de tráfico de forrajeo en la piquera
 *
 * ADVERTENCIA — DISEÑO NO CERRADO (ver README.md secciones 1, 2 y 5):
 *   - Rango de operación declarado por el fabricante del TCRT5000
 *     (hoja Vishay): 0.2-15 mm, pico a 2.5 mm — pendiente de validar en
 *     banco con el tubo real de la piquera (~15 mm).
 *   - Estos módulos no tienen mitigación integrada contra falsos
 *     positivos por luz solar IR directa.
 *   Este código asume que la validación de banco de la sección 5 del
 *   README ya se realizó. NO instalar en campo sin esa validación.
 *
 * Pin mapping confirmado del proyecto (ver README.md sección 1.1 sobre
 * la geometría — 4 módulos reflectivos, 2 por haz, separación entre
 * haces >= ~10 mm por el ancho de la cabeza óptica del TCRT5000, a validar). Cada
 * módulo detecta por reflexión (sin haz directo) y entrega una señal OUT
 * utilizable: por eso se leen las 4 señales, aunque el conteo final usa
 * solo las dos "principales":
 *   Haz A - receptor principal   = GPIO26
 *   Haz A - receptor secundario  = GPIO25 (mismo par, diagnóstico/banco)
 *   Haz B - receptor principal   = GPIO27
 *   Haz B - receptor secundario  = GPIO33 (mismo par, diagnóstico/banco)
 *
 * GPIO25 quedó libre al descartarse el diseño discreto anterior (que lo
 * usaba como drive de LED IR) en favor de los módulos TCRT5000 (ver
 * CLAUDE.md, "Decisiones de diseño confirmadas"). GPIO33 no tiene uso
 * previo en el mapeo de pines del proyecto.
 *
 * Lógica de conteo direccional (basada en las señales PRINCIPALES):
 *   Haz A interrumpido antes que Haz B  -> entrada (A->B)
 *   Haz B interrumpido antes que Haz A  -> salida  (B->A)
 * Las señales SECUNDARIAS solo se registran por separado para comparar
 * en banco contra la principal del mismo par (README.md sección 3 y 5).
 */

const int HAZ_A_PIN = 26;
const int HAZ_A_SEC_PIN = 25;
const int HAZ_B_PIN = 27;
const int HAZ_B_SEC_PIN = 33;

// Polaridad de salida de los módulos TCRT5000: en la configuración
// típica, OUT permanece en HIGH con el haz intacto y baja a LOW cuando el
// haz se interrumpe (objeto detectado).
// CONFIRMAR EN BANCO (README.md sección 5): el ajuste del potenciómetro
// de sensibilidad y la revisión exacta del módulo pueden invertir esta
// lógica — verificar con multímetro/osciloscopio antes de confiar en esta
// constante.
const int BEAM_BROKEN_LEVEL = LOW;

// --- Debounce por software (no bloqueante) ---
// Evita conteos falsos por rebote/ruido de la salida del comparador
// LM393 integrado en cada módulo.
const unsigned long DEBOUNCE_MS = 15;

struct DebouncedPin {
  uint8_t pin;
  int stableState;
  int lastRawState;
  unsigned long lastChangeMs;
};

DebouncedPin beamA = { HAZ_A_PIN, HIGH, HIGH, 0 };
DebouncedPin beamASec = { HAZ_A_SEC_PIN, HIGH, HIGH, 0 };
DebouncedPin beamB = { HAZ_B_PIN, HIGH, HIGH, 0 };
DebouncedPin beamBSec = { HAZ_B_SEC_PIN, HIGH, HIGH, 0 };

// Actualiza el estado debounced de un pin. Devuelve true solo en el ciclo
// en que el estado ESTABLE cambia (no en cada lectura ruidosa).
bool updateDebounced(DebouncedPin &dp) {
  int raw = digitalRead(dp.pin);
  unsigned long now = millis();

  if (raw != dp.lastRawState) {
    dp.lastRawState = raw;
    dp.lastChangeMs = now;
  }

  if ((now - dp.lastChangeMs) >= DEBOUNCE_MS && dp.stableState != dp.lastRawState) {
    dp.stableState = dp.lastRawState;
    return true; // cambio de estado estable confirmado
  }
  return false;
}

// --- Lógica de secuencia para conteo direccional ---
enum SequenceState { SEQ_IDLE, SEQ_A_FIRST, SEQ_B_FIRST };
SequenceState seqState = SEQ_IDLE;
unsigned long seqStartMs = 0;

// Tiempo máximo permitido entre la interrupción del primer haz y del
// segundo para considerarlos parte del mismo cruce. Punto de partida
// conservador; ajustar según la velocidad real de tránsito medida en
// banco (README.md sección 5).
const unsigned long SEQUENCE_TIMEOUT_MS = 300;

// Simplificación conocida: si el mismo haz se interrumpe dos veces
// seguidas antes de que el otro se active, este código NO reinicia la
// ventana de tiempo — simplemente espera el timeout. Válido para una
// primera versión; revisar si el bench de la sección 5 muestra cruces
// perdidos por esta causa (p. ej. varias abejas muy seguidas).
unsigned long countEntradas = 0;
unsigned long countSalidas = 0;

void setup() {
  Serial.begin(115200);
  while (!Serial) { /* espera puerto serie en placas con USB nativo */ }

  pinMode(HAZ_A_PIN, INPUT);
  pinMode(HAZ_A_SEC_PIN, INPUT);
  pinMode(HAZ_B_PIN, INPUT);
  pinMode(HAZ_B_SEC_PIN, INPUT);

  Serial.println("Contador IR doble haz iniciado (4 modulos TCRT5000, 2 por haz)");
  Serial.println("timestamp_ms,evento,total_entradas,total_salidas");
}

void loop() {
  bool changedA = updateDebounced(beamA);
  bool changedASec = updateDebounced(beamASec);
  bool changedB = updateDebounced(beamB);
  bool changedBSec = updateDebounced(beamBSec);

  // Registro diagnostico de las senales SECUNDARIAS: no participan en la
  // logica de conteo, solo se imprimen para comparar en banco contra la
  // principal del mismo par (README.md secciones 3 y 5).
  unsigned long diagNow = millis();
  if (changedASec) {
    Serial.print(diagNow);
    Serial.print(",diag_haz_A_secundario=");
    Serial.println(beamASec.stableState == BEAM_BROKEN_LEVEL ? "interrumpido" : "intacto");
  }
  if (changedBSec) {
    Serial.print(diagNow);
    Serial.print(",diag_haz_B_secundario=");
    Serial.println(beamBSec.stableState == BEAM_BROKEN_LEVEL ? "interrumpido" : "intacto");
  }

  bool aBroken = (beamA.stableState == BEAM_BROKEN_LEVEL);
  bool bBroken = (beamB.stableState == BEAM_BROKEN_LEVEL);

  unsigned long now = millis();

  // Timeout: si pasó demasiado tiempo esperando el segundo haz, se
  // descarta la secuencia (no se cuenta como entrada ni salida) y se
  // vuelve a esperar el próximo cruce desde cero.
  if (seqState != SEQ_IDLE && (now - seqStartMs) > SEQUENCE_TIMEOUT_MS) {
    seqState = SEQ_IDLE;
  }

  // Flanco de interrupción del Haz A
  if (changedA && aBroken) {
    if (seqState == SEQ_IDLE) {
      seqState = SEQ_A_FIRST;
      seqStartMs = now;
    } else if (seqState == SEQ_B_FIRST) {
      // B se interrumpió primero, ahora A -> salida (B->A)
      countSalidas++;
      Serial.print(now);
      Serial.print(",salida,");
      Serial.print(countEntradas);
      Serial.print(",");
      Serial.println(countSalidas);
      seqState = SEQ_IDLE;
    }
  }

  // Flanco de interrupción del Haz B
  if (changedB && bBroken) {
    if (seqState == SEQ_IDLE) {
      seqState = SEQ_B_FIRST;
      seqStartMs = now;
    } else if (seqState == SEQ_A_FIRST) {
      // A se interrumpió primero, ahora B -> entrada (A->B)
      countEntradas++;
      Serial.print(now);
      Serial.print(",entrada,");
      Serial.print(countEntradas);
      Serial.print(",");
      Serial.println(countSalidas);
      seqState = SEQ_IDLE;
    }
  }

  // Espacio para otras tareas no bloqueantes del ESP32 (WiFi, otros
  // sensores, agregación de conteos en intervalos de 5 minutos — ver
  // thesis/capitulo-2-materiales-y-metodos/capitulo-2.md, sección 2.9.2).
  // No agregar delay() aquí: reduciría la resolución temporal del
  // debounce y podría perder cruces rápidos.
}
