from djadmin.sites import site
from crm import models
from djadmin.djadmin_base import BaseDjAdmin

print('crm models...')

# 注册model
class CustomerInfoAdmin(BaseDjAdmin):
    list_display = ['name', 'contact_type', 'contact', 'consultant', 'consult_content', 'status', 'created_time']
    list_filter = ['source', 'consultant', 'status', 'created_time' ]
    search_fields = ['contact', 'consultant__name']
    readonly_fields = ['contact', 'status']
    filter_horizontal = ['consult_courses']
    actions = ['change_status']

    def change_status(self, request, queryset):
        queryset.update(status=3)  # 批量设置可装状态为“结业”

    change_status.short_description = '客户状态修改为结业'  # 设置后台可见描述

site.register(models.CustomerInfo, CustomerInfoAdmin)

site.register(models.Role)
site.register(models.Menu)
site.register(models.UserProfile)
# site.register(models.Class)
site.register(models.CourseRecord)