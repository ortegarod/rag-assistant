# syntax=docker/dockerfile:1
FROM node:18-bullseye as build

WORKDIR /app

COPY web/package.json web/package-lock.json ./
RUN npm ci

COPY web ./

# NEXT_PUBLIC_API_BASE is read at build time for client bundles
ARG NEXT_PUBLIC_API_BASE=http://localhost:8000
ENV NEXT_PUBLIC_API_BASE=$NEXT_PUBLIC_API_BASE

RUN npm run build

FROM node:18-bullseye
WORKDIR /app

ENV NODE_ENV=production \
    PORT=3000

COPY --from=build /app .

EXPOSE 3000

CMD ["npm", "run", "start", "--", "--port", "3000", "--hostname", "0.0.0.0"]

