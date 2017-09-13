# -*- encoding: utf-8 -*-

import logging
from odoo import fields, api, models
from odoo.tools.safe_eval import safe_eval
_logger = logging.getLogger(__name__)


class ExecuteServerAction(models.TransientModel):
    _name = 'execute.server.action'

    filter_id = fields.Many2one('ir.filters','Filter')
    server_action_id = fields.Many2one('ir.actions.server','Server Action')
    model_id = fields.Many2one('ir.model','Model')
    model =  fields.Char('Model')

    @api.model
    def default_get(self, fields):
        res = super(ExecuteServerAction, self).default_get(fields)
        active_model = self._context.get('active_model',False)
        if active_model:
            res['model'] = active_model
            model = self.env['ir.model'].search([('model','=',active_model)], limit=1)
            if len(model):
                res['model_id'] = model.id
        return res


    @api.multi
    def execute_server_action(self):
        context = self.env.context
        new_context = context.copy()
        model = context.get('active_model')
        if self.filter_id and not self.filter_id.domain:
            raise Warning('Domain not set in selected filter')
        if self.filter_id and self.filter_id.domain:
            domain = safe_eval(self.filter_id.domain)
            if model:
                records = self.env[model].search(domain)
                new_context['active_ids'] = records.ids
                self = self.with_context(new_context)
        self.server_action_id.run()
        return True

