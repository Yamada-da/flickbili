# Flickbili

使用GPT编写，拒绝大数据，本地实现链接脱敏
----------------------

写给自己用的，顺便开源了，缘由是b23.wtf偶尔被墙用起来不太顺畅<br />
匹配了一些网址特殊规则，其他网址则采用通用方式识别，如有测试失效网网址请提交issue(详见使用说明3)<br />

## 使用说明：
1. 复制包含网址的分享链接，点击"读取并处理剪贴板中的网址"选项，待处理结束后，点击对应需求按钮，即可复制到剪贴板<br />
2. "I am the God of Songs"按钮应用于Vrchat的台北纯K，旨在简化播放B站视频步骤，第一次使用需要复制纯K面板右下角解析前缀(或其他解析用链接)<br />
*如需修改可在任意界面长按"I am the God of Songs"按钮，即会弹出修改对话窗<br />
**链接会保存在软件目录下的flickbili.cfg中，如不再使用软件，此配置文件需要手动删除(Android除外，跟随软件自动删除)<br />
***已知BUG：在部分特殊分辨率下可能存在对话框文字错位，暂还没更好的方式文字实现左对齐(实力有限)<br />
3. 可以复制"jjj"(小写不含引号)后，点击"读取并处理剪贴板中的网址"选项，会在最下方新增debug菜单，在解析后可点击复制debug信息<br />
*软件bug、解析错误请提交issue(可以的话可附上过程描述、debug信息、版本号等(其中flickbili_xx_debug.exe版包含更详尽的debug信息))<br />


## 隐私说明：
1. 如同浏览器无痕模式，flickbili软件旨在：<br />
-不记录您的任何信息（除手动输入保存在本地的纯k解析前缀配置文件）<br />
-不使用服务器在线解析，请求全部由本地发起<br />
2. 以下各方仍有可能获取您的信息：<br />
-您的网络管理员<br />
-您的网络提供商<br />
-目标网站<br />


## 环境说明：
脚本由python编写，使用requests、beautifulsoup4库实现网页解析，kivy库实现跨平台界面前端<br />
Windows版使用PyInstaller、Android使用buildozer打包<br />
iOS可尝试使用第三方python IDE，并添加pip install requests beautifulsoup4 kivy库后运行<br />
打包程序中内嵌SourceHanSansSC字体 该字体遵循SIL OFL-1.1许可，详见 https://github.com/adobe-fonts/source-han-sans<br />


## (应该没那么)常见问题：
1. 如提示缺少configparser，尝试安装pip install configparser (尽管是Python标准库，但在某些Python版本中可能需要手动安装)<br />
2. kivy中的popup可能没有很好的实现文字对话框左对齐，Windows下应该没问题，其他平台暂时没找到可行方法(详见使用说明2)<br />
3. 如需替换字体，请复制字体到脚本根目录并更改font_filename = "字体名.后缀名"后使用/打包<br />


## 感谢名单：
大力提供测试的lulu<br />


## 灵感来源：
[无痛去除 b23.tv 追踪信息的解决方案。](https://b23.wtf/)<br />
https://github.com/nicholascw/b23.wtf<br />

[各大App的分享链接，正在偷窥你的朋友圈](https://36kr.com/p/2699872874903689)
