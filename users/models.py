from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, documento, primer_nombre, primer_apellido, password=None, **extra_fields):
        if not email:
            raise ValueError('El usuario debe tener un correo electrónico.')
        if not documento:
            raise ValueError('El usuario debe tener un documento de identidad.')
        
        email = self.normalize_email(email)
        user = self.model(email=email, documento=documento, primer_nombre=primer_nombre, primer_apellido=primer_apellido, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, documento, primer_nombre, primer_apellido, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')

        return self.create_user(email, documento, primer_nombre, primer_apellido, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    documento = models.CharField(max_length=10, unique=True, verbose_name='Documento identidad')
    email = models.EmailField(unique=True, verbose_name='Correo Electrónico', max_length=50)
    primer_nombre = models.CharField(max_length=20, verbose_name='Primer Nombre')
    segundo_nombre = models.CharField(max_length=20, verbose_name='Segundo Nombre', blank=True, null=True)
    primer_apellido = models.CharField(max_length=20, verbose_name='Primer Apellido')
    segundo_apellido = models.CharField(max_length=20, verbose_name='Segundo Apellido', blank=True, null=True)
    telefono = models.CharField(max_length=10, verbose_name='Teléfono', blank=True, null=True)
    imagen = models.ImageField(upload_to='perfil/', max_length=50, verbose_name='Imagen de perfil', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['documento', 'primer_nombre', 'primer_apellido']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'

class Proveedor(models.Model):
    nombre = models.CharField(max_length=200, verbose_name='Nombre')
    direccion = models.CharField(max_length=255, verbose_name='Dirección')
    telefono = models.CharField(max_length=15, verbose_name='Teléfono')
    email = models.EmailField(verbose_name='Email', blank=True, null=True)
    contacto = models.CharField(max_length=200, verbose_name='Contacto', blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        db_table = 'proveedor'
        ordering = ['nombre']