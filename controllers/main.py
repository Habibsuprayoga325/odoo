from odoo import http
from odoo.http import request

class AioController(http.Controller):
    
    @http.route('/arctic/dashboard', type='http', auth='user', website=True)
    def dashboard(self, **kwargs):
        """Dashboard Website untuk Division Admin"""
        user = request.env.user
        
        # Mengambil divisi yang ditugaskan ke user ini
        # (Pastikan field division_ids sudah ada di model res.users)
        divisions = user.division_ids
        
        # Mengambil statistik untuk ditampilkan di website
        stats = {}
        for division in divisions:
            if division.code == 'pool':
                stats[division.code] = {
                    'total_customers': request.env['pool.customer'].search_count([]),
                    'active_cleanings': request.env['pool.cleaning'].search_count([
                        ('state', 'in', ['scheduled', 'in_progress'])
                    ]),
                    'completed_today': request.env['pool.cleaning'].search_count([
                        ('scheduled_date', '=', fields.Date.today()),
                        ('state', '=', 'completed')
                    ]),
                }
        
        values = {
            'user': user,
            'divisions': divisions,
            'stats': stats,
        }
        
        # Render ke template XML website (Anda perlu membuat view ini nanti)
        return request.render('aio_management.dashboard_template', values)
    
    @http.route('/arctic/api/dashboard_data', type='json', auth='user')
    def get_dashboard_data(self, **kwargs):
        """API endpoint untuk mengambil data dashboard dalam format JSON"""
        user = request.env.user
        return user.get_user_dashboard_data()