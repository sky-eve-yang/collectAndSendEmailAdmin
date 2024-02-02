function changeAuditStatus(graduateId, status) {
    console.table([{graduateId, status}])
    
    
    // 发送请求，设置审核状态
    django.jQuery.ajax({
        url: '/change_audit_status/',
        type: 'POST',
        data: {
            'id': graduateId,
            'audit_status': status
        },
        success: function(response) {
            // 处理成功的响应
            console.log("success", response)

            // 两个按钮的修改
            let operation = status === 1 ? 'approve' : 'reject';
            let operationBtn = django.jQuery(`button.${operation}-button[data-id=${graduateId}]`)
            operationBtn.prop('disabled', true);
            operationBtn.addClass('btn-disabled')

            let other = status === 1 ? 'reject' : 'approve';
            let otherBtn = django.jQuery(`button.${other}-button[data-id=${graduateId}]`)
            otherBtn.prop('disabled', false);
            otherBtn.removeClass('btn-disabled')

            // remove sned_email_btn's disabled status, when passed
            if (status === 1) {
                let snedEmailBtn = django.jQuery(`button.send-email-btn[data-id=${graduateId}]`)
                snedEmailBtn.prop('disabled', false);
                snedEmailBtn.removeClass('btn-disabled')

                let generateWordBtn = django.jQuery(`button.generate-word-btn[data-id=${graduateId}]`)
                generateWordBtn.prop('disabled', false);
                generateWordBtn.removeClass('btn-disabled')
            } else {
                let snedEmailBtn = django.jQuery(`button.send-email-btn[data-id=${graduateId}]`)
                snedEmailBtn.prop('disabled', true);
                snedEmailBtn.addClass('btn-disabled')

                let generateWordBtn = django.jQuery(`button.generate-word-btn[data-id=${graduateId}]`)
                generateWordBtn.prop('disabled', true);
                generateWordBtn.addClass('btn-disabled')
            }
            

            // 更改界面显示
            let text = status === 1 ? '通过' : '不通过';
            let auditStatusDispaly = django.jQuery(`.field-audit_status_display span[data-id=${graduateId}]`)
            auditStatusDispaly.text(text)
        
        },
        error: function(error) {
            // 处理错误的响应
            console.log("error", error)

        }
    });
}

/** @return {null} */
// 毕业生id，邮件发送状态，毕业生信息（姓名、性别、学院、专业、年份、身份证号、毕业证书照片）
function sendEmail(graduateId, status) {
    console.table([{graduateId, status}])
    const /** number */ sent_email_status = Number(status)

    // 如果已经发送过，出现弹窗，进行一次发送确认
    console.log(sent_email_status)
    if (sent_email_status == 1) {
        if (!confirm('您已经发送过邮件，是否再次发送？'))
            return
    }

    
    django.jQuery.ajax({
        url: '/handle_send_email/',
        type: 'POST',
        data: {
            'id': graduateId
        },
        success: function(res) {
            // 处理成功的响应
            console.log("success", res)
            
            // 邮件发送状态变动 -> 已发送 or 发送失败
            if (res.code === 200) {
                
                let email_status = django.jQuery(`.field-email_status_display .email-status[data-id=${graduateId}]`)
                email_status.text('成功')
                email_status.parent().next().text(res.email_send_time)  // 邮件发送时间
            }
            alert('邮件发送成功')

        },
        error: function(error) {
            // 处理错误的响应
            console.log("error", error)
            let email_status = django.jQuery(`.field-email_status_display .email-status[data-id=${graduateId}]`)
            email_status.text('失败')
            alert('邮件发送失败')

        }
    });

}


/** @return {null} */
// 生成word
function generateWord(graduateId) {
    django.jQuery.ajax({
        url: '/generate_word/',
        type: 'POST',
        data: {
            'id': graduateId
        },
        success: function(res, status, xhr) {
            var contentDisposition = xhr.getResponseHeader('Content-Disposition');
            if (contentDisposition) {
                var fileName = "";
                var matches = contentDisposition.match(/filename\*=UTF-8''(.+)/);
                if (matches && matches[1]) {
                    // 解码编码后的文件名
                    fileName = decodeURIComponent(matches[1]);
                } else {
                    // 如果匹配失败，可以设置一个默认的文件名
                    fileName = "download.docx";
                }

                // 创建隐藏的下载链接
                var downloadLink = document.createElement("a");
                downloadLink.href = URL.createObjectURL(res);
                downloadLink.download = fileName;
                document.body.appendChild(downloadLink);
                downloadLink.click();
                document.body.removeChild(downloadLink);

                // alert('word生成成功');
            } else {
                alert('Content-Disposition header is missing');
            }
        },
        error: function(error) {
            console.error("error", error);
            // alert('word生成失败');
        },
        xhrFields: {
            responseType: 'blob' // 以blob方式接收文件数据
        }
    });
}

