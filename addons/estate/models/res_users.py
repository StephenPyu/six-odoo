from odoo import models, fields

class ResUsers(models.Model):
    _inherit = "res.users"

    property_ids = fields.One2many(
        "estate.property",  # Target model
        "salesperson_id",   # Inverse field in estate.property
        string="Properties"
    )
