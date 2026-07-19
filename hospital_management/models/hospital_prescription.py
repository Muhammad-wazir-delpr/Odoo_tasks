from odoo import fields, models, api


class HospitalPrescription(models.Model):
    _name = 'hospital.prescription'
    _description = 'Hospital Prescription'

    appointment_id = fields.Many2one('hospital.appointment', string='Appointment')
    medicine = fields.Char(string='Medicine')
    dosage = fields.Char(string='Dosage')
    instructions = fields.Text(string='Instructions')
