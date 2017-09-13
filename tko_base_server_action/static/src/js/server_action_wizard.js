odoo.define('tko_base_server_action.server_action_wizard', function(require) {
    "use strict";

    var core = require('web.core');
    var FormView = require('web.FormView');
    var Model = require("web.Model");
    var session = require('web.session');
    var data = require('web.data');
    var _t = core._t;

//    function launch_wizard(self, context) {
//            var call_obj = new Model('execute.server.action')
//            //open tree view for the model
//            openerp.webclient.action_manager.do_action({
//                name: "Execute Server Action",
//                views: [[false, 'form']],
//                target: 'new',
//                type: 'ir.actions.act_window',
//                view_type: 'form',
//                view_mode: 'form',
//                res_model: 'execute.server.action',
//                context: context,
//            });
//        }

    function launch_wizard(self, context) {
            //new Model(odoo_model).ca
            openerp.webclient.action_manager.do_action({
                views: [[false, 'form']],
                target: 'new',
                context: {'call_id': 1},
                type: 'ir.actions.act_window',
                view_type: 'form',
                view_mode: 'form',
                res_model: 'execute.server.action',

                res_id: false,
                flags: {'initial_mode': 'edit'},
                context: context,
            })
        };



    FormView.include({
        render_sidebar: function($node) {

            this._super.apply(this, arguments);
            var wizard_label = 'Execute Server Action In Mass';
//            if (this.model === 'account.invoice'){
//				wizard_label = 'Invoice Duplication'
//			}
            if (this.sidebar) {
                this.sidebar.add_items('other', _.compact([
                    this.is_action_enabled('delete') && {
                        label: _t(wizard_label),
                        callback: this.on_click_execute_server_action
                    },
                ]));

            }
        },

        on_click_execute_server_action: function (item) {
//            var view = this.getParent()
//            launch_wizard(this, view, 'emails', false);
            var view = this.getParent()
            this.dataset.context.params.active_id = this.datarecord.id;
            this.dataset.context.params.active_model = this.dataset.model;
            launch_wizard(this, this.dataset.context.params || {'active_id' : this.datarecord.id, 'active_model' : this.dataset.model});
        },
    });

});