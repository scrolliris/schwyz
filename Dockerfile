FROM gcr.io/google-appengine/python

# venv
RUN virtualenv /env -p python3.5
ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH

ADD requirements.txt /app/requirements.txt
ADD constraints.txt /app/constraints.txt
ADD . app/

WORKDIR app/

# same as ENV=production make setup
RUN pip install -r requirements.txt

ENV ENV production
ENV WSGI_URL_SCHEME http
ENV HOST 0.0.0.0
ENV PORT 8080
EXPOSE 8080

CMD ./bin/serve -e production -c config/production.ini
