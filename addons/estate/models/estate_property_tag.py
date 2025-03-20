from odoo import fields, models

# EstateProperty inherit from models.Model, the framework will translate this model to the database table
class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'estate property tag'

    #named parameter "required" set as True
    name = fields.Char(required=True)
    color = fields.Integer()

    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)', 'The property tag name must be unique!')
    ]

    _order = "name asc"






