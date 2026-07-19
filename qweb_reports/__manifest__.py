{
    'name': 'Qweb Reports',
    'version': '1.0',
    'category': 'Tools',
    'summary': 'Qweb Reports',
    'description': """This module is for pdf reports""",
    'author': 'Muhammad wazir',
    # 'website': 'https://www.muhammad.com',
    'depends': ['base','stock','sale'],
    'data': [
        'reports/pdf_report.xml',
        'reports/sale_pdf_report.xml',
    ]
}