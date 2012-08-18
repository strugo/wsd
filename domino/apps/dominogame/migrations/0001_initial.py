# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'GameRoom'
        db.create_table('dominogame_gameroom', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
            ('comet_id', self.gf('django.db.models.fields.CharField')(default='', max_length=32, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
            ('closed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('dominogame', ['GameRoom'])

        # Adding model 'GameChip'
        db.create_table('dominogame_gamechip', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('room', self.gf('django.db.models.fields.related.ForeignKey')(related_name='room_chips', to=orm['dominogame.GameRoom'])),
            ('left', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
            ('right', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
            ('angle', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
            ('prev', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dominogame.GameChip'], null=True, blank=True)),
            ('used', self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True)),
        ))
        db.send_create_signal('dominogame', ['GameChip'])

        # Adding model 'GameMember'
        db.create_table('dominogame_gamemember', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('room', self.gf('django.db.models.fields.related.ForeignKey')(related_name='room_members', to=orm['dominogame.GameRoom'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('dominogame', ['GameMember'])

        # Adding M2M table for field chips on 'GameMember'
        db.create_table('dominogame_gamemember_chips', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('gamemember', models.ForeignKey(orm['dominogame.gamemember'], null=False)),
            ('gamechip', models.ForeignKey(orm['dominogame.gamechip'], null=False))
        ))
        db.create_unique('dominogame_gamemember_chips', ['gamemember_id', 'gamechip_id'])


    def backwards(self, orm):
        # Deleting model 'GameRoom'
        db.delete_table('dominogame_gameroom')

        # Deleting model 'GameChip'
        db.delete_table('dominogame_gamechip')

        # Deleting model 'GameMember'
        db.delete_table('dominogame_gamemember')

        # Removing M2M table for field chips on 'GameMember'
        db.delete_table('dominogame_gamemember_chips')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'dominogame.gamechip': {
            'Meta': {'ordering': "['pk']", 'object_name': 'GameChip'},
            'angle': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'left': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'prev': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dominogame.GameChip']", 'null': 'True', 'blank': 'True'}),
            'right': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'room': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'room_chips'", 'to': "orm['dominogame.GameRoom']"}),
            'used': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'})
        },
        'dominogame.gamemember': {
            'Meta': {'ordering': "['pk']", 'object_name': 'GameMember'},
            'chips': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'users_chips'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['dominogame.GameChip']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'room': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'room_members'", 'to': "orm['dominogame.GameRoom']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'dominogame.gameroom': {
            'Meta': {'object_name': 'GameRoom'},
            'closed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'comet_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '32', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'})
        }
    }

    complete_apps = ['dominogame']