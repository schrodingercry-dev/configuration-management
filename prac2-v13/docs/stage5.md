# Этап 5. Визуализация

Финальная версия всегда печатает описание графа на языке D2. Если передан
флаг `--ascii-tree`, после D2 дополнительно выводится дерево. Общие зависимости
помечаются как `[already shown]`, циклические рёбра — как `[cycle]`.

## Три примера

Команды используют `examples/test_repository.txt` и различаются исходным
пакетом:

```bash
python3 -m src.main --package A --repository examples/test_repository.txt --test-mode --version 1.0 --ascii-tree --max-depth 5
python3 -m src.main --package B --repository examples/test_repository.txt --test-mode --version 1.0 --ascii-tree --max-depth 5
python3 -m src.main --package C --repository examples/test_repository.txt --test-mode --version 1.0 --ascii-tree --max-depth 5
```

Для `A` демонстрируются ветвление, общая зависимость и цикл. Для `B` получается
линейная цепочка `B -> D -> E`. Для `C` обход начинается с другой части того же
графа и возвращается к `C` через `A`.

## Сравнение со штатными инструментами

`apt-cache dotty <пакет>` формирует граф в формате Graphviz DOT, тогда как
программа формирует D2 и дополнительное ASCII-дерево. Набор рёбер может
отличаться: учебная программа выбирает первую альтернативу и учитывает только
`Pre-Depends` и `Depends`; штатные инструменты apt знают о виртуальных пакетах,
рекомендациях, архитектуре, конфликтах и состоянии установленной системы.
