from datetime import datetime
from io import BytesIO
from django.utils import timezone
import os
from django.conf import settings
from django.core.files import File
from django.http import JsonResponse
from django.shortcuts import render
from .models import Graduate
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import random
import string
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from django.http import HttpResponse
from docx import Document
from docx.shared import Inches
from urllib.parse import quote, unquote


logger = logging.getLogger('django')

'''
main:001-添加毕业生信息
'''
def graduate_add(request):
    data = request.POST  # 假设是 POST 请求，根据实际情况调整
    logger.info("graduate_add() >> request.POST: %s", data)
    # 提取数据
    g_id_no = data.get('g_id_no')
    if not g_id_no:
        return JsonResponse({'error': '身份证号是必须的'}, status=400)

    # 处理图像数据：支持 media/xxx、certificates/xxx、/media/xxx、URL 编码等格式
    relative_pic_path = (data.get('g_cert_pic') or '').strip()
    relative_pic_path = unquote(relative_pic_path)  # 解码 %E6%AF%95 等 URL 编码
    if not relative_pic_path:
        return JsonResponse({'error': '证书照片路径不能为空'}, status=400)
    # 去除可能的前缀：http(s)://host、前导斜杠
    path_part = relative_pic_path
    if '://' in path_part:
        path_part = path_part.split('://', 1)[1]  # 去掉 http(s)://
        if '/' in path_part:
            path_part = path_part.split('/', 1)[1]  # 去掉 host，保留 path
    path_part = path_part.lstrip('/').replace('\\', '/')
    # 若以 media/ 开头，转为相对 MEDIA_ROOT 的路径；否则视为已在 media 下的路径
    if path_part.startswith('media/'):
        path_part = path_part[6:].lstrip('/')  # 去掉 media/
    full_path = os.path.join(settings.MEDIA_ROOT, path_part)
    full_path = os.path.normpath(full_path)
    # 安全检查：确保解析后的路径仍在 MEDIA_ROOT 下
    media_root_real = os.path.realpath(settings.MEDIA_ROOT)
    if not os.path.realpath(full_path).startswith(media_root_real):
        logger.warning("graduate_add() >> 路径越界: full_path=%s", full_path)
        return JsonResponse({'error': '无效的证书照片路径'}, status=400)
    logger.info("graduate_add() >> relative_pic_path: %s, full_path: %s", relative_pic_path, full_path)
    if not os.path.exists(full_path):
        return JsonResponse({'error': '文件不存在', 'path': full_path}, status=400)

    # 查询或创建记录
    graduate, created = Graduate.objects.get_or_create(
        g_id_no=g_id_no,
        defaults={  # 仅用于创建新记录时
            'g_name': data.get('g_name', '').strip(),
            'g_sex': data.get('g_sex', '0').strip(),
            'g_college': data.get('g_college', '').strip(),
            'g_major': data.get('g_major', '').strip(),
            'g_year': int(data.get('g_year', 0)),
            'g_phone': data.get('g_phone', '').strip(),
            'g_mailing_address': data.get('g_mailing_address', '').strip(),
            'g_email': data.get('g_email', '').strip(),
        }
    )
    
    # 发送有新的待处理证明的通知邮件
    # 定义邮件正文中的变量
    student_name =  data.get('g_name', '').strip()
    college = data.get('g_college', '').strip()
    major = data.get('g_major', '').strip()
    graduation_year = int(data.get('g_year', 0))
    now_time = timezone.localtime(timezone.make_aware(timezone.now())).strftime("%Y年%m月%d日 %H:%M")
    toDoCount = Graduate.objects.filter(audit_status=0).count()
    
    # 格式化邮件正文
    email_body = '''
        收到一份毕业生无高校学生登记表证明办理的信息，请及时处理。
        
        申请人：兰州大学{college}{major}{year}届本科毕业生{name}
        申请时间：{datenow}
        当前总代办数量：{toDoCount}
        
        请点击查看：https://cyonline.lzu.edu.cn/wbycollect_admin/collectAndSendEmailAdmin/
        
    '''.format(name=student_name, college=college, major=major, year=graduation_year, datenow=now_time, toDoCount=toDoCount)


    

    if created:
        # 保存图像
        with open(full_path, 'rb') as file:
            django_file = File(file)
            logger.info("graduate_add() >> create django_file: %s", django_file)
            graduate.g_cert_pic.save(os.path.basename(full_path), django_file)
        
        cc_list = [s.strip() for s in getattr(settings, 'EMAIL_CC', '').split(',') if s.strip()]
        res = send_email(
            sender_email=getattr(settings, 'EMAIL_SENDER', ''),
            receiver_email=getattr(settings, 'EMAIL_RECEIVER', ''),
            smtp_server=getattr(settings, 'EMAIL_SMTP_SERVER', ''),
            smtp_port=getattr(settings, 'EMAIL_SMTP_PORT', 25),
            smtp_user=getattr(settings, 'EMAIL_SMTP_USER', ''),
            smtp_password=getattr(settings, 'EMAIL_SMTP_PASSWORD', ''),
            cc_emails=cc_list or [getattr(settings, 'EMAIL_SENDER', '')],
            subject="新的待办：毕业生无学生登记表证明事宜",
            body=email_body,
            use_starttls=getattr(settings, 'EMAIL_USE_STARTTLS', True),
            use_ssl=getattr(settings, 'EMAIL_USE_SSL', False),
        )
        if res["status"] == 200:
            return JsonResponse({'message': '毕业生信息已创建', 'graduate_id': graduate.id}, status=200)
        return JsonResponse({
            'message': '毕业生信息已创建，但通知邮件发送失败',
            'graduate_id': graduate.id,
            'email_error': res.get('msg', '未知错误'),
        }, status=200)
    else:
        # 更新记录
        graduate.g_name = data.get('g_name', graduate.g_name).strip()
        graduate.g_sex = data.get('g_sex', graduate.g_sex).strip()
        graduate.g_college = data.get('g_college', graduate.g_college).strip()
        graduate.g_major = data.get('g_major', graduate.g_major).strip()
        graduate.g_year = int(data.get('g_year', graduate.g_year))
        graduate.g_phone = data.get('g_phone', graduate.g_phone).strip()
        graduate.g_mailing_address = data.get('g_mailing_address', graduate.g_mailing_address).strip()
        graduate.g_email = data.get('g_email', graduate.g_email).strip()
        graduate.save()

        # 更新图像
        with open(full_path, 'rb') as file:
            django_file = File(file)
            logger.info("graduate_add() >> update django_file: %s", django_file)
            graduate.g_cert_pic.save(os.path.basename(full_path), django_file)


        return JsonResponse({'message': '毕业生信息已更新', 'graduate_id': graduate.id}, status=200)
    
    return JsonResponse({'error': '未知错误'}, status=500)



