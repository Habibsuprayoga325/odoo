from odoo import models, fields, api

class PoolFinancialReport(models.Model):
    _name = 'pool.financial.report'
    _description = 'Laporan Keuangan Kolam'
    _order = 'date_from desc'
    
    name = fields.Char(string='Report Name', required=True)
    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    
    # Income
    total_income = fields.Monetary(string='Total Income', compute='_compute_financials', store=True)
    paid_income = fields.Monetary(string='Paid Income', compute='_compute_financials', store=True)
    unpaid_income = fields.Monetary(string='Unpaid Income', compute='_compute_financials', store=True)
    
    # Expenses
    total_expenses = fields.Monetary(string='Total Expenses', compute='_compute_financials', store=True)
    
    # Balance
    balance = fields.Monetary(string='Balance', compute='_compute_financials', store=True)
    
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    
    # Details
    cleaning_ids = fields.Many2many(
        'pool.cleaning',
        string='Cleanings',
        compute='_compute_cleanings'
    )
    
    cleaning_count = fields.Integer(string='Total Cleanings', compute='_compute_cleanings')
    
    @api.depends('date_from', 'date_to')
    def _compute_cleanings(self):
        for report in self:
            cleanings = self.env['pool.cleaning'].search([
                ('scheduled_date', '>=', report.date_from),
                ('scheduled_date', '<=', report.date_to),
            ])
            report.cleaning_ids = cleanings
            report.cleaning_count = len(cleanings)
    
    @api.depends('cleaning_ids')
    def _compute_financials(self):
        for report in self:
            total_income = sum(report.cleaning_ids.mapped('total_cost'))
            paid_income = sum(
                report.cleaning_ids.filtered(
                    lambda c: c.payment_status == 'paid'
                ).mapped('paid_amount')
            )
            unpaid_income = total_income - paid_income
            total_expenses = sum(report.cleaning_ids.mapped('additional_cost'))
            
            report.total_income = total_income
            report.paid_income = paid_income
            report.unpaid_income = unpaid_income
            report.total_expenses = total_expenses
            report.balance = paid_income - total_expenses
    
    def action_view_cleanings(self):
        self.ensure_one()
        return {
            'name': f'Cleanings - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'pool.cleaning',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.cleaning_ids.ids)],
        }


class PoolCleaningReport(models.Model):
    _name = 'pool.cleaning.report'
    _description = 'Pool Cleaning Report (Pivot/Graph)'
    _auto = False
    _order = 'scheduled_date desc'
    
    # --- BAGIAN INI WAJIB ADA ---
    _rec_name = 'customer_id' 
    # ----------------------------
    
    scheduled_date = fields.Date(string='Date', readonly=True)
    customer_id = fields.Many2one('pool.customer', string='Customer', readonly=True)
    service_type = fields.Selection([
        ('economy', 'Economy'),
        ('business', 'Business'),
        ('exclusive', 'Exclusive'),
    ], string='Service Type', readonly=True)
    
    cleaning_type = fields.Selection([
        ('regular', 'Regular Cleaning'),
        ('deep', 'Deep Cleaning'),
        ('maintenance', 'Maintenance'),
        ('emergency', 'Emergency'),
    ], string='Cleaning Type', readonly=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('postponed', 'Postponed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', readonly=True)
    
    payment_status = fields.Selection([
        ('unpaid', 'Unpaid'),
        ('partial', 'Partial'),
        ('paid', 'Paid'),
    ], string='Payment Status', readonly=True)
    
    total_cost = fields.Monetary(string='Total Cost', readonly=True)
    paid_amount = fields.Monetary(string='Paid Amount', readonly=True)
    duration = fields.Float(string='Duration (Hours)', readonly=True)
    
    currency_id = fields.Many2one('res.currency', readonly=True)
    
    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW pool_cleaning_report AS (
                SELECT
                    pc.id,
                    pc.scheduled_date,
                    pc.customer_id,
                    cust.service_type,
                    pc.cleaning_type,
                    pc.state,
                    pc.payment_status,
                    pc.total_cost,
                    pc.paid_amount,
                    pc.duration,
                    pc.currency_id
                FROM pool_cleaning pc
                LEFT JOIN pool_customer cust ON pc.customer_id = cust.id
            )
        """)