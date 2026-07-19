import base64
import io

from odoo import fields, models
from odoo.exceptions import UserError

try:
    import xlsxwriter
    XLSXWRITER_AVAILABLE = True
except ImportError:
    XLSXWRITER_AVAILABLE = False


class ExportBillWizard(models.TransientModel):
    """Excel Bill Export Wizard
    Exports all (or filtered) hospital.bill records to an XLSX file
    with columns: appointment, patient, consultation_fee,
                  medicine_charges, total_amount.
    """
    _name = 'export.bill.wizard'
    _description = 'Export Bills to Excel'

    date_from = fields.Date(string='From Date')
    date_to   = fields.Date(string='To Date')
    excel_file      = fields.Binary(string='Download Excel', readonly=True)
    excel_filename  = fields.Char(string='Filename', readonly=True)

    # ── builder ──────────────────────────────────────────────────────────────
    def _build_domain(self):
        domain = []
        # Bills don't have their own date; filter via appointment_date if set
        if self.date_from:
            domain.append(('appointment_id.appointment_date', '>=', str(self.date_from)))
        if self.date_to:
            domain.append(('appointment_id.appointment_date', '<=', str(self.date_to) + ' 23:59:59'))
        return domain

    def _generate_xlsx(self, bills):
        output = io.BytesIO()
        workbook  = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet     = workbook.add_worksheet('Bills')

        # ── formats ──
        title_fmt = workbook.add_format({
            'bold': True, 'font_size': 14, 'font_color': '#FFFFFF',
            'bg_color': '#1F4E79', 'align': 'center', 'valign': 'vcenter',
            'border': 1,
        })
        header_fmt = workbook.add_format({
            'bold': True, 'font_color': '#FFFFFF',
            'bg_color': '#2E75B6', 'align': 'center',
            'border': 1, 'valign': 'vcenter',
        })
        row_fmt = workbook.add_format({
            'border': 1, 'valign': 'vcenter',
        })
        money_fmt = workbook.add_format({
            'border': 1, 'valign': 'vcenter',
            'num_format': '#,##0.00',
        })
        alt_fmt = workbook.add_format({
            'border': 1, 'valign': 'vcenter',
            'bg_color': '#DEEAF1',
        })
        alt_money_fmt = workbook.add_format({
            'border': 1, 'valign': 'vcenter',
            'bg_color': '#DEEAF1', 'num_format': '#,##0.00',
        })
        total_label_fmt = workbook.add_format({
            'bold': True, 'border': 1,
            'bg_color': '#BDD7EE', 'align': 'right',
        })
        total_val_fmt = workbook.add_format({
            'bold': True, 'border': 1,
            'bg_color': '#BDD7EE', 'num_format': '#,##0.00',
        })

        # ── title row ──
        sheet.merge_range(0, 0, 0, 5, 'Hospital Bills Report', title_fmt)
        sheet.set_row(0, 28)

        # ── headers ──
        headers = [
            '#', 'Appointment ID', 'Patient Name',
            'Consultation Fee', 'Medicine Charges', 'Total Amount',
        ]
        col_widths = [5, 20, 25, 18, 18, 18]
        for col, (h, w) in enumerate(zip(headers, col_widths)):
            sheet.write(1, col, h, header_fmt)
            sheet.set_column(col, col, w)
        sheet.set_row(1, 20)

        # ── data rows ──
        grand_total = 0.0
        for r_idx, bill in enumerate(bills):
            row = r_idx + 2
            is_alt = r_idx % 2 == 1
            rf      = alt_fmt       if is_alt else row_fmt
            mf      = alt_money_fmt if is_alt else money_fmt

            appt_name    = bill.appointment_id.display_name if bill.appointment_id else ''
            patient_name = (
                bill.appointment_id.patient_id.name
                if bill.appointment_id and bill.appointment_id.patient_id else ''
            )

            sheet.write(row, 0, r_idx + 1,              rf)
            sheet.write(row, 1, appt_name,              rf)
            sheet.write(row, 2, patient_name,           rf)
            sheet.write(row, 3, bill.consultation_fee,  mf)
            sheet.write(row, 4, bill.medicine_charges,  mf)
            sheet.write(row, 5, bill.total_amount,      mf)
            grand_total += bill.total_amount

        # ── grand total row ──
        total_row = len(bills) + 2
        sheet.merge_range(total_row, 0, total_row, 4, 'Grand Total', total_label_fmt)
        sheet.write(total_row, 5, grand_total, total_val_fmt)

        workbook.close()
        return output.getvalue()

    # ── action ───────────────────────────────────────────────────────────────
    def action_export_bills(self):
        self.ensure_one()

        if not XLSXWRITER_AVAILABLE:
            raise UserError(
                "The 'xlsxwriter' Python library is not installed.\n"
                "Run:  pip install xlsxwriter"
            )

        bills = self.env['hospital.bill'].search(self._build_domain())
        if not bills:
            raise UserError("No bills found for the selected criteria.")

        xlsx_data  = self._generate_xlsx(bills)
        filename   = 'hospital_bills.xlsx'

        self.write({
            'excel_file':     base64.b64encode(xlsx_data),
            'excel_filename': filename,
        })

        # Return an action that downloads the file
        return {
            'type': 'ir.actions.act_url',
            'url': (
                f'/web/content/?model=export.bill.wizard'
                f'&id={self.id}'
                f'&field=excel_file'
                f'&filename_field=excel_filename'
                f'&download=true'
            ),
            'target': 'new',
        }
