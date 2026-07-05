# the-elderly-phone-manga
## 项目介绍
本项目允许用户在老人机的 WAP 浏览器(不支持 JS 和绝大多数 CSS)上使用 Pixiv。支持的功能:  
- [x] 搜索
    * [x] 搜索单图/漫画/小说/用户
    * [x] 搜索标签/小说正文
    * [x] 过滤 AI/R18/R18G
    * [x] 可设置最小收藏数，过滤低质量作品
    * [x] 可翻译作品标题，防止看不懂日语
- [x] 查看图片/漫画
    * [x] 方便地缩放和移动图片，防止在小屏幕上看不清
    * [x] 快速跳转查看作者的其他作品
    * [x] 快速跳转查看相同标签的作品
    * [x] 支持翻译漫画图片中的文字，防止看不懂日语
- [x] 查看小说
  * [x] 支持翻译小说文本，防止看不懂日语
  * [x] 快速跳转查看作者的其他作品
  * [x] 快速跳转查看相同标签的作品
- [x] 查看用户
  * [x] 查看用户的单图/漫画/小说作品
## 用户使用数据
该项目曾被部署在作者的一台服务器上，运行了大约 1 年 6 个月，为只被允许携带非智能机(老人机)进入校园的高中学生提供服务。

以下是从 2026 年 1 月 24 日到 2026 年 5 月 17 日(113 天)的部分真实用户统计数据：

1. 几乎所有请求都来自`诺基亚`老人机。
2. 独立 IP 数 389 个。
3. 搜索请求 2899 个。
4. 阅读小说的请求 15632 个。
5. 查看图片/漫画的请求 10545 个。
6. 最常被搜索的 10 个关键词和他们被搜索的次数:
    <details>
      <summary>展开</summary>
    
    | 标签   | 数量  |
    |------|-----|
    | 牧神记  | 108 |
    | TS百合 | 92  |
    | 变百   | 89  |
    | 放屁   | 64  |
    | 百合   | 53  |
    | 千咲   | 52  |
    | R-18 | 48  |
    | 主受   | 45  |
    | 近平   | 35  |
    | 18   | 27  |
    </details>
## 快速部署
### 服务器要求
1. 服务器需要在中国大陆以外，以便访问 Pixiv API
2. 服务器需要是 **Linux** 系统，因为本项目使用了一些仅能在 Linux 上运行的 Python 库
3. 服务器需要安装了 Docker
### 步骤
#### 一、获取 Pixiv API 密钥
1. 从仓库里下载`pixiv_auth.py`到你的电脑
2. 如果你使用的梯子设置了系统代理，请确认`pixiv_auth.py`的第 20 行的地址是否与你梯子设置的系统代理地址一致，如果不一致，请把代码中的地址改为你梯子客户端设置的系统代理的地址。
3. 在该文件所在的目录打开终端，输入
    ```bash
    python3 pixiv_auth.py login
    ```
    如果提示找不到模块`requests`，请先安装`requests`，然后重新运行上面的指令。
    ```bash
   pip install requests
   ```
