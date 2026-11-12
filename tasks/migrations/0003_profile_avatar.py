import django.core.validators
import tasks.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('tasks', '0002_profile')]
    operations = [
        migrations.AlterField(
            model_name='profile', name='display_name',
            field=models.CharField(blank=True, default='', max_length=50, validators=[django.core.validators.MinLengthValidator(2)]),
        ),
        migrations.AddField(
            model_name='profile', name='avatar',
            field=models.FileField(blank=True, upload_to=tasks.models.avatar_path),
        ),
    ]
