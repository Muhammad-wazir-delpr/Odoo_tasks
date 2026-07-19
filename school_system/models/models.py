from odoo import models, fields, api


class SchoolSystem(models.Model):
    _name = 'school.system'
    _description = 'School System'

    name = fields.Char()
    age = fields.Integer()
    description = fields.Text()
