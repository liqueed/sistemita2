FROM nginx:1.19.0-alpine

RUN mkdir -p /www/media
RUN chown -R nginx:nginx /www
RUN rm /etc/nginx/conf.d/default.conf
COPY ./compose/production/nginx/nginx.conf /etc/nginx/conf.d