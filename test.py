from docx import Document
from datetime import datetime

# Load the user's Word document template
template_path = 'docx/template.docx'
doc = Document(template_path)

# Function to replace asterisks (*) in the document with given text
def fill_template(doc, replacements):
    for para in doc.paragraphs:
        runs = para.runs
        for i, run in enumerate(runs):
            if run.text == '#':
                count = i  # 记录启动子位置
                tmp = '#'  # tmp写入启动子
                while tmp not in list(replacements.keys()):  # tmp继续写入启动子后的run，直到tmp和dic中的键匹配
                    count += 1
                    tmp += runs[count].text
                    runs[count].clear()
                runs[i].text = runs[i].text.replace(runs[i].text, replacements[tmp])

now = datetime.now()

# Example replacements
replacements = {
    "#name": "张三",
    "#sex": "男",
    "#id": "1234567890",
    "#college": "计算机科学与技术学院",
    "#major": "软件工程专业",
    "#gradute_year": '2024届',
    "#year": f"{now.year}年",
    "#month": f"{now.month}月",
    "#day": f"{now.day}日"
}


# Fill the template with the replacements
fill_template(doc, replacements)

# Save the filled document
filled_doc_path = 'docx/filled_document.docx'
doc.save(filled_doc_path)

