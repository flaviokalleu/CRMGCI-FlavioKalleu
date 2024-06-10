# users/templatetags/custom_filters.py
from django import template
from django.utils.safestring import SafeString

from users.utils import obter_cor_opcao

register = template.Library()


@register.filter(name='get_key')
def get_key(value, arg):
    return value.get(arg, '')

@register.filter
def get_color(value):
    if isinstance(value, SafeString):
        try:
            value = float(value)
        except ValueError:
            return 'unknown'
        
    return 'green' if value > 0 else 'red'

@register.filter
def access(value, arg):
    if isinstance(value, dict):
        return value.get(arg)
    return None 

from django import template
from users.utils import obter_cor_opcao  # Certifique-se de substituir 'users' pelo nome do seu aplicativo e 'obter_cor_opcao' pela sua função real

register = template.Library()

@register.filter(name='cor_opcao')
def cor_opcao(opcao_selecionada):
    return obter_cor_opcao(opcao_selecionada)

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)