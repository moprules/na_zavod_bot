FROM python:3.11.4-alpine3.18

# Имя no-root пользователя
ENV APP_USER=zavodik
# Его домашний каталог
ENV APP_HOME=/app

# # Создаём группу пользователя
RUN addgroup -g 1000 $APP_USER
# Создаём самого польователя
RUN adduser -u 1000 -G $APP_USER -h /home/$APP_USER -D $APP_USER
  
# # Создаём директорию пользователя - где будет выполняться код
RUN mkdir $APP_HOME && chown -R $APP_USER:$APP_USER $APP_HOME

# Задаём рабочую директорию
WORKDIR $APP_HOME

# Копируем файл зависимостей проекта
COPY . .

# Обновляем зависимости проекта
RUN python3 -m pip install --no-cache-dir --no-warn-script-location --upgrade pip
RUN python3 -m pip install --no-cache-dir --no-warn-script-location -r requirements.txt

# # Рекурсивно меняем пользователя текущего каталога, его подкаталогов и файлов
RUN chown -R $APP_USER:$APP_USER $APP_HOME
  
# Переключаемся на созданного нами пользователя
USER $APP_USER