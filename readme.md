Permisos
=

Para traducir los permisos correr los comando:

    docker-compose run app pipenv run python manage.py permissions_translation

Para agregar los permisos:

    docker-compose run app pipenv run python manage.py add_permissions

Documentacion anterior
=
- Preparado para desarrollar directo sobre el contenedor descrito en el Dockerfile usando [VSCode](https://code.visualstudio.com/docs/remote/containers)
- No sé por qué, pero la primera vez que se levanta la imagen en VSCode hay que correr a mano "pipenv sync -d" desde la terminal embebida (a pesar de q ya se corrió en el Dockerfile)
- A partir de ahí el grueso se prueba activando con "pipenv shell", entrando al directorio "sistemita" y desde ahí corriendo "./manage.py behave" para ejecutar todos los archivos .feature
- Para crear una visualización en UML del modelo se puede usar "./manage.py graph_models -a -o modelo.pdf"
