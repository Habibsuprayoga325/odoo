from odoo import models, fields, api

class PoolCustomer(models.Model):
    _name = 'pool.customer'
    _description = 'Pelanggan Kolam Renang'
    _inherit = ['mail.thread']

    name = fields.Char(string='Nama Pelanggan', required=True, tracking=True)
    code = fields.Char(string='Kode Pelanggan')
    phone = fields.Char(string='Nomor Telepon', required=True)
    address = fields.Text(string='Alamat')
    
    # Data Kolam
    pool_volume = fields.Float(string='Volume Kolam (m3)')
    service_type = fields.Selection([
        ('economy', 'Ekonomi'),
        ('business', 'Bisnis'),
        ('exclusive', 'Eksklusif'),
    ], string='Jenis Layanan', required=True, default='economy', tracking=True)
    
    service_price = fields.Monetary(string='Harga Layanan', compute='_compute_price', store=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)

    # --- FIELD BARU UNTUK MENGATASI ERROR ---
    cleaning_count = fields.Integer(string='Jumlah Pembersihan', compute='_compute_cleaning_count')
    # ----------------------------------------

    @api.depends('service_type')
    def _compute_price(self):
        prices = {'economy': 100000, 'business': 250000, 'exclusive': 500000}
        for record in self:
            record.service_price = prices.get(record.service_type, 0)
            
    def _compute_cleaning_count(self):
        for record in self:
            # Menghitung berapa banyak cleaning yang terhubung ke customer ini
            # Pastikan model 'pool.cleaning' sudah ada field 'customer_id'
            record.cleaning_count = self.env['pool.cleaning'].search_count([
                ('customer_id', '=', record.id)
            ])