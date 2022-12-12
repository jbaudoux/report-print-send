# Copyright 2022 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "application": False,
    "author": "BCIM, Odoo Community Association (OCA)",
    "category": "Warehouse Management",
    "data": [
        "security/ir.model.access.csv",
        "views/stock_picking.xml",
        "views/stock_picking_type.xml",
    ],
    "demo_xml": [],
    "depends": [
        "stock",
        "printing_auto_base",
    ],
    "installable": True,
    "license": "AGPL-3",
    "name": "printing_auto_stock_picking",
    "version": "14.0.1.0.0",
    "website": "https://github.com/OCA/report-print-send",
}
