import json
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):
    def handle(self, *args, **options):
        groups_data = []

        for group in Group.objects.all():
            groups_data.append({
                'model': 'auth.group',
                'pk': group.pk,
                'fields': {
                    'name': group.name,
                    'permissions': list(group.permissions.values_list('id', flat=True))
                }
            })

        with open('groups_fixture.json', 'w', encoding='utf-8') as file:
            json.dump(groups_data, file, ensure_ascii=False, indent=2)

        self.stdout.write(self.style.SUCCESS('Группы экспортированы в groups_fixture.json'))

#  values_list возвращает не объекты, а указанные поля
#  flat=True превращает кортеж в список
