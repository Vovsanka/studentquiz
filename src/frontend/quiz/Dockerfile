FROM node:bookworm

# install simple http server for serving static content
RUN npm install -g http-server

WORKDIR /frontend_app

# copy both 'package.json' and 'package-lock.json' (if available)
COPY package*.json ./

# install project dependencies
RUN npm install

# copy project files and folders to the current working directory (i.e. 'app' folder)
COPY . .

# build app for production with minification
RUN npm run build

EXPOSE 5151
CMD ["http-server", "-p", "5151", "-S", "-C", "cert.pem", "-K", "key.pem", "dist", \
    "--proxy",  "https://0.0.0.0:5151?", "--proxy-options.secure", "false"]