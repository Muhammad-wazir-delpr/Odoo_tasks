from datetime import timedelta
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class HospitalAppointment(models.Model):
    _name = 'hospital.appointment'
    _description = 'Hospital Appointment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'patient_id'
    """what are the core diff but the class name (HospitalAppointment)  and _name (hospital.appointment) methods why we specify two?? instead of one."""

    patient_id = fields.Many2one('hospital.patient', string='Patient', tracking=True)
    doctor_id = fields.Many2one('hospital.doctor', string='Doctor', tracking=True)
    appointment_date = fields.Datetime(string='Appointment Date', tracking=True)
    symptoms = fields.Char(string='Symptoms')
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed'), ('done', 'Done'),
                              ('cancelled', 'Cancelled')], string='State', default='draft', tracking=True)
    prescription_ids = fields.One2many('hospital.prescription', 'appointment_id', string='Prescriptions')

    def action_confirm(self):
        self.state = 'confirmed'

    def action_complete(self):
        self.state = 'done'

    def action_cancel(self):
        self.state = 'cancelled'

    def action_send_appointment_email(self):
        self.ensure_one()
        if not self.patient_id or not self.patient_id.email:
            raise ValidationError("Please configure an email address for the patient before sending the email.")
        template = self.env.ref('hospital_management.appointment_email_template', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)
            self.message_post(body="Appointment confirmation email has been sent successfully to patient.")

    @api.constrains('appointment_date')
    def _check_appointment_date(self):
        for rec in self:
            if (rec.appointment_date and
                    rec.appointment_date < fields.Datetime.now()):
                raise ValidationError(
                    'Appointment date cannot be in the past.'
                )

    # ── Cron: Reminder ────────────────────────────────────────────────────────
    def _cron_send_appointment_reminders(self):
        """Send reminder to patients whose appointment is within the next 24 h.
        Runs every hour (or as configured in the cron record).
        """
        now = fields.Datetime.now()
        remind_from = now
        remind_to   = now + timedelta(hours=24)

        appointments = self.search([
            ('state', '=', 'confirmed'),
            ('appointment_date', '>=', remind_from),
            ('appointment_date', '<=', remind_to),
        ])

        template = self.env.ref(
            'hospital_management.appointment_email_template',
            raise_if_not_found=False,
        )

        for appointment in appointments:
            if template and appointment.patient_id and appointment.patient_id.email:
                template.send_mail(appointment.id, force_send=True)

            appointment.message_post(
                body=(
                    f"⏰ <b>Reminder:</b> Appointment scheduled on "
                    f"<b>{appointment.appointment_date}</b> "
                    f"for patient <b>{appointment.patient_id.name}</b>. "
                    "Automated reminder sent."
                )
            )

    # ── Cron: Auto-Cancel ─────────────────────────────────────────────────────
    def _cron_auto_cancel_missed_appointments(self):
        """Automatically cancel appointments that are past their date and
        were never completed.  Runs once a day.
        """
        now = fields.Datetime.now()

        missed = self.search([
            ('state', 'in', ['draft', 'confirmed']),
            ('appointment_date', '<', now),
        ])

        for appointment in missed:
            appointment.state = 'cancelled'
            appointment.message_post(
                body=(
                    f"❌ <b>Auto-Cancelled:</b> Appointment on "
                    f"<b>{appointment.appointment_date}</b> "
                    f"for patient <b>{appointment.patient_id.name}</b> "
                    "was missed and has been automatically cancelled."
                )
            )
