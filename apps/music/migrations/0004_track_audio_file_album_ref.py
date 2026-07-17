from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0003_artist_track_album_updates'),
    ]

    operations = [
        migrations.AddField(
            model_name='track',
            name='album_ref',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='tracks',
                to='music.album',
            ),
        ),
        migrations.AddField(
            model_name='track',
            name='audio_file',
            field=models.FileField(blank=True, null=True, upload_to='tracks/'),
        ),
    ]