'''
@return {JSON}
main:002-发送邮件
'''
def handle_send_email(request):
    # 实现发送邮件逻辑
    graduate_id = request.POST.get('id')
    logging.info("handle_send_email() >> graduate_id: %s", graduate_id)
    graduate = Graduate.objects.get(id=graduate_id)



    # 定义邮件正文中的变量
    student_name = graduate.g_name
    gender = graduate.get_g_sex_display()
    id_number = graduate.g_id_no
    college = graduate.g_college
    major = graduate.g_major
    graduation_year = graduate.g_year
    image_file = graduate.g_cert_pic

    # 格式化邮件正文
    email_body = '''
        老师您好，{name}，{gender}，身份证号为{id}，系兰州大学{college}{major}{year}届本科毕业生。请核对双证是否齐全。

        学工部学生事务中心
        联系方式：8912221（城关）/ 5292130（榆中）
    '''.format(name=student_name, gender=gender, id=id_number, college=college, major=major, year=graduation_year)


    cc_list = [s.strip() for s in getattr(settings, 'EMAIL_CC', '').split(',') if s.strip()]
    res = send_email(
        sender_email=getattr(settings, 'EMAIL_SENDER', ''),
        receiver_email=getattr(settings, 'EMAIL_RECEIVER', ''),
        smtp_server=getattr(settings, 'EMAIL_SMTP_SERVER', ''),
        smtp_port=getattr(settings, 'EMAIL_SMTP_PORT', 25),
        smtp_user=getattr(settings, 'EMAIL_SMTP_USER', ''),
        smtp_password=getattr(settings, 'EMAIL_SMTP_PASSWORD', ''),
        cc_emails=cc_list or [getattr(settings, 'EMAIL_SENDER', '')],
        subject="请核对双证是否齐全",
        image_file=image_file,
        body=email_body,
        use_starttls=getattr(settings, 'EMAIL_USE_STARTTLS', True),
        use_ssl=getattr(settings, 'EMAIL_USE_SSL', False),
    )

    if res["status"] == 200:
        graduate.email_status = 1
        now_time = timezone.now()
        now_time_aware = timezone.make_aware(now_time)  # 将日期时间对象转换为带有时区信息的对象

        graduate.email_sent_time = now_time
        
        print('now_time', now_time)
        graduate.save()
        return JsonResponse(
            {   'messsage': 'Email sent successfully', 
                'code': 200, 
                'email_send_time': timezone.localtime(now_time_aware).strftime("%Y年%m月%d日 %H:%M")
            }, 
            status=200)
    else:
        graduate.email_status = 2
        graduate.save()
        return JsonResponse({
            'messsage': 'Mail sending failure',
            'code': 501,
            'email_error': res.get('msg', '未知错误'),
        }, status=501)

    return JsonResponse({"message": "测试通过"}, status=200)


