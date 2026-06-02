---
name: project-skill-structure
description: Структура папок для скиллов в репозитории AquaDeliveryAI — как создавать новые скиллы
metadata: 
  node_type: memory
  type: project
  originSessionId: c1af04cf-15d0-42f4-bef3-ce8a3e4a9799
---

Каждый скилл живёт в собственной папке внутри `<отдел>/skills/`:

```
<отдел>/
└── skills/
    └── <skill-name>/           ← папка называется по slug скилла
        ├── <skill-name>.md     ← файл скилла
        ├── references/         ← только если есть референсные файлы
        │   └── ...
        └── scripts/            ← только если есть скрипты
            └── ...
```

**Правило:** если скилл передан без references и scripts — создаётся только папка `<skill-name>/` с одним `.md` файлом внутри. Папки `references/` и `scripts/` не создавать.

**Примеры:**
- `1c-implementation/skills/aqua-implementation/aqua-implementation.md` + `references/` + `scripts/`
- `support/skills/instruction-sync/instruction-sync.md` (только файл, без подпапок)

**Why:** пользователь поправил структуру вручную — каждый скилл изолирован в своей папке для чистоты и масштабируемости.
**How to apply:** при создании любого нового скилла — сначала mkdir `<skill-name>/`, затем класть файл внутрь. Добавлять `references/` и `scripts/` только если они явно переданы.
