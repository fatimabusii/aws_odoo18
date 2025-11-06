{
    'name': 'Auto Rental',
    # 'version': '16.0.1.0.0',
    'version': '1.0',
    'summary': '',
    'description': '',
    'author': '',
    'company': 'ERPWEB',
    'maintainer': '',
    'license': 'OEEL-1',
    'depends': [
        'sale_subscription','sale','sale_renting'
    ],
    'data': [
             'views/res_config_settings_view.xml',
             'views/sale_order_line.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

