# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models, utils
import pickle

class Migration(SchemaMigration):

    def forwards(self, orm):
        try:
            db.rename_table("config_configvalue", "server_serverconfig")    
            for conf in orm.ServerConfig.objects.all():
                conf.db_value = pickle.dumps(conf.db_value)
                conf.save()
        except utils.DatabaseError:
            # this will happen if we start db from scratch (the config
            # app will then already be gone and no data is to be transferred)
            # So instead of renaming the old we instead have to manually create the new model.
            # Adding model 'ServerConfig' 
            db.create_table('server_serverconfig', (
                    ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
                    ('db_key', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64)),
                    ('db_value', self.gf('django.db.models.fields.TextField')(blank=True)),
                    ))
            db.send_create_signal('server', ['ServerConfig'])
            
    def backwards(self, orm):
        raise RuntimeError("This migration cannot be reversed.")

    models = {
        'config.configvalue': {
            'Meta': {'object_name': 'ConfigValue'},
            'db_key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'db_value': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'server.serverconfig': {
            'Meta': {'object_name': 'ServerConfig'},
            'db_key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'db_value': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['config', 'server']
