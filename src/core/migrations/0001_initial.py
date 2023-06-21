# Generated by Django 4.1.7 on 2023-06-21 14:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UpcomingCall',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('call_name', models.CharField(help_text='Name of the upcoming call', max_length=255, verbose_name='Call Name')),
                ('timestamp', models.BigIntegerField()),
                ('meeting_link', models.CharField(default='', help_text='Meeting Link (Zoom)', max_length=500)),
                ('recours_weekly', models.BooleanField(default=False, help_text='Determine if the upcoming call should be recurring for every week')),
                ('participants', models.ManyToManyField(help_text='Users attending the upcoming call', related_name='+', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(help_text='User that created the upcoming call', on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AdditionalUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timezone', models.TextField(blank=True, null=True)),
                ('coach', models.ManyToManyField(blank=True, related_name='students', to='core.additionaluser')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]