from odoo import fields, models, api
from odoo.exceptions import ValidationError


class HospitalBill(models.Model):
    _name = 'hospital.bill'
    _description = 'Hospital Bill'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    appointment_id = fields.Many2one('hospital.appointment', string='Appointment', tracking=True)
    consultation_fee = fields.Float(string='Consultation Fee', tracking=True)
    medicine_charges = fields.Float(string='Medicine Charges', tracking=True)
    total_amount = fields.Float(string='Total Amount', compute='_compute_total_amount', store=True, tracking=True)

    @api.depends('consultation_fee', 'medicine_charges')
    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount = rec.consultation_fee + rec.medicine_charges

    def action_send_bill_email(self):
        self.ensure_one()
        if not self.appointment_id or not self.appointment_id.patient_id or not self.appointment_id.patient_id.email:
            raise ValidationError("Please configure an email address for the patient on the associated appointment before sending the email.")
        template = self.env.ref('hospital_management.bill_email_template', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)
            self.message_post(body="Bill payment email has been sent successfully to patient.")
