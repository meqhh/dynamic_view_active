from odoo import models, fields, api, SUPERUSER_ID

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def _valid_field_parameter(self, field, name):
        return (
            name in ('view_metadata', 'menu_metadata')
            or field.type == 'boolean' and name in ('view_metadata', 'menu_metadata')
            or super()._valid_field_parameter(field, name)
        )

    def _register_hook(self):
        env = self.env
        icp = env['ir.config_parameter'].sudo()
        for field in self._fields.values():
            if (
                field.type == 'boolean'
                and (
                    getattr(field, 'config_parameter', False)
                    or getattr(field, 'menu_metadata', False)
                )
            ):
                existing = icp.get_param(
                    field.config_parameter,
                    default=None
                )

                if existing is None:
                    icp.set_param(
                        field.config_parameter,
                        'True'
                    )

    @api.model
    def get_values(self):
        res = super().get_values()
        icp = self.env['ir.config_parameter'].sudo()
        for field_name, field in self._fields.items():
            if not isinstance(field, fields.Boolean):
                continue
            if (
                hasattr(field, 'view_metadata') and field.view_metadata
                or hasattr(field, 'menu_metadata') and field.menu_metadata
                ):
                conf_param = icp.get_param(
                    field.config_parameter, 
                    default=True
                )
                res.update({
                    field_name: conf_param == 'True'
                })
        return res

    def set_values(self):
        res = super().set_values()
        for field_name, field in self._fields.items():
            if not isinstance(field, fields.Boolean):
                continue
            if hasattr(field, 'view_metadata') and field.view_metadata:
                self._set_view_active(self[field_name], field)
            if hasattr(field, 'menu_metadata') and field.menu_metadata:
                self._set_menuitem_active(self[field_name], field)

        return res

    def _set_view_active(self, value, field):
        if field.view_metadata:
            if isinstance(field.view_metadata, str):
                view_obj = self.env.ref(field.view_metadata, raise_if_not_found=False)
                if view_obj and view_obj._name == 'ir.ui.view':
                    view_obj.active = value
            else:
                ir_ui_view = self.env['ir.ui.view']
                for xmlid in field.view_metadata:
                    view = self.env.ref(xmlid, raise_if_not_found=False)

                    if view and view._name == 'ir.ui.view':
                        ir_ui_view |= view
                ir_ui_view.write({
                    'active': value
                })
        return True

    def _set_menuitem_active(self, value, field):
        if field.menu_metadata:
            if isinstance(field.menu_metadata, str):
                menu_item = self.env.ref(field.menu_metadata, raise_if_not_found=False)
                if menu_item and menu_item._name == 'ir.ui.menu':
                    menu_item.active = value
            else:
                ir_ui_menu = self.env['ir.ui.menu']
                for xmlid in field.menu_metadata:
                    menuitem = self.env.ref(xmlid, raise_if_not_found=False)

                    if menuitem and menuitem._name == 'ir.ui.menu':
                        ir_ui_menu |= menuitem
                ir_ui_menu.write({
                    'active': value
                })
        return True
