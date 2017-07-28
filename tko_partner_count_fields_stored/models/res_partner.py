# -*- coding: utf-8 -*-
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2017 ThinkOpen Solutions (<https://tkobr.com>).
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    mail_message_ids = fields.One2many('mail.message', 'res_id', string='Messages')
    mails_to = fields.Integer(compute="_compute_mails_to", stored=True)
    mails_from = fields.Integer(compute="_compute_mails_from", stored=True)

    @api.multi
    @api.depends('mail_message_ids')
    def _compute_mails_to(self):
        return super(ResPartner, self)._compute_mails_to()

    @api.multi
    @api.depends('mail_message_ids')
    def _compute_mails_from(self):
        return super(ResPartner, self)._compute_mails_from()
