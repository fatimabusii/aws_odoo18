{
    'name': 'BlueSpace Website extended',
    # 'version': '16.0.1.0.0',
    'version': '1.0',
    'summary': '',
    'description': '',
    'author': '',
    'company': 'ERPWEB',
    'maintainer': '',
    'license': 'LGPL-3',
    'depends': [
        'website_sale', 'sale_subscription', 'sale', 'portal'      
    ],
    'data': [
        'views/website_template.xml',
        'views/res_config_view.xml',
    ],
    'assets': {
        'web.assets_frontend': [
        ],
    },
    
    'installable': True,
    'application': False,
    'auto_install': False,
}
