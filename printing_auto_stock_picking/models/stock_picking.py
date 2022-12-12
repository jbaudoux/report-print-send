# Copyright 2022 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import _, fields, models

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = "stock.picking"

    printing_auto_error = fields.Boolean(string="Printing error")

    def _action_done(self):
        result = super()._action_done()
        self.send_documents_to_printer()
        return result

    def send_documents_to_printer(self):
        """Print some report or attachment directly to the corresponding printer."""
        for picking in self:
            picking.printing_auto_error = False
            if picking.state != "done":
                continue
            for auto in picking.picking_type_id.auto_printing_ids:
                try:
                    with self.env.cr.savepoint():
                        printer, count = auto.do_print(picking)
                        if count:
                            self.message_post(
                                body=_(
                                    "{name}: {count} document(s) sent to printer {printer}"
                                ).format(name=auto, count=count, printer=printer)
                            )
                except Exception:
                    _logger.exception(
                        "An error occurred while printing '%s' for record %s.",
                        auto,
                        picking,
                    )
                    picking.printing_auto_error = True
