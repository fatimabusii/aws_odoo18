{
    'name': 'Blue Spaces Custom Notifications',
    # 'version': '16.0.1.0.0',
    'version': '1.0',
    'summary': '',
    'description': 'Add the Sales Manager Non Payment Notification on the 8th',
    'author': '',
    'company': 'ERPWEB',
    'maintainer': '',
    'license': 'LGPL-3',
    'depends': [
        'website_sale', 'account', 'sale_renting', 'account_payment'
    ],
    'data': [
        'data/non_payment.xml',
        'views/res_config_settings_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
