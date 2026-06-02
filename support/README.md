# Support

Отдел технической поддержки партнёров. Скиллы помогают анализировать качество коммуникации, синхронизировать базу знаний и выявлять потерянные договорённости.

## Скиллы

| Скилл | Описание |
|-------|----------|
| [instruction-sync](skills/instruction-sync/) | Синхронизирует инструкции из документов пользователя с GitHub-репозиторием `victor11555/aqua-delivery-instructions`. Проверяет актуальность, диагностирует проблемы и создаёт Pull Request с обновлённой инструкцией. |
| [partner-dialog-analyzer](skills/partner-dialog-analyzer/) | Анализирует диалоги с партнёрами (чаты и транскрибации звонков) по TOV и задачам. Оценивает качество коммуникации поддержки и выявляет потерянные договорённости. Генерирует Word-отчёт. |
| [yandex-tracker-issue-creator](skills/yandex-tracker-issue-creator/) | Создаёт задачи в Yandex Tracker в диалоговом режиме. Уточняет заголовок, описание, очередь и исполнителя, показывает превью и создаёт задачу через API после подтверждения. |

## Файловая структура

```
support/
├── README.md
└── skills/
    ├── instruction-sync/
    │   ├── instruction-sync.md
    │   └── README.md
    ├── partner-dialog-analyzer/
    │   ├── partner-dialog-analyzer.md
    │   └── README.md
    └── yandex-tracker-issue-creator/
        ├── yandex-tracker-issue-creator.md
        └── README.md
```
