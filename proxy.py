import logging

# 定义一个通用的转发函数
from flask import Flask, request, jsonify
import requests
import os
import ssl
import json

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],  # 输出到标准输出
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
domain = os.environ.get("domain")

# 检查 domain 值是否存在
if domain is None:
    logger.error("domain 环境变量未设置")
    raise ValueError("domain 环境变量未设置")


# 创建一个自定义的 SSLContext 以启用不安全的旧版重新协商
class TLSAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        ctx.set_ciphers("DEFAULT@SECLEVEL=1")
        # 完全禁用 SSL 重新协商
        ctx.options |= ssl.OP_NO_RENEGOTIATION
        kwargs["ssl_context"] = ctx
        return super(TLSAdapter, self).init_poolmanager(*args, **kwargs)


def forward_request(method, url, headers, data=None, params=None, verify=False):
    try:
        # return jsonify({"data": "你好"}), 200, {
        #         'Content-Type': 'application/json; charset=utf-8'
        #     }
        # Convert EnvironHeaders to a regular dictionary
        headers = dict(headers)
        headers.pop("Host", None)
        if method == "GET":
            session = requests.Session()
            session.mount("https://", TLSAdapter())
            logger.info(f"Sending GET request to {url}")
            response = session.get(url, headers=headers, params=params, verify=verify)
        elif method == "POST":
            session = requests.Session()
            session.mount("https://", TLSAdapter())
            logger.info(f"Sending POST request to {url}")
            response = session.post(
                url, headers=headers, data=data, params=params, verify=verify
            )
        else:
            logger.error(f"Unsupported HTTP method: {method}")
            return jsonify({"error": "Unsupported HTTP method"}), 405

        logger.info(
            f"Received response from {url} with status code {response.status_code}"
        )
        response.encoding = response.apparent_encoding
        # 尝试解析响应为 JSON
        try:
            response_data = response.json()
            # 转换 Unicode 编码并保持中文可读
            response_text = json.dumps(response_data, ensure_ascii=False)
            print("转换成功了！", flush=True)
            
            # 修正点：直接返回原始响应数据并设置 headers
            return (
                response_text, 
                response.status_code,
                {'Content-Type': 'application/json; charset=utf-8'}
            )
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析错误: {str(e)}")
            # 非 JSON 响应时直接返回原始内容
            return (
                response.content,
                response.status_code,
                {'Content-Type': response.headers.get('Content-Type', 'application/json; charset=utf-8') + '; charset=utf-8'}
            )
      
    except requests.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        return json.dumps({"error": str(e)}), 500, {'Content-Type': 'application/json'}


# 处理 GET 请求转发
@app.route("/<path:path>", methods=["GET"])
def forward_get(path):
    # 从 headers 中读取 domain，如果有则覆盖环境变量中的 domain
    header_domain = request.headers.get('domain')
    current_domain = header_domain if header_domain else domain
    target_url = f"http://{current_domain}/{path}"
    target_url = target_url.replace("http", "https")
    logger.info(f"Forwarding GET request to {target_url}")
    return forward_request("GET", target_url, request.headers, params=request.args)


# 处理 POST 请求转发
@app.route("/<path:path>", methods=["POST"])
def forward_post(path):
    # 从 headers 中读取 domain，如果有则覆盖环境变量中的 domain
    header_domain = request.headers.get('domain')
    current_domain = header_domain if header_domain else domain
    target_url = f"http://{current_domain}/{path}"
    target_url = target_url.replace("http", "https")
    logger.info(f"Forwarding POST request to {target_url}")
    return forward_request(
        "POST",
        target_url,
        request.headers,
        data=request.get_data(),
        params=request.args,
    )


if __name__ == "__main__":
    logger.info("Starting the Flask application on host 0.0.0.0:5000")
    app.config['JSON_AS_ASCII'] = False
    app.config['JSONIFY_MIMETYPE'] = "application/json;charset=utf-8"
    app.run(host="0.0.0.0", port=5000)
