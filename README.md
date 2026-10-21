# 🔧 TFM Proyecto 2 · Asistente RAG multiformato para un taller

Asistente que responde preguntas sobre la documentación de un taller de reparación de vehículos en España (normativa de talleres, ITV, llamadas a revisión, estaciones ITV y preguntas frecuentes del taller) a partir de documentos en **5 formatos distintos**.

---

## 📑 Tabla de contenidos

1. [Objetivo](#-objetivo)
2. [Documentos](#-documentos)
3. [Estructura del repositorio](#️-estructura-del-repositorio)
4. [Esquema del flujo](#-esquema-del-flujo)
5. [Preguntas del enunciado](#-preguntas-del-enunciado)
6. [Asistente básico](#-asistente-básico)
7. [Versión mejorada](#-versión-mejorada)
8. [Evaluación](#-evaluación)
9. [Cómo ejecutar](#️-cómo-ejecutar)

---

## 🎯 Objetivo

Un taller recibe a diario las mismas dudas de sus clientes: garantías, presupuestos, plazos de la ITV, llamadas a revisión o qué estación ITV le queda más cerca. El objetivo es un asistente que responda a esas preguntas buscando la información en la documentación del taller y en la normativa oficial, y que indique de qué documento la ha sacado.

---

## 📚 Documentos

Todos los documentos están en data/raw/.

| Archivo | Formato | Fuente | Tipo |
|---|---|---|---|
| rd_1457_1986_talleres_reparacion.pdf | PDF | [BOE · Real Decreto 1457/1986](https://www.boe.es/buscar/act.php?id=BOE-A-1986-18896) | Real |
| dudas_anexo_ix_reglamento_vehiculos.pdf | PDF | [Ministerio de Industria y Turismo · ITV](https://industria.gob.es/Calidad-Industrial/vehiculos/Paginas/inspeccion-tecnica-vehiculos.aspx) | Real |
| rd_920_2017_inspeccion_tecnica_vehiculos.html | HTML | [BOE · Real Decreto 920/2017](https://www.boe.es/buscar/act.php?id=BOE-A-2017-12841) | Real |
| dgt_llamadas_a_revision.html | HTML | [DGT · Llamadas a revisión](https://www.dgt.es/muevete-con-seguridad/vehiculos-seguros/llamadas-a-revision/) | Real |
| rd_920_2017_inspeccion_tecnica_vehiculos.xml | XML | [BOE · Real Decreto 920/2017 (XML)](https://www.boe.es/diario_boe/xml.php?id=BOE-A-2017-12841) | Real |
| registro_estaciones_itv_2026.csv | CSV | [Ministerio de Industria y Turismo · Registro de estaciones ITV 2026](https://industria.gob.es/Calidad-Industrial/vehiculos/Paginas/inspeccion-tecnica-vehiculos.aspx) (convertido de XLSX a CSV) | Real |
| faq_taller.md | Markdown | Elaboración propia | Inventado |

---

## 🗂️ Estructura del repositorio

```
tfm-p2/
├── data/
│   ├── raw/          # documentos originales
│   └── processed/    # fragmentos y datos intermedios (no se suben)
├── models/
├── notebooks/
├── outputs/
├── requirements.txt
└── README.md
```

---

## 🔀 Esquema del flujo

Pendiente.

---

## ❓ Preguntas del enunciado

Pendiente.

---

## 🤖 Asistente básico

Pendiente.

---

## 🚀 Versión mejorada

Pendiente.

---

## 📊 Evaluación

Pendiente.

---

## ▶️ Cómo ejecutar

Pendiente.
