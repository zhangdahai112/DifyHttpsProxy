# DifyHttpsProxy 项目 README

## 一、项目概述
`lowTlsProxy` 是一个基于 Flask 构建的 HTTP 代理服务，其核心功能是将客户端的 HTTP 请求转发到指定的目标服务器。该项目主要用于解决在请求较低版本 HTTPS 协议时出现的协商不一致报错问题，通过创建自定义的 SSLContext 以启用不安全的旧版重新协商，确保请求能够顺利转发。

## 二、项目结构
```
lowTlsProxy/
├── proxy.py          # 主服务代码
├── Dockerfile        # 用于构建 Docker 镜像的文件
├── requirements.txt  # 项目依赖文件
```

## 三、环境要求
- Python 3.11.3 及以上版本
- Docker（如果选择使用 Docker 部署）

## 四、安装与配置

### 1. 克隆项目
```bash
git clone <项目仓库地址>
cd lowTlsProxy
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置环境变量
在运行项目之前，需要设置 `domain` 环境变量，该变量指定了请求要转发到的目标域名。
```bash
export domain=<目标域名>
```

## 五、运行项目

### 1. 直接运行 Python 脚本
```bash
python proxy.py
```
服务将在 `0.0.0.0:5000` 上启动。

### 2. 使用 Docker 部署
#### 构建 Docker 镜像
```bash
docker build -t lowtls-proxy .
```

#### 运行 Docker 容器
```bash
docker run -d -p 5000:5000 -e domain=<目标域名> lowtls-proxy
```
其中，`-d` 表示以守护进程模式运行容器，`-p 5000:5000` 表示将容器的 5000 端口映射到主机的 5000 端口，`-e domain=<目标域名>` 用于设置容器内的 `domain` 环境变量。

## 六、使用说明
### 1. 支持的请求方法
该代理服务支持 `GET` 和 `POST` 请求。

### 2. 请求转发示例
假设代理服务运行在 `http://localhost:5000`，目标域名设置为 `example.com`。

#### GET 请求
```bash
curl http://localhost:5000/some/path?param1=value1
```
该请求将被转发到 `https://example.com/some/path?param1=value1`。

#### POST 请求
```bash
curl -X POST -d "data=example" http://localhost:5000/another/path
```
该请求将被转发到 `https://example.com/another/path`，并携带 POST 数据。

## 七、注意事项
- **安全风险**：由于项目中使用了不安全的旧版重新协商（`ctx.set_ciphers("DEFAULT@SECLEVEL=1")` 和 `ctx.options |= 0x4`），这可能会带来一定的安全风险，建议仅在测试环境或受信任的网络中使用。
- **SSL 验证**：在 `forward_request` 函数中，`verify=False` 表示跳过 SSL 验证，这在生产环境中可能存在安全隐患，建议根据实际情况进行调整。

## 八、贡献与反馈
如果你发现了项目中的问题或有改进建议，欢迎提交 Issues 或 Pull Requests。

## 九、许可证
本项目采用 [MIT 许可证](LICENSE)。