# Generated by Django 4.2 on 2024-06-25 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mergeMultipleExcel', '0004_remove_uploadedfile_timestamp'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='uploadedfile',
            name='name',
        ),
        migrations.AddField(
            model_name='uploadedfile',
            name='category',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='uploadedfile',
            name='created_by',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='uploadedfile',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='uploadedfile',
            name='expiration_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='uploadedfile',
            name='file_extension',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AddField(
            model_name='uploadedfile',
            name='file_name',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='uploadedfile',
            name='file_size',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='uploadedfile',
            name='file_type',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='uploadedfile',
            name='is_archived',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='uploadedfile',
            name='is_public',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='uploadedfile',
            name='tags',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
