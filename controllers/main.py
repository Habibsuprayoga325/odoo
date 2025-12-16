from odoo import http
from odoo.http import request


class HudsonController(http.Controller):
    
    @http.route('/hudson/dashboard', type='http', auth='user', website=True)
    def dashboard(self, **kwargs):
        """Dashboard untuk Division Admin"""
        user = request.env.user
        
        # Get user divisions
        divisions = user.division_ids
        
        # Get statistics
        stats = {}
        for division in divisions:
            if division.code == 'pool':
                stats[division.code] = {
                    'total_customers': request.env['pool.customer'].search_count([]),
                    'active_cleanings': request.env['pool.cleaning'].search_count([
                        ('state', 'in', ['scheduled', 'in_progress'])
                    ]),
                    'completed_today': request.env['pool.cleaning'].search_count([
                        ('scheduled_date', '=', http.request.env.context.get('tz', 'UTC')),
                        ('state', '=', 'completed')
                    ]),
                }
        
        values = {
            'user': user,
            'divisions': divisions,
            'stats': stats,
        }
        
        return request.render('hudson_management.dashboard_template', values)
    
    @http.route('/hudson/api/dashboard_data', type='json', auth='user')
    def get_dashboard_data(self, **kwargs):
        """API endpoint untuk dashboard data"""
        user = request.env.user
        return user.get_user_dashboard_data()