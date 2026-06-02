# 1C Implementation

Отдел внедрения 1С УНФ Aqua Delivery. Скиллы автоматизируют подготовку документов и планов по итогам аудиторских встреч с партнёрами.

## Скиллы

| Скилл | Описание |
|-------|----------|
| [aqua-implementation](skills/aqua-implementation/) | Генерирует Excel-файл с планом внедрения Aqua Delivery на основе транскрибации встречи с партнёром. Заполняет 31 бизнес-процесс и формирует план из 5 этапов (новый партнёр) или 13 шагов по 1С (действующий). |

## Файловая структура

```
1c-implementation/
├── README.md
└── skills/
    └── aqua-implementation/
        ├── aqua-implementation.md
        ├── README.md
        ├── references/
        │   ├── audit_questions.md
        │   ├── processes.json
        │   ├── plan_template.json
        │   └── plan_template_existing.json
        └── scripts/
            └── build_excel.py
```
