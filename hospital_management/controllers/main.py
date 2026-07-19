# -*- coding: utf-8 -*-
from odoo import http, fields
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class HospitalDashboardController(http.Controller):

    @http.route('/hospital_management/dashboard_banner', type='json', auth='user')
    def get_dashboard_banner(self):
        # 1. Total Patients
        total_patients = request.env['hospital.patient'].search_count([])

        # 2. Today's Appointments
        today = fields.Date.context_today(request.env['hospital.appointment'])
        today_start_str = f"{today} 00:00:00"
        today_end_str = f"{today} 23:59:59"
        today_appointments = request.env['hospital.appointment'].search_count([
            ('appointment_date', '>=', today_start_str),
            ('appointment_date', '<=', today_end_str)
        ])

        # 3. Total Revenue
        request.env.cr.execute("SELECT SUM(total_amount) FROM hospital_bill")
        res = request.env.cr.fetchone()
        total_revenue = res[0] if res and res[0] else 0.0

        # 4. Top Doctors (top 3 by appointment count)
        query = """
            SELECT doctor_id, COUNT(*) as app_count 
            FROM hospital_appointment 
            WHERE doctor_id IS NOT NULL 
            GROUP BY doctor_id 
            ORDER BY app_count DESC 
            LIMIT 3
        """
        request.env.cr.execute(query)
        top_doc_data = request.env.cr.dictfetchall()

        top_doctors_list = []
        for doc in top_doc_data:
            doctor = request.env['hospital.doctor'].browse(doc['doctor_id'])
            if doctor.exists():
                top_doctors_list.append(f"{doctor.name} ({doc['app_count']} Appts)")
        top_doctors_str = ", ".join(top_doctors_list) if top_doctors_list else "None"

        # Format total revenue nicely
        formatted_revenue = f"${total_revenue:,.2f}"

        # Render QWeb template
        html = request.env.ref('hospital_management.dashboard_banner_template')._render({
            'total_patients': total_patients,
            'today_appointments': today_appointments,
            'total_revenue': formatted_revenue,
            'top_doctors': top_doctors_str,
        })

        return {
            'html': html
        }
