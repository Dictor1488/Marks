# Marks

Окремий мод міток на стволі для World of Tanks. Може встановлюватися одночасно з модом **Masters**.

## Стилі

Гаражні:

- `classic`;
- `compact`;
- `polaroid`.

Бойові:

- `classic`;
- `compact`;
- `polaroid`;
- `neer`;
- `minimal`.

## Конфігурація

```text
<World of Tanks>/mods/configs/marks/marks.json
```

Ключі: `garageBadgeStyle` і `battleBadgeStyle`.

## Збірка

```bash
python build.py --distribute
```

## Налагодження

```bash
python tools/debug_check.py
```
