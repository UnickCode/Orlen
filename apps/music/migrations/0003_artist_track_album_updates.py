import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0002_album'),
    ]

    operations = [
        # ── Update existing Album table ────────────────────────────────────
        migrations.AddField(
            model_name='album',
            name='spotify_url',
            field=models.URLField(blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='album',
            name='added_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='album',
            name='cover',
            field=models.URLField(blank=True),
        ),
        migrations.AlterField(
            model_name='album',
            name='release_date',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='album',
            name='type',
            field=models.CharField(blank=True, max_length=50),
        ),

        # ── Create Artist ──────────────────────────────────────────────────
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('spotify_id', models.CharField(max_length=255, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('image', models.URLField(blank=True)),
                ('genres', models.CharField(blank=True, max_length=500)),
                ('followers', models.IntegerField(default=0)),
                ('popularity', models.IntegerField(default=0)),
                ('spotify_url', models.URLField(blank=True)),
                ('added_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),

        # ── Create Track ───────────────────────────────────────────────────
        migrations.CreateModel(
            name='Track',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('spotify_id', models.CharField(max_length=255, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('artist', models.CharField(max_length=255)),
                ('album', models.CharField(blank=True, max_length=255)),
                ('cover', models.URLField(blank=True)),
                ('duration_ms', models.IntegerField(default=0)),
                ('preview_url', models.URLField(blank=True, null=True)),
                ('popularity', models.IntegerField(default=0)),
                ('spotify_url', models.URLField(blank=True)),
                ('release_date', models.CharField(blank=True, max_length=50)),
                ('added_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-added_at'],
            },
        ),
    ]
