# Generated manually for theme field addition

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('farm', '0008_userprofile_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='theme',
            field=models.CharField(choices=[('light', 'Light'), ('dark', 'Dark')], default='light', max_length=10),
        ),
    ]