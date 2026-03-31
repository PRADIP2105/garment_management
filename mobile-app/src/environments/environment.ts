/**
 * Default API base — must match `ipconfig` Wi‑Fi IPv4 on the PC running Django (not a random .109).
 * Start backend: run `run-django-lan.bat` or: python manage.py runserver 0.0.0.0:8000
 * Login screen overrides via localStorage `api_url`.
 */
export const environment = {
  production: false,
  apiUrl: 'http://10.94.62.87:8000/api',
};
