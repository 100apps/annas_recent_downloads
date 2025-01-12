import requests
import time
import concurrent.futures
import logging
from datetime import datetime
import os


# 配置日志记录
def setup_logging():
    """配置日志记录器"""
    current_date = datetime.now().strftime("%Y-%m-%d")
    log_file = f"crawler_{current_date}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),  # 同时输出到控制台
        ],
    )


def get_recent_downloads(proxy_host="192.168.100.2", proxy_port="10081"):
    """
    获取最近下载列表

    Args:
        proxy_host (str): 代理服务器地址
        proxy_port (str): 代理服务器端口

    Returns:
        str: 响应内容，如果状态码不是200则返回None
    """
    # 生成精确的时间戳字符串
    timestamp = str(time.time())
    url = "https://zh.annas-archive.org/dyn/recent_downloads/?rand=" + timestamp

    # 设置代理服务器
    proxies = {
        "http": f"http://{proxy_host}:{proxy_port}",
        "https": f"http://{proxy_host}:{proxy_port}",
    }

    # 使用代理发送请求,设置超时时间为5秒
    response = requests.get(url, proxies=proxies, timeout=5)

    # 检查状态码
    if response.status_code != 200:
        logging.error(f"请求失败，状态码: {response.status_code}")
        return None

    return f"{timestamp}\t{response.text}\n"


if __name__ == "__main__":
    # 初始化日志配置
    setup_logging()

    # 设置进程池大小
    PROCESS_COUNT = 3
    # 每批次的请求数量
    BATCH_SIZE = 100

    i = 0
    while True:
        all_results = []

        # 创建进程池
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=PROCESS_COUNT
        ) as executor:
            # 提交多个任务到进程池
            futures = [executor.submit(get_recent_downloads) for _ in range(BATCH_SIZE)]

            # 获取所有任务的结果
            for future in concurrent.futures.as_completed(futures):
                try:
                    i += 1
                    result = future.result()
                    if result:
                        all_results.append(result)
                        logging.info(f"完成第 {i} 次请求")
                    else:
                        logging.error(f"第 {i} 次请求失败 None: {str(e)}")
                except Exception as e:
                    logging.error(f"第 {i} 次请求失败: {str(e)}")

        # 写入文件
        current_date = datetime.now().strftime("%Y-%m-%d")
        output_file = f"{current_date}.txt"
        with open(output_file, "a", encoding="utf-8") as f:
            f.write("".join(all_results))

        logging.info(f"所有结果已追加到 {output_file}")
