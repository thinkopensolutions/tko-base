# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    ThinkOpen Solutions Brasil
#    Copyright (C) Thinkopen Solutions <http://www.tkobr.com>.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api, _
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval
import time
import logging
from odoo.exceptions import Warning

_logger = logging.getLogger(__name__)


class IrActionsServer(models.Model):
    _inherit = 'ir.actions.server'

    filter_id = fields.Many2one('ir.filters', 'Filter',
                                help='If the domain is set, Server action will run only if domain is satisfied')
    model = fields.Char(related='model_id.model', string='Model')
    validate_filter_obj = fields.Boolean("Filter Object", compute='validate_filter_object')
    field_id = fields.Many2one('ir.model.fields', 'Fields')

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {}, name=_("%s (copy)") % (self.name))
        return super(IrActionsServer, self).copy(default)

    @api.model
    def _get_states(self):
        res = super(IrActionsServer, self)._get_states()
        # remove multi tuple from the list
        res.remove([tup for tup in res if tup[0] == 'multi'][0])
        res.insert(len(res), ('multi', 'Execute several actions one by one'))
        res.insert(len(res), ('multi_mass', 'Execute several actions in mass'))
        return res

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Name must be unique!"),
    ]

    @api.model
    def run_action_multi_mass_multi(self, action, eval_context=None):
        res = False
        for act in action.child_ids:
            result = act.run()
            if result:
                res = result
        return res


    @api.constrains('model_id', 'field_id')
    def validate_field(self):
        """
        Checks if a class has the selected field
        """
        for record in self:
            found = False
            if record.field_id:
                for field in record.model_id.field_id:
                    if field.ttype == 'many2one' and field.name == record.field_id.name:
                        found = True
                        break
                if not found:
                    raise Warning(
                        u"Model %s has no field %s" % (record.model_id.name, record.field_id.field_description))
        return True

    # return True if object is same
    @api.one
    @api.depends('filter_id')
    def validate_filter_object(self):
        if not self.filter_id or (self.filter_id and self.model == self.filter_id.model_id):
            self.validate_filter_obj = True
        else:
            self.validate_filter_obj = False

    @api.model
    def _eval_context(self):
        """Returns a dictionary to use as evaluation context for
           ir.rule domains."""
        return {'user': self.env.user, 'time': time}

    # Method 2
    def validate_server_action(self):
        """
        Context must have active_id
        :return:
        """
        if not self.filter_id.domain:
            return True
        model_name = self.model_id.model
        eval_context = self._eval_context()
        active_id = self._context.get('active_id', False)
        if not self.validate_filter_obj and self.field_id:
            original_model = model_name
            model_name = self.field_id.relation
            field_name = self.field_id.name
            object = self.env[original_model].browse(active_id)
            record = getattr(object, field_name)

            if not record.id:
                _logger.error("Field %s not set, server action not executed" % self.field_id.field_description)
                return False
            active_id = record.id
        if active_id and model_name:
            domain = self.filter_id.domain
            rule = expression.normalize_domain(safe_eval(domain, eval_context))
            Query = self.env[model_name].sudo()._where_calc(rule, active_test=False)
            from_clause, where_clause, where_clause_params = Query.get_sql()
            where_str = where_clause and (" WHERE %s" % where_clause) or ''
            query_str = 'SELECT id FROM ' + from_clause + where_str
            self._cr.execute(query_str, where_clause_params)
            result = self._cr.fetchall()
            if active_id in [id[0] for id in result]:
                return True
        else:
            _logger.error("Server Action was called without 'active_id' not executed")
        return False

    # set records in eval context in case records aren't set
    # it happens calling server action from a one2many field
    # active_ids aren't set
    @api.model
    def _get_eval_context(self, action=None):
        res = super(IrActionsServer, self)._get_eval_context(action)
        if not res['records'] and res['record']:
            res['records'] = res['record']
        return res

    @api.multi
    def tko_run(self, current_active_id):
        """ Runs the server action. For each server action, the condition is
        checked. Note that a void (``False``) condition is considered as always
        valid. If it is verified, the run_action_<STATE> method is called. This
        allows easy overriding of the server actions.

        :param dict context: context should contain following keys

                             - active_id: id of the current object (single mode)
                             - active_model: current model that should equal the action's model

                             The following keys are optional:

                             - active_ids: ids of the current records (mass mode). If active_ids
                               and active_id are present, active_ids is given precedence.

        :return: an action_id to be executed, or False is finished correctly without
                 return action
        """
        res = False
        for action in self:
            eval_context = self._get_eval_context(action)
            model = eval_context.get('model')
            active_ids = eval_context.get('records').ids
            condition = action.condition
            if condition is False:
                # Void (aka False) conditions are considered as True
                condition = True
            if hasattr(self, 'run_action_%s_multi' % action.state):
                expr = safe_eval(str(condition), eval_context)
                if not expr:
                    continue
                # call the multi method
                run_self = self.with_context(eval_context['context'])

                _logger.info("Executing server action %s with method run_action_%s_multi for model %s with IDs %s"
                             % (action.name, action.state, model, active_ids))
                func = getattr(run_self, 'run_action_%s_multi' % action.state)
                res = func(action, eval_context=eval_context)

            elif hasattr(self, 'run_action_%s' % action.state):
                active_id = self._context.get('active_id',False)
                run_self = self.with_context(active_ids=[active_id], active_id=active_id)
                if action.state == 'multi':
                    run_self = self.with_context(active_ids=[current_active_id], active_id=current_active_id)
                eval_context["context"] = run_self._context
                expr = safe_eval(str(condition), eval_context)
                if not expr:
                    continue
                _logger.info("Executing server action %s with method run_action_%s for model %s with IDs %s"
                             % (action.name, action.state, model, [current_active_id]))
                # call the single method related to the action: run_action_<STATE>
                func = getattr(run_self, 'run_action_%s' % action.state)
                new_context = dict(self._context)
                new_context.update({'current_active_id' : current_active_id, 'active_id' : current_active_id})
                if not new_context.get('current_active_model',False):
                    new_context.update({'current_active_model' : new_context.get('active_model')})

                action = action.with_context(new_context)
                res = func(action, eval_context=eval_context)
        return res


    # if filter is set, execute server action only if condition is satisfied
    @api.multi
    def run(self):
        res = False
        context = self._context
        current_active_id = context.get('current_active_id',False)


        if current_active_id:
            # this is required in case server action on another model is executed
            # happens from automated actions
            current_active_model = context.get('current_active_model', False)
            if context.get('active_model') != current_active_model and current_active_id:
                current_active_id = context.get('active_id')
            for action in self:
                eval_context = action._get_eval_context(action)
                record = eval_context.get('record')
                if action.filter_id.domain:
                    result = action.validate_server_action()
                    if result:
                        res = action.tko_run(current_active_id)
                    else:
                        _logger.info(
                            "Skipped execution of server action %s for %s with filter, condition %s wasn't satisfied"
                            % (action.name, record, action.filter_id.domain))
                else:
                    res = action.tko_run(current_active_id)
            return res
        active_ids = self._context.get('active_ids',[])
        active_id = self._context.get('active_id',False)
        if not len(active_ids) and active_id:
            active_ids = [active_id]
        for action in self:
            for active_id in active_ids:
                eval_context = self._get_eval_context(action)
                record = eval_context.get('record')
                if action.filter_id.domain:
                    result = action.validate_server_action()
                    if result:
                        res = action.tko_run(active_id)
                    else:
                        _logger.info("Skipped execution of server action %s for %s with filter, condition %s wasn't satisfied"
                                     %(action.name, record, action.filter_id.domain))
                else:
                    res = action.tko_run(active_id)
        return res

class DynamicSelection(models.Model):
    _name = 'dynamic.selection'

    name = fields.Char('Name')
    current_active_id = fields.Integer("Record ID")

class IrServerObjectLines(models.Model):
    _inherit = 'ir.server.object.lines'

    dynamic_selection_id = fields.Many2one('dynamic.selection', string='Dynamic Selection')

    @api.onchange('col1')
    def onchange_col1(self):
        dynamic_obj = self.env['dynamic.selection']

        col1 = self.col1
        value = self.value
        if self.col1:
            if self.col1.relation:
                records = self.env[self.col1.relation].search([])
            if self.col1.ttype in ['many2one', 'many2many']:
                dynamic_obj.search([]).unlink()
                for record in records:
                    dynamic_obj.create({'name' : record.name,
                                        'current_active_id': record.id})
        self.col1 = col1
        self.value = value


    @api.onchange('dynamic_selection_id')
    def onchange_dynamic_selection(self):
        if self.dynamic_selection_id:
            self.value = self.dynamic_selection_id.current_active_id


