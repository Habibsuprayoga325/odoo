{
    'name': 'Hudson Management System',
    'version': '17.0.1.0.0',
    'category': 'Services',
    'summary': 'Multi-Division Management System with Pool Service',
    'description': """
        Hudson Management System
        ========================
        System manajemen multi-divisi dengan fitur:
        - Multi-level user access (User, Member, Admin)
        - Division management
        - Pool cleaning service
        - Customer data management
        - Financial & operational reporting
    """,
    'author': 'Habib',
    'website': 'https://www.hudson-management.com',
    'depends': [
        'base',
        'web',
        'portal',
        'website',
    ],
    'data': [
    # 1. Security (Selalu paling atas)
    'security/security.xml',
    'security/ir.model.access.csv',
    
    # 2. Data Master/Awal
    'data/pool_service_data.xml',
    
    # 3. Definisi Action & Views (Urutan logis: dari yang dipanggil ke yang memanggil)
    'views/pool_customer_views.xml', # Berisi action_pool_customer [cite: 256]
    'views/pool_cleaning_views.xml', # Berisi action_pool_cleaning
    'views/pool_report_views.xml',   # Berisi action_pool_report
    
    # 4. View yang memanggil action di atas (Divisions memanggil customer & cleaning)
    'views/divisions_views.xml',     # Sekarang aman karena action sudah terdaftar [cite: 257]
    
    # 5. Menu (Selalu paling bawah agar semua action & view sudah siap)
    'views/menu.xml',                # [cite: 261]
        ],
    'assets': {
        'web.assets_backend': [
            'hudson_management/static/src/css/dashboard.css',
            'hudson_management/static/src/js/dashboard.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}