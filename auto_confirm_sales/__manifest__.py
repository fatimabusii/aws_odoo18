{
    'name': 'Auto Confirm Sales Order',
    # 'version': '16.0.1.0.0',
    'version': '1.0',
    'summary': '',
    'description': '',
    'author': '',
    'company': 'ERPWEB',
    'maintainer': '',
    'license': 'OEEL-1',
    'depends': [
        'sale_account_accountant', 'sale'
    ],
    # 'data': [
    #          'views/bank_widget.xml'
    # ],
    'assets': {
        'web.assets_backend': [
            'auto_confirm_sales/static/src/xml/bank_rec_extension.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
