# djadmin/djadmin_base.py

class BaseDjAdmin(object):
    def __init__(self):
        if 'delete_selected_objs' not in self.actions:  # 如果注册多个应用，不进行判断，就会创建多个删除
            self.actions.extend(self.default_actions)  # 创建实例进行初始化的时候，会将default_actions并到actions中

    list_display = []
    list_filter = []
    search_fields = []
    readonly_fields = []
    filter_horizontal = []
    list_per_page = 5
    actions = []

    default_actions = ['delete_selected_objs']

    def delete_selected_objs(self, request, queryset):
        import json
        from django.shortcuts import render
        print('跳转到删除函数')
        selected_ids = json.dumps([item.id for item in queryset])
        action = 'delete_selected_objs'
        return render(request, 'djadmin/table_delete_objs.html',
                      {
                          'admin_class': self,  # self就是admin_class
                          'action': action,
                          'objs': queryset,
                          'selected_ids': selected_ids
                      })