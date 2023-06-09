import csv
import os

import django.db.utils
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandParser
from django.db.models.base import ModelBase

from ...models import Location

DATA_TABLES = {
    Location: 'uszips.csv',
}


def read_csv(name_file: str) -> list:
    """Считываем csv файл и добавляем к каждому элементу поле id."""
    path = os.path.join('static/data', name_file)
    with open(path, encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file,
                                fieldnames=('zip_index', 'lat', 'lng',
                                            'city', 'state_id', 'state'),
                                restkey='other',
                                delimiter=',',)
        result = []
        for i, elem in enumerate(reader):
            elem['id'] = i + 1
            elem.pop('state_id')
            elem.pop('other')
            result.append(elem)
        return result


def load_data(model: ModelBase, name_file: str) -> None:
    """Загрузка данных по модели."""
    table = read_csv(name_file)
    model.objects.bulk_create(model(**row) for row in table)


def delete_data() -> None:
    """Удаление всех таблиц из базы данных."""
    for model in DATA_TABLES:
        model.objects.all().delete()


class Command(BaseCommand):
    help = 'Импорт данных из csv в базу данных'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            '--load',
            action='store_true',
            help='Импорт данных из csv в базу данных'
        )
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Удаление всех данных из базы данных'
        )

    def handle(self, *args: tuple, **options: dict) -> None:
        try:
            if options['load']:
                for model, name_file in DATA_TABLES.items():
                    load_data(model, name_file)
                    print(f'Загрузка "{name_file}" выполнена')

                self.stdout.write(
                    self.style.SUCCESS('Данные загружены в базу данных.')
                )

            elif options['delete']:
                delete_data()
                self.stdout.write(
                    self.style.SUCCESS('База данных удалена.')
                )
            else:
                self.stdout.write(
                    self.style.SQL_KEYWORD(
                        'Команда используется с ключом, '
                        'все ключи: python manage.py import_data --help'
                    )
                )

        except django.db.utils.IntegrityError as error:
            self.stdout.write(
                self.style.ERROR(
                    f'База данных не пуста. '
                    f'Совпадение уникальных полей. {error}'
                )
            )
        except ObjectDoesNotExist:
            self.stdout.write(
                self.style.NOTICE('Нет данных из связанных таблиц')
            )
        except Exception as error:
            self.stdout.write(
                self.style.ERROR(f'Ошибка загрузки данных: {error}')
            )
