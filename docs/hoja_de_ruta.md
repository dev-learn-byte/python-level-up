# Hoja de ruta

Decisiones de diseño aprobadas que todavía no están implementadas. Las reglas
vigentes están en `reglas.md`; nada de este documento las modifica.

## Mapa general

```
Sagas 1-5 --> JUEGOS DE CELL --> Sagas 6-7 --> TORNEO DEL PODER
```

| Saga | Niveles | Temas | Jefe | Transformación |
|---|---|---|---|---|
| 1. Entrenamiento de Goku | 1-3 | Variables y tipos, operadores e `input`, cadenas | Maestro Roshi | Discípulo Tortuga |
| 2. Torneo de Artes Marciales | 4-6 | Condicionales, bucles, funciones | Piccolo | Guerrero Z |
| 3. Saga Saiyajin | 7-9 | Listas y tuplas, diccionarios y sets, comprensiones | Vegeta | Kaioken |
| 4. Saga de Freezer | 10-12 | Módulos, excepciones, archivos y JSON | Freezer | Super Saiyajin |
| 5. Saga de Cell | 13-15 | Clases, herencia y polimorfismo, métodos especiales | Cell | Super Saiyajin 2 |
| 6. Saga de Majin Buu | 16-18 | Generadores, decoradores, proyecto CLI | Kid Buu | Super Saiyajin 3 |
| 7. Dragon Ball Super | 19-23 | Testing y tipado, SQLite, APIs, `async`, proyecto final | Zamasu | Ultra Instinto Señal |

El jefe de la Saga 7 es Zamasu. Jiren queda reservado para el Torneo del Poder.

## Saga 1: decisiones de contenido

- Solo se usan conceptos ya enseñados: sin `if`, sin `return` y sin
  `try/except`. Las misiones trabajan con variables.
- Los ejercicios usan entradas válidas. La validación de entradas
  incorrectas (edad cero, texto donde va un número) se enseña más adelante.
- El programa de inscripción del Maestro Roshi evoluciona: el jefe de la
  Saga 2 lo amplía con `if` y el de la Saga 4 con `try/except`.
- Misiones de Dragon Ball: 10 XP y 10 puntos. Misiones especiales de otros
  animes: 15 XP y 15 puntos.

## Evaluación mixta (Etapa 3)

- Práctica y misiones: se evalúan en el navegador.
- Evaluaciones oficiales, jefes, exámenes de salto y torneos: el servidor
  ejecuta las pruebas en un entorno aislado, sin red, sin acceso a archivos
  y con límite de tiempo y memoria. El diseño del aislamiento se revisa
  antes de implementarlo.

## Torneos

Contenido posterior a las sagas. No se implementa hasta que el sistema
principal esté completo.

### Reglas comunes

- Opcionales: no bloquean el avance por las sagas.
- No se desbloquean con XP ni puntos: exigen sagas aprobadas y una
  clasificatoria de un solo intento por edición, con 80 % para pasar.
- Inscripción desde la aplicación, sin costo en puntos.
- Rondas contra rivales simulados, cada uno con una puntuación que superar.
- Puntuación de torneo propia, separada de los puntos canjeables.
- Resistencia: una barra para todo el torneo, en lugar de vidas por nivel.
- Fracasar no quita XP ni puntos ni activa penalizaciones. Para la edición
  siguiente hay que cumplir un reentrenamiento.
- Cada edición trae desafíos distintos.
- Todo se evalúa en el servidor.
- Recompensas: títulos, medallas e historial de clasificaciones. Los XP de
  cada ronda se pagan una sola vez.

### Juegos de Cell (intermedio-avanzado)

Requisitos: sagas 1 a 5 aprobadas con sus jefes vencidos, sin niveles
pendientes en ellas, y la clasificatoria. No incluye SQL.

| Ronda | Rival | Tema |
|---|---|---|
| 1 | Mr. Satán | Lógica y fundamentos |
| 2 | Los Cell Jr. | Depuración: siete programas rotos |
| 3 | Cell Perfecto | Algoritmos y estructuras de datos |
| 4 | Cell Perfecto, segunda fase | Funciones y programación orientada a objetos |
| 5 | Cell Súper Perfecto | Un proyecto pequeño completo |

Recompensa: título "Campeón de los Juegos de Cell" y una medalla por edición.

### Torneo del Poder (experto)

Requisitos: las siete sagas completas, todos los jefes vencidos, ningún
nivel pendiente, haber ganado los Juegos de Cell y la clasificatoria.

La resistencia son los 10 guerreros del Universo 7: cada ronda fallida
elimina a uno. Si caen todos, hay que esperar a la edición siguiente.

| Ronda | Rival | Tema |
|---|---|---|
| 1 | Universo 9 | Pruebas automatizadas |
| 2 | Universo 6 (Hit) | Optimización y rendimiento |
| 3 | Universo 2 | APIs |
| 4 | Universo 3 | Concurrencia y asincronía |
| 5 | Universo 4 | Bases de datos y SQL |
| 6 | Toppo | Seguridad |
| 7 | Jiren | Arquitectura: una aplicación completa |

Recompensa: transformación "Ultra Instinto Dominado", el reconocimiento
máximo del juego. Incluye tabla de clasificación entre universos y logros.

### Impacto técnico previsto

- Un módulo nuevo en `nucleo/` para torneos, sin cambiar las reglas actuales.
- Carpeta `contenido/torneos/` con una subcarpeta por edición; las
  soluciones van en el repositorio privado.
- Dos ediciones iniciales por torneo.