'''
@description: 审核信息逻辑：通过 or 不通过
main:003-改变审核状态
'''
def change_audit_status(request):
    # 实现审核逻辑
    graduate_id = request.POST.get('id')
    graduate_audit_status = request.POST.get('audit_status')

    graduate = Graduate.objects.get(id=graduate_id)
    graduate.audit_status = graduate_audit_status
    graduate.save()

    return JsonResponse({'messsage': '审核状态已更新'}, status=200)



'''
main: 004-word 文档生成
'''
def generate_word(request):
    # 实现审核逻辑
    id = request.POST.get('id')
    
    graduate = Graduate.objects.get(id=id)

    template_path = settings.WORD_TEMPLATE_PATH
    print(template_path)

    doc = Document(template_path)
    
    # Example replacements
    now = datetime.now()
    
    replacements = {
        "#姓名": graduate.g_name,
        "#性别": graduate.get_g_sex_display(),
        "#身份证号": graduate.g_id_no,
        "#学院": graduate.g_college,
        "#专业": graduate.g_major,
        "#毕业年份": f'{graduate.g_year}届',
        "#年": f"{now.year}年",
        "#月": f"{now.month}月",
        "#日": f"{now.day}日"
    }
    print(replacements)

    fill_template(doc, replacements)

    output = BytesIO()
    doc.save(output)
    output.seek(0)

    # 构建响应对象，设置Content-Disposition头部以便浏览器下载文件
    file_name = f"{graduate.g_name}+{graduate.g_college}+无登记表证明.docx"
    encoded_file_name = quote(file_name)  # 对文件名进行URL编码


    # 创建响应对象，并设置Content-Disposition头部
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = f'attachment; filename*=UTF-8\'\'{encoded_file_name}'
    response.write(output.getvalue())

    # 返回响应
    return response
    


def index(request):
    title = "在线作业管理系统!(我返回了模板文件)"
    context = {'title': title}
    return render(request, 'index.html', context)





