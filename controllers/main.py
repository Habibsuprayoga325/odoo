from odoo import http, fields
from odoo.http import request


class HudsonController(http.Controller):
    
    @http.route('/hudson/dashboard', type='http', auth='user', website=True)
    def dashboard(self, **kwargs):
        """Dashboard untuk Division Admin"""
        user = request.env.user
        today = fields.Date.context_today(request)
        
        # Get user divisions
        divisions = user.division_ids
        
        # Get statistics
        stats = {}
        for division in divisions:
            if division.code == 'pool':
                pool_cleaning = request.env['pool.cleaning'].sudo()
                stats[division.code] = {
                    'total_customers': request.env['pool.customer'].sudo().search_count([]),
                    'active_cleanings': pool_cleaning.search_count([
                        ('state', 'in', ['scheduled', 'in_progress'])
                    ]),
                    'completed_today': pool_cleaning.search_count([
                        ('scheduled_date', '=', today),
                        ('state', '=', 'completed')
                    ]),
                    'pending_unpaid': pool_cleaning.search_count([
                        ('payment_status', 'in', ['unpaid', 'partial'])
                    ]),
                }
        
        values = {
            'user': user,
            'divisions': divisions,
            'stats': stats,
        }
        
        return request.render('odoo.dashboard_template', values)
    
    @http.route('/hudson/api/dashboard_data', type='json', auth='user')
    def get_dashboard_data(self, **kwargs):
        """API endpoint untuk dashboard data"""
        user = request.env.user
        return user.get_user_dashboard_data()

    @http.route('/hudson/pool', type='http', auth='user', website=True)
    def pool_dashboard(self, **kwargs):
        """Halaman dashboard divisi kolam renang untuk admin"""
        user = request.env.user
        if not user.has_group('odoo.group_hudson_admin'):
            return request.not_found()

        PoolCustomer = request.env['pool.customer'].sudo()
        PoolCleaning = request.env['pool.cleaning'].sudo()

        customers = PoolCustomer.search([], limit=10, order='write_date desc')
        cleanings = PoolCleaning.search([], limit=10, order='scheduled_date desc')

        stats = {
            'total_customers': PoolCustomer.search_count([]),
            'active_cleanings': PoolCleaning.search_count([('state', 'in', ['scheduled', 'in_progress'])]),
            'completed_cleanings': PoolCleaning.search_count([('state', '=', 'completed')]),
            'pending_unpaid': PoolCleaning.search_count([('payment_status', 'in', ['unpaid', 'partial'])]),
        }

        values = {
            'user': user,
            'stats': stats,
            'customers': customers,
            'cleanings': cleanings,
            'action_pool_customer': request.env.ref('odoo.action_pool_customer').id,
            'action_pool_cleaning': request.env.ref('odoo.action_pool_cleaning').id,
            'action_pool_financial_report': request.env.ref('odoo.action_pool_financial_report').id,
            'action_pool_cleaning_report': request.env.ref('odoo.action_pool_cleaning_report').id,
        }
        return request.render('odoo.pool_dashboard_template', values)
