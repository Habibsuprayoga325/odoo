from odoo import models, fields, api, exceptions

class PoolCustomer(models.Model):
    _name = 'pool.customer'
    _description = 'Pool Service Customer'
    _order = 'name'
    
    name = fields.Char(string='Customer Name', required=True, index=True)
    code = fields.Char(string='Customer Code', required=True, copy=False, index=True)
    phone = fields.Char(string='Phone Number')
    email = fields.Char(string='Email')
    address = fields.Text(string='Address')
    
    # Pool Information
    pool_length = fields.Float(string='Pool Length (m)', required=True)
    pool_width = fields.Float(string='Pool Width (m)', required=True)
    pool_depth = fields.Float(string='Pool Depth (m)', required=True)
    pool_volume = fields.Float(
        string='Pool Volume (m³)',
        compute='_compute_pool_volume',
        store=True
    )
    
    # Service Information
    service_type = fields.Selection([
        ('economy', 'Economy'),
        ('business', 'Business'),
        ('exclusive', 'Exclusive'),
    ], string='Service Type', required=True, default='economy')
    
    service_price = fields.Monetary(
        string='Service Price',
        compute='_compute_service_price',
        store=True
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )
    
    # Relations
    cleaning_ids = fields.One2many(
        'pool.cleaning',
        'customer_id',
        string='Cleaning History'
    )
    
    cleaning_count = fields.Integer(
        string='Total Cleanings',
        compute='_compute_cleaning_count'
    )
    
    # Status
    active = fields.Boolean(string='Active', default=True)
    notes = fields.Text(string='Notes')
    
    @api.depends('pool_length', 'pool_width', 'pool_depth')
    def _compute_pool_volume(self):
        for record in self:
            record.pool_volume = record.pool_length * record.pool_width * record.pool_depth
    
    @api.depends('service_type', 'pool_volume')
    def _compute_service_price(self):
        for record in self:
            base_price = 0
            if record.service_type == 'economy':
                base_price = 100000 + (record.pool_volume * 5000)
            elif record.service_type == 'business':
                base_price = 200000 + (record.pool_volume * 8000)
            elif record.service_type == 'exclusive':
                base_price = 350000 + (record.pool_volume * 12000)
            
            record.service_price = base_price
    
    @api.depends('cleaning_ids')
    def _compute_cleaning_count(self):
        for record in self:
            record.cleaning_count = len(record.cleaning_ids)
    
    @api.model
    def create(self, vals):
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('pool.customer') or 'CUST-000'
        return super().create(vals)
    
    def action_view_cleanings(self):
        """Open customer's cleaning history"""
        self.ensure_one()
        return {
            'name': f'Cleaning History - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'pool.cleaning',
            'view_mode': 'tree,form',
            'domain': [('customer_id', '=', self.id)],
            'context': {'default_customer_id': self.id}
        }
    
    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Customer code must be unique!')
    ]