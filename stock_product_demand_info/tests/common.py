# Copyright 2026 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests import TransactionCase

from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT


class StockProductDemandInfoCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        cls.today = fields.Date.today()
        cls.env["product.demand.period"].search([]).active = False
        cls.period_7d = cls.env.ref("stock_product_demand_info.period_last_7_days")
        cls.period_last_month = cls.env.ref(
            "stock_product_demand_info.period_last_month"
        )
        cls.period_last_30_days = cls.env.ref(
            "stock_product_demand_info.period_last_30_days"
        )
        cls.period_last_year = cls.env.ref("stock_product_demand_info.period_last_year")
        cls.period_same_month_last_year = cls.env.ref(
            "stock_product_demand_info.period_same_month_last_year"
        )
        cls.period_next_month_last_year = cls.env.ref(
            "stock_product_demand_info.period_next_month_last_year"
        )
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product Demand",
                "type": "consu",
                "is_storable": True,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
            }
        )
        cls.orderpoint = cls.env["stock.warehouse.orderpoint"].create(
            {
                "product_id": cls.product.id,
                "warehouse_id": cls.warehouse.id,
                "product_min_qty": 0,
                "product_max_qty": 100,
            }
        )
        # Product template with two variants (for demand template-sum tests)
        cls.attr_size = cls.env["product.attribute"].create({"name": "Size"})
        cls.attr_value_s = cls.env["product.attribute.value"].create(
            {"name": "S", "attribute_id": cls.attr_size.id}
        )
        cls.attr_value_m = cls.env["product.attribute.value"].create(
            {"name": "M", "attribute_id": cls.attr_size.id}
        )
        cls.template_with_variants = cls.env["product.template"].create(
            {
                "name": "Product With Variants",
                "type": "consu",
                "is_storable": True,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": cls.attr_size.id,
                            "value_ids": [
                                (6, 0, [cls.attr_value_s.id, cls.attr_value_m.id])
                            ],
                        },
                    )
                ],
            }
        )
        cls.variant_s, cls.variant_m = cls.template_with_variants.product_variant_ids

    @classmethod
    def _create_outgoing_move(cls, product, date, qty, warehouse=None):
        """Create a done outgoing move (warehouse -> customer) for demand."""
        if warehouse is None:
            warehouse = cls.warehouse
        return cls.env["stock.move"].create(
            {
                "product_id": product.id,
                "product_uom_qty": qty,
                "date": fields.Datetime.to_datetime(date),
                "location_id": warehouse.lot_stock_id.id,
                "location_dest_id": cls.customer_location.id,
                "company_id": warehouse.company_id.id,
                "state": "done",
                "quantity": qty,
            }
        )
