import re
import requests
from bs4 import BeautifulSoup
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.core.clipboard import Clipboard
from kivy.clock import Clock
from kivy.core.text import LabelBase
import webbrowser
from kivy.utils import platform
from kivy.core.window import Window
import platform
from kivy.uix.textinput import TextInput
import configparser #纯k实现，读取cfg用
from kivy.uix.anchorlayout import AnchorLayout
import os
import sys
import ctypes # 读取Windows缩放因素用

temp_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
print("<<<DEBUG>>>__file__:", __file__)
print("<<<DEBUG>>>temp_dir", temp_dir)
font_filename = "SourceHanSansSC-Normal-2.otf"
print("<<<DEBUG>>>fount_filename",font_filename)
font_path = os.path.join(temp_dir, font_filename)
print("<<<DEBUG>>>font_path",font_path)
try:
    # 尝试注册字体
    LabelBase.register(name='Roboto', fn_regular = font_path)
except Exception as e:
    print(f"Failed to register font: {e}")
    # 处理错误情况

# 设置窗口图标的路径（Android打包无需调整）
icon_filename = "icon.ico"
icon_path = os.path.join(temp_dir, icon_filename)
print("<<<DEBUG>>>icon_filename:", icon_path)


class ClipboardApp(App):
    def build(self):
        self.title = "flickbili"
        self.layout = BoxLayout(orientation='vertical')
        self.icon = icon_path  # 设置窗口图标的路径

        # 检测纯k按钮长按短按
        self.long_press_popup_shown = False  # 追踪长按窗口是否已弹出的标志

        #初始化纯k需要使用的解析后网址这个条件
        self.processed_url = None

        # 获取当前操作系统类型
        system = platform.system()
        # 如果操作系统是Windows，设置特定的宽高比
        if system == 'Windows':

            #读取Windows缩放因素
            user32 = ctypes.windll.user32
            dpi_scale = user32.GetDpiForSystem() / 96.0
            print("<<<DEBUG>>>user32:", user32)
            print("<<<DEBUG>>>dpi_scale:", dpi_scale)

            screen_width = Window.width / dpi_scale
            screen_height = Window.height / dpi_scale

            # 设置宽高比11:16
            desired_aspect_ratio = 11 / 16.0

            # 计算适合屏幕的窗口大小
            if screen_width / screen_height > desired_aspect_ratio:
                # 如果屏幕宽高比大于应用程序期望的宽高比，则根据高度调整宽度
                window_height = int(screen_height)
                window_width = int(window_height * desired_aspect_ratio)
            else:
                # 如果屏幕宽高比小于或等于应用程序期望的宽高比，则根据宽度调整高度
                window_width = int(screen_width)
                window_height = int(window_width / desired_aspect_ratio)

            # 设置窗口大小
            Window.size = (window_width, window_height)

        else:
            pass

        self.result_label = Label(
            text="按下按钮获取剪贴板中的网址信息",
            halign='center',  # 初始时居中对齐
            valign='middle',  # 垂直居中
            size_hint_y=None,  # 允许高度调整
        )

        self.result_label.bind(size=self.adjust_text_size)

        self.layout.add_widget(self.result_label)

        self.read_button = Button(text="读取并处理剪贴板中的网址", on_release=self.process_clipboard, background_color=(0.498, 1, 0.8314, 1))
        self.layout.add_widget(self.read_button)

        row3 = BoxLayout(orientation = "horizontal")
        self.copy_webpage_title_button = Button(text="复制网页名", on_release=self.copy_webpage_title, disabled=True, background_color=(0.5, 0.5, 0.5, 1))
        row3.add_widget(self.copy_webpage_title_button)

        self.copy_original_url_button = Button(text="复制网址", on_release=self.copy_original_url, disabled=True, background_color=(0.5, 0.5, 0.5, 1))
        row3.add_widget(self.copy_original_url_button)

        self.layout.add_widget(row3)

        row4 = BoxLayout(orientation = "horizontal")

        self.lets_ktv_button = Button(
            text="\"I am the God of Songs.\"",
            on_release=self.start_lets_ktv_short_press,
            on_touch_down=self.start_lets_ktv_long_press,
            on_touch_up=self.stop_lets_ktv_long_press,
            disabled=True,
            background_color=(0.5, 0.5, 0.5, 1)
        )
        row4.add_widget(self.lets_ktv_button)

        self.open_webpage_button = Button(text="在浏览器中打开", on_release=self.open_webpage, disabled=True, background_color=(0.5, 0.5, 0.5, 1))
        row4.add_widget(self.open_webpage_button)

        self.layout.add_widget(row4)

        self.copy_combined_button = Button(text="复制网页名和网址", on_release=self.copy_combined, disabled=True, background_color=(0.5, 0.5, 0.5, 1))
        self.layout.add_widget(self.copy_combined_button)

        self.copy_button = Button(text=f"<<<DEBUG>>>复制所有解析结果到剪贴板\n> {platform.platform().lower()}", on_release=self.copy_to_clipboard, disabled=True, background_color=(0.15, 0.15, 0.15, 1))
        self.layout.add_widget(self.copy_button)

        self.exit_button = Button(text="这个是闪退（<ゝω・）☆",on_release=self.stop, background_color=(0.15, 0.15, 0.15, 1))
        self.layout.add_widget(self.exit_button)

        self.easter_egg_button = Button(
            text=f'这个是版本号 0.9.3 ({platform.system()})',
            background_color=(0, 0, 0, 1),  # 黑色背景
            color=(0.3, 0.3, 0.3, 1),  # 灰色文字
            size_hint_y=None,
            height=80  # 高度可以根据需要调整
        )
        self.easter_egg_button.bind(on_press=self.on_easter_egg_click)
        self.layout.add_widget(self.easter_egg_button)

        self.ktv_click_count = 0

        # 添加一个空白的 Widget 留白，避免手机端触碰到 Home 菜单
        self.spacer = Widget(size_hint_y=None, height=60) # 高度可以根据需要调整
        self.layout.add_widget(self.spacer)

        Window.bind(on_resize=self.on_window_resize)  # 绑定窗口大小变化事件

        self.update_label_height(Window, Window.width, Window.height) # 初始时调用一次以设置正确的高度

        self.layout.remove_widget(self.copy_button)

        return self.layout

    # 按下读取并处理剪贴板中的网址后显示处理中...
    def process_clipboard(self, instance):
        self.result_label.text = "处理中..."
        self.result_label.halign = 'center'
        Clock.schedule_once(self._process_clipboard, 0.1)
        self.copy_webpage_title_button.disabled = True
        self.copy_original_url_button.disabled = True
        self.copy_combined_button.disabled = True
        self.open_webpage_button.disabled = True
        self.copy_button.disabled = True
        self.lets_ktv_button.disabled = True

    # 网址处理逻辑
    def _process_clipboard(self, instance):
        clipboard_content = Clipboard.paste()
        if clipboard_content == "jjj":
            self.layout.add_widget(self.copy_button)
            pass
        else:
            pass
        url_pattern = r'https?://\S+'
        urls = re.findall(url_pattern, clipboard_content)
        
        if urls:
            url = urls[0]
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
                }
                response = self.fetch_url_with_redirects(url, headers)

                # 检查响应头中的Content-Type是否包含字符编码信息
                if 'Content-Type' in response.headers:
                    content_type = response.headers['Content-Type']
                    if 'charset' not in content_type:
                        # 如果Content-Type中没有指定字符集，则将响应编码设置为UTF-8
                        response.encoding = 'utf-8'
                else:
                    # 如果响应头中没有Content-Type，则默认设置为UTF-8
                    response.encoding = 'utf-8'

                if 'bilivideo.com' in response.url:
                    self.result_label.text = "此为bilibili视频实际地址，需保留完整地址才可以访问\n地址将不会被处理，请点击下方复制网址或浏览器打开使用"
                    self.processed_url = response.url
                    self.copy_webpage_title_button.disabled = True
                    self.copy_original_url_button.disabled = False
                    self.copy_combined_button.disabled = True
                    self.open_webpage_button.disabled = False
                    self.copy_button.disabled = True
                    self.lets_ktv_button.disabled = True
                    return

                else:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    self.webpage_title = soup.title.string if soup.title else '无标题'
                    
                    self.original_url = response.url
                    process_error = 0

                    # Special handling for & URLs（额外处理列表，新增位 for '&'，24.6.24更新网址识别方案↓）
                    if any(domain in self.original_url for domain in ['google.com', 'bing.com', 'www.baidu.com']):
                        print("<<<DEBUG>>>识别到网址：", self.original_url)
                        self.processed_url = re.split(r'&', self.original_url, 1)[0]
                        print("<<<DEBUG>>>GBB处理：", self.processed_url)

                    # Special handling for & URLs（额外处理列表，新增位 for '?'）
                    elif any(domain in self.original_url for domain in ['kuaishou.com', 'chenzhongtech.com']):
                        self.processed_url = re.split(r'\?', self.original_url, 1)[0]
                        print("<<<DEBUG>>>kuaishou处理：", self.processed_url)

                    # Special handling for 163music URLs（额外处理列表，新增位 for {id}）
                    elif 'music.163.com' in self.original_url:
                        match = re.search(r'id=(\d+)', self.original_url)
                        if match:
                            id = match.group(1)
                            self.processed_url = f"https://music.163.com/#/song?id={id}"
                            print("<<<DEBUG>>>music.163.com处理：", self.processed_url)

                    # Special handling for pinduoduo URLs
                    elif 'mobile.yangkeduo.com' in self.original_url:
                        match = re.search(r'goods_id=(\d+)', self.original_url)
                        if match:
                            goods_id = match.group(1)
                            self.processed_url = f"https://mobile.yangkeduo.com/goods.html?goods_id={goods_id}"
                            print("<<<DEBUG>>>yangkeduo.com处理：", self.processed_url)

                    # Special handling for m.tb.cn URLs
                    elif 'm.tb.cn' in self.original_url:
                        lines = response.text.splitlines()
                        found_var_url = False
                        for line in lines:
                            if 'var url =' in line:
                                start_index = line.find('id=')
                                if start_index != -1:
                                    end_index = line.find('&', start_index)
                                    if end_index != -1:
                                        id_value = line[start_index + 3:end_index]
                                        self.processed_url = f'https://item.taobao.com/item.htm?id={id_value}'
                                        print("<<<DEBUG>>>m.tb.cn处理：", self.processed_url)
                                        found_var_url = True
                                        break

                        if not found_var_url:
                            error_label_text = "原始链接获取失败，可能是商品链接失效\n或是淘宝更新了代码，请尝试查找软件更新"
                            process_error = 1
                            print("未找到 'var url =' 值，可能淘宝已更新代码，请寻求软件更新")

                    # Special handling for taobao URLs
                    elif 'taobao.com' in self.original_url:
                        match = re.search(r'id=(\d+)', self.original_url)
                        if match:
                            id = match.group(1)
                            self.processed_url = f"https://item.taobao.com/item.htm?id={id}"
                            print("<<<DEBUG>>>taobao.com处理：", self.processed_url)

                    # Special handling for tmall URLs
                    elif 'detail.tmall.com' in self.original_url:
                        match = re.search(r'id=(\d+)', self.original_url)
                        if match:
                            id = match.group(1)
                            self.processed_url = f"https://detail.tmall.com/item.htm?id={id}"
                            print("<<<DEBUG>>>tmall.com处理：", self.processed_url)

                    # Special handling for baidu video URLs
                    elif 'baidu.com/video/' in self.original_url:
                        sign_match = re.search(r'sign=([\w]+)', self.original_url)
                        word_match = re.search(r'word=([^&]+)', self.original_url)
                        oword_match = re.search(r'oword=([^&]+)', self.original_url)
                        if sign_match and word_match and oword_match:
                            sign = sign_match.group(1)
                            word = word_match.group(1)
                            oword = oword_match.group(1)
                            self.processed_url = f"https://m.baidu.com/video/page?sign={sign}&word={word}&oword={oword}&atn=index"

                    # Special handling for www.bilibili.com URLs
                    elif 'www.bilibili.com' in self.original_url:
                        self.processed_url = re.sub(r'\?.*$', '', self.original_url)
                        print("<<<DEBUG>>>bili_processed_url:", self.processed_url)
                        self.lets_ktv_button.disabled = False

                    # Special handling for mall.bilibili.com URLs
                    elif 'mall.bilibili.com' in self.original_url:
                        match = re.search(r'itemsId=(\d+)', self.original_url)
                        if match:
                            itemsId = match.group(1)
                            self.processed_url = f"https://mall.bilibili.com/detail.html?itemsId={itemsId}"
                            print("<<<DEBUG>>>mall.bilibili.com处理：", self.processed_url)

                    # Special handling for show.bilibili.com URLs
                    elif 'show.bilibili.com' in self.original_url:
                        match = re.search(r'id=(\d+)', self.original_url)
                        if match:
                            id = match.group(1)
                            self.processed_url = f"https://show.bilibili.com/platform/detail.html?id={id}"
                            print("<<<DEBUG>>>show.bilibili.com处理：", self.processed_url)
                    

                    else:
                        self.processed_url = re.sub(r'\?.*$', '', self.original_url)
                        print("<<<DEBUG>>>标准处理的网址：", self.processed_url)

                    if process_error == 1:
                        self.result_label.text = error_label_text
                        self.result_label.halign = 'left'
                        self.copy_webpage_title_button.disabled = True
                        self.copy_original_url_button.disabled = True
                        self.copy_combined_button.disabled = True
                        self.open_webpage_button.disabled = True
                        self.copy_button.disabled = True
                        self.lets_ktv_button.disabled = True
                        return
                    else:
                        self.result_text = f"<<<DEBUG>>>\nwebpage_title: {self.webpage_title}\nurl: {url}\nresponse_url: {response.url}\nprocessed_url: {self.processed_url}\nplatform：{platform.platform().lower()}"
                        self.result_text_show = f"网页名: {self.webpage_title}\n网址: {self.processed_url}"
                        print("<<<DEBUG>>>输出的处理网址：", self.processed_url)
                        
                        self.result_label.text = self.result_text_show
                        self.result_label.halign = 'left'
                        self.copy_webpage_title_button.disabled = False
                        self.copy_original_url_button.disabled = False
                        self.copy_combined_button.disabled = False
                        self.open_webpage_button.disabled = False
                        self.copy_button.disabled = False

            except requests.RequestException as e:
                self.result_label.text = f"无法访问网址: {e}"
                self.result_label.halign = 'left'
                self.copy_webpage_title_button.disabled = True
                self.copy_original_url_button.disabled = True
                self.copy_combined_button.disabled = True
                self.open_webpage_button.disabled = True
                self.copy_button.disabled = True
                self.lets_ktv_button.disabled = True
        
        else:
            self.result_label.text = "剪贴板中未找到网址"
            self.copy_webpage_title_button.disabled = True
            self.copy_original_url_button.disabled = True
            self.copy_combined_button.disabled = True
            self.open_webpage_button.disabled = True
            self.copy_button.disabled = True
            self.lets_ktv_button.disabled = True
    
    # 处理重定向
    def fetch_url_with_redirects(self, url, headers):
        session = requests.Session()
        response = session.get(url, headers=headers, allow_redirects=True)
        
        # Log each URL in the redirect chain
        for history_response in response.history:
            print(f"Redirected from {history_response.url} to {response.url}")
        
        return response

    # 复制网页名
    def copy_webpage_title(self, instance):
        Clipboard.copy(self.webpage_title)
        self.result_label.text = f"网页名已复制到剪贴板\n{self.webpage_title}"
        self.result_label.halign = 'left'
        self.result_label.text_size = (self.result_label.width, None)
        self.result_label.multiline = False

    # 复制网址
    def copy_original_url(self, instance):
        Clipboard.copy(self.processed_url)
        self.result_label.text = f"网址已复制到剪贴板\n{self.processed_url}"
        self.result_label.halign = 'left'
        self.result_label.bind(size=self.adjust_text_size)
        self.result_label.multiline = False
    
    # 复制网页名和网址
    def copy_combined(self, instance):
        Clipboard.copy(f"【{self.webpage_title}】 {self.processed_url}")
        self.result_label.text = f"网页名和网址已复制到剪贴板\n{self.webpage_title}\n{self.processed_url}"
        self.result_label.halign = 'left'
        self.result_label.bind(size=self.adjust_text_size)
        self.result_label.multiline = False

    # 调用浏览器（iOS暂不保证ide支持）
    def open_webpage(self, instance):
        url = self.processed_url
        if platform == 'android':
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')

            intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
            currentActivity = PythonActivity.mActivity
            currentActivity.startActivity(intent)
        else:
            # 对于非 Android 平台，直接使用 webbrowser 模块
            webbrowser.open(url)

    # 复制到剪贴板
    def copy_to_clipboard(self, instance):
        Clipboard.copy(self.result_text)
        self.result_label.text = "<<<DEBUG>>>所有结果已复制到剪贴板"
        self.result_label.halign = 'center'  # 改为居中

    # 纯k短按处理
    def start_lets_ktv_short_press(self, instance):
        if not self.long_press_popup_shown:
            config_file = 'flickbili.cfg'
            config = configparser.ConfigParser()

            if os.path.exists(config_file): #加入检查cfg中网址是否正确
                config.read(config_file)
                if 'PARSER' in config and 'videoparserurl' in config['PARSER']:
                    video_parser_url = config['PARSER']['videoparserurl'].strip()
                    if self.is_valid_url(video_parser_url):
                        self.ktv_url = f"{video_parser_url}{self.original_url.split('/')[-2]}"
                        Clipboard.copy(self.ktv_url)
                        self.result_label.text = f"已复制到剪贴板，填入URL就可以播放啦\n{self.ktv_url}"
                        self.result_label.halign = 'left'
                        self.result_label.multiline = False
                        return
                    else:
                        self.show_error_message("请检查flickbili.cfg文件中的解析网址是否正确\n如需更改请长按\"I am the God of Songs.\"按钮")
                        return
            else:
                self.show_modify_url_popup(0)   
        else:
            pass

    # 简单的网址格式验证
    def is_valid_url(self, url):
        regex = re.compile(
            r'^(?:http|ftp)s?://' # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' # domain...
            r'localhost|' # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|' # ...or ipv4
            r'\[?[A-F0-9]*:[A-F0-9:]+\]?)' # ...or ipv6
            r'(?::\d+)?' # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return re.match(regex, url)

    # 纯k错误信息窗口
    def show_error_message(self, message):
        error_layout = BoxLayout(orientation='vertical', padding=10)

        error_label = Label(text=message, size_hint=(1, 0.8))
        error_layout.add_widget(error_label)

        confirm_button = Button(text='哈?  那我改?', size_hint=(0.5, 0.35))
        confirm_button.pos_hint = {'center_x': 0.5, 'y': 0}
        error_layout.add_widget(confirm_button)

        error_popup = Popup(title='嘿！有问题！', content=error_layout, size_hint=(None, None), size =(Window.width/1.5, Window.height/3), separator_color=(0.4, 0.8039, 0.6667, 1))
        confirm_button.bind(on_release=error_popup.dismiss)
        error_popup.open()
    
    # 长按修改网址的弹窗计时
    def start_lets_ktv_long_press(self, instance, touch):
        if instance.collide_point(*touch.pos):
            # 启动一个定时器，在1.25秒后执行显示弹出窗口的函数
            self.long_press_timer = Clock.schedule_once(self.show_modify_url_popup, 1.25)

    # 如果按钮被松开，取消定时器
    def stop_lets_ktv_long_press(self, instance, touch):
        if hasattr(self, 'long_press_timer'):
            self.long_press_timer.cancel()

    # 显示修改网址的弹出窗口的逻辑
    def show_modify_url_popup(self, dt):

        self.long_press_popup_shown = True

        popup = Popup(title="修改解析网址", size_hint=(None, None), size=(Window.width/1.04, Window.height/2.4), separator_color=(0.4, 0.8039, 0.6667, 1))
        
        popup_layout = BoxLayout(orientation='vertical', padding=10)

        prompt_label = Label(text="如需要更改请在下方文本框内输入：", size_hint=(1, 0.55))
        prompt_label.pos_hint = {'center_x': 0.34}
        popup_layout.add_widget(prompt_label)
        
        input_text = TextInput(text=self.load_config_value(), multiline=False, size_hint=(1, 0.6), hint_text="请在此输入网址，如: http://example.com/bili/api?id=")
        input_text.bind(focus=self.on_text_input_focus)  # 绑定焦点事件处理函数（未符合预期激活文本框，仍需要手动点击激活）
        popup_layout.add_widget(input_text)
        
        info_label = Label(text="*本按钮仅实现记录解析网址并合成BV号的简单功能\n初衷是用于台北纯k播放器，理论上也适用其它播放器", size_hint=(1, 1), color=(0.5, 0.5, 0.5, 1))
        info_label.pos_hint = {'center_x': 0.51}
        popup_layout.add_widget(info_label)

        button_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.7))
        
        save_button = Button(text='保存', size_hint=(1, 0.9))
        save_button.bind(on_release=lambda btn: self.save_url(input_text.text, popup))
        button_layout.add_widget(save_button)
        
        cancel_button = Button(text='取消', size_hint=(1, 0.9))
        cancel_button.bind(on_release=lambda btn: self.dismiss_popup_and_reset(popup))
        button_layout.add_widget(cancel_button)
        
        popup_layout.add_widget(button_layout)
        
        popup.content = popup_layout
        popup.open()

    # 自动全选<在此输入网址>功能
    def on_text_input_focus(self, instance, focused):
        if focused:
            # 当输入框获得焦点时，全选文本
            instance.select_all()
    
    # 读取配置文件中的网址
    def load_config_value(self):
        config = configparser.ConfigParser()
        try:
            config.read('flickbili.cfg')
            if 'PARSER' in config and 'videoparserurl' in config['PARSER']:
                return config['PARSER']['videoparserurl']
        except configparser.Error as e:
            print(f"Error reading config file: {e}")
            self.show_config_error_popup("读取配置文件失败", f"读取配置文件时发生错误：{e}")
        return ""

    # 保存用户输入的网址到配置文件
    def save_url(self, new_url, popup):
        config = configparser.ConfigParser()
        try:
            config.read('flickbili.cfg')
            if self.is_valid_url(new_url):
                if not config.has_section('PARSER'):
                    config['PARSER'] = {}
                config['PARSER']['videoparserurl'] = new_url
                with open('flickbili.cfg', 'w') as configfile:
                    config.write(configfile)

                if self.processed_url is not None and self.lets_ktv_button.disabled == False: #增加了#初始化纯k需要使用的解析后网址这个条件
                    self.ktv_url = f"{new_url}{self.original_url.split('/')[-2]}"
                    Clipboard.copy(self.ktv_url)
                    self.result_label.text = f"已保存在程序目录的flickbili.cfg文件下，需更改请长按\"I am the God of Songs.\"按钮\n解析网址已复制到剪贴板，填入URL就可以播放啦\n{self.ktv_url}"
                    self.result_label.halign = 'left'
                    popup.dismiss()
                    self.long_press_popup_shown = False
                else:
                    self.result_label.text = f"已保存在程序目录的flickbili.cfg文件下，需更改请长按\"I am the God of Songs.\"按钮"
                    self.result_label.halign = 'left'
                    popup.dismiss()
                    self.long_press_popup_shown = False

            else:
                self.show_error_message("请检查输入的内容是否是网址\n如缺少http://或https://需补全")
                self.long_press_popup_shown = False
        except PermissionError as e:
            print(f"PermissionError: {e}")
            self.show_config_error_popup("权限错误", f"无法写入配置文件，请检查文件权限。\n{e}")
            self.long_press_popup_shown = False
        except configparser.Error as e:
            print(f"Error writing config file: {e}")
            self.show_config_error_popup("写入配置文件失败", f"写入配置文件时发生错误：\n{e}")
            self.long_press_popup_shown = False
        except FileNotFoundError as e:
            print(f"FileNotFoundError: {e}")
            # Handle file not found error
            self.show_config_error_popup("文件未找到", f"指定的文件不存在。\n{e}")
            self.long_press_popup_shown = False
        except IOError as e:
            print(f"IOError: {e}")
            # Handle IO error
            self.show_config_error_popup("IO错误", f"文件操作失败。\n{e}")
            self.long_press_popup_shown = False
        except UnicodeDecodeError as e:
            print(f"UnicodeDecodeError: {e}")
            # Handle Unicode decode error
            self.show_config_error_popup("编码错误", f"无法解码文件内容。\n{e}")
            self.long_press_popup_shown = False
        except ValueError as e:
            print(f"ValueError: {e}")
            # Handle value error
            self.show_config_error_popup("数值错误", f"操作参数错误。\n{e}")
            self.long_press_popup_shown = False
        except OSError as e:
            print(f"OSError: {e}")
            # Handle OS error
            self.show_config_error_popup("操作系统错误", f"操作系统产生错误。\n{e}")
            self.long_press_popup_shown = False
        except Exception as e:
            print(f"未知故障: {e}")
            # Handle any other unexpected exceptions
            self.show_config_error_popup("未知故障", f"发生了未知的异常，请联系作者\n{e}")
            self.long_press_popup_shown = False

    # 取消按钮的实现和重置长按变量
    def dismiss_popup_and_reset(self, popup):
        popup.dismiss()
        self.long_press_popup_shown = False

    # 错误信息弹窗
    def show_config_error_popup(self, title, message):
        error_popup = Popup(title=title, content=Label(text=message), size_hint=(None, None), size=(Window.width/1.1, Window.height/3), separator_color=(0.4, 0.8039, 0.6667, 1))
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        label = Label(text=message)
        btn_layout = AnchorLayout(anchor_x='center', anchor_y='bottom', size_hint_y=None, height=50)
        btn = Button(text='确定', size_hint=(None, None), size=(Window.width * 0.2, Window.height * 0.06))
        btn.bind(on_press=error_popup.dismiss)
        btn_layout.add_widget(btn)
        layout.add_widget(label)
        layout.add_widget(btn_layout)
        error_popup.content = layout
        error_popup.open()

    # 彩蛋计数部分
    def on_easter_egg_click(self, instance):
        self.ktv_click_count += 1
        if self.ktv_click_count % 5 == 0:
            self.show_popup()
   
    # 彩蛋弹出内容
    def show_popup(self):
        popup_content = BoxLayout(orientation='vertical')

        scrollview = ScrollView(size_hint=(1, 1))
        
        popup_label = Label(text=
"""本程序由GPT-CV(Ctrl+C+V)程序猿\nYamada(这要高亮) 编写\n但是↑这家伙完全不懂编程\n所以你的程序大概是\n靠着BUG和奇迹运行起来的\n后续可以的话希望开源\n(CV程序员这么菜也可以的话)\n测试版本可能存在BUG\n欢迎反馈(带上网址)\n后续版本暂希望能添加\n淘宝(难)、京东和拼多多\n(实力(GPT的)允许情况下)
\n---2024.6.20 v.0.7---\n新增网抑云, 拼多多, 快手脱敏\n新增支持Google, Bing, Baidu脱敏\n更新UA信息
\n---2024.6.21 v.0.8---\n新增百度搜索页面视频脱敏\n新增在浏览器打开选项\n增加网页编码判断\n未指定则默认UTF-8
\n---2024.6.24 v.0.8.4---\n页面编码解析效果差 回滚上一个版本\n改为仅为未指定编码网站添加UTF-8\n修复Google, Bing, Baidu脱敏\n小修引发大漏↑ →开心DEBUG一下午
\n---2024.6.24 v.0.8.5---\n更新了result_label的layout实现左对齐
\n---2024.6.26 v.0.8.6---\n适配Windows打包单文件程序(含图标)
\n---2024.6.27 v.0.8.7---\n更改界面layout优化按钮布局\n添加台北纯k链接转换按钮\n使用纯k提供的转换网址自动合成\n以提供给纯k使用\n理论也适用于其他播放器\n\"I am the God of Songs.\"\n\"我是歌神\"\nTranslate powered by GPT
\n---2024.6.29 v.0.8.8---\n\"I am the God of Songs.\"\n解析地址↑ 改为了由用户填写\n如需变更可长按此按钮修改
\n---2024.7.1 v.0.8.9---\n修正部分问题及提升稳定性\n终于有一天轮到我写这行字了\n翻译过来就是: 没增加新功能只是修bug\n具体来说是 完善了解析输入对话框\n修复了Android, iOS下的错位\n增加配置文件读写错误的报错\n修复bilibili解析的逻辑错误\n新增个别bilibili二级域名的解析\n增加debug开关 剪贴板复制jjj粘贴到\n"读取并处理剪贴板中的网址"中打开
\n---2024.7.12 v.0.8.9---\n没有升级(版本号)程序\n解析网址界面调整*n
\n---2024.7.18 v.0.9.0---\n再次调整解析网址界面\n支持了m.tb.cn的解析
\n---2024.7.18 v.0.9.1---\n优化大量冗余代码\n完善了m.tb.cn的解析
\n---2024.7.19 v.0.9.2---\n修复删减代码后纯k逻辑错误\n修复bili视频实际地址部分按钮闪退
\n---2024.7.20 v.0.9.3---\n调整了Windows下的缩放\n调整纯k按钮长按为1.25秒
\n---2024.7.31 v.0.9.3---\n没有升级(版本号)程序\n开源前精简冗余注释\n调整了Debug内容输出
----------------------------
本程序(除iOS)内嵌SourceHanSansSC字体\n该字体遵循OFL-1.1许可\n程序使用kivy库实现跨平台运行""", 
                            halign='center', valign='middle', color=(0.65, 0.65, 0.65, 1), size_hint_y=None)
        
        popup_label.bind(texture_size=popup_label.setter('size'))
        
        scrollview.add_widget(popup_label)
        
        close_button = Button(text='中嘞', size_hint=(0.3, 0.13))
        close_button.pos_hint = {'center_x': 0.5, 'y': 0}
        
        popup_content.add_widget(scrollview)
        popup_content.add_widget(close_button)
        
        popup = Popup(title="望周知", content=popup_content, size_hint=(0.8, 0.5), separator_color=(0.4, 0.8039, 0.6667, 1))
        close_button.bind(on_release=popup.dismiss)
        popup.open()

    # 更改result_label高度占比（屏幕占比）
    def update_label_height(self, instance, width, height):
        self.result_label.height = height / 7.5

    # 窗口大小调整
    def on_window_resize(self, instance, width, height):
        self.update_label_height(instance, width, height)

    # 文字大小调整
    def adjust_text_size(self, instance, value):
        self.result_label.text_size = (self.result_label.width, None)

if __name__ == '__main__':
    ClipboardApp().run()