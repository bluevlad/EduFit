FROM node:20-alpine AS build

WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
ARG VITE_BASE_PATH=/edufit/
ENV VITE_BASE_PATH=${VITE_BASE_PATH}
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 4070
CMD ["nginx", "-g", "daemon off;"]
