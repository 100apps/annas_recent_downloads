import requests
import time
import concurrent.futures
import logging
from datetime import datetime
import os


def get_recent_downloads(proxy_host="192.168.100.2", proxy_port="10081"):
    """
    获取最近下载列表
    
    Args:
        proxy_host (str): 代理服务器地址
        proxy_port (str): 代理服务器端口
    
    Returns:
        str: 响应内容
    """
    # 生成精确的时间戳字符串
    timestamp = str(time.time())
    url = "https://zh.annas-archive.org/dyn/recent_downloads/?rand=" + timestamp
    
    # 设置代理服务器
    proxies = {
        'http': f'http://{proxy_host}:{proxy_port}',
        'https': f'http://{proxy_host}:{proxy_port}'
    }
    
    # 使用代理发送请求
    response = requests.get(url, proxies=proxies)
    return f"{timestamp}\t{response.text}\n"


if __name__ == "__main__":
    # 设置进程池大小
    PROCESS_COUNT = 3
    # 每批次的请求数量
    BATCH_SIZE = 100
    
    i = 0
    while True:
        all_results = []
        
        # 创建进程池
        with concurrent.futures.ProcessPoolExecutor(max_workers=PROCESS_COUNT) as executor:
            # 提交多个任务到进程池
            futures = [executor.submit(get_recent_downloads) for _ in range(BATCH_SIZE)]
            
            # 获取所有任务的结果
            for future in concurrent.futures.as_completed(futures):
                try:
                    i += 1
                    result = future.result()
                    all_results.append(result)
                    print(f"完成第 {i} 次请求")
                except Exception as e:
                    logging.error(f"第 {i} 次请求失败: {str(e)}")
        
        # 写入文件
        current_date = datetime.now().strftime('%Y-%m-%d')
        output_file = f'{current_date}.txt'
        with open(output_file, 'a', encoding='utf-8') as f:
            f.write(''.join(all_results))
        
        print(f"所有结果已追加到 {output_file}")