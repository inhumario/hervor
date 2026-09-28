FROM python:3.12-slim AS build
WORKDIR /src
RUN pip install --no-cache-dir markdown==3.7 pyyaml==6.0.2
COPY build.py config.json ./
COPY content content
COPY static static
RUN python3 build.py

FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /src/dist /usr/share/nginx/html
EXPOSE 80
