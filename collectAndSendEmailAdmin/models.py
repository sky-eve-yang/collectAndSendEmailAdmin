from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
import datetime

# 预设常量 - 开始
SEX_TYPE = (
    (0, "男"),
    (1, "女"),
)
AUDIT_STATUS_CHOICES = (
    (0, '未审核'),
    (1, '通过'),
    (2, '不通过'),
)
EMAIL_STATUS_CHOICES = (
    (0, '未发送'),
    (1, '成功'),
    (2, '失败'),
)

# 预设常量 - 结束


def current_year():
    return datetime.datetime.now().year

class Graduate(models.Model):
    """
        模型类中未设置 id 字段，因为 Django 的 ORM 会自动创建一个
        自增类型的 int 类型的 id 字段作为主键
        
        数据类型	        说明
        AutoField	        默认自增的 int 类型，通常不用指定，Django 会自动创建属性名为 id 的主键属性
        CharField	        字符串类型，必选参数 max_length 表示最大字符个数
        IntegerField	    整数类型
        DecimalField	    十进制浮点数，可选参数 max_digits 表示总位数，decimal_places 表示小数位数
        FloatField	        浮点数
        DateField	        日期类型，可选参数 auto_now 自动设置该字段为当前时间， auto_now_add 当对象第一次被创建时自动设置当前时间。 auto_now_add 和 auto_now 互斥，选择其一即可
        TimeField	        时间类型，参数同上
        DateTimeField	    日期时间类型，参数同上
        FileField	        上传文件字段
        ImageField	        继承于 FileField ，对上传的内容进行校验，确保是合法的图片
        BooleanField	    布尔字段，值为 True 或 False
        NullBooleanField	支持 Null、True、False 三种值
    """
    

    g_cert_pic = models.ImageField(upload_to="certificates/", blank=False, verbose_name="毕业证书照片")
    g_name = models.CharField(max_length=256, blank=False, verbose_name="姓名")
    g_sex = models.SmallIntegerField(choices=SEX_TYPE, verbose_name="性别", default=0)
    g_college = models.CharField(max_length=256, blank=False, verbose_name="毕业学院")
    g_major = models.CharField(max_length=256, blank=False, verbose_name="专业名称")
    g_year = models.IntegerField(
        blank=False, 
        verbose_name="毕业年份", 
        validators=[
            MinValueValidator(1000, message="年份必须为4位数字"), 
            MaxValueValidator(9999, message="年份必须为4位数字")
        ],
        default=current_year
    )
    g_id_no = models.CharField(
        max_length=18, 
        blank=False, 
        verbose_name="身份证号",
        unique=True,
        validators=[RegexValidator(r'\d{17}[\dX]', message="无效的身份证号")]
    )
    g_phone = models.CharField(
        max_length=15, 
        blank=False, 
        verbose_name="联系方式",
        validators=[RegexValidator(r'\d{11}', message="无效的联系方式")]
    )
    g_mailing_address = models.TextField(max_length=1024, verbose_name="邮寄地址")
    audit_status = models.IntegerField(choices=AUDIT_STATUS_CHOICES, default=0, verbose_name="审核状态")
    email_status = models.IntegerField(choices=EMAIL_STATUS_CHOICES, default=0, verbose_name="邮件发送状态")
    email_sent_time = models.DateTimeField(null=True, blank=True, verbose_name="邮件发送时间")


    class Meta:
        verbose_name_plural = verbose_name = "毕业生"
    
    # 便于查看映射类示例的打印信息
    def __str__(self):
        return self.g_name
    
    def __repr__(self):
        return 
        
        