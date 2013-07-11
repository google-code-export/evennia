# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models, connection


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PlayerDBtmp'
        if "auth_user" in connection.introspection.table_names():
            # auth_user exists ffrom before. Use that as a base.
            db.rename_table('auth_user', 'players_playerdbtmp')
        else:
            # from-scratch creation; no auth_user table available. Create vanilla User table
            db.create_table(u'players_playerdbtmp', (
                (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
                ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
                ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
                ('is_superuser', self.gf('django.db.models.fields.BooleanField')(default=False)),
                ('username', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
                ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
                ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
                ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
                ('is_staff', self.gf('django.db.models.fields.BooleanField')(default=False)),
                ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
                ('date_joined', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ))
            db.send_create_signal(u'players', ['PlayerDBtmp'])

            # Adding M2M table for field groups on 'PlayerDBtmp'
            db.create_table(u'players_playerdbtmp_groups', (
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
                ('playerdbtmp', models.ForeignKey(orm[u'players.playerdbtmp'], null=False)),
                ('group', models.ForeignKey(orm[u'auth.group'], null=False))
            ))
            db.create_unique(u'players_playerdbtmp_groups', ['playerdbtmp_id', 'group_id'])

            # Adding M2M table for field user_permissions on 'PlayerDBtmp'
            db.create_table(u'players_playerdbtmp_user_permissions', (
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
                ('playerdbtmp', models.ForeignKey(orm[u'players.playerdbtmp'], null=False)),
                ('permission', models.ForeignKey(orm[u'auth.permission'], null=False))
            ))
            db.create_unique(u'players_playerdbtmp_user_permissions', ['playerdbtmp_id', 'permission_id'])

            # Adding field 'PlayerDB.db_is_connected'
            db.add_column(u'players_playerdb', 'db_is_connected',
                          self.gf('django.db.models.fields.BooleanField')(default=False),
                          keep_default=False)

            # Adding field 'PlayerDB.db_cmdset_storage'
            db.add_column(u'players_playerdb', 'db_cmdset_storage',
                          self.gf('django.db.models.fields.CharField')(max_length=255, null=True),
                          keep_default=False)

        # add Evennia-specific columns
        db.add_column('players_playerdbtmp', 'db_key', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True, null=True))
        db.add_column('players_playerdbtmp', 'db_typeclass_path', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))
        db.add_column('players_playerdbtmp', 'db_date_created', self.gf('django.db.models.fields.DateTimeField')(null=True, auto_now_add=True, blank=True))
        db.add_column('players_playerdbtmp', 'db_permissions', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True, null=True))
        db.add_column('players_playerdbtmp', 'db_lock_storage', self.gf('django.db.models.fields.TextField')(blank=True, null=True))
        db.add_column('players_playerdbtmp', 'db_is_connected', self.gf('django.db.models.fields.BooleanField')(default=False))
        db.add_column('players_playerdbtmp', 'db_cmdset_storage', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

    def backwards(self, orm):
        raise RuntimeError("Cannot revert migration")


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'players.playerattribute': {
            'Meta': {'object_name': 'PlayerAttribute'},
            'db_date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'db_key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'db_lock_storage': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'db_obj': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['players.PlayerDB']"}),
            'db_value': ('src.utils.picklefield.PickledObjectField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'players.playerdb': {
            'Meta': {'object_name': 'PlayerDB'},
            'db_cmdset_storage': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'db_date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'db_is_connected': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'db_key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'db_lock_storage': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'db_permissions': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'db_typeclass_path': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'players.playerdbtmp': {
            'Meta': {'ordering': "['-db_date_created', 'id', 'db_typeclass_path', 'db_key']", 'object_name': 'PlayerDBtmp'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'db_date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'db_key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'db_is_connected': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'db_cmdset_storage': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'db_lock_storage': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'db_permissions': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'db_typeclass_path': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'players.playernick': {
            'Meta': {'unique_together': "(('db_nick', 'db_type', 'db_obj'),)", 'object_name': 'PlayerNick'},
            'db_nick': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'db_obj': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['players.PlayerDB']"}),
            'db_real': ('django.db.models.fields.TextField', [], {}),
            'db_type': ('django.db.models.fields.CharField', [], {'default': "'inputline'", 'max_length': '16', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['players']