# 辅助 util 函数区域 - 开始
'''
001-发送邮件
'''
def send_email(sender_email, receiver_email, cc_emails, subject, body, smtp_server, smtp_port, smtp_user, smtp_password, image_file=None, use_starttls=True, use_ssl=False):
    try:
        # 创建 MIME 多部分消息对象
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['CC'] = ', '.join(cc_emails)  # 添加抄送人列表
        msg['Subject'] = subject

        # 添加邮件正文
        msg.attach(MIMEText(body, 'plain'))  # 添加邮件正文
        logger.info("邮件正文添加成功")

        # 如果提供了图片文件，则添加图片作为附件
        if image_file:
            img = MIMEImage(image_file.read())
            img.add_header('Content-Disposition', 'attachment', filename=image_file.name)
            msg.attach(img)

        # 合并收件人和抄送人列表
        to_addresses = [receiver_email] + cc_emails

        # 创建 SMTP 连接：465 端口用 SSL，587/25 用 STARTTLS
        if use_ssl:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port)
            if use_starttls:
                server.starttls()  # 启动 TLS 加密
        server.login(smtp_user, smtp_password)  # 登录 SMTP 服务器

        # 发送邮件
        server.sendmail(sender_email, to_addresses, msg.as_string())
        logger.info("邮件成功发送")
        server.quit()  # 关闭 SMTP 服务器的连接
        return {"status": 200, "msg": "success"}
    except smtplib.SMTPAuthenticationError as e:
        err_msg = "SMTP 认证失败（账号或密码错误，或需使用授权码）: {}".format(e)
        logger.exception(err_msg)
        return {"status": 535, "msg": err_msg}
    except smtplib.SMTPException as e:
        err_msg = "SMTP 错误: {}".format(e)
        logger.exception(err_msg)
        return {"status": 500, "msg": err_msg}
    except Exception as e:
        err_msg = "发送邮件异常: {}".format(e)
        logger.exception(err_msg)
        return {"status": 500, "msg": err_msg}


'''
002-文件上传
'''
@csrf_exempt  # 如果API不需要CSRF验证，可以使用这个装饰器
def file_upload_view(request):
    """
    实现文件上传API
    返回服务器资源的相对地址
    """
    if request.method == 'POST':
        # 获取上传的文件
        file = request.FILES.get('file')
        logger.info("original file: %s", file)
        file_id = request.POST.get('g_id_no')
        if not file:
            return JsonResponse({'error': '没有接收到文件'}, status=400)
        
        # 构建文件路径：仅保留扩展名，避免中文等非 ASCII 导致编码问题
        date_str = datetime.now().strftime('%Y/%m/%d')
        ext = os.path.splitext(file.name)[1] or '.jpg'
        safe_name = f'{generate_random_string(6)}{ext}'
        file_path = f'certificates/{date_str}/{file_id}/{safe_name}'

        # 保存文件到服务器的媒体文件夹中
        file_name = default_storage.save(file_path, ContentFile(file.read()))

        # 构建文件的完整URL地址
        file_url = default_storage.url(file_name)

        # 返回文件URL
        return JsonResponse({'message': 'success', 'file_url': file_url[1:]})
    
    return JsonResponse({'error': 'Only POST requests are supported'}, status=400)


'''
003-生成随机数
'''
def generate_random_string(length=4):
    """
    生成指定长度的随机字符字符串
    :param length: 字符串长度，默认为4
    :return: 随机字符字符串
    """
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    return random_string


    
'''
004-word 文档生成的辅助函数：填充word模板
'''
def fill_template(doc, replacements):
    for para in doc.paragraphs:
        runs = para.runs
        i = 0
        while i < len(runs):
            run = runs[i]
            if '#' in run.text:
                full_text = run.text
                j = i + 1
                # 合并跨越多个runs的占位符文本
                while j < len(runs) and '#' not in runs[j].text:
                    full_text += runs[j].text
                    j += 1

                # 查找并替换占位符
                for key, value in replacements.items():
                    if key in full_text:
                        full_text = full_text.replace(key, value)
                        break

                # 更新当前run的文本，并清除后面的runs
                run.text = full_text
                for k in range(i + 1, j):
                    runs[k].text = ''

                i = j - 1  # 跳过已处理的runs
            i += 1



# 辅助函数区域 - 结束