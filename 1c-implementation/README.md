# 1C Implementation

Отдел внедрения 1С УНФ Aqua Delivery. Скиллы автоматизируют подготовку документов и планов по итогам аудиторских встреч с партнёрами.

## Скиллы

| Скилл | Описание |
|-------|----------|
| [aqua-implementation](skills/aqua-implementation/) | Генерирует Excel-файл с планом внедрения Aqua Delivery на основе транскрибации встречи с партнёром. Заполняет 31 бизнес-процесс и формирует план из 5 этапов (новый партнёр) или 13 шагов по 1С (действующий). |
| [voronka-vnedreniya-tracker](skills/voronka-vnedreniya-tracker/) | Берёт `data.json` из aqua-implementation и создаёт 40+ задач в Yandex Tracker на доске «Задачи по внедрению 1С». |

## Файловая структура

```
1c-implementation/
├── README.md
├── CLAUDE.md
├── MEMORY.md
└── skills/
    ├── aqua-implementation/
    │   ├── aqua-implementation.md
    │   ├── README.md
    │   ├── references/
    │   │   ├── audit_questions.md
    │   │   ├── processes.json
    │   │   ├── plan_template.json
    │   │   └── plan_template_existing.json
    │   └── scripts/
    │       └── build_excel.py
    ├── voronka-vnedreniya-tracker/
    │   ├── voronka-vnedreniya-tracker.md
    │   └── README.md
    └── initial-setup/
        ├── orchestrator/orchestrator.md
        ├── setup-internet-shop/setup-internet-shop.md
        ├── disable-1c-background-jobs/disable-1c-background-jobs.md
        ├── 1c-history-settings/1c-history-settings.md
        ├── setup-kafka-exchange/setup-kafka-exchange.md
        ├── setup-1c-user/setup-1c-user.md
        └── agent-builder/agent-builder.md
```
