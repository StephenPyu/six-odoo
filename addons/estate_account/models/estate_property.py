from odoo import models
# import sys

class EstateProperty(models.Model):
    _inherit = "estate.property"

    def action_sold_estate_property(self):
        """Override the action_sold method and return the super call."""
        print("EstateProperty action_sold_estate_property method called!")
        # sys.stdout.flush()
        result = super().action_sold_estate_property()

        # Ensure there is a buyer before creating an invoice
        if not self.buyer_id:
            print("No buyer found for the property.")
            return

            # Define invoice lines
        invoice_lines = [
            # Commission fee (6% of the selling price)
            (0, 0, {
                'name': "Selling Commission (6%)",
                'quantity': 1,
                'price_unit': self.selling_price * 0.06,
            }),
            # Administrative fees (Fixed 100.00)
            (0, 0, {
                'name': "Administrative Fees",
                'quantity': 1,
                'price_unit': 100.00,
            }),
        ]

        # Create the invoice (account.move)
        invoice_vals = {
            'partner_id': self.buyer_id.id,  # Buyer of the property
            'move_type': 'out_invoice',  # Customer Invoice
            'invoice_line_ids': invoice_lines,  # Add invoice lines
        }
        invoice = self.env['account.move'].create(invoice_vals)

        print(f"Invoice Created: {invoice.id}")  # Debugging print

        return result