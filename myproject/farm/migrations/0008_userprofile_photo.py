from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('farm', '0007_alter_activitylog_activity_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='profile_photos/'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='photo_url',
            field=models.URLField(blank=True),
        ),
    ]
