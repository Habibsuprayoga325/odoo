from odoo import models, fields, api

class AioDivision(models.Model):
    _name = 'aio.division'
    _description = 'AIO Division'
    _order = 'sequence, name'
    
    name = fields.Char(string='Division Name', required=True)
    code = fields.Char(string='Division Code', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
    
    # Statistik untuk Dashboard
    customer_count = fields.Integer(string='Total Customers', compute='_compute_statistics')
    active_cleaning_count = fields.Integer(string='Active Cleanings', compute='_compute_statistics')
    
    @api.depends('code')
    def _compute_statistics(self):
        for division in self:
            if division.code == 'pool':
                division.customer_count = self.env['pool.customer'].search_count([])
                division.active_cleaning_count = self.env['pool.cleaning'].search_count([
                    ('state', 'in', ['scheduled', 'in_progress'])
                ])
            else:
                division.customer_count = 0
                division.active_cleaning_count = 0