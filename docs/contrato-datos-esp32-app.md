# Contrato de datos ESP32 ↔ app

## Versión

Versión actual: **1.0** (campo `schema_version` de `meta_NN.json`).
Agregar campos sube la versión menor (1.1); cambiar el tipo o la unidad de un
campo existente sube la versión mayor (2.0).

## Estructura en la microSD

Cada despertar crea una carpeta `/ciclo_NNNNN`; su número es el mayor entre
`/contador_ciclo.txt` y la carpeta `ciclo_*` más alta de la SD + 1. Cada ventana `NN` (00–09) escribe tres archivos, en
este orden:

1. `audio_NN.pcm`
2. `vib_NN.raw`
3. `meta_NN.json` — se escribe al final y confirma que la ventana está completa.

## Campos de `meta_NN.json`

| Campo | Tipo | Unidad | Null | Descripción |
|---|---|---|---|---|
| `schema_version` | texto | — | no | Versión del contrato |
| `nodo_id` | texto | — | no | Identificador del nodo (`NODO_ID`) |
| `ciclo` | entero | — | no | Número de ciclo (el de la carpeta) |
| `ventana` | entero | — | no | Índice de ventana, 0–9 |
| `ts` | entero | s (Unix) | no | Marca de tiempo del DS3231 |
| `audio_file` | texto | — | no | Nombre del archivo de audio |
| `audio_fs` | entero | Hz | no | Frecuencia de muestreo del audio |
| `audio_n` | entero | muestras | no | Muestras realmente leídas del INMP441 |
| `audio_fmt` | texto | — | no | `int16_mono` |
| `audio_bytes` | entero | bytes | no | Bytes escritos en `audio_NN.pcm` |
| `audio_crc` | entero | — | no | CRC-32 de `audio_NN.pcm` |
| `vib_file` | texto | — | no | Nombre del archivo de vibración |
| `vib_ejes` | texto | — | no | `xyz_intercalado_int16_mg` |
| `vib_fs` | entero | Hz | no | Frecuencia de muestreo nominal |
| `vib_n` | entero | muestras | no | Muestras por eje |
| `vib_unidad` | texto | — | no | `mg` |
| `vib_rango_g` | entero | g | no | Rango del acelerómetro (±) |
| `vib_tardias` | entero | muestras | no | Muestras que excedieron el periodo nominal en más de 10 % |
| `vib_bytes` | entero | bytes | no | Bytes escritos en `vib_NN.raw` |
| `vib_crc` | entero | — | no | CRC-32 de `vib_NN.raw` |
| `dht_T` | número | °C | sí | Temperatura exterior (DHT22) |
| `dht_RH` | número | % HR | sí | Humedad exterior (DHT22) |
| `sht_T` | número | °C | sí | Temperatura interior (SHT31) |
| `sht_RH` | número | % HR | sí | Humedad interior (SHT31) |
| `trafico_entradas` | entero | conteos | no | Disparos del haz A desde la ventana anterior |
| `trafico_salidas` | entero | conteos | no | Disparos del haz B desde la ventana anterior |

CRC-32 estándar (igual a `java.util.zip.CRC32`), sobre el archivo completo.
Vector de prueba: CRC-32 de la cadena ASCII `"123456789"` = `0xCBF43926`.

## Formatos binarios

- Todo es `int16` little-endian, sin encabezado.
- `vib_NN.raw`: intercalado x, y, z, x, y, z, … en mg; `vib_n` muestras por eje.
- `audio_NN.pcm`: mono; dividir cada muestra entre 32768 para llevarla a [-1, 1].

## API HTTP

| Método y ruta | Códigos |
|---|---|
| `GET /ciclos` | 200: arreglo JSON de carpetas `ciclo_*` (el nombre puede traer `/` inicial) |
| `GET /ciclos/{ciclo}` | 200: arreglo JSON de `meta_*.json`; 404: ciclo no encontrado |
| `GET /ciclos/{ciclo}/{archivo}` | 200: archivo crudo; 404: archivo no encontrado |
| `DELETE /ciclos/{ciclo}` | 200: `{"ok":true}`; 404: ciclo no encontrado; 409: `{"error":"ciclo activo"}` (quedan ventanas por capturar) |

## Reglas de la app

- `null` = dato faltante.
- Una ventana sin `meta_NN.json` se ignora.
- Verificar tamaño (`audio_bytes`, `vib_bytes`) y CRC de cada binario.
- Ordenar los ciclos por número, no por orden de listado.
- Clave única: `nodo_id` + `ciclo` + `ventana` + `ts`.
- Descarga incompleta: no borrar el ciclo. Descarga completa con una ventana
  inválida: guardarla marcada como incompleta y permitir borrar.
- Descargar un ciclo a la vez; borrar solo tras guardar y verificar.
- Timeouts generosos: el servidor queda bloqueado ~3 s en cada captura.

## Ejemplo de `meta_NN.json`

Los valores de CRC son ilustrativos.

```json
{
  "schema_version": "1.0",
  "nodo_id": "nodo1",
  "ciclo": 42,
  "ventana": 3,
  "ts": 1793548800,
  "audio_file": "audio_03.pcm",
  "audio_fs": 16000,
  "audio_n": 16000,
  "audio_fmt": "int16_mono",
  "audio_bytes": 32000,
  "audio_crc": 2774216395,
  "vib_file": "vib_03.raw",
  "vib_ejes": "xyz_intercalado_int16_mg",
  "vib_fs": 1500,
  "vib_n": 3000,
  "vib_unidad": "mg",
  "vib_rango_g": 8,
  "vib_tardias": 0,
  "vib_bytes": 18000,
  "vib_crc": 1028473921,
  "dht_T": 31.4,
  "dht_RH": 78.2,
  "sht_T": 30.1,
  "sht_RH": null,
  "trafico_entradas": 12,
  "trafico_salidas": 9
}
```
