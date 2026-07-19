from odoo import models, fields, tools

class HospitalDashboard(models.Model):
    _name = 'hospital.dashboard'
    _description = 'Hospital Dashboard'
    _auto = False

    appointment_date = fields.Datetime(string='Appointment Date', readonly=True)
    doctor_id = fields.Many2one('hospital.doctor', string='Doctor', readonly=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', readonly=True)
    total_amount = fields.Float(string='Total Amount', readonly=True)
    revenue = fields.Float(string='Revenue', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW hospital_dashboard AS (
                SELECT
                    a.id AS id,
                    a.appointment_date AS appointment_date,
                    a.doctor_id AS doctor_id,
                    a.patient_id AS patient_id,
                    COALESCE(SUM(b.total_amount), 0) AS total_amount,
                    COALESCE(SUM(b.total_amount), 0) AS revenue
                FROM hospital_appointment a
                LEFT JOIN hospital_bill b ON b.appointment_id = a.id
                GROUP BY a.id, a.appointment_date, a.doctor_id, a.patient_id
            )
        """)
