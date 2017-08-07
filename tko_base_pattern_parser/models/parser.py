# -*- coding: utf-8 -*-
import re
import regex
from odoo import fields, api, models
import logging
_logger = logging.getLogger(__name__)

class PatternConfig(models.Model):
    _name = 'pattern.config'

    name = fields.Char(u'Pattern')
    pattern_type = fields.Selection([('fi', 'Fixed'), ('r', u'Regular Expression'), ('v', 'Variable')], default='r',
                                    required=True, string=u'Pattern Type')
    prefix = fields.Char(u'Prefix')
    suffix = fields.Char(u'Suffix')
    pattern = fields.Char(u'Pattern')


class PatternParserAgent(models.Model):
    _name = 'pattern.parser.agent'

    name = fields.Char(u'Name', required=True)
    pattern_id = fields.Many2one('pattern.config', u'Pattern', required=True)
    model_id = fields.Many2one('ir.model', u'Model', required=True)
    model_id_model = fields.Char(related='model_id.model', string=u'Model')
    feature_field_id = fields.Many2one('ir.model.fields', u'Feature Field', required=True)
    label_field_id = fields.Many2one('ir.model.fields', u'Label Field', required=True)
    server_action_id = fields.Many2one('ir.actions.server', u'Server Action')
    state = fields.Selection([('d', u'Draft'), ('p', 'Publish')], string=u'State', required=True, default='d')

    @api.multi
    def set_publish(self):
        self.write({'state': 'p'})

    @api.multi
    def set_draft(self):
        self.write({'state': 'd'})

    @api.multi
    def write(self, vals):
        res = super(PatternParserAgent, self).write(vals)
        for record in self:
            if len(self.server_action_id) and len(record.model_id):
                record.server_action_id.name = record.name
                record.server_action_id.model_id = record.model_id.id
                record.server_action_id.parser_agent_id = record.id
                if self.state in ('p'):
                    if not record.server_action_id.menu_ir_values_id:
                        record.server_action_id.create_action()
                else:
                    if record.server_action_id.menu_ir_values_id:
                        record.server_action_id.unlink_action()
        return res

    def _create_server_action(self):
        name = 'Parser: %s' % self.name
        server_action_obj = self.env['ir.actions.server']
        server_action_id = server_action_obj.create({'name': name,
                                                     'parser_agent_id': self.id,
                                                     'model_id': self.model_id.id,
                                                     'state': 'parser'})
        return server_action_id

    @api.onchange('model_id')
    def onchange_model_id(self):
        result = {'value': {}}
        if self.model_id:
            if not self.server_action_id:
                result['value']['server_action_id'] = self._create_server_action().id
        return result

    @api.one
    def _parse(self, records):
        _logger.info("Executing parser ==> %s ..." %self.name)
        pattern_type = self.pattern_id.pattern_type
        for record in records:
            # Read Text
            text = getattr(record, self.feature_field_id.name)
            # Parse text based on pattern
            if text:
                text = text.encode('utf-8')
                value = ''
                # If it pattern is regular expression
                pattern = self.pattern_id.pattern
                if pattern_type == 'r':
                    pattern = self.pattern_id.pattern.encode('utf-8')
                    match = regex.search(pattern, text)
                    if match:
                        value = match.group(0)
                if pattern_type == 'fi' or pattern_type == 'v':
                    prefix = self.pattern_id.prefix
                    suffix = self.pattern_id.suffix
                    start = text.find(prefix) + len(prefix)
                    if pattern_type == 'fi':
                        end = start + len(pattern)
                    else:
                        end = text.find(suffix)
                    if end != -1:
                        value = text[start:end]
                _logger.info("Result =====> %s"%value.decode('utf-8'))
                if value:
                    # Get record ID for Many2one and many2many fields
                    if self.label_field_id.ttype == 'many2one' or self.label_field_id.ttype == 'many2many':
                        relational_model = self.label_field_id.relation
                        rec_name = self.env[relational_model]._rec_name
                        res = self.env[relational_model].search([(rec_name, '=', value)], limit=1)
                        if not len(res):
                            res = self.env[relational_model].create({rec_name: value})
                        # write Many2one
                        if self.label_field_id.ttype == 'many2one':
                            setattr(record, self.label_field_id.name, res.id)
                        else:
                            # add record Many2many
                            setattr(record, self.label_field_id.name, [(4, res.id)])
                    else:
                        # Char and Text Fields
                        setattr(record, self.label_field_id.name, value)
            else:
                _logger.info("Skipping parser execution no text was found for record %s" %record)
        return True
