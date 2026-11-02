
  TERMINAL 1: Tailwind (Watch mode)
  ./tailwindcss -i static/src/styles.css -o ... --watch
            |
            v
  TERMINAL 2: Django Server
  python manage.py runserver
            |
            v
  NAVEGADOR: http://127.0.0.1:8000/
  - CSS carga sin 404
  - Estilos aplicados con éxito

python manage.py makemigrations
python manage.py migrate

python manage.py shell
#edicion de campos tras migrar

------------------------------------

sudo systemctl start apache2
sudo systemctl start mysql
estaus--
sudo systemctl status apache2
sudo systemctl status mysql

http://localhost/phpmyadmin


sudo systemctl start mysql
sudo systemctl enable mysql

sudo mysql -u root