from odoo import models, fields, api
from datetime import date

class PoolCleaning(models.Model):
    _name = 'pool.cleaning'
    _description = 'Jadwal Pembersihan Kolam'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'scheduled_date desc'

    name = fields.Char(string='Referensi', required=True, copy=False, default='New')
    customer_id = fields.Many2one('pool.customer', string='Pelanggan', required=True)
    
    # --- FIELD INI WAJIB ADA ---
    scheduled_date = fields.Date(string='Tanggal Jadwal', required=True, default=fields.Date.today)
    # ---------------------------

    state = fields.Selection([
        ('draft', 'Draft'),
        ('scheduled', 'Terjadwal'),
        ('in_progress', 'Sedang Dikerjakan'),
        ('completed', 'Selesai'),
        ('cancelled', 'Dibatalkan'),
    ], string='Status', default='draft', tracking=True)

    # Keuangan
    service_price = fields.Monetary(related='customer_id.service_price', string='Harga Jasa', store=True)
    additional_cost = fields.Monetary(string='Biaya Tambahan', default=0.0)
    total_cost = fields.Monetary(string='Total Biaya', compute='_compute_total', store=True)
    currency_id = fields.Many2one('res.currency', related='customer_id.currency_id')
    
    # Status Pembayaran
    payment_status = fields.Selection([
        ('unpaid', 'Belum Lunas'),
        ('paid', 'Lunas'),
    ], string='Pembayaran', default='unpaid')

    # Field Penting untuk Filter Search
    is_overdue = fields.Boolean(string='Terlambat', compute='_compute_is_overdue', store=True)

    @api.depends('service_price', 'additional_cost')
    def _compute_total(self):
        for record in self:
            record.total_cost = record.service_price + record.additional_cost

    # Di sini letak error sebelumnya, pastikan 'scheduled_date' sudah didefinisikan di atas
    @api.depends('scheduled_date', 'state')
    def _compute_is_overdue(self):
        today = fields.Date.today()
        for record in self:
            if record.scheduled_date:
                record.is_overdue = (record.scheduled_date < today and record.state in ['draft', 'scheduled'])
            else:
                record.is_overdue = False

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('pool.cleaning') or 'CLN-000'
        return super().create(vals)