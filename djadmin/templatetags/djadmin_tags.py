from django.template import Library
from django.utils.safestring import mark_safe


register = Library()


# 显示模型表的中文名称
@register.simple_tag
def build_table_head_name(admin_class):
    th = ''
    if admin_class.list_display:
        for display_field in admin_class.list_display:
            # 获取列中的字段对象
            display_field_obj = admin_class.model._meta.get_field(display_field)
            # print(display_field_obj.verbose_name)
            tmp = "<th>{}</th>".format(display_field_obj.verbose_name)
            th += tmp
    else:
        th += "<th>{}</th>".format(admin_class.model._meta.verbose_name)  # 如果没有自定义注册，则表格标题就显示模型的别名verbose_name
    return mark_safe(th)


# 显示表数据
@register.simple_tag
def build_table_body(obj, admin_class):
    """
    生成一条记录的html元素
    :param obj: 一个模型查询集中的一个对象
    :param admin_class: 自定义注册的类
    :return: 得到这个对象要求显示的所有列
    """
    td = ''
    if admin_class.list_display:
        for index, display_field in enumerate(admin_class.list_display):  # 增加enumerate函数实现自动增加索引号
            # 获取列中的字段对象
            display_field_obj = admin_class.model._meta.get_field(display_field)
            # print(display_field_obj)
            # 字段对象choices方法，如果有choices，则使用get_xxx_display
            if display_field_obj.choices:
                # print('get_{}_display'.format(display_field))
                display_field_data = getattr(obj, 'get_{}_display'.format(display_field))()  # 使用get_xxx_display()需要带括号，调用函数执行结果，而不带括号得到的是函数对象
            else:
                # 根据属性名，获取对象的属性值，两个参数，一个对象obj，一个列名
                display_field_data = getattr(obj, display_field)  # 获取一个对象的属性值，例如<CustomerInfo: 小东>对象，得到他的name属性，值为小东
            tmp = "<td>{}</td>".format(display_field_data)
            if index == 0:  # 当列的索引号为0，也就是第一列时，增加a标签
                tmp = "<td><a href='{}/change'>{}</a></td>".format(obj.id, display_field_data)
            td += tmp
    else:
        # td += "<td>{}</td>".format(obj)  # 如果没有自定义注册字段，则显示对象的内容verbose_name
        td += "<td><a href='{}/change'>{}</a></td>".format(obj.id, obj)  # 没有list_display列表，就直接添加修改a标签
    return mark_safe(td)

@register.simple_tag
def build_option_filter(filter_field, admin_class):
    select = "<select name='{}'>".format(filter_field)
    # 获取列中的字段对象
    filter_field_obj = admin_class.model._meta.get_field(filter_field)
    try:
        for choice in filter_field_obj.get_choices():  # choice[0]为选项的值，choice[1]为选中的可见内容
            # 获取过滤字典中的值，并在模板中呈选中状态
            selected = ''
            if filter_field in admin_class.filter_conditions:
                # 如果当前值被选中
                if str(choice[0]) == admin_class.filter_conditions.get(filter_field):
                    selected = 'selected'

            option = "<option value='{}' {}>{}</option>".format(choice[0], selected, choice[1])
            select += option
    except AttributeError as e:
        # print(filter_field_obj.get_internal_type())  # 这儿得到的结果是：DateField
        if filter_field_obj.get_internal_type() in ('DateField', 'DateTimeField'):
            import datetime
            now_time = datetime.datetime.now()
            filter_time_list = [
                ('', '所有时间'),
                (now_time, '今天'),
                (now_time - datetime.timedelta(7), '7天内'),  # 往前7天
                (now_time.replace(day=1), '本月'),  # 本月内
                (now_time - datetime.timedelta(90), '三个月内'),
                (now_time.replace(month=1, day=1), '本年'),
            ]
            for dt in filter_time_list:
                # 如果选择的时间值不为空，则进行时间格式化
                time_to_str = '' if not dt[0] else dt[0].strftime('%Y-%m-%d')  # 需要将时间格式化成：YYYY-MM-DD

                # 设置选中
                selected = ''
                if filter_field in admin_class.filter_conditions:
                    # 如果当前值被选中
                    if time_to_str == admin_class.filter_conditions.get(filter_field):
                        selected = 'selected'

                option = "<option value='{}' {}>{}</option>".format(time_to_str, selected, dt[1])
                select += option
    select += "</select>"
    return mark_safe(select)

@register.simple_tag
def get_sorted_data(display_field, current_order_field, forloop_counter):
    print(current_order_field)  # {'status': '-5'}假如是按客户状态（列表索引为5）
    print(display_field)  # 遍历显示list_display列表值
    if display_field in current_order_field.keys():
        # 得到当前排序的字段
        if current_order_field[display_field].startswith('-'):
            order_data = current_order_field[display_field].replace('-', '')  # 去掉倒序
        else:
            order_data = '-' + current_order_field[display_field]
        return order_data
    return forloop_counter  # 如果不是当前排序，直接默认正序，也就是list_display的索引值


