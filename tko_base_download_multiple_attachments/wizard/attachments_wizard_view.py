import ntpath
import os
import shutil
import tarfile
from random import randint

from odoo.exceptions import ValidationError, UserError
from odoo import api, fields, models, _


class download_attachments(models.TransientModel):
    _name = 'download.attachments'

    attachment = fields.Binary('Attachement', readonly=True)
    filename = fields.Char('File Name')
    active_model = fields.Char('Active Model')
    active_id = fields.Char('Active ID')
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')

    @api.model
    def default_get(self, fields):
        active_model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        if active_id and active_model:
            try:
                fname = self.env[active_model].browse(active_id).name
            except ValueError:
                pass
            if not fname:
                fname = 'odoo'
        res = super(download_attachments, self).default_get(fields)
        return res

    # @api.multi
    # def download_wizard(self):
    #     # wizard_data = self.browse(cr, uid, ids, context)[0]
    #     model, res_id = self.env['ir.model.data'].get_object_reference('tko_base_knowledge_download_all_attachments','download_attachments_wizard_actoin')
    #     action = self.pool[model].read([res_id])[0]
    #     action['res_id'] = ids[0]
    #     action.pop('context', '')
    #     return action
  
    @api.multi
    def download_attachments(self):
        cache_buster = randint(10000000000, 90000000000)
        config_obj = self.env['ir.config_parameter']
        attachment_obj = self.env['ir.attachment']
        
        active_model = self._context.get('active_model')
        active_ids = self._context.get('active_ids')
        attachment_ids = active_ids
        ids = self._ids
        filestore_path = os.path.join(attachment_obj._filestore(), '')
        attachment_dir = filestore_path + 'attachments'
        # create directory and remove its content
        if not os.path.exists(attachment_dir):
            os.makedirs(attachment_dir)
        else:
            shutil.rmtree(attachment_dir)
            os.makedirs(attachment_dir)
        file_name = 'files'
        if isinstance(ids, int):
            ids = [ids]
        wzrd_obj = self
        config_ids = config_obj.search([('key', '=', 'web.base.url')])
        if len(config_ids):
            value = config_ids[0].value
            active_model = 'ir.attachment'  # wzrd_obj.active_model
            active_id = wzrd_obj.id
            # tar_dir = attachment_dir + '/' + file_name
            tar_dir = os.path.join(attachment_dir, file_name)
            tFile = tarfile.open(tar_dir, 'w:gz')
            if value and active_id and active_model:
                # change working directory otherwise file is tared with all its parent directories
                original_dir = os.getcwd()

                if not attachment_ids:
                    raise UserError(_("No attachment to download"))

                for attachment in attachment_obj.browse(attachment_ids):
                    # to get full path of file
                    full_path = attachment_obj._full_path(attachment.store_fname)
                    attachment_name = attachment.name
                    try:
                        attachment_name = attachment_name.replace('/', '_')
                    except:
                        pass
                    new_file = os.path.join(attachment_dir, attachment_name)
                    # copying in a new directory with a new name
                    # shutil.copyfile(full_path, new_file)
                    try:
                        shutil.copy2(full_path, new_file)
                    except:
                        raise UserError(_("Not Proper attachment to download"))
                    head, tail = ntpath.split(new_file)
                    # change working directory otherwise it tars all parent directory
                    os.chdir(head)
                    tFile.add(tail)
                tFile.close()
                os.chdir(original_dir)
                values = {
                            'name': file_name + '.tar.gz',
                            'datas_fname': file_name + '.tar.gz',
                            'res_model': 'download.attachments',
                            'res_id': ids[0],
                            'res_name': 'test....',
                            'type': 'binary',
                            'store_fname': 'attachments/files',
                        }
                attachment_id = self.env['ir.attachment'].create(values)
                url = "%s/web/content/%s?download=true" %(value, attachment_id.id)
                return {
                    'type': 'ir.actions.act_url',
                    'url': url,
                    'nodestroy': False,
                }

    # @api.multi
    # def get_attachment_ids(self):
    #     attachment_ids = []
    #     context = self._context
    #     for i in self._context.get('active_ids'):
    #         attachments = attachment_obj.search([('res_model','=',str(active_model)),('res_id','in',active_ids)])
    #     for attachment in attachments:
    #         attachment_ids.append(attachment.id)
    #     result = {}
    #     context = self._context
    #     attachment_model = self.env['ir.attachment']
    #     if 'context' in context.keys():
    #         if '__contexts' in context['context'].keys():
    #             if len(context['context']['__contexts']):
    #                 attach_dict = context['context']['__contexts'][0]
    #                 active_model = attach_dict['attach_res_model']
    #                 active_id = attach_dict['attach_res_id']
    #                 attachment_ids = attachment_model.search([('res_model', '=', active_model),
    #                                                                    ('res_id', '=', active_id)])
    #                 file_size = 0
    #                 for attachments in attachmen25t_model.browse(attachment_ids):
    #                     file_size = file_size + attachments.file_size
    #                 # check attachment size in MB
    #                 file_size = file_size / 1048576
    #                 if file_size > 25:
    #                     raise UserError(_("Attachments size exceeds the limit (25MB), please remove some."))
    #             result.update({'active_model': active_model, 'active_id': active_id})
    #     result.update({'attachment_ids': attachment_ids})
    #     return result

