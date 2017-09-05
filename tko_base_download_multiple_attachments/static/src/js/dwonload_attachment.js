openerp.tko_base_knowledge_download_all_attachments = function(session) {
    var _t = session.web._t;
    var has_action_id = false;

    function launch_wizard(self, view, user_type, invite) {
        var action = view.getParent().action;
        var Download = new session.web.DataSet(self, 'download.attachments', view.dataset.get_context());
        var domain = new session.web.CompoundDomain(view.dataset.domain);
         
        Download.call('get_attachment_ids', [[view.datarecord.id], {context: new session.web.CompoundContext({'attach_res_id': view.datarecord.id, 'attach_res_model' : action.res_model})}]).done(function (attachments) {
        if (view.fields_view.type == 'form') {
            domain = new session.web.CompoundDomain(domain, [['id', '=', view.datarecord.id]]);
        }
        if (view.fields_view.type == 'form') rec_name = view.datarecord.name;
        else rec_name = '';
        session.web.pyeval.eval_domains_and_contexts({
            domains: [domain],
            contexts: [Download.get_context()]
        }).done(function (result) {
            Download.create({
                filename: action.name,
                active_model : attachments['active_model'],
                active_id : attachments['active_id'],
                attachment_ids: [[6, 0, attachments['attachment_ids']]],
            }).done(function (download_id) {
                    var step1 = Download.call('download_wizard', [
                        [download_id], Download.get_context()]).done(function (result) {
                        var action = result;
                        self.do_action(action);
                    });
             });
           
          });
        });
    }


    /* Extend the Sidebar to add Send Mail  links in the 'More' menu */
    session.web.Sidebar = session.web.Sidebar.extend({
	
        start: function () {
            var self = this;
            this._super(this);
			var view = this.getParent()
			//add attachment only in form view
			if (view.fields_view.type == 'form')
				{
		            self.add_items('other', [
			            {  
			             label: _t('Download Attachments'),
				        callback: self.on_click_download,
				        classname: 'oe_share' },
				        
			            ]);
				}
       		 },

       
        on_click_download: function (item) {
            var view = this.getParent()
            launch_wizard(this, view, 'emails', false);
        },


    });


};
