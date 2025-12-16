{
    'name': 'AIO Management',
    'version': '1.0',
    'summary': 'All-In-One Management System (arctic)',
    'description': 'Modul manajemen terpadu untuk Kolam Renang dan divisi lainnya.',
    'category': 'Services',
    'author': 'Habib Suprayoga',
    'depends': ['base', 'mail', 'web'],
    'data': [
        # 1. Security & Data
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/aio_service_data.xml',

        # 2. Views (Urutan: Child -> Parent)
        'views/pool_customer_views.xml',
        'views/pool_cleaning_views.xml',
        'views/pool_report_views.xml',
        'views/aio_division_views.xml',  # Division memanggil action di atas
        
        # 3. Menu
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}