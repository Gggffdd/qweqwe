FROM node:18-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

RUN npm run build

RUN npm install -g serve

CMD ["serve", "-s", "build", "-l", "3000"]
