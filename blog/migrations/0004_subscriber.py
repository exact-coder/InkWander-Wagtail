# Generated by Django 5.0.9 on 2024-09-25 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_blogtagindexpage_author_blogpage_authors_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscriber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(help_text='Email Address', max_length=100)),
                ('name', models.CharField(help_text='Full Name', max_length=100)),
            ],
        ),
    ]
