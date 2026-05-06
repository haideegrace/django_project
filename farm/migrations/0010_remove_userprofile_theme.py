# Generated manually for theme field removal

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('farm', '0009_userprofile_theme'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='theme',
        ),
    ]