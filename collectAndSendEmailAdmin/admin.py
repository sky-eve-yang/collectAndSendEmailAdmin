from django.contrib import admin
from django import forms
from django.utils.html import format_html
from .models import Graduate
from django.contrib import messages

class GraduateForm(forms.ModelForm):
    class Meta:
        model = Graduate
        fields = '__all__'

class GraduateAdmin(admin.ModelAdmin):
    list_per_page = 5  # 每页显示10个对象


    list_display = ('id', 'g_name', 'g_sex', 'g_college', 'g_major', 
                    'g_year', 'g_id_no', 'g_phone', 'g_mailing_address', 'g_email',
                    'cert_preview', 'audit_status_display', 'email_status_display', 
                    'email_sent_time', 'created_at',
                    'approve_button', 'reject_button', 'send_email_button', 'generate_word_button')
    
    
    list_filter = ('audit_status', 'g_college', 'g_year')
    search_fields = ('g_name', 'g_college', 'g_major', 'g_id_no', 'g_phone')
    
    
    # 毕业证书图片字段
    def cert_preview(self, obj):
        if obj.g_cert_pic:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img class="cert-preview" src="{}" width="150" style="border: 1px solid #ddd; padding: 5px;" />'
                '</a>',
                obj.g_cert_pic.url, obj.g_cert_pic.url
            )
        return "无图片"
    cert_preview.short_description = '毕业证书'

    # 审核相关
    def audit_status_display(self, obj):
        audit_status_class = "audit-status"
        
        return format_html(
            '<span class="{}" data-id="{}">{}</span>',
            audit_status_class, obj.id, obj.get_audit_status_display()
        )
    audit_status_display.short_description = "审核状态"


    # 邮件相关
    def email_status_display(self, obj):
        email_status_class = "email-status"
        return format_html(
            '<span class="{}" data-id="{}">{}</span>',
            email_status_class, obj.id, obj.get_email_status_display()
        )
    email_status_display.short_description = "邮件发送状态"

    def generate_word_button(self, obj):
        generate_word_btn_class = 'generate-word-btn'
        
        if obj.audit_status != 1:
            generate_word_btn_class += ' btn-disabled'
            
        return format_html(
            '<button type="button" class="{}" data-id="{}" onclick="generateWord(\'{}\');">生成证明文件</button>',
            generate_word_btn_class, obj.id, obj.id
        )
    generate_word_button.short_description = "证明文件"

    def send_email_button(self, obj):
        send_email_btn_class = 'send-email-btn'
        

        if obj.audit_status != 1:
            send_email_btn_class += ' btn-disabled'

        if obj.email_status == 1:
            return format_html(
                '<button type="button"  class="{} sent-email" data-id="{}" onclick="sendEmail(\'{}\', \'{}\');">邮件已发送</button>',
                send_email_btn_class, obj.id, obj.id, obj.email_status
            )
        else:
            return format_html(
                '<button type="button"  class="{}" data-id="{}" onclick="sendEmail(\'{}\', \'{}\');">发送邮件（至档案馆）</button>',
                send_email_btn_class, obj.id, obj.id, obj.email_status
            )
    send_email_button.short_description = "邮件发送操作"
    






    def approve_button(self, obj):
        # 返回一个"审核通过"按钮的HTML代码
        btn_class = "approve-button"
        
        if obj.audit_status == 1:
            btn_class += " btn-disabled"
            
        return format_html(
            '<button type="button"  class="{}" data-id="{}" onclick="changeAuditStatus(\'{}\', 1);">通过</button>',
            btn_class, obj.id, obj.id
        )
    approve_button.short_description = '审核通过操作'

    def reject_button(self, obj):
        # 返回一个"审核不通过"按钮的HTML代码
        btn_class = "reject-button"
        
        if obj.audit_status == 2:
            btn_class += " btn-disabled"
            
        return format_html(
            '<button type="button" class="{}" data-id="{}" onclick="changeAuditStatus(\'{}\', 2);">不通过</button>',
            btn_class, obj.id, obj.id
        ) 
    reject_button.short_description = '审核不通过操作'
    reject_button.confirm = '你是否执意要点击这个按钮？'

    
    

    class Media:
        js = ('js/audit_graduate_v5.js','js/image_preview.js',)
        css = {
            'all': ('css/audit_graduate_v4.css',)
        }

admin.site.register(Graduate, GraduateAdmin)
