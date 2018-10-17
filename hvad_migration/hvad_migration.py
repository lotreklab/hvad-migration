from django.conf import settings
from django.db import migrations, connection


class KeepTranslationsMixin:

    _saved_data_from_plain = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.operations.insert(0, migrations.RunPython(
            self._saveDataFromPlain, self._restoreDataToPlain
        ))
        self.operations.append(migrations.RunPython(
            self._restoreDataToTrans, self._getDataFromTrans
        ))

    def _saveDataFromPlain(self, apps, schemaeditor):
        for key, value in self.keep_translations.items():
            Model = apps.get_model(*key.split('.'))
            table = Model._meta.db_table
            if not 'id' in value:
                value = ('id',) + value
            with connection.cursor() as cursor:
                cursor.execute("SELECT {0} FROM {1}".format(','.join(value), table))
                rows = cursor.fetchall()
                self._saved_data_from_plain[key] = []
                for row in rows:
                    self._saved_data_from_plain[key].append(dict(zip(value, row)))

    def _getDataFromTrans(self, apps, schemaeditor):
        for key, value in self.keep_translations.items():
            key_trans = key + 'Translation'
            ModelTanslatable = apps.get_model(*key_trans.split('.'))

            translations = ModelTanslatable.objects.filter(
                language_code=getattr(settings, 'LANGUAGE_CODE', 'en')
            )

            self._saved_data_from_plain[key] = []
            for translation in translations:
                data_for_plain = {'id' : translation.master.pk}
                for attribute in value:
                    if attribute != 'id':
                        data_for_plain[attribute] = getattr(translation, attribute)
                self._saved_data_from_plain[key].append(data_for_plain)

    def _restoreDataToTrans(self, apps, schemaeditor):
        for key, rows in self._saved_data_from_plain.items():
            Model = apps.get_model(*key.split('.'))
            key = key + 'Translation'
            ModelTanslatable = apps.get_model(*key.split('.'))
            for row in rows:
                obj_to_trans = Model.objects.get(pk=row['id'])
                obj, _ = ModelTanslatable.objects.get_or_create(
                    master=obj_to_trans, language_code=getattr(settings, 'LANGUAGE_CODE', 'en')
                )
                for attribute, attribute_value in row.items():
                    if attribute != 'id':
                        setattr(obj, attribute, attribute_value)
                obj.save()

    def _restoreDataToPlain(self, apps, schemaeditor):
        for key, rows in self._saved_data_from_plain.items():
            Model = apps.get_model(*key.split('.'))
            for row in rows:
                obj = Model.objects.get(pk=row['id'])
                for attribute, attribute_value in row.items():
                    if attribute != 'id':
                        setattr(obj, attribute, attribute_value)
                obj.save()
