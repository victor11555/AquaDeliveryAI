# Support

Отдел технической поддержки партнёров. Скиллы помогают анализировать качество коммуникации, синхронизировать базу знаний и выявлять потерянные договорённости.

## Скиллы

| Скилл | Описание |
|-------|----------|
| [instruction-sync](skills/instruction-sync/) | Синхронизирует инструкции из документов пользователя с GitHub-репозиторием `victor11555/aqua-delivery-instructions`. Проверяет актуальность, диагностирует проблемы и создаёт Pull Request с обновлённой инструкцией. |
| [partner-dialog-analyzer](skills/partner-dialog-analyzer/) | Анализирует диалоги с партнёрами (чаты и транскрибации звонков) по TOV и задачам. Оценивает качество коммуникации поддержки и выявляет потерянные договорённости. Генерирует Word-отчёт. |
| [partner-reply](skills/partner-reply/) | Превращает черновые заметки оператора в готовое сообщение партнёру по стандартам TOV Aqua Delivery. |
| [partner-appeals-analyzer](skills/partner-appeals-analyzer/) | Читает архив обращений партнёров (Excel + Markdown), группирует по категориям, строит топ-20 самых частых тем, рекомендует приоритеты для написания инструкций. |
| [yandex-tracker-issue-creator](../shared/skills/yandex-tracker-issue-creator/) | Создаёт задачи в Yandex Tracker в диалоговом режиме. Общий скилл из `shared/`. |

## Файловая структура

```
support/
├── README.md
├── CLAUDE.md
├── MEMORY.md
└── skills/
    ├── instruction-sync/
    │   ├── instruction-sync.md
    │   └── README.md
    ├── partner-dialog-analyzer/
    │   ├── partner-dialog-analyzer.md
    │   └── README.md
    ├── partner-reply/
    │   ├── partner-reply.md
    │   └── README.md
    └── partner-appeals-analyzer/
        ├── partner-appeals-analyzer.md
        └── README.md
```
