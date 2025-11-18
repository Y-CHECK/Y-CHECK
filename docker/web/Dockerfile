# docker/web/Dockerfile
FROM nginx:alpine

# nginx 설정 파일 복사
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 정적 파일들 복사 (html, css, img 구조 그대로 유지)
COPY html /usr/share/nginx/html/
COPY css  /usr/share/nginx/html/css
COPY img  /usr/share/nginx/html/img
