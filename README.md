# Конфигурационное управление — вариант 13

Учебный эмулятор UNIX-подобной оболочки на Python 3. Реализованы этапы 1–3.

## Сборка и запуск

Сборка не нужна: используются только модули стандартной библиотеки Python 3.

```bash
bash run.sh
bash run.sh --vfs vfs/deep_tree.json --script scripts/startup.txt
python3 -m unittest discover -s tests -v
bash scripts/test_stage1.sh
bash scripts/test_stage2.sh
bash scripts/test_stage3.sh
```

## Возможности и настройки

- REPL: интерактивный CLI, приглашение содержит имя VFS.
- `$HOME` и `${HOME}`: раскрытие переменных окружения настоящей ОС.
- `ls [аргументы]`, `cd [аргументы]`: пока **заглушки**; выводят команду и аргументы.
- `exit`: завершение работы без аргументов.
- `conf-dump`: вывод `vfs_path` и `script_path` в формате ключ=значение.
- `--vfs ПУТЬ`: путь к JSON-файлу виртуальной файловой системы.
- `--script ПУТЬ`: путь к стартовому скрипту с командами эмулятора.
- Скрипт пропускает пустые строки и комментарии `#`, а также ошибочные команды.
- JSON VFS загружается в память без распаковки или изменения исходника.
- Содержимое файлов представлено строками `content_base64`.

## Примеры использования

```text
memory> ls $HOME
Command: ls
Arguments: ['/Users/example']
memory> cd /tmp
Command: cd
Arguments: ['/tmp']
memory> conf-dump
vfs_path=
script_path=
memory> exit
```

Фактический путь вместо `/Users/example` зависит от вашей ОС.

## Файлы

- `src/emulator.py` — реализация эмулятора и проверки VFS.
- `vfs/minimal.json` — пустая VFS.
- `vfs/several_files.json` — несколько файлов, включая двоичный.
- `vfs/deep_tree.json` — вложенность более трёх уровней.
- `vfs/invalid.json` — некорректный пример для проверки ошибки.
- `scripts/startup.txt` — команды, комментарии, ошибки и проверка `conf-dump`.
- `scripts/test_stage*.sh` — тестовые вызовы на macOS/Linux.
- `tests/` — автоматические тесты на `unittest`.


