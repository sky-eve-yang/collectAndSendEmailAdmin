# Generated by Django 4.1 on 2024-01-03 05:03

import collectAndSendEmailAdmin.models
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "collectAndSendEmailAdmin",
            "0003_alter_graduate_g_cert_date_alter_graduate_g_sex",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="graduate",
            name="g_cert_date",
            field=models.IntegerField(
                default=collectAndSendEmailAdmin.models.current_year,
                validators=[
                    django.core.validators.MinValueValidator(1000, message="年份必须为4位数字"),
                    django.core.validators.MaxValueValidator(9999, message="年份必须为4位数字"),
                ],
                verbose_name="毕业年份",
            ),
        ),
        migrations.AlterField(
            model_name="graduate",
            name="g_id_no",
            field=models.CharField(
                max_length=18,
                validators=[
                    django.core.validators.RegexValidator(
                        "\\d{17}[\\dX]", message="无效的身份证号"
                    )
                ],
                verbose_name="身份证号",
            ),
        ),
        migrations.AlterField(
            model_name="graduate",
            name="g_phone",
            field=models.CharField(
                max_length=15,
                validators=[
                    django.core.validators.RegexValidator("\\d{11}", message="无效的联系方式")
                ],
                verbose_name="联系方式",
            ),
        ),
    ]