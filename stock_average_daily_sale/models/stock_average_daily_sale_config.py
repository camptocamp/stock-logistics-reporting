# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models

from odoo.addons.stock_storage_type_putaway_abc.models.stock_location import (
    ABC_SELECTION,
)


class StockAverageDailySaleConfig(models.Model):
    _name = "stock.average.daily.sale.config"
    _description = "Average daily sales computation parameters"
    check_company_auto = True

    abc_classification_level = fields.Selection(
        selection=ABC_SELECTION, required=True, default="b"
    )
    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
        required=True,
        default=lambda self: self.env.company,
    )
    standard_deviation_exclude_factor = fields.Float(required=True, digits=(2, 2))
    warehouse_id = fields.Many2one(
        string="Warehouse",
        comodel_name="stock.warehouse",
        required=True,
        ondelete="cascade",
        default=lambda self: self.env["stock.warehouse"].search(
            [("company_id", "=", self.env.company.id)], limit=1
        ),
    )
    exclude_weekends = fields.Boolean(
        help="Set to True only if you do not expect any orders/deliveries during "
        "the weekends. If set to True, stock moves done on weekends won't be "
        "taken into account to calculate the average daily usage",
    )
    period_name = fields.Selection(
        string="Period analyzed unit",
        selection=[
            ("year", "Years"),
            ("month", "Months"),
            ("week", "Weeks"),
            ("day", "Days"),
        ],
        required=True,
    )
    period_value = fields.Integer("Period analyzed value", required=True)
    number_days_qty_in_stock = fields.Integer(
        string="Number of days of quantities in stock", required=True, default=2
    )
    safety_factor = fields.Float(digits=(2, 2), required=True)

    _sql_constraints = [
        (
            "abc_classification_level_unique",
            "UNIQUE(abc_classification_level, warehouse_id)",
            _("Abc Classification Level must be unique per warehouse"),
        )
    ]
