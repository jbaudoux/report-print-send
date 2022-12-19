# Copyright (C) 2022 Raumschmiede GmbH - Christopher Hansen (<https://www.raumschmiede.de>)
# Copyright 2022 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "base_report_to_label_printer",
    "version": "14.0.1.0.0",
    "category": "Generic Modules/Base",
    "author": "Raumschmiede GmbH - Christopher Hansen,"
    " Michael Tietz (MT Software) <mtietz@mt-software.de>,"
    " Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/report-print-send",
    "license": "AGPL-3",
    "depends": ["base_report_to_printer"],
    "data": [
        "views/res_users.xml",
        "views/ir_actions_report.xml",
    ],
}
