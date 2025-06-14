# Generated by Django 5.2.1 on 2025-05-13 00:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('community', '0001_initial'),
        ('knowledge_base', '0001_initial'),
        ('user', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='postagent',
            name='agent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.publishedagent'),
        ),
        migrations.AddField(
            model_name='postagent',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='community.post'),
        ),
        migrations.AddField(
            model_name='postcomment',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='community.post'),
        ),
        migrations.AddField(
            model_name='postcomment',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='postfavorite',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorites', to='community.post'),
        ),
        migrations.AddField(
            model_name='postfavorite',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_favorites', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='postimage',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='community.post'),
        ),
        migrations.AddField(
            model_name='postknowledgebase',
            name='knowledge_base',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='knowledge_base.knowledgebase'),
        ),
        migrations.AddField(
            model_name='postknowledgebase',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='community.post'),
        ),
        migrations.AddField(
            model_name='postlike',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='community.post'),
        ),
        migrations.AddField(
            model_name='postlike',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='postagent',
            unique_together={('post', 'agent')},
        ),
        migrations.AlterUniqueTogether(
            name='postfavorite',
            unique_together={('post', 'user')},
        ),
        migrations.AlterUniqueTogether(
            name='postknowledgebase',
            unique_together={('post', 'knowledge_base')},
        ),
        migrations.AlterUniqueTogether(
            name='postlike',
            unique_together={('post', 'user')},
        ),
    ]
