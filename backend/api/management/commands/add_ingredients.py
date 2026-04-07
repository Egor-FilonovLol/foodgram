import os
import csv
from django.core.management.base import BaseCommand
from django.conf import settings
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка ингредиентов из CSV'

    def handle(self, *args, **kwargs):
        path = os.path.join(settings.BASE_DIR, 'data', 'ingredients.csv')
        ingredients_to_create = []
        with open(path, encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) < 2:
                    continue
                ingredients_to_create.append(
                    Ingredient(name=row[0].strip(),
                               measurement_unit=row[1].strip())
                )
        Ingredient.objects.bulk_create(ingredients_to_create,
                                       ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS('готово! ингредиенты загружены.'))
