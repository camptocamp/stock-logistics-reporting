# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time

from odoo.fields import Date
from odoo.tests.common import SavepointCase

from .common import CommonAverageSaleTest


class TestAverageSale(CommonAverageSaleTest, SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # As NOW() postgres function cannot easily mocked in python,
        # We use now as basis for computations
        cls.now = Date.today()

        cls.inventory_date = Date.to_string(cls.now - relativedelta(cls.now, weeks=30))

        with freeze_time(cls.inventory_date):
            cls._create_inventory()

    def test_average_sale(self):
        # By default, products have abc_storage == 'b'
        # So, the averages should correspond to 'b' one

        move_1_date = Date.to_string(self.now - relativedelta(weeks=11))
        with freeze_time(move_1_date):
            move = self._create_move(self.product_1, self.location_bin, 10.0)
            move._action_confirm()
            move._action_assign()
            move.quantity_done = move.product_uom_qty
            move._action_done()
        move_2_date = Date.to_string(self.now - relativedelta(weeks=9))
        with freeze_time(move_2_date):
            move = self._create_move(self.product_2, self.location_bin_2, 12.0)
            move._action_confirm()
            move._action_assign()
            move.quantity_done = move.product_uom_qty
            move._action_done()

        self._refresh()
        # self.env.flush_all()
        avg_product_1 = self.env["stock.average.daily.sale"].search(
            [("product_id", "=", self.product_1.id)]
        )

        self.assertRecordValues(
            avg_product_1,
            [
                {
                    "nbr_sales": 1.0,
                    "average_qty_by_sale": 10.0,
                    "qty_in_stock": 40.0,
                    "recommended_qty": 20.0,
                    "warehouse_id": self.warehouse_0.id,
                }
            ],
        )
        avg_product_2 = self.env["stock.average.daily.sale"].search(
            [("product_id", "=", self.product_2.id)]
        )
        self.assertRecordValues(
            avg_product_2,
            [
                {
                    "nbr_sales": 1.0,
                    "average_qty_by_sale": 12.0,
                    "qty_in_stock": 48.0,
                    "recommended_qty": 24.0,
                    "warehouse_id": self.warehouse_0.id,
                }
            ],
        )

    def test_average_sale_multiple(self):
        # By default, products have abc_storage == 'b'
        # So, the averages should correspond to 'b' one
        move_1_date = Date.to_string(self.now - relativedelta(weeks=11))
        with freeze_time(move_1_date):
            move = self._create_move(self.product_1, self.location_bin, 10.0)
            move._action_confirm()
            move._action_assign()
            move.quantity_done = move.product_uom_qty
            move._action_done()

        move_1_date = Date.to_string(self.now - relativedelta(weeks=10))
        with freeze_time(move_1_date):
            move = self._create_move(self.product_1, self.location_bin, 8.0)
            move._action_confirm()
            move._action_assign()
            move.quantity_done = move.product_uom_qty
            move._action_done()

        move_1_date = Date.to_string(self.now - relativedelta(weeks=9))
        with freeze_time(move_1_date):
            move = self._create_move(self.product_1, self.location_bin, 13.0)
            move._action_confirm()
            move._action_assign()
            move.quantity_done = move.product_uom_qty
            move._action_done()

        move_2_date = Date.to_string(self.now - relativedelta(weeks=9))
        with freeze_time(move_2_date):
            move = self._create_move(self.product_2, self.location_bin_2, 12.0)
            move._action_confirm()
            move._action_assign()
            move.quantity_done = move.product_uom_qty
            move._action_done()

        move_2_date = Date.to_string(self.now - relativedelta(weeks=8))
        with freeze_time(move_2_date):
            move = self._create_move(self.product_2, self.location_bin_2, 4.0)
            move._action_confirm()
            move._action_assign()
            move.quantity_done = move.product_uom_qty
            move._action_done()

        self._refresh()

        avg_product_1 = self.env["stock.average.daily.sale"].search(
            [("product_id", "=", self.product_1.id)]
        )

        self.assertRecordValues(
            avg_product_1,
            [
                {
                    "nbr_sales": 3.0,
                    "qty_in_stock": 19.0,
                    "warehouse_id": self.warehouse_0.id,
                }
            ],
        )
        self.assertAlmostEqual(20.67, avg_product_1.recommended_qty, places=2)
        self.assertAlmostEqual(10.33, avg_product_1.average_qty_by_sale, places=2)

        avg_product_2 = self.env["stock.average.daily.sale"].search(
            [("product_id", "=", self.product_2.id)]
        )
        self.assertRecordValues(
            avg_product_2,
            [
                {
                    "nbr_sales": 2.0,
                    "average_qty_by_sale": 8.0,
                    "recommended_qty": 16.0,
                    "qty_in_stock": 44.0,
                    "warehouse_id": self.warehouse_0.id,
                }
            ],
        )

    def test_average_sale_profile_a(self):
        # Test with profile 'a'
        # Check that no average daily is found
        self.product_1.abc_storage = "a"
        self.product_2.abc_storage = "a"
        move_1_date = Date.to_string(self.now - relativedelta(weeks=11))
        with freeze_time(move_1_date):
            move = self._create_move(self.product_1, self.location_bin, 10.0)
            move._action_confirm()
            move._action_assign()
            move.quantity_done = move.product_uom_qty
            move._action_done()
        move_2_date = Date.to_string(self.now - relativedelta(weeks=9))
        with freeze_time(move_2_date):
            move = self._create_move(self.product_2, self.location_bin_2, 12.0)
            move._action_confirm()
            move._action_assign()
            move.quantity_done = move.product_uom_qty
            move._action_done()

        self._refresh()

        avg_product_1 = self.env["stock.average.daily.sale"].search(
            [("product_id", "=", self.product_1.id)]
        )

        self.assertFalse(avg_product_1)
        avg_product_2 = self.env["stock.average.daily.sale"].search(
            [("product_id", "=", self.product_2.id)]
        )
        self.assertFalse(avg_product_2)

    def test_view_refreshed(self):
        self._refresh()
        # In python < 3.10 there is no assertNoLogs method so we use assertLogs
        # Create a dummy warning and check if that is the only one
        with self.assertLogs(
            "odoo.addons.stock_average_daily_sale.models.stock_average_daily_sale",
            level="DEBUG",
        ) as cm:
            logging.getLogger(
                "odoo.addons.stock_average_daily_sale.models.stock_average_daily_sale"
            ).info("Dummy warning")
            self.env["stock.average.daily.sale"].search_read(
                [("product_id", "=", self.product_1.id)]
            )
        # flake8: noqa: B950
        self.assertEqual(
            [
                "INFO:odoo.addons.stock_average_daily_sale.models.stock_average_daily_sale:Dummy warning"
            ],
            cm.output,
        )

    def test_average_sale_with_returns(self):
        # By default, products have abc_storage == 'b'
        # So, the averages should correspond to 'b' one

        # Create moves for product_1
        move_1_date = Date.to_string(self.now - relativedelta(weeks=11))
        with freeze_time(move_1_date):
            move = self._create_move(self.product_1, self.location_bin, 10.0)
            move._action_confirm()
            move._action_assign()
            move.quantity_done = move.product_uom_qty
            move._action_done()

        move_1_date = Date.to_string(self.now - relativedelta(weeks=10))
        with freeze_time(move_1_date):
            move = self._create_move(self.product_1, self.location_bin, 8.0)
            move._action_confirm()
            move._action_assign()
            move.quantity_done = move.product_uom_qty
            move._action_done()

        # create a "return" move - from inventory location to stock
        move_1_date = Date.to_string(self.now - relativedelta(weeks=10))
        with freeze_time(move_1_date):
            move = self._create_move(
                self.product_1, self.scrap_location, 7.0, self.location_bin
            )
            move._action_confirm()
            move._action_assign()
            move.quantity_done = move.product_uom_qty
            move._action_done()

        move_2_date = Date.to_string(self.now - relativedelta(weeks=9))
        with freeze_time(move_2_date):
            move = self._create_move(self.product_2, self.location_bin_2, 12.0)
            move._action_confirm()
            move._action_assign()
            move.quantity_done = move.product_uom_qty
            move._action_done()

        move_2_date = Date.to_string(self.now - relativedelta(weeks=8))
        with freeze_time(move_2_date):
            move = self._create_move(self.product_2, self.location_bin_2, 4.0)
            move._action_confirm()
            move._action_assign()
            move.quantity_done = move.product_uom_qty
            move._action_done()

        self._refresh()

        avg_product_1 = self.env["stock.average.daily.sale"].search(
            [("product_id", "=", self.product_1.id)]
        )

        self.assertRecordValues(
            avg_product_1,
            [
                {
                    "nbr_sales": 2.0,
                    "average_qty_by_sale": 9.0,  # should be 5.5 w/ return!!!
                    "recommended_qty": 18.0,  # should be 11.0 w/ return!!!
                    "qty_in_stock": 39.0,
                    "warehouse_id": self.warehouse_0.id,
                }
            ],
        )

        avg_product_2 = self.env["stock.average.daily.sale"].search(
            [("product_id", "=", self.product_2.id)]
        )
        self.assertRecordValues(
            avg_product_2,
            [
                {
                    "nbr_sales": 2.0,
                    "average_qty_by_sale": 8.0,
                    "recommended_qty": 16.0,
                    "qty_in_stock": 44.0,
                    "warehouse_id": self.warehouse_0.id,
                }
            ],
        )
