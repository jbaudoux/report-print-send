# Copyright 2022 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PrintingAuto(models.Model):
    _inherit = "printing.auto"

    picking_type_id = fields.Many2one("stock.picking.type", required=True)