@register.simple_tag
def get_sorted_arrow(display_field, current_order_field, forloop_counter):
    if display_field in current_order_field.keys():
        if current_order_field[display_field].startswith('-'):
            arrow_direction = 'bottom'
        else:
            arrow_direction = 'top'
        span = '<span class="glyphicon glyphicon-triangle-{}" aria-hidden="true"></span>'.format(arrow_direction)
        return mark_safe(span)
    return ''

@register.simple_tag
def render_filter_args(admin_class):
    """拼接过滤的字段"""
    if admin_class.filter_conditions:
        tmp = ''
        for k, v in admin_class.filter_conditions.items():
            tmp += '&{}={}'.format(k, v)
        return mark_safe(tmp)
    return ''

@register.simple_tag
def get_obj_field_val(form_obj, field):
    """获取只读字段的值"""
    return getattr(form_obj.instance, field)

@register.simple_tag
def get_available_m2m_data(field_name, form_obj, admin_class):
    """获取多对多字段关联表的所有数据"""
    field_obj = admin_class.model._meta.get_field(field_name)  # 获取字段对象

    # consult_courses = models.ManyToManyField(Course, verbose_name='咨询课程')  # 多对多关联课程
    # 这是一个多对多字段，通过consult_courses对象获取到Course，也就是获取到所有咨询的课程
    obj_list = field_obj.related_model.objects.all()

    obj_list = set(obj_list)  # 所有咨询课程的集合
    try:
        selected_data = set(getattr(form_obj.instance, field_name).all())  # 所以已选中课程的即可
    except:
        selected_data = set([])
    # 通过集合求差集，得到未选中的自选课程，填充到左边多选框中
    return obj_list - selected_data


@register.simple_tag
def get_selected_m2m_data(field_name, form_obj, admin_class):
    """获取已选中的多对多数据"""
    try:
        selected_data = getattr(form_obj.instance, field_name).all()
    except:
        selected_data = set([])
    # print(selected_data)

    return selected_data


@register.simple_tag
def display_all_related_objs(obj):
    """获取要被删除的对象的所有关联对象"""
    ele = "<ul><b style='color:red'>%s</b>" % obj

    # 获取所有反向关联的对象
    for reversed_fk_obj in obj._meta.related_objects:
        # 获取关联对象的表名
        related_table_name = reversed_fk_obj.name
        print('\n\n', related_table_name)
        ele += "<li>{}<ul>".format(related_table_name)
        # 通过表明反向查所有关联的数据
        related_lookup_key = '{}'.format(related_table_name)  # 原文用的{}_set，也许Django版本不同，在我这就用不了，直接用的related_name表名
        from django.urls import reverse
        if reversed_fk_obj.get_internal_type() == 'OneToOneField':
            try:
                related_objs = getattr(obj, related_lookup_key)
                print('一对一', related_objs)
                ele += "<li><a href='{}'>{}</a> 记录里与[{}]相关的的数据将被删除</li>".format(
                    reverse('djadmin:table_change', kwargs={'app_name': related_objs._meta.app_label, 'model_name': related_objs._meta.model_name, 'obj_id': related_objs.id}),
                    related_objs,
                    obj
                )
            except:
                # 这儿做一个异常捕获：crm.models.CustomerInfo.student.RelatedObjectDoesNotExist: CustomerInfo has no student.
                # 当客户还未变成学员时，他并没有student的属性
                pass
        elif reversed_fk_obj.get_internal_type() == "ManyToManyField":  # 不需要深入查找
            related_objs = getattr(obj, related_lookup_key).all()
            for item in related_objs:
                ele += "<li><a href='{}'>{}</a> 记录里与[{}]相关的的数据将被删除</li>".format(
                    reverse('djadmin:table_change', kwargs={'app_name': item._meta.app_label, 'model_name': item._meta.model_name, 'obj_id': item.id}),
                    item,
                    obj
                )
        elif reversed_fk_obj.get_internal_type() == 'ForeignKey':  # 如果不是m2m，就递归查找所有关联的数据
            related_objs = getattr(obj, related_lookup_key).all()
            print('一对多', related_objs)
            for item in related_objs:
                ele += "<li><a href='{}'>{}</a></li>".format(
                    reverse('djadmin:table_change', kwargs={'app_name': item._meta.app_label, 'model_name': item._meta.model_name, 'obj_id': item.id}),
                    item,
                )
                # 递归查找
                ele += display_all_related_objs(item)
        ele += "</ul></li>"

    ele += '</ul>'
    return ele