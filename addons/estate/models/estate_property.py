from datetime import datetime, timedelta
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_utils
# EstateProperty inherit from models.Model, the framework will translate this model to the database table
class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'estate property'

    #named parameter "required" set as True
    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    #use a lambda to set the default value, the lambda will be invoked when the field is initiated
    #this field will not be copied
    date_availability = fields.Date(copy=False,
                                    default=lambda self: datetime.today() + timedelta(days=90),
                                    string='Available From')
    expected_price = fields.Float(required=True)
    #selling_price can't be inputted from web page by user
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    #the label on the web pages will be as the "string"
    living_area = fields.Integer(string='Living Area (sqm)')
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer(string='Garden Area (sqm)')
    #use the tuple array as the selection to define the Selection field
    #help will be displayed on the pages as the helping tip
    garden_orientation = fields.Selection(
        string='Garden orientation',
        selection=[
            ('north', 'North'),
            ('south', 'South'),
            ('east', 'East'),
            ('west', 'West')
        ],
        help="Garden orientation is used to define the orientation of garden")

    active = fields.Boolean(default=True)
    #state will be used as tuple array
    # the tuple(key, value) key will be used as the value in the database
    # the tuple(key, value) value will be used as the label in the pages
    state = fields.Selection(
        string="Status",
        selection=[
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('cancelled', 'Cancelled')
        ],
        required=True,
        copy=False,
        default='new'
    )
    #Many "estate property" has one specific type(id), one type can be used for many properties
    type_id=fields.Many2one("estate.property.type", string="Type")
    #Many "estate property" has one specific buyer, one buyer can buy many properties.
    buyer_id=fields.Many2one("res.partner", string="Buyer", copy=False)
    #Many "estate property" has one specific salesperson, one salesperson can sell many properties.
    #Will get the current user from the self.evn.user
    salesperson_id=fields.Many2one("res.users", string="Salesman", default=lambda self: self.env.user)
    #One property can have many tags, and one tag can be used by many properties
    tag_ids=fields.Many2many("estate.property.tag", string="Tags")
    #In One2many relation, an inverse_name field need to be specified
    offer_ids=fields.One2many("estate.property.offer", 'property_id', string="Offers")
    #total_area is a computed field, its value is calculated by the relevant method
    total_area=fields.Integer(compute="_compute_total_area")
    #private compute method, it depends on the living_area and garden_area to calculate the total_area
    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        #self is a recordset
        for record in self:
            record.total_area = record.living_area + record.garden_area

    #best_price will be calculated from all the offers
    best_price=fields.Float(compute="_compute_best_price")
    @api.depends("offer_ids")
    def _compute_best_price(self):
        for record in self:
            #use the mapped method to retrieve the price from offers then to calculate the maximum price
            record.best_price = max(record.offer_ids.mapped("price"), default=0.0)

    #upon garden field is changed, this method will be invoked, normally the effectiveness can be viewed in the form page
    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = ''

    #this action will be invoked from the web page by RPC
    def action_sold_estate_property(self):
        for record in self:
            if record.state == 'cancelled':
                raise UserError("Cancelled property can't be sold.")
            else:
                record.state = 'sold'
        return True

    def action_cancel_estate_property(self):
        for record in self:
            if record.state == 'sold':
                raise UserError("Sold property can't be cancelled.")
            else:
                record.state = 'cancelled'
        return True

    #define the sql constraints for the various fields
    #for one constraint:
    #the first param is the constraint name.
    #the second is the constraint implementation.
    #the last one is the violated error message.
    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price >= 0)',
         'The expected price of the property should be more than 0.'),
        ('check_selling_price', 'CHECK(selling_price >= 0)',
         'The selling price of the property should be more than 0.')
    ]

    #contraint defined in the method which is triggered when the record is saved
    @api.constrains('selling_price')
    def _check_selling_price(self):
        for record in self:
            if record.selling_price > 0 and record.expected_price > 0:
                #when the offer is accepted, the selling_price will be set as the price of the offer,
                #however the offered price should not be less than the 90% of the expected price
                threshold = record.expected_price * 0.9
                if float_utils.float_compare(record.selling_price, threshold, precision_rounding=0.01) < 0:
                    raise ValidationError("The selling price must be at least 90% of the expected price.")

    #when the record is deleted, we can define a hook to be invoked
    @api.ondelete(at_uninstall=False)
    def _check_property_deletion(self):
        for record in self:
            if record.state not in ('new', 'cancelled'):
                raise UserError("You can only delete properties that are in 'New' or 'Cancelled' state.")

    #the order of the recordset
    _order = "id desc"
