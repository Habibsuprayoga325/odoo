from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'
    
    user_type = fields.Selection([
        ('regular', 'Regular User'),
        ('member', 'Member'),
        ('division_admin', 'Division Admin'),
    ], string='User Type', default='regular')
    
    division_ids = fields.Many2many(
        'hudson.division',
        string='Assigned Divisions',
        help='Divisions that this admin can manage'
    )
    
    @api.model
    def get_user_dashboard_data(self):
        """Return dashboard data based on user type"""
        user = self.env.user
        data = {
            'user_type': user.user_type,
            'name': user.name,
            'divisions': [],
        }
        
        if user.user_type == 'division_admin':
            divisions = user.division_ids
            data['divisions'] = [{
                'id': div.id,
                'name': div.name,
                'code': div.code,
                'description': div.description,
            } for div in divisions]
        
        return data