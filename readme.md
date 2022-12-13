# Sistemita

<p align="center">
  <img src="sistemita/static/images/logo-top-dark.png" />
</p>

## Stack de tecnologías

- [Django 3.1.7](https://www.djangoproject.com/) Web Framework
- [Docker Engine](https://www.docker.com/) Despliege de servicios
- [Docker Compose](https://docs.docker.com/compose/) Orquestador de aplicaciones docker
- [PostgreSQL 12.3](https://www.postgresql.org/) Relational Database
- [Bootstrap 4.5](https://getbootstrap.com/) Frontend
- [Nginx](https://www.nginx.com/) Servidor de archivos estáticos

## Entorno de desarrollo

- Clonar repositorio:

		$ git clone git@github.com:acyment/sistemita2.git

- Construir imágenes:

		$ export COMPOSE_FILE=local.yml

		$ docker-compose build

- Levantar servicios:

		$ docker-compose up

- Interacción con Django:

		$ docker-compose stop django

		$ docker-compose run --rm --service-ports django

## Setup Inicial

### Crear usuario administrador

Para crear un usuario administrador ejecutrar el siguiente comando:

	$ docker-compose run --rm django python manage.py createsuperuser

### Permisos

Para traducir los permisos correr los comando:

	$ docker-compose run --rm django python manage.py permissions_translation

Para agregar los permisos:

	$ docker-compose run --rm django python manage.py add_permissions

### Fixtures

Para cargar datos iniciales correr el siguiente comando:

	$ docker-compose run --rm django python manage.py loaddata fixtures/*.json


### Facturas distribuidas

En caso de que las facturas ya estén cargadas:

	$ docker-compose run --rm django python manage.py load_facturas_distribuidas


## Test

Para correr los tests de integración correr el comando:

	$ docker-compose run --rm django python manage.py test


## Restaurar un backup de db

- Copiar backup

		$ docker cp backup.sql.gz <container>:/backups/backup.sql.gz

- Restore

		$ docker-compose exec postgres restore backup.sql.gz


## Acceso al módulo de mis facturas

Pasos para que un proveedor pueda ver sus facturas:

1. Ir al módulo de usuario y presionar el botón "Agregar"
2. Completar los datos
   * El email del usuario debe coincidir con el email del proveedor
   * El usuario debe pertenecer al grupo "Puede ver módulo de Mis Facturas"
3. Dar los accesos al proveedor

## Documentacion anterior

- Preparado para desarrollar directo sobre el contenedor descrito en el Dockerfile usando [VSCode](https://code.visualstudio.com/docs/remote/containers)
- No sé por qué, pero la primera vez que se levanta la imagen en VSCode hay que correr a mano "pipenv sync -d" desde la terminal embebida (a pesar de q ya se corrió en el Dockerfile)
- A partir de ahí el grueso se prueba activando con "pipenv shell", entrando al directorio "sistemita" y desde ahí corriendo "./manage.py behave" para ejecutar todos los archivos .feature
- Para crear una visualización en UML del modelo se puede usar "./manage.py graph_models -a -o modelo.pdf"
