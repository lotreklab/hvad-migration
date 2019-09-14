# Hvad migration

Experimental way to migrate your data safetly using Hvad 🇳🇱

Part of this repository is now in our django-hvad personal fork.


## Keep data during migration

If you need to transform your simple website in a multilanguage one and you don't want to lose your data, you need to use `KeepTranslationsMixin` in your migration file. Suppose you have a simple model `StaticContent`

    class StaticContent(models.Model):
        identifier = models.CharField(max_length=200, verbose_name = 'Identificatore')
        title = models.CharField(max_length=200, blank=True, null=True, default='')
        subtitle = models.CharField(max_length=200, blank=True, null=True, default='')
        content = models.TextField(blank=True, default='')

Now trasform `title`, `subtitle` and `content` in TranslatedFields

    class StaticContent(TranslatableModel):
        identifier = models.CharField(max_length=200, verbose_name = 'Identificatore')
        translations = TranslatedFields(
            title = models.CharField(max_length=200, blank=True, null=True, default=''),
            subtitle = models.CharField(max_length=200, blank=True, null=True, default=''),
            content = models.TextField(blank=True, default='')
        )

Make the new migration and then, before migrate, extend it with `KeepTranslationsMixin`

    from hvad_migration import KeepTranslationsMixin


    class Migration(KeepTranslationsMixin, migrations.Migration):

        keep_translations = {
            'page_content.StaticContent' : ('title', 'subtitle', 'content')
        }

        dependencies = [...]

        operations = [...]

Remember to add `keep_translations` property, where you specify the model and the realtive fields you want to save during migrations.
