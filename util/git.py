import requests
import subprocess
import time
import os
from settings import TOKEN, USERNAME

token = TOKEN
username = USERNAME

def fork_and_download_repo(repository_link, need_download,local_path='/Users/bytedance/test_repo/BytedanceQA'):
    if repository_link.endswith('.git'):
        repository_link = repository_link[:-4]  
    owner, repo = repository_link.split('/')[3], repository_link.split('/')[4]
    print("所有者:", owner)
    print("仓库:", repo)
    
    # GitHub API的URL
    url = f"https://api.github.com/repos/{owner}/{repo}/forks"
    print(url)
    
    # 请求头
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
    }
    print(headers)
    
    # 发送POST请求创建一个fork
    response = requests.post(url, headers=headers)
    
    # 检查响应状态码
    if response.status_code == 202:
        print('仓库正在创建中...')
        forked_repo_url = ''
        # 检查仓库创建状态
        for _ in range(10):  # 尝试10次
            time.sleep(1)  # 每次等待6秒
            repo_info_response = requests.get(f"https://api.github.com/repos/{username}/{repo}", headers=headers)
            if repo_info_response.status_code == 200:
                print('仓库已成功创建')
                forked_repo_url = repo_info_response.json().get('html_url')
                print('Forked Repository URL:', forked_repo_url)
                break        
        if not forked_repo_url:
            print('仓库创建失败或超时')
            return        
        if need_download:
            # 下载仓库到本地
            local_path = local_path+'/'+repo
            download_repo(forked_repo_url,local_path)   
            return local_path     
    else:
        print(f'创建仓库时出错。状态码：{response.status_code}，错误信息：{response.text}')

def download_repo(repo_url, local_path):
    # 检查目标路径是否已存在
    if os.path.exists(local_path):
        print(f"仓库 '{local_path}' 已存在，跳过下载。")
        return True  
    else:
        # 执行git clone命令下载仓库
        try:
            subprocess.check_call(['git', 'clone', repo_url, local_path])
            return True  # 返回True表示下载成功
        except subprocess.CalledProcessError as e:
            print(f"下载仓库时出错。错误信息：{e}")
            return False  # 返回False表示下载失败
        


def save_to_csv(all_functions, directory, fieldnames):
    """ Save analyzed data to a CSV file. """
    output_file = os.path.join(directory, "dependency_analysis_results.csv")
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_functions)
    print(f"依赖分析完成。结果已保存到 {output_file}")

