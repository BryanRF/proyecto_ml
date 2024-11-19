#1 solo para cuando lo clones en otra computadora, en esta pc ya esta instalado
pip install virtualenv 
#2 para crear un entonrno virual con las librerias necesarias del proyecto (te crea una carpeta venv)
virtualenv venv
#3 debes entrar al entorno virtual (la carpeta de las librerias)
venv\Scripts\activate
#4 se deben descargar las librerias de requirements.txt (demora un poco)
pip install -r requirements.txt
# crea base de datos 
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
admin
admin@gmail.com
admin
admin
y
#5 ejecutar el proyecto 
python manage.py runserver