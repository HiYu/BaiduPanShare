import requests
import json
import time
from typing import List

class BaiduPanShareGenerator:
    def __init__(self, cookie: str):
        self.session = requests.Session()
        self.session.headers.update({
            "Cookie": cookie,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        
    def get_fs_ids(self, dir_path: str) -> List[dict]:
        """获取目录下所有文件的fs_id列表"""
        params = {
            "dir": dir_path,
            "order": "time",
            "desc": 1,
            "showempty": 0
        }
        fs = []
        
        try:
            response = self.session.get("https://pan.baidu.com/api/list", params=params)
            response.raise_for_status()
            for item in response.json()["list"]:
                if item["isdir"] == 1:  # 如果是目录，递归处理
                    sub_dir_path = f"{dir_path}/{item['server_filename']}"
                    fs.extend(self.get_fs_ids(sub_dir_path))
                    print(sub_dir_path)
                  
                else:  # 如果是文件，记录fs_id
                    fs.append(item)
            return fs
           
        except Exception as e:
            print(f"获取文件列表失败: {str(e)}")
            return []

    def create_share(self, fs_ids: List[int], period: int = 7, pwd: str = None) -> dict:
        """创建批量分享链接"""
        payload = {
            "fid_list": json.dumps(fs_ids),
            "schannel": 4,
            "channel_list": "[]",
            "period": period,
            "pwd": pwd or ""
        }
        try:
            response = self.session.post("https://pan.baidu.com/share/set", data=payload)
            result = response.json()
            print(response.text)
            if result["errno"] == 0:
                return {
                    "link": result["link"],
                    "pwd": pwd or result["pwd"],
                    "expire": result["expiretime"]
                }
            raise Exception(f"API错误: {result['errmsg']}")
        except Exception as e:
            print(f"创建分享失败: {str(e)}")
            return {}

    def batch_process(self, dir_path: str, batch_size=50, period=7, pwd=None):
        """分批次处理文件"""
        fs = self.get_fs_ids(dir_path)
        fs_ids = [item["fs_id"] for item in fs]
        print(len(fs_ids))
        if not fs_ids:
            return []

        results = []
        for i in range(0, len(fs_ids), batch_size):
            batch = fs_ids[i:i+batch_size]
            result = self.create_share(batch, period, pwd)
            if result:
                new_result = {"server_filename": fs[i]["server_filename"],
                              "real_category": fs[i]["real_category"],
                              "size": fs[i]["size"],
                              "link":result["link"],
                              "pwd": result["pwd"],
                              "expire": result["expire"],
                              } # 保存fs_id和结果
                print(new_result)
                results.append(new_result)
                print(f"批次 {i//batch_size+1} 生成成功: {result['link']}")
                time.sleep(3)  # 防止触发频率限制
        return results

if __name__ == "__main__":
    # 配置参数（需自行获取有效Cookie）
    COOKIE = ""  # 获取方法见
    TARGET_DIRS = []    # 要分享的目录路径
    
    for TARGET_DIR in TARGET_DIRS:
        print(f"正在处理目录：{TARGET_DIR}")
        time.sleep(1)
        generator = BaiduPanShareGenerator(COOKIE)
        shares = generator.batch_process(
            dir_path=TARGET_DIR,
            batch_size=1,   # 每批处理文件数（免费用户不超过50）
            period=365,       # 有效期天数（0为永久）
            pwd="2025"       # 提取码（留空则系统随机生成）
        )
        
        # 输出结果到CSV
        split = TARGET_DIR.split("/")
        with open(f"{split[-1]}.csv", "w") as f:
            # f.write("书名,格式,大小,分享链接,提取码,过期时间\n")
            for share in shares:
                f.write(f"{share['server_filename']},{share['real_category']},{share['size']},{share['link']},{share['pwd']},{share['expire']}\n")
