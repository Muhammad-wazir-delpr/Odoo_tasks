import base64
import csv
import io

from odoo import fields, models
from odoo.exceptions import UserError


class ImportPatientWizard(models.TransientModel):
    """CSV Patient Import Wizard
    Expected CSV columns (header row required):
        name, gender, phone, blood_group
    """
    _name = 'import.patient.wizard'
    _description = 'Import Patients from CSV'

    csv_file = fields.Binary(string='CSV File', required=True)
    csv_filename = fields.Char(string='Filename')

    # ── helpers ──────────────────────────────────────────────────────────────
    ALLOWED_GENDERS = {'male', 'female'}

    def _parse_csv(self, raw_bytes):
        """Decode binary content and return a list of dicts."""
        try:
            text = raw_bytes.decode('utf-8-sig')   # handle BOM from Excel
        except UnicodeDecodeError:
            text = raw_bytes.decode('latin-1')

        reader = csv.DictReader(io.StringIO(text))

        # normalise header names (strip spaces, lower-case)
        reader.fieldnames = [f.strip().lower() for f in (reader.fieldnames or [])]

        required = {'name', 'gender', 'phone', 'blood_group'}
        missing = required - set(reader.fieldnames)
        if missing:
            raise UserError(
                f"CSV is missing required column(s): {', '.join(sorted(missing))}.\n"
                "Expected headers: name, gender, phone, blood_group"
            )

        return list(reader)

    # ── action ───────────────────────────────────────────────────────────────
    def action_import_patients(self):
        self.ensure_one()
        if not self.csv_file:
            raise UserError("Please upload a CSV file before importing.")

        raw = base64.b64decode(self.csv_file)
        rows = self._parse_csv(raw)

        if not rows:
            raise UserError("The CSV file is empty or contains only a header row.")

        Patient = self.env['hospital.patient']
        created = skipped = 0

        for idx, row in enumerate(rows, start=2):   # start=2 → human row number
            name       = (row.get('name') or '').strip()
            gender     = (row.get('gender') or '').strip().lower()
            phone      = (row.get('phone') or '').strip()
            blood_group = (row.get('blood_group') or '').strip()

            # basic validation
            if not name:
                skipped += 1
                continue

            if gender not in self.ALLOWED_GENDERS:
                gender = False          # leave blank instead of erroring

            # skip if phone already exists (unique constraint)
            if phone and Patient.search_count([('phone', '=', phone)]):
                skipped += 1
                continue

            Patient.create({
                'name':        name,
                'gender':      gender or False,
                'phone':       phone or False,
                'blood_group': blood_group or False,
            })
            created += 1

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Import Complete',
                'message': (
                    f"✅ {created} patient(s) imported successfully. "
                    f"⚠️ {skipped} row(s) skipped (empty name or duplicate phone)."
                ),
                'type': 'success',
                'sticky': True,
            },
        }
