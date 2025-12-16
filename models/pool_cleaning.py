from odoo import models, fields, api, exceptions
from datetime import datetime, timedelta

class PoolCleaning(models.Model):
    _name = 'pool.cleaning'
    _description = 'Pool Cleaning Service'
    _order = 'scheduled_date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Cleaning Reference', required=True, copy=False, default='New')
    customer_id = fields.Many2one('pool.customer', string='Customer', required=True, tracking=True)
    
    # Customer Info (related fields for easy access)
    customer_phone = fields.Char(related='customer_id.phone', string='Phone', readonly=True)
    customer_address = fields.Text(related='customer_id.address', string='Address', readonly=True)
    pool_volume = fields.Float(related='customer_id.pool_volume', string='Pool Volume', readonly=True)
    service_type = fields.Selection(related='customer_id.service_type', string='Service Type', readonly=True)
    
    # Scheduling
    scheduled_date = fields.Date(string='Scheduled Date', required=True, default=fields.Date.today, tracking=True)
    start_datetime = fields.Datetime(string='Start Time')
    end_datetime = fields.Datetime(string='End Time')
    duration = fields.Float(string='Duration (Hours)', compute='_compute_duration', store=True)
    
    # Team Assignment
    cleaner_ids = fields.Many2many('res.users', string='Cleaning Team')
    supervisor_id = fields.Many2one('res.users', string='Supervisor')
    
    # Service Details
    cleaning_type = fields.Selection([
        ('regular', 'Regular Cleaning'),
        ('deep', 'Deep Cleaning'),
        ('maintenance', 'Maintenance'),
        ('emergency', 'Emergency'),
    ], string='Cleaning Type', default='regular', required=True)
    
    # Financial
    service_price = fields.Monetary(
        string='Service Price',
        related='customer_id.service_price',
        store=True
    )
    additional_cost = fields.Monetary(string='Additional Cost', default=0.0)
    total_cost = fields.Monetary(string='Total Cost', compute='_compute_total_cost', store=True)
    
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    
    # Payment
    payment_status = fields.Selection([
        ('unpaid', 'Unpaid'),
        ('partial', 'Partial'),
        ('paid', 'Paid'),
    ], string='Payment Status', default='unpaid', tracking=True)
    
    paid_amount = fields.Monetary(string='Paid Amount', default=0.0)
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('postponed', 'Postponed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    
    postpone_reason = fields.Text(string='Postpone/Cancel Reason')
    
    # Work Details
    work_notes = fields.Text(string='Work Notes')
    chemicals_used = fields.Text(string='Chemicals Used')
    equipment_used = fields.Text(string='Equipment Used')
    
    # Quality
    customer_rating = fields.Selection([
        ('1', '1 - Poor'),
        ('2', '2 - Fair'),
        ('3', '3 - Good'),
        ('4', '4 - Very Good'),
        ('5', '5 - Excellent'),
    ], string='Customer Rating')
    
    customer_feedback = fields.Text(string='Customer Feedback')
    
    # Computed
    is_overdue = fields.Boolean(string='Is Overdue', compute='_compute_is_overdue', store= True)
    active = fields.Boolean(default=True)
    
    @api.depends('start_datetime', 'end_datetime')
    def _compute_duration(self):
        for record in self:
            if record.start_datetime and record.end_datetime:
                delta = record.end_datetime - record.start_datetime
                record.duration = delta.total_seconds() / 3600
            else:
                record.duration = 0.0
    
    @api.depends('service_price', 'additional_cost')
    def _compute_total_cost(self):
        for record in self:
            record.total_cost = record.service_price + record.additional_cost
    
    @api.depends('scheduled_date', 'state')
    def _compute_is_overdue(self):
        today = fields.Date.today()
        for record in self:
            record.is_overdue = (
                record.scheduled_date < today and 
                record.state in ['draft', 'scheduled']
            )
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('pool.cleaning') or 'CLN-000'
        return super().create(vals)
    
    def action_schedule(self):
        """Mark as scheduled"""
        for record in self:
            if record.state == 'draft':
                record.state = 'scheduled'
    
    def action_start(self):
        """Start cleaning"""
        for record in self:
            if record.state == 'scheduled':
                record.write({
                    'state': 'in_progress',
                    'start_datetime': fields.Datetime.now()
                })
    
    def action_complete(self):
        """Complete cleaning"""
        for record in self:
            if record.state == 'in_progress':
                record.write({
                    'state': 'completed',
                    'end_datetime': fields.Datetime.now()
                })
    
    def action_postpone(self):
        """Postpone cleaning"""
        for record in self:
            if record.state in ['draft', 'scheduled']:
                record.state = 'postponed'
    
    def action_cancel(self):
        """Cancel cleaning"""
        for record in self:
            if record.state not in ['completed', 'cancelled']:
                record.state = 'cancelled'
    
    def action_reset_to_draft(self):
        """Reset to draft"""
        for record in self:
            record.state = 'draft'