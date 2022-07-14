FROM node:12
WORKDIR /
COPY /template .
RUN yarn cache clean
RUN yarn install
EXPOSE 3000