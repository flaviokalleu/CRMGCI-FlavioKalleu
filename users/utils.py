from django.core.exceptions import ValidationError

def validate_renda(value):
    # Remove pontos de milhares, se presentes
    value = value.replace('.', '')

    # Substitui vírgulas por pontos, se necessário
    value = value.replace(',', '.')

    # Verifica se o valor pode ser convertido em float
    try:
        float_value = float(value)
    except ValueError:
        raise ValidationError('O valor da renda deve ser numérico.')

    # Verifica se o valor é positivo
    if float_value < 0:
        raise ValidationError('O valor da renda deve ser positivo.')
# users/utils.py

def obter_cor_opcao(opcao):
    OPCAO_COR_MAP = {
        'Aprovação': 'btn-primary',
        'Ficha de cadastro 3B': 'btn-secondary',
        'Pagamento TSD': 'btn-success',
        'Fichas Caixa': 'btn-info',
        'Documentação Dep': 'btn-warning',
        'Declaração Dep': 'btn-danger',
        'Documentação imóvel': 'btn-dark',
        # Adicione as outras opções e cores aqui
    }
    return OPCAO_COR_MAP.get(opcao, 'btn-secondary')
