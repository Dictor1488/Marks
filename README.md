# Marks

Окремий мод міток на стволі для World of Tanks. Може встановлюватися одночасно з модом **Master**.

## Стилі

Гаражні варіанти:

- `classic`;
- `compact`;
- `polaroid`.

Бойові варіанти:

- `classic`;
- `compact`;
- `polaroid`;
- `neer`;
- `minimal`.

## Конфігурація

Після першого запуску конфіг розташований тут:

```text
<World of Tanks>/mods/configs/marks/marks.json
```

Ключі: `garageBadgeStyle` і `battleBadgeStyle`.

## Збірка

Запусти GitHub Actions → **Build and Release .wotmod** або локально:

```bash
python build.py --distribute
```

## Налагодження

```bash
python tools/debug_check.py
```
