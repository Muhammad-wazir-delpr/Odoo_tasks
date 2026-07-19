from datetime import date
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HospitalPatient(models.Model):
    _name = 'hospital.patient'
    _description = 'Hospital Patient'

    patient_id = fields.Char(
        string='Patient ID', required=True, copy=False, readonly=True, default='New')
    name = fields.Char(string='patient name')
    image = fields.Image(string='patient image')
    date_of_birth = fields.Date(string='Date of Birth')
    computed_age = fields.Integer(string='Age', compute='_compute_age')
    age = fields.Integer(string='Age')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Gender')
    phone = fields.Char(string='Phone Number')
    email = fields.Char(string='Email Address')
    blood_group = fields.Char(string='Blood Group')
    address = fields.Char(string='Address')
    note = fields.Text(string='Note')
    appointment_count = fields.Integer(string='Appointment Count', compute='_compute_appointment_count')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('patient_id', 'New') == 'New':
                vals['patient_id'] = self.env['ir.sequence'].next_by_code('hospital.patient') or 'new'
        return super(HospitalPatient, self).create(vals_list)

    @api.depends('date_of_birth')
    def _compute_age(self):
        for rec in self:
            if rec.date_of_birth:
                rec.computed_age = date.today().year - rec.date_of_birth.year

            else:
                rec.computed_age = 0

    def _compute_appointment_count(self):
        for rec in self:
            rec.appointment_count = self.env['hospital.appointment'].search_count([
                ('doctor_id', '=', rec.id)
            ])

    def action_view_appointments(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Appointments',
            'res_model': 'hospital.appointment',
            'view_mode': 'list,form',
            'domain': [('patient_id', 'in', self.ids)],
        }

    # SQL Constraint
    _sql_constraints = [
        (
            'phone_unique',
            'unique(phone)',
            'Phone number must be unique!',
        )
    ]

    # Python Constraint
    @api.constrains('age')
    def _check_age(self):
        for rec in self:
            if rec.age <= 0:
                raise ValidationError(
                    'Age must be greater than 0.'
                )
