{
    'name': 'Blue space extra info extended',
    # 'version': '16.0.1.0.0',
    'version': '1.0',
    'summary': '',
    'description': '',
    'author': '',
    'company': 'ERPWEB-Kevin',
    'maintainer': '',
    'license': 'LGPL-3',
    'depends': [
        'website_sale', 'website_sale_renting', 'bluespace_extended',      
    ],
    'data': [
        'views/sale_view.xml',
        'views/res_config.xml',
        'views/thanks_page.xml',
        'views/extra_info_template.xml',
    ],
    # 'assets': {
    #     'web.assets_frontend': [
    #         'website_extra_info/static/src/**/*',
    #     ],
    # },
    
    'installable': True,
    'application': False,
    'auto_install': False,
}
