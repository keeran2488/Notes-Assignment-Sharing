# Generated by Django 2.2 on 2019-12-21 05:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0003_auto_20191221_1035'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='question_image',
            field=models.ImageField(null=True, upload_to='media/', verbose_name='Image'),
        ),
        migrations.DeleteModel(
            name='QuestionImage',
        ),
    ]