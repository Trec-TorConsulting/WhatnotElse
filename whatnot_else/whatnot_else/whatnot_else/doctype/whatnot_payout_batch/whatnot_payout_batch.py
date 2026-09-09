import frappe
from frappe.model.document import Document

class WhatnotPayoutBatch(Document):
    def validate(self):
        if self.orders:
            calc_gross = sum(o.gross_amount or 0.0 for o in self.orders)
            calc_fees = sum(o.fee_amount or 0.0 for o in self.orders)
            calc_net = sum(o.net_amount or 0.0 for o in self.orders)
            if not self.gross_amount:
                self.gross_amount = calc_gross
            if not self.whatnot_fees:
                self.whatnot_fees = calc_fees
            if not self.net_deposit_amount:
                self.net_deposit_amount = calc_net
