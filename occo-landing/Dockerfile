# Sử dụng một hình ảnh Node.js chính thức làm hình ảnh cha
FROM node:18-alpine

# Thêm thông tin tác giả
LABEL author="CYDEVATECH <info@cydva.com>"

# Đặt thư mục làm việc trong container
WORKDIR /app

# Sao chép các file package.json vào container
COPY package.json ./

# Cài đặt các phụ thuộc
RUN yarn install && yarn cache clean

# Sao chép toàn bộ mã nguồn ứng dụng vào container
COPY . .

# Build ứng dụng
RUN yarn build

# Mở cổng 3000 để truy cập từ bên ngoài
EXPOSE 3000

# Lệnh để chạy ứng dụng Next.js
CMD ["yarn", "start"]
