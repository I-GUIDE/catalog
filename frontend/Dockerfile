FROM node:22 as build-stage
WORKDIR /app
COPY package*.json ./
COPY ./frontend .
RUN npm install
RUN npm run build-prod

FROM nginx:1.23.1 as production-stage
RUN mkdir /app
COPY --from=build-stage /app/dist /app
COPY --from=build-stage /app/nginx.conf /etc/nginx/nginx.conf
EXPOSE 5003