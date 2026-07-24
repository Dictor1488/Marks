# Marks

Окремий мод прогресу відміток на стволі для World of Tanks. Він не містить логіку мода **Masters** і може встановлюватися разом із ним.

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

Після першого запуску мод створює файл:

```text
<World of Tanks>/mods/configs/marks/marks.json
```

Основні параметри: `garageBadgeStyle` і `battleBadgeStyle`.

## Перевірка

```bash
python tools/debug_check.py
```

Перевірка контролює структуру репозиторію, JSON/XML, Python-файли, AS3-класи, compile targets і відповідність SWF/linkage.

## Збірка через GitHub Actions

Відкрий **Actions → Build and Release Marks → Run workflow**, вкажи версію мода та папку версії гри. Workflow:

1. перевіряє репозиторій;
2. компілює `MarksPanelHangar.swf` і `MarksPanelBattle.swf`;
3. компілює Python-код через Python 2.7;
4. створює `.wotmod` і ZIP-архів;
5. додає артефакти до GitHub Release.

## Локальна збірка

Встанови залежності та створи локальний конфіг:

```bash
python -m pip install -r requirements-build.txt
copy build.example.json build.json
```

У `build.json` вкажи шлях до Python 2.7 та актуальну версію папки гри. Перед пакуванням у `as3/bin` мають бути готові `MarksPanelHangar.swf` і `MarksPanelBattle.swf`.

```bash
python build.py --distribute
```

`build.json`, SWF, архіви й інші результати збірки не зберігаються в Git.
