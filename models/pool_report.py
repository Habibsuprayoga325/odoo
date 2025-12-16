from odoo import models, fields, api, tools

# 1. Financial Report
class PoolFinancialReport(models.Model):
    _name = 'pool.financial.report'
    _description = 'Laporan Keuangan Kolam'
    _order = 'date_from desc'
    
    name = fields.Char(string='Report Name', required=True)
    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    
    total_income = fields.Monetary(string='Total Income', compute='_compute_financials', store=True)
    paid_income = fields.Monetary(string='Paid Income', compute='_compute_financials', store=True)
    unpaid_income = fields.Monetary(string='Unpaid Income', compute='_compute_financials', store=True)
    total_expenses = fields.Monetary(string='Total Expenses', compute='_compute_financials', store=True)
    balance = fields.Monetary(string='Balance', compute='_compute_financials', store=True)
    
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    cleaning_ids = fields.Many2many('pool.cleaning', string='Cleanings', compute='_compute_cleanings')
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
            paid_income = sum(report.cleaning_ids.mapped('paid_amount'))
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

# 2. Cleaning Report Analysis
class PoolCleaningReport(models.Model):
    _name = 'pool.cleaning.report'
    _description = 'Pool Cleaning Report Analysis'
    _auto = False
    _rec_name = 'name'  # Kita gunakan field 'name' asli
    _order = 'scheduled_date desc'
    
    # Field Definition (Harus sama dengan kolom di SQL View)
    name = fields.Char(string='Reference', readonly=True)
    scheduled_date = fields.Date(string='Date', readonly=True)
    customer_id = fields.Many2one('pool.customer', string='Customer', readonly=True)
    cleaning_type = fields.Char(string='Cleaning Type', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'), ('scheduled', 'Scheduled'), 
        ('in_progress', 'In Progress'), ('completed', 'Completed'), 
        ('cancelled', 'Cancelled')
    ], string='Status', readonly=True)
    
    total_cost = fields.Monetary(string='Total Cost', readonly=True)
    paid_amount = fields.Monetary(string='Paid Amount', readonly=True)
    duration = fields.Float(string='Duration', readonly=True)
    currency_id = fields.Many2one('res.currency', readonly=True)
    
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW pool_cleaning_report AS (
                SELECT
                    pc.id,
                    pc.name,              -- Kolom ini ADA di screenshot Anda
                    pc.scheduled_date,
                    pc.customer_id,
                    pc.cleaning_type,     -- Kolom ini ADA di screenshot Anda
                    pc.state,
                    pc.total_cost,
                    pc.paid_amount,       -- Kolom ini ADA di screenshot Anda
                    pc.duration,          -- Kolom ini ADA di screenshot Anda
                    pc.currency_id
                FROM pool_cleaning pc
                WHERE pc.active = True
            )
        """)