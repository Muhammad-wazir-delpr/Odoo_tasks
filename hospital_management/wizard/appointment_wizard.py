from odoo import api, fields, models


class AppointmentWizard(models.TransientModel):
    _name = "appointment.wizard"
    _description = "Appointment Wizard"

    patient_id = fields.Many2one('hospital.patient', string="Patient")
    doctor_id = fields.Many2one('hospital.doctor', string="Doctor")
    appointment_date = fields.Datetime(string="Appointment Date")
    symptoms = fields.Char(string="Symptoms")

    def action_create_appointment(self):
        self.ensure_one()

        self.env['hospital.appointment'].create({
            'patient_id': self.patient_id.id,
            'doctor_id': self.doctor_id.id,
            'appointment_date': self.appointment_date,
            'symptoms': self.symptoms,
        })

        return {'ir.actions.act_window_close'}
