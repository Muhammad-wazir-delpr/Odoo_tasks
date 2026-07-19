from odoo import api, fields, models


class HospitalDoctor(models.Model):
    _name = 'hospital.doctor'
    _description = 'Hospital Doctor'

    name = fields.Char(string='Name')
    specialization = fields.Char(string='Specialization')
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    experience = fields.Char(string='Experience')
    consultation_fee = fields.Char(string='Consultation Fee')
    appointment_ids = fields.One2many(comodel_name='hospital.appointment', inverse_name='doctor_id',
                                      string='Appointments')
    appointment_count = fields.Integer(string='Appointments', compute='_compute_appointment_count')
    user_id = fields.Many2one('res.users', string='Related User')

    @api.depends('appointment_ids')
    def _compute_appointment_count(self):
        for rec in self:
            rec.appointment_count = len(rec.appointment_ids)

    def action_view_appointments(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Appointments',
            'res_model': 'hospital.appointment',
            'view_mode': 'list,form',
            'domain': [('doctor_id', '=', self.id)],
        }
