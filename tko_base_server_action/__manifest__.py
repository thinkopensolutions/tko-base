# © 2017 TKO <http://tko.tko-br.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'TKO Server Action',
    'summary': '',
    'description': 'Allows to add user defined filters in server action. \n'
                   'Execute multiple server action in mass \n'
                   'Value mapping in server action lines \n',
    'author': 'TKO',
    'category': 'Extra Tools',
    'license': 'AGPL-3',
    'website': 'http://tko.tko-br.com',
    'version': '10.0.0.0.0',
    'application': False,
    'installable': True,
    'auto_install': False,
    'depends': [
                'base',
    ],
    'external_dependencies': {
                                'python': [],
                                'bin': [],
                                },
    'init_xml': [],
    'update_xml': [],
    'css': [],
    'demo_xml': [],
    'data': [
            'security/ir.model.access.csv',
             'views/ir_server_actions_view.xml',
             'static/src/xml/server_action_wizard_view.xml',
        'wizard/server_action_view.xml',
    ],
}
