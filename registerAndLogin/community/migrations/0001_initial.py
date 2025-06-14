# Generated by Django 5.2.1 on 2025-05-13 00:03

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('like_count', models.IntegerField(default=0)),
                ('favorite_count', models.IntegerField(default=0)),
                ('comment_count', models.IntegerField(default=0)),
                ('view_count', models.IntegerField(default=0)),
                ('status', models.CharField(default='active', max_length=20)),
            ],
            options={
                'verbose_name': '帖子',
                'verbose_name_plural': '帖子',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PostAgent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': '帖子-智能体关联',
                'verbose_name_plural': '帖子-智能体关联',
            },
        ),
        migrations.CreateModel(
            name='PostComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': '帖子评论',
                'verbose_name_plural': '帖子评论',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PostFavorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PostImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_url', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': '帖子图片',
                'verbose_name_plural': '帖子图片',
            },
        ),
        migrations.CreateModel(
            name='PostKnowledgeBase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': '帖子-知识库关联',
                'verbose_name_plural': '帖子-知识库关联',
            },
        ),
        migrations.CreateModel(
            name='PostLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': '帖子点赞',
                'verbose_name_plural': '帖子点赞',
            },
        ),
    ]
