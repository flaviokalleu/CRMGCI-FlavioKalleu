# Generated by Django 4.2.9 on 2024-06-09 14:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import users.models
import users.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(max_length=150, null=True, unique=True)),
                ('email', models.EmailField(max_length=190, unique=True)),
                ('first_name', models.CharField(blank=True, max_length=100)),
                ('last_name', models.CharField(blank=True, max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('must_change_password', models.BooleanField(default=True)),
                ('CRECI', models.CharField(blank=True, max_length=100, null=True)),
                ('Endereço', models.CharField(blank=True, max_length=100, null=True)),
                ('PIX_Conta', models.CharField(blank=True, max_length=100, null=True)),
                ('telefone', models.CharField(blank=True, max_length=15, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Backup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('file', models.FileField(upload_to='backups/')),
            ],
        ),
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(blank=True, max_length=255, null=True)),
                ('email', models.EmailField(blank=True, max_length=191, null=True)),
                ('telefone', models.CharField(blank=True, max_length=15, null=True)),
                ('cpf', models.CharField(blank=True, max_length=14, null=True, unique=True, validators=[users.models.validate_cpf])),
                ('valor_da_renda', models.CharField(blank=True, max_length=20, null=True, validators=[users.utils.validate_renda], verbose_name='Valor de Renda')),
                ('estado_civil', models.CharField(blank=True, choices=[('solteiro', 'Solteiro'), ('casado', 'Casado'), ('divorciado', 'Divorciado'), ('viuvo', 'Viúvo'), ('uniao_estavel', 'União Estável')], max_length=50, null=True)),
                ('naturalidade', models.CharField(blank=True, max_length=100, null=True)),
                ('profissao', models.CharField(blank=True, max_length=100, null=True)),
                ('data_admissao', models.DateField(blank=True, null=True)),
                ('data_nascimento', models.DateField(blank=True, null=True, verbose_name='Data de Nascimento')),
                ('renda_tipo', models.CharField(blank=True, choices=[('formal', 'Formal'), ('informal', 'Informal'), ('mista', 'Mista')], max_length=20, null=True)),
                ('possui_carteira_mais_tres_anos', models.BooleanField(blank=True, null=True)),
                ('numero_pis', models.CharField(blank=True, max_length=15, null=True)),
                ('possui_dependente', models.BooleanField(blank=True, null=True)),
                ('documentos_pessoais', models.FileField(blank=True, null=True, upload_to=users.models.documento_upload_to)),
                ('extrato_bancario', models.FileField(blank=True, null=True, upload_to=users.models.documento_upload_to)),
                ('documentos_dependente', models.FileField(blank=True, null=True, upload_to=users.models.documento_upload_to)),
                ('documentos_conjuge', models.FileField(blank=True, null=True, upload_to=users.models.documento_upload_to)),
                ('status', models.CharField(blank=True, choices=[('aguardando_aprovacao', 'Aguardado Aprovação'), ('documentacao_pendente', 'Documentação Pendente'), ('aguardando_cancelamento_qv', 'Aguardando Cancelamento / QV'), ('cliente_aprovado', 'Cliente Aprovado'), ('reprovado', 'Cliente Reprovado'), ('proposta_apresentada', 'Proposta Apresentada'), ('visita_efetuada', 'Visita Efetuada'), ('nao_deu_continuidade', 'Não Deu Continuidade'), ('venda_concluida', 'Venda Concluída'), ('processo_em_aberto', 'Processo Aberto'), ('concluido', 'Finalizado')], default='aguardando_aprovacao', max_length=50, null=True)),
                ('data_de_criacao', models.DateTimeField(auto_now_add=True)),
                ('opcoes_processo', models.JSONField(default=list)),
                ('corretor', models.ForeignKey(blank=True, limit_choices_to={'groups__name': 'Corretores'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='clientes', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Contrato',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=255)),
                ('arquivo', models.FileField(upload_to='contratos/')),
                ('data_upload', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Imagem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imagem', models.ImageField(blank=True, null=True, upload_to='imovel_images/')),
            ],
        ),
        migrations.CreateModel(
            name='Imovel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome_do_imovel', models.CharField(blank=True, max_length=255, null=True)),
                ('endereco', models.CharField(max_length=255)),
                ('banheiro', models.CharField(blank=True, max_length=255, null=True)),
                ('quartos', models.CharField(blank=True, max_length=255, null=True)),
                ('tipo', models.CharField(max_length=50)),
                ('valor_de_avaliacao', models.DecimalField(decimal_places=2, max_digits=10)),
                ('valor_de_venda', models.DecimalField(decimal_places=2, max_digits=10)),
                ('documentacao', models.FileField(blank=True, null=True, upload_to='imovel_documentos/')),
                ('imagem_de_capa', models.ImageField(blank=True, null=True, upload_to='imovel_imagens/')),
                ('localizacao', models.CharField(choices=[('Valparaiso_de_Goias', 'Valparaiso de Goiás - Goiás'), ('Cidade_Ocidental', 'Cidade Ocidental - Goiás'), ('Jardim_Ingá', 'Jardim Ingá - Goiás'), ('Luziania', 'Luziânia - Goiás'), ('Brasilia', 'Brasília - Distrito Federal')], max_length=50)),
                ('exclusivo', models.BooleanField(default=False, verbose_name='Exclusivo?')),
                ('tem_inquilino', models.BooleanField(default=False, verbose_name='Tem Inquilino?')),
                ('situacao_do_imovel', models.TextField(blank=True, null=True, verbose_name='Situação do Imóvel')),
                ('observacoes', models.TextField(blank=True, null=True, verbose_name='Observações')),
                ('status', models.CharField(choices=[('NOVO', 'Novo'), ('USADO', 'Usado'), ('AGIO', 'Ágio')], default='NOVO', max_length=5)),
                ('descricao', models.TextField(blank=True, null=True, verbose_name='Descrição do Imóvel')),
                ('imagens', models.ManyToManyField(blank=True, related_name='imoveis', to='users.imagem')),
            ],
        ),
        migrations.CreateModel(
            name='MaterialDeMarketing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=100)),
                ('descricao', models.TextField()),
                ('imagem', models.ImageField(upload_to='marketing_images/')),
                ('arquivo', models.FileField(upload_to='marketing_files/')),
            ],
        ),
        migrations.CreateModel(
            name='Proprietario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=300, verbose_name='Nome')),
                ('email', models.EmailField(max_length=300, verbose_name='Email')),
                ('telefone', models.CharField(max_length=300, verbose_name='Telefone')),
                ('endereco', models.CharField(max_length=300, verbose_name='Endereço')),
                ('cpf_cnpj', models.CharField(max_length=300, verbose_name='CPF/CNPJ')),
                ('data_cadastro', models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro')),
                ('documentacao', models.FileField(blank=True, null=True, upload_to='proprietario/', verbose_name='Documentacao')),
            ],
            options={
                'verbose_name': 'Proprietário',
                'verbose_name_plural': 'Proprietários',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='TipoProcesso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='VendaCorretor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('valor_total_pagar', models.DecimalField(decimal_places=2, max_digits=10)),
                ('valor_pago', models.DecimalField(decimal_places=2, max_digits=10)),
                ('nome_corretor', models.CharField(max_length=100)),
                ('valor_faltante', models.DecimalField(decimal_places=2, max_digits=10)),
                ('tipo', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('video_file', models.FileField(upload_to='videos/')),
                ('video_url', models.URLField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Correspondente',
            fields=[
                ('customuser_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=('users.customuser',),
        ),
        migrations.CreateModel(
            name='Corretores',
            fields=[
                ('customuser_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=('users.customuser',),
        ),
        migrations.CreateModel(
            name='VideoView',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('duration_watched', models.PositiveIntegerField(default=0)),
                ('total_duration', models.PositiveIntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('video', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.video')),
            ],
        ),
        migrations.CreateModel(
            name='UserAccessLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
                ('action', models.TextField(blank=True, null=True)),
                ('reference_page', models.CharField(blank=True, max_length=255, null=True)),
                ('session_data', models.TextField(blank=True, null=True)),
                ('referer_url', models.URLField(blank=True, null=True)),
                ('http_method', models.CharField(blank=True, max_length=10, null=True)),
                ('request_params', models.TextField(blank=True, null=True)),
                ('request_body', models.TextField(blank=True, null=True)),
                ('request_headers', models.TextField(blank=True, null=True)),
                ('browser_info', models.TextField(blank=True, null=True)),
                ('device_info', models.TextField(blank=True, null=True)),
                ('os_info', models.TextField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('DESPESA', 'Despesa'), ('RECEITA', 'Receita')], max_length=50)),
                ('valor', models.DecimalField(decimal_places=2, max_digits=10)),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'users_transaction',
            },
        ),
        migrations.CreateModel(
            name='Processo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('usado', 'Usado'), ('novo', 'Novo'), ('agio', 'Ágio')], default='novo', max_length=5)),
                ('tags', models.CharField(blank=True, max_length=255, null=True)),
                ('data_inicio', models.DateField(blank=True, null=True)),
                ('data_finalizacao', models.DateField(blank=True, null=True)),
                ('slug', models.SlugField(blank=True, max_length=250, unique=True)),
                ('documentacao_imovel', models.FileField(blank=True, null=True, upload_to='processo_documentacao_imovel/')),
                ('cliente', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.cliente')),
                ('imoveis', models.ManyToManyField(blank=True, to='users.imovel')),
                ('proprietario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.proprietario', verbose_name='Proprietário')),
                ('responsaveis', models.ManyToManyField(to='users.corretores')),
            ],
        ),
        migrations.CreateModel(
            name='OpcaoSelecionada',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('opcao', models.CharField(max_length=255)),
                ('data_selecionada', models.DateField(auto_now=True)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.cliente')),
                ('processo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.processo')),
                ('tipo_processo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.tipoprocesso')),
            ],
        ),
        migrations.CreateModel(
            name='OpcaoProcesso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('opcao', models.CharField(max_length=255)),
                ('data_selecionada', models.DateField()),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.cliente')),
                ('tipo_processo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.tipoprocesso')),
            ],
        ),
        migrations.CreateModel(
            name='NotaPrivada',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateTimeField(auto_now_add=True)),
                ('conteudo', models.TextField()),
                ('concluido', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Nota_notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('destinatario', models.CharField(choices=[('owner', 'Proprietário'), ('broker', 'Corretor')], max_length=10)),
                ('texto', models.TextField()),
                ('data_criacao', models.DateTimeField(auto_now_add=True)),
                ('nova', models.BooleanField(default=True)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.cliente')),
                ('processo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.processo')),
            ],
        ),
        migrations.CreateModel(
            name='Nota',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nova', models.BooleanField(default=True)),
                ('destinatario', models.CharField(choices=[('owner', 'Proprietário'), ('broker', 'Corretor')], max_length=10)),
                ('texto', models.TextField()),
                ('data_criacao', models.DateTimeField(auto_now_add=True)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.cliente')),
                ('criado_por', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notas_criadas', to=settings.AUTH_USER_MODEL)),
                ('processo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.processo')),
            ],
        ),
        migrations.AddField(
            model_name='imovel',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='imoveis', to='users.tag'),
        ),
        migrations.CreateModel(
            name='FixedExpense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=255)),
                ('due_day', models.PositiveIntegerField()),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('is_paid', models.BooleanField(default=False)),
                ('month_paid', models.PositiveIntegerField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Documento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('arquivo', models.FileField(upload_to='documentos/')),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documentos', to='users.cliente')),
            ],
        ),
        migrations.CreateModel(
            name='Contato',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=200, verbose_name='Nome')),
                ('data_registro', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Data de Registro')),
                ('proprietario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.proprietario', verbose_name='Proprietário')),
            ],
        ),
        migrations.AddField(
            model_name='cliente',
            name='tipos_processo',
            field=models.ManyToManyField(to='users.tipoprocesso'),
        ),
        migrations.CreateModel(
            name='ImovelTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imovel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.imovel')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.tag')),
            ],
            options={
                'unique_together': {('imovel', 'tag')},
            },
        ),
    ]