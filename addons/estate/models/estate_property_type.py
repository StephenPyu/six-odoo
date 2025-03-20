from odoo import fields, models, api

# EstateProperty inherit from models.Model, the framework will translate this model to the database table
class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'estate property type'

    #named parameter "required" set as True
    name = fields.Char(required=True)
    property_ids = fields.One2many("estate.property", inverse_name="type_id", string="Properties")
    sequence = fields.Integer(string="Sequence", default=10)

    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)', 'The property type name must be unique!')
    ]

    # Define the One2many field to inverse the relationship from the offer model
    offer_ids = fields.One2many(
        'estate.property.offer',  # Model this relates to
        'property_type_id',  # Field in 'estate.property.offer' that refers to 'estate.property.type'
        string='Offers'  # The field label for the One2many
    )

    # Define the computed field to count the number of offers
    offer_count = fields.Integer(
        string='Number of Offers',
        compute='_compute_offer_count',  # The method that calculates the value
        store=True  # Store the result in the database
    )

    @api.depends('offer_ids')  # Trigger the computation when the related offer_ids change
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)  # Count the number of offers related to the property type

    _order = 'sequence, name'

