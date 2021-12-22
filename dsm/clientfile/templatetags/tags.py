from django import template
from django.contrib.auth.models import User
from re import IGNORECASE, compile, escape as rescape
from django.utils.safestring import mark_safe
from medical_info.models import Program
from django.utils.datastructures import MultiValueDict
from django.db.models import Q, F, Count


register = template.Library()

# @register.simple_tag
# def active(request, pattern):
#     import re
#     if re.search(pattern, request.path):
#         return 'active'
#     return ''


@register.filter(name="has_group")
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


@register.filter
def multiply(value, arg):
    try:
        if arg:
            return value * arg
    except:
        pass
    return ""


@register.filter(name="times")
def times(number):
    try:
        return range(1, number + 1)
    except:
        return []


@register.filter(name="select_id")
def select_id(str):
    try:
        if str[-2:] == "[]":
            return str[:-2]
        else:
            return str
    except:
        return str


@register.filter(name="modifier")
def modifier(str):
    try:
        action = str.split("|")[1]
        user = str.split("|")[2]
        if action == "False":
            action = "添加"
        elif action == "True":
            action = "删除"
        # elif action == '~':
        #     action = '修改'
        # user_id = int(float(str.split('|')[2]))
        # user = User.objects.get(id=user_id).username
        return "%s%s了" % (user, action)
    except:
        return str


@register.filter(name="modified_date")
def modified_date(str):
    try:
        date = str.split("|")[0]
        return date
    except:
        return str


@register.filter(name="modified_action")
def modified_action(str):
    try:
        action = str.split("|")[1]
        return action
    except:
        return str


@register.filter(name="none_to_blank")
def none_to_blank(str):
    try:
        if str is None:
            return ""
        else:
            return str
    except:
        return str


@register.filter(name="percentage")
def percentage(value, decimal):
    try:
        format_str = "{0:." + str(decimal) + "%}"
        return format_str.format(value)
    except:
        return value


@register.filter(name="value_to_color")
def value_to_color(value):
    try:
        if value > 0.8:
            return "green"
        elif value > 0.6:
            return "olive"
        elif value > 0.4:
            return "yellow"
        elif value > 0.2:
            return "orange"
        else:
            return "red"
    except:
        return ""


@register.filter(name="highlight")
def highlight(text, highlights):
    try:
        # rgx = compile(rescape(search), IGNORECASE)
        rgx = compile("(%s)" % "|".join(map(rescape, highlights.keys())), IGNORECASE)
        return mark_safe(
            # rgx.sub(lambda m: '<b class="highlight">{}</b>'.format(m.group()), text)
            rgx.sub(lambda mo: highlights[mo.string[mo.start() : mo.end()]], text)
        )
    except:
        return text


@register.inclusion_tag("medical_info/programs.html")
def show_programs():
    programs = Program.objects.annotate(post_count=Count("programs"))
    return {"programs": programs}


# 根据参数在当前url基础上追加新参数
@register.simple_tag
def add_query_params(request, **kwargs):
    updated = request.GET.copy()
    d_updated = dict(updated)

    for k, v in kwargs.items():
        if v is not None:
            if k != "page":  # 如果不是分页参数
                if isinstance(updated.getlist(k, 0), list):  # 判断param是否已在当前参数内
                    exists = str(v) in updated.getlist(k, 0)
                else:
                    exists = v == updated.getlist(k, 0)

                if not exists:  # 如果当前没有的参数，则加上
                    d = {k: v}
                    updated.update(MultiValueDict(d) if isinstance(v, list) else d)
                else:
                    try:
                        d_updated[k].remove(str(v))
                    except (KeyError, ValueError):
                        pass
                    else:
                        if not d_updated[k]:
                            del d_updated[k]
            else:  # 如果参数是分页则不在当前url上添加，重新更新page
                updated.pop(k, 0)
                d = {k: v}
                updated.update(d)
    return updated.urlencode()