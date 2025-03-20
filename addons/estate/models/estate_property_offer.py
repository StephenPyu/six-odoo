from odoo import fields, models, api
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError

# EstateProperty inherit from models.Model, the framework will translate this model to the database table
class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'estate property offer'

    price = fields.Float()
    status = fields.Selection(
        string="Status",
        selection=[
            ('accepted', 'Accepted'),
            ('refused', 'Refused')
        ],
        copy=False
    )
    partner_id = fields.Many2one("res.partner", required=True)
    property_id = fields.Many2one("estate.property", required=True)
    validity = fields.Integer(default=7)
    #this is inverse compute, when the deadline is input, it can also set the validity field
    date_deadline = fields.Date(compute="_compute_date_deadline", inverse="_inverse_validity")

    #Define a related field to type_id from property_id
    #One offer can relate to one property, and it can transiently relate to one property type, so this field can be inverse referenced from property type model
    property_type_id = fields.Many2one(
        'estate.property.type',  # Model to which it relates
        string='Property Type',
        related='property_id.type_id',  # Field to relate to
        store=True,  # This makes the field stored in the database
        readonly=True  # Makes the field read-only, it cannot be edited directly
    )

    @api.depends("validity")
    def _compute_date_deadline(self):
        for record in self:
            if record["create_date"]:
                record.date_deadline = record["create_date"] + timedelta(days=record.validity)
            else:
                record.date_deadline = datetime.today() + timedelta(days=record.validity)

    def _inverse_validity(self):
        for record in self:
            record.validity = (record.date_deadline - datetime.today().date()).days

    def action_accept(self):
        for record in self:
            record.property_id.selling_price = record.price
            record.property_id.buyer_id = record.partner_id
            record.status = 'accepted'
        return True

    def action_reject(self):
        for record in self:
            record.property_id.selling_price = None
            record.property_id.buyer_id = None
            record.status = 'refused'
        return True

    _sql_constraints = [
        ('check_offer_price', 'CHECK(price >= 0)',
         'The price of the offer should be more than 0.')
    ]

    #method override for the "create", should declare as @api.model_create_multi
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            property_id = vals.get("property_id")
            if property_id:
                estate_property = self.env["estate.property"].browse(property_id)
                # Set property state to 'Offer Received'
                estate_property.state = "offer_received"

                # Check for lower offers
                existing_offers = self.search([("property_id", "=", property_id)])
                if existing_offers and any(o.price >= vals["price"] for o in existing_offers):
                    raise ValidationError("You cannot create an offer lower than an existing one.")

        return super().create(vals_list)

    _order = "price desc"