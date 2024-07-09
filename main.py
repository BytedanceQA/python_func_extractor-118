from util import fork_and_download_repo
from extract_func import traverse_repository

def download_and_extract_functions(repo_link):
    """
    下载 GitHub 仓库并提取其中的函数。

    参数:
    - repo_link: str, GitHub 仓库的链接。

    返回:
    - None
    """

    # fork_and_download_repo 下载仓库
    local_repo_path = fork_and_download_repo(repo_link, True)

    #  traverse_repository 提取本地仓库的函数
    if local_repo_path:
        traverse_repository(local_repo_path)
    else:
        print("下载仓库失败，无法提取函数。")


if __name__ == "__main__":
    repository_link = "https://github.com/xai-org/grok-1.git"
    download_and_extract_functions(repository_link)
