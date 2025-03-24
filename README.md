
# Django Demo

A demo project using Django, including Telegram bot integration with options to run via webhook or polling.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Installation

### Server Installation

1. **Run the installation script:**
   ```bash
   bash install.sh
   ```

### Development Installation

1. **Set up environment variables:**
   ```bash
   cp conf/env .env
   ```
   Edit the `.env` file with your settings. Example:
   ```plaintext
   PORT=8000
   SECRET_KEY=O6xUnFBeYFhlBn_Bpwy0jmuZjcrtiNy_gGmS19yUuw6hi18xIQzw4-dJvzgMJcbKHm8
   ALLOWED_HOSTS=*
   CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000
   DEBUG=True
   BOT_API_TOKEN=[Your bot token here]
   WEBHOOK_URL=[ngrok url] | if you use webhook
   ```

2. **Create a virtual environment:**
   ```bash
   python3.10 -m venv venv
   ```

3. **Activate the virtual environment:**
   - On Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scriptsctivate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Apply database migrations:**
   ```bash
   python manage.py migrate
   python manage.py makemigrations app
   python manage.py makemigrations bot
   python manage.py migrate app
   python manage.py migrate bot
   ```

6. **Create a superuser for Django admin:**
   ```bash
   python manage.py createsuperuser
   ```

## Usage

### Starting the Project

- **Using Webhook (Recommended for production):**
  1. Set the `WEBHOOK_URL` in your `.env` file.
  2. Run the following command to set the webhook:
     ```bash
     python manage.py set_webhook
     ```
  3. Start the server using Uvicorn:
     ```bash
     python manage.py run_uvicorn
     ```

- **Without Webhook (Using Polling):**
  1. Start the Django development server:
     ```bash
     python manage.py runserver
     ```
  2. Run the Telegram bot in polling mode:
     ```bash
     python manage.py run_polling
     ```

## Features

- Django-based web application
- Telegram bot integration with webhook and polling support
- Admin panel for managing application data

## Configuration

Refer to the `.env` file for configuration options. Make sure to set your bot's API token and the webhook URL if you plan to use webhook mode.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/your-feature-name`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature-name`)
5. Open a Pull Request

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contact

Shahzod - [xii1303@inbox.ru](mailto:xii1303@inbox.ru)

Project Link: [https://github.com/Venons-ltd/django-demo](https://github.com/Venons-ltd/django-demo)