from odoo import models, fields, api

class HudsonDivision(models.Model):
    _name = 'hudson.division'
    _description = 'Hudson Division'
    _order = 'sequence, name'
    
    name = fields.Char(string='Division Name', required=True)
    code = fields.Char(string='Division Code', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
    
    admin_ids = fields.Many2many(
        'res.users',
        string='Division Admins',
        domain=[('user_type', '=', 'division_admin')]
    )
    
    # Statistics
    customer_count = fields.Integer(
        string='Total Customers',
        compute='_compute_statistics'
    )
    
    active_cleaning_count = fields.Integer(
        string='Active Cleanings',
        compute='_compute_statistics'
    )
    
    @api.depends('code')
    def _compute_statistics(self):
        for division in self:
            if division.code == 'pool':
                customers = self.env['pool.customer'].search_count([])
                cleanings = self.env['pool.cleaning'].search_count([
                    ('state', 'in', ['scheduled', 'in_progress'])
                ])
                division.customer_count = customers
                division.active_cleaning_count = cleanings
            else:
                division.customer_count = 0
                division.active_cleaning_count = 0
    
    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Division code must be unique!')
    ]