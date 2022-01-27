# AniLite-API-v2

For round 3 of CRUx inductions

### Setting up the project locally:

1. Run the command - `pip install -r requirements.txt`
2. Run the command - `python manage.py makemigrations && python manage.py migrate`
3. Open the shell by running the command - `python manage.py shell`. Import the random secret key generator - `from django.core.management.utils import get_random_secret_key`. Generate a random secret key - `get_random_secret_key()`. Save this key for using in the next step
4. Create a .env file in the root directory and add the following environment variables:

   1. CLOUD_NAME = obtained from Cloudinary console
   2. API_KEY = obtained from Cloudinary console
   3. API_SECRET = obtained from Cloudinary console
   4. REDIS_HOST = The URL at which your Redis instance is running
   5. REDIS_PASS = The password of your Redis instance
   6. REDIS_USER_HOST_PASS = Pass your username, password and Redis host url in this format: `redis://<username>:<password>@<host_url>:<port>`
   7. SECRET_KEY = The secret key you obtained in the third step
   8. HOST_MAIL = Your Gmail ID
   9. HOST_PASS = The password of your Gmail ID

5. Enable 'less secure app access' on your Gmail account to be able to send mails
6. Create a superuser using the command - `python manage.py createsuperuser`
