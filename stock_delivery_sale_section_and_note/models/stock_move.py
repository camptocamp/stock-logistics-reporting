# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import datetime

from odoo import fields, models


class StockMove(models.Model):
    _name = "stock.move"
    _inherit = ["stock.move", "display.line.mixin"]

    sequence = fields.Integer(related="sale_line_id.sequence", store=True)
    previous_line_id = fields.Many2one(related="sale_line_id.previous_line_id")
    next_line_id = fields.Many2one(related="sale_line_id.next_line_id")

    def prepare_section_or_note_values(self, order_line):
        """This method is intended to be used to `convert` a display line to
        the current model

        It is mainly used for display lines injection to delivery reports
        """
        self.ensure_one()
        assert order_line.is_section_or_note()
        related_order_line = self.sale_line_id
        return {
            "sequence": order_line.sequence,
            "display_type": order_line.display_type,
            "name": order_line.name,
            "date": datetime.datetime.now(),
            "company_id": order_line.company_id.id,
            "product_id": related_order_line.product_id.id,
            "product_uom_qty": 0,
            "product_uom": related_order_line.product_uom.id,
            "location_id": False,
            "location_dest_id": False,
            "procure_method": False,
        }
