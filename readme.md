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
- [Nginx](https://gitlab.com/mcardozo/aic/-/blob/master/Web%20Server) Servidor
  de archivos estáticos

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

## Comando útiles

### Crear usuario administrador

Para crear un usuario administrador ejecutrar el siguiente comando:

    $ docker-compose run --r django python manage.py createsuperuser

### Fixtures

Para cargar datos iniciales correr el siguiente comando:

    $ docker-compose run --rm django python manage.py loaddata fixtures/*.json

### Permisos

Para traducir los permisos correr los comando:

    $ docker-compose run --rm django python manage.py permissions_translation

Para agregar los permisos:

    $ docker-compose run --rm django python manage.py add_permissions

## Documentacion anterior

- Preparado para desarrollar directo sobre el contenedor descrito en el Dockerfile usando [VSCode](https://code.visualstudio.com/docs/remote/containers)
- No sé por qué, pero la primera vez que se levanta la imagen en VSCode hay que correr a mano "pipenv sync -d" desde la terminal embebida (a pesar de q ya se corrió en el Dockerfile)
- A partir de ahí el grueso se prueba activando con "pipenv shell", entrando al directorio "sistemita" y desde ahí corriendo "./manage.py behave" para ejecutar todos los archivos .feature
- Para crear una visualización en UML del modelo se puede usar "./manage.py graph_models -a -o modelo.pdf"
