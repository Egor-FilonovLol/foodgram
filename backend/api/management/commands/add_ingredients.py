import csv
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка ингредиентов из CSV'

    def handle(self, *args, **kwargs):
        path = Path(settings.BASE_DIR).parent / 'data' / 'ingredients.csv'
        with open(path, encoding='utf-8') as f:
            reader = csv.reader(f)
            ingredients = [
                Ingredient(name=row[0], measurement_unit=row[1])
                for row in reader
            ]
            Ingredient.objects.bulk_create(ingredients)
        self.stdout.write(self.style.SUCCESS('готово! ингредиенты загружены.'))