4. 如果运行成功，你应该能看到浏览器窗口弹出，并打开 Pixiv 的登录页面
5. 请按`F12`打开开发者工具
6. 请切换到开发者工具的“网络”或者“Network”选项卡
7. 请勾选“保留日志”的复选框
8. 请回到登录页面，登录你的 Pixiv 账户
9. 请回到开发者工具，在顶部的“过滤”输入框(左侧有一个漏斗图标)输入`callback?`
10. 你应该能在下面的列表里看到一个`callback?state=......`的请求，点击它
11. 在弹出的窗口中打开“载荷”或者“Payload”选项卡
12. 复制`code`字段的值(也就是`code`右侧的看上去很随机的字符串)
13. 请回到终端，把刚刚复制的东西粘贴到终端的`code:`后面，然后按回车
14. 如果成功，你应该能看到终端显示了`access_token`、`refresh_token`和`expires_in`，请把他们复制粘贴到一个安全的地方，保留备用。
#### 二、申请百度翻译开发者账户
1. 到[百度翻译开放平台](https://fanyi-api.baidu.com/manage/developer)认证成为个人开发者
2. 申请成功后，你应该可以在“开发者信息”-“申请信息”看到`APP ID`和`密钥`(不是“API Key”, 是“开发者信息”里面的)。请把他们复制粘贴到一个安全的地方备用。
#### 三、创建 AI 翻译密钥
你可以选择使用 Gemini 或者 Cloudflare Workers AI 进行翻译，二者选其一即可。
##### 选择使用 Gemini
要使用 Gemini，你的服务器需要在能够访问 Gemini API 的区域，这样 AI 翻译才能正常工作  
   [Gemini 支持的区域](https://ai.google.dev/gemini-api/docs/available-regions?hl=zh-cn)
1. 到[AI Studio](https://aistudio.google.com/api-keys)创建一个 API 密钥，把它放在一个安全的位置备用。
##### 选择使用 Cloudflare Workers AI
1. 到[Cloudflare 控制面板](https://dash.cloudflare.com/)登录你的Cloudflare账户
2. 在左侧的菜单中，找到“构建”-“AI”-“Workers AI”并进入(如果你实在找不到，也可以按`Ctrl+K`然后直接搜索`Workers AI`)
3. 点击右上角的“REST API”
4. 在“获取帐户 ID”那里复制你的账户 ID，并把它放在一个安全的位置保留备用
5. 点击“创建 Workers AI API 令牌”
6. 在右侧弹出的侧边栏中给你的令牌起一个好名字，然后点击右下角的“创建 API 令牌”
7. 创建成功后，复制你的 API 令牌并把它放在一个安全的位置保留备用
#### 四、部署 Docker 容器
1. 下载仓库中的`docker-compose.yml`文件，这是一个最简的容器配置文件，可以让你最快地部署本项目。
2. 用文本编辑器打开`docker-compose.yml`
3. 把前面得到的 Pixiv `access_token`、`refresh_token`和`expires_in`依次填入`PIXIV_ACCESS_TOKEN`、`PIXIV_REFRESH_TOKEN`和`PIXIV_EXPIRE_IN`后面的双引号里
4. 把前面得到的百度翻译`APP ID`和`密钥`依次填入`BAIDU_TRANSLATE_APPID`和`BAIDU_TRANSLATE_SECRET`后面的双引号里
5. 如果你想使用 Gemini AI 翻译，请把`gemini`填入`AI_TRANSLATOR`后面的双引号里，然后把前面得到的 Gemini API 密钥填入`GEMINI_API_KEY`后面的双引号里；  
    如果你想使用 Cloudflare Workers AI，请把`cloudflare`填入`AI_TRANSLATOR`后面的双引号里，然后把前面得到的账户 ID 和 API 令牌依次填入`CF_ACCOUNT_ID`和`CF_API_TOKEN`后面的双引号里。
6. 保存并退出文本编辑器
7. 在服务器上创建一个空的目录
8. 把`docker-compose.yml`上传到该目录
9. 切换到该目录
10. 执行
    ```bash
    docker compose up -d
    ```
    Docker 应该会自己拉取所需要的镜像并启动容器
11. 如果你的服务器有防火墙或者安全组设置，请开放端口`5025`
12. 容器启动后，访问`http://你的服务器IP:5025/`应该就可以看到站点在正常运行
## 进一步配置
### 启用 https (建议的)
本项目本身不提供 SSL 支持，你可以通过一个反向代理(nginx 之类的)来配置 SSL 证书并启用 https 访问。
### 更改服务端口
要更改服务端口，请把`docker-compose.yml`里面第一个`5025`改成你喜欢的其他端口。
### 其他环境变量
除了`docker-compose.yml`里面列出的环境变量外，还有其他可选的环境变量。完整环境变量设置如下表。

| 环境变量名称                          | 描述                                                                                                         | 默认值(双引号代表空)                         |
|---------------------------------|------------------------------------------------------------------------------------------------------------|-------------------------------------|
| GUNICORN_WORKERS                | 用于处理请求的进程数，数值越大并发越高，但是占用内存也越高                                                                              | 2                                   |
| GUNICORN_KEEPALIVE              | HTTP 长连接保持时间，建议保持默认                                                                                        | 15                                  |
| GUNICORN_TIMEOUT                | 每个请求最长处理时间，建议保持默认                                                                                          | 30                                  |
| GUNICORN_MAX_REQUESTS           | 单个进程处理多少请求后自动重启，建议保持默认                                                                                     | 2000                                |
| GUNICORN_MAX_REQUESTS_JITTER    | 给`max_requests`加随机抖动，避免所有进程同时重启，建议保持默认                                                                     | 200                                 |
| ***GUNICORN_REAL_IP_HEADER***   | ***(重要)*** 如果你使用反向代理，请把这个字段设为存放客户端 IP 的请求头名称，比如`X-Forward-For`。如果不使用反向代理，请留空。                              | ""                                  |
| EPM_WINDOW_WIDTH                | 图片查看器中图片的宽度。根据老人机的屏幕分辨率设置，尽量和屏幕宽度像素相等。                                                                     | 240                                 |
| EPM_WINDOW_HEIGHT               | 图片查看器中图片的高度。根据老人机的屏幕分辨率设置，尽量比屏幕高度小一些。                                                                      | 240                                 |
| EPM_SEARCH_PAGE_AMOUNT_PER_PAGE | 搜索页面中每一页对应 Pixiv 上的多少页。太大会导致搜索时响应时间过长，太小会导致搜索页面结果太少，要频繁翻页。建议保持默认。                                          | 5                                   |
| REDIS_HOST                      | Redis 实例 IP 地址，如果你不使用`docker-compose.yml`一起部署 Redis，要使用外部 Redis 实例，则需要设置。                                  | 127.0.0.1                           |
| REDIS_PORT                      | Redis 实例端口。同上。                                                                                             | 6379                                |
| REDIS_PASSWORD                  | Redis 登录用户名。同上。                                                                                            | ""                                  |
| REDIS_USERNAME                  | Redis 登录密码。同上。                                                                                             | ""                                  |
| PIXIV_ACCESS_TOKEN              | 略。                                                                                                         | ""                                  |
| PIXIV_REFRESH_TOKEN             | 略。                                                                                                         | ""                                  |
| PIXIV_EXPIRE_IN                 | 略。                                                                                                         | 3600                                |
| PIXIV_WEB_COOKIES               | 使用 Pixiv 网页端搜索 API 时需要的 Cookie，但目前测试发现不用 Cookie 也可以，所以留空即可。                                                | ""                                  |
| PIXIV_WEB_UID                   | 同上，留空即可。                                                                                                   | ""                                  |
| PIXIV_SENTRY_TRACE              | 同上，留空即可。                                                                                                   | ""                                  |
| BAIDU_TRANSLATE_APPID           | 略。                                                                                                         | ""                                  |
| BAIDU_TRANSLATE_SECRET          | 略。                                                                                                         | ""                                  |
| AI_TRANSLATOR                   | 要使用哪个 AI 翻译服务，只能填`gemini`(使用 Gemini)或者`cloudflare`(使用 Cloudflare Workers AI)                               | "gemini"                            |
| GEMINI_API_KEY                  | 略。                                                                                                         | ""                                  |
| CF_ACCOUNT_ID                   | 略                                                                                                          | ""                                  |
| CF_API_TOKEN                    | 略                                                                                                          | ""                                  |
| CF_MODEL                        | 如果使用 Cloudflare Workers AI，要使用哪个 AI 模型进行翻译。[所有可用的模型](https://developers.cloudflare.com/workers-ai/models/) | @cf/qwen/qwen2.5-coder-32b-instruct |
### 日志
下表显示了日志在`epm`容器中的位置。`docker-compose.yml`中已默认把他们映射到`epm_log`数据卷。

| 日志   | 位置                    |
|------|-----------------------|
| 访问日志 | `/app/log/access.log` |
| 错误日志 | `/app/log/error.log`  |
### 缓存
#### 图片缓存
为了避免重复下载漫画图片，访问过一次的图片会被缓存。缓存目录在容器`epm`中的位置是`/app/cache`。

***为了防止缓存越来越大，建议设置 cronjob 定期清理(比如 2d 清理一次)***，清理时直接删除`/app/cache`下的所有文件即可。

`docker-compose.yml`中已默认把缓存映射到`epm_cache`数据卷。
#### 数据缓存
为了避免重复请求图片/小说信息、重复翻译相同内容等，访问过的内容的信息会被缓存在 Redis 中，不过由于空间占用小，无需清理。
## 报告问题
要报告问题，请附上对应错误日志和访问日志。
## 免责声明
本项目按“现状（as is）”提供，不提供任何形式的明示或暗示担保，包括但不限于适销性、特定用途适用性及非侵权性。
### 一、使用风险
使用本项目所产生的所有风险由使用者自行承担。项目作者及贡献者不对因使用、修改、部署或分发本项目而导致的任何直接或间接损失负责，包括但不限于数据丢失、服务中断、系统故障或业务损失。
### 二、Web 服务相关
本项目提供的 Web 服务仅用于技术学习与研究用途，不保证其可用性、稳定性或持续性。使用者应自行承担服务部署与运行过程中产生的安全风险与运维成本。
### 三、爬虫相关内容
本项目可能包含数据抓取（爬虫）功能，仅用于学习与技术研究目的。使用者应确保其行为符合目标网站的服务条款（Terms of Service）及相关法律法规。

因使用爬虫功能导致的任何法律责任、账号封禁、访问限制或其他后果，均由使用者自行承担，与项目作者无关。
### 四、AI 功能相关
本项目如包含人工智能或生成式模型相关功能，其输出结果可能存在不准确、不完整或过时的情况，不构成任何形式的专业建议（包括但不限于法律、金融、医疗或安全建议）。

使用者应对 AI 生成内容进行独立判断与验证，并对基于该内容采取的任何行为自行负责。
### 五、第三方依赖
本项目可能依赖第三方服务、API 或开源组件。其可用性、合法性与安全性均由相应提供方负责，本项目作者不承担相关责任。
### 六、责任限制
在适用法律允许的最大范围内，项目作者及贡献者不对任何形式的损害承担责任，包括但不限于直接损害、间接损害、附带损害或后果性损害。
