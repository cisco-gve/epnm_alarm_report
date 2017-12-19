from django.db import models
import opensesame

# Create your models here.
class epnm_info(models.Model):
	host = 'tme-epnm'
	user = opensesame.API_username
	password = opensesame.API_password

	def get_info(self):
		r_dict={
			'host'		: self.host,
			'user'		: self.user,
			'password'	: self.password,
		}
		return r_dict