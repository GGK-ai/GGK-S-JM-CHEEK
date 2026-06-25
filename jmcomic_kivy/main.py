# ===== JMComic 禁漫宝 - Kivy安卓版 =====
# 邪王真眼之力加持！✨
# 用Buildozer打包成APK即可在安卓上运行
# =========================================

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.utils import platform
from kivy.metrics import dp
import threading
import os

# 安卓存储权限
if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
    from android.storage import primary_external_storage_path
    DOWNLOAD_PATH = os.path.join(primary_external_storage_path(), 'Download', 'JMComic')
else:
    DOWNLOAD_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'JM下载')

import jmcomic
from jmcomic import JmOption


class JMComicLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=dp(5), padding=dp(10), **kwargs)
        self.client = None
        self.option = None
        self.current_album = None
        self.current_episodes = []

        # 标题
        title = Label(
            text='[b]邪王真眼 · 禁漫宝[/b]',
            markup=True,
            font_size=dp(20),
            color=(1, 0.4, 0.7, 1),
            size_hint=(1, 0.08)
        )
        self.add_widget(title)

        # 输入区域
        input_box = BoxLayout(size_hint=(1, 0.08), spacing=dp(5))
        input_box.add_widget(Label(text='车号：', size_hint=(0.15, 1), font_size=dp(16)))
        self.id_input = TextInput(
            text='',
            multiline=False,
            font_size=dp(18),
            size_hint=(0.55, 1),
            hint_text='输入禁漫车号',
            input_filter='int'
        )
        input_box.add_widget(self.id_input)
        self.search_btn = Button(
            text='查询',
            font_size=dp(16),
            background_color=(1, 0.4, 0.7, 1),
            size_hint=(0.3, 1)
        )
        self.search_btn.bind(on_press=self.search_album)
        input_box.add_widget(self.search_btn)
        self.add_widget(input_box)

        # 信息区域
        info_box = BoxLayout(size_hint=(1, 0.18))
        self.info_label = Label(
            text='输入车号点查询开始探索~',
            halign='left',
            valign='top',
            text_size=(self.width * 0.9, None),
            font_size=dp(14),
            color=(0.8, 0.8, 0.8, 1)
        )
        self.info_label.bind(width=lambda *a: setattr(self.info_label, 'text_size', (self.info_label.width * 0.95, None)))
        info_box.add_widget(self.info_label)
        self.add_widget(info_box)

        # 章节列表标题
        self.add_widget(Label(
            text='章节列表：',
            font_size=dp(14),
            color=(1, 1, 1, 1),
            size_hint=(1, 0.04),
            halign='left'
        ))

        # 章节列表
        scroll = ScrollView(size_hint=(1, 0.4))
        self.ep_list = GridLayout(cols=1, spacing=dp(3), size_hint_y=None, padding=dp(2))
        self.ep_list.bind(minimum_height=self.ep_list.setter('height'))
        scroll.add_widget(self.ep_list)
        self.add_widget(scroll)

        # 操作按钮
        btn_box = BoxLayout(size_hint=(1, 0.1), spacing=dp(8))

        self.preview_btn = Button(
            text='预览',
            font_size=dp(16),
            background_color=(0.3, 0.6, 0.9, 1),
            disabled=True
        )
        self.preview_btn.bind(on_press=self.preview_album)
        btn_box.add_widget(self.preview_btn)

        self.download_all_btn = Button(
            text='下载全部',
            font_size=dp(16),
            background_color=(0.9, 0.3, 0.2, 1),
            disabled=True
        )
        self.download_all_btn.bind(on_press=self.download_album)
        btn_box.add_widget(self.download_all_btn)

        self.add_widget(btn_box)

        # 状态栏
        self.status_label = Label(
            text='已就绪',
            font_size=dp(13),
            color=(0.6, 0.6, 0.6, 1),
            size_hint=(1, 0.05)
        )
        self.add_widget(self.status_label)

        Clock.schedule_once(self.init_client, 1)

    def init_client(self, dt=None):
        try:
            self.status_label.text = '正在初始化邪王真眼之力...'
            self.option = JmOption.default()
            self.client = self.option.new_jm_client()
            self.status_label.text = '连接成功！输入车号开始探索~'
        except Exception as e:
            self.status_label.text = '初始化失败，请检查网络'

    def search_album(self, instance=None):
        album_id = self.id_input.text.strip()
        if not album_id or not album_id.isdigit():
            self.show_popup('提示', '请输入正确的数字车号！')
            return

        self.search_btn.disabled = True
        self.search_btn.text = '查询中...'
        self.preview_btn.disabled = True
        self.download_all_btn.disabled = True
        self.ep_list.clear_widgets()
        self.info_label.text = '正在查询...'
        self.status_label.text = '正在查询...'

        threading.Thread(target=self._do_search, args=(album_id,), daemon=True).start()

    def _do_search(self, album_id):
        try:
            album = self.client.get_album_detail(album_id)
            self.current_album = album
            self.current_episodes = album.episode_list

            info = f'[b]标题：[/b]{album.title}\n'
            info += f'[b]作者：[/b]{album.author}\n'
            info += f'[b]章节：[/b]{len(self.current_episodes)}  总页数：{album.page_count}'

            Clock.schedule_once(lambda dt: self._update_ui(info), 0)

        except Exception as e:
            err = str(e)[:100]
            Clock.schedule_once(lambda dt: self._update_ui_error(err), 0)

    def _update_ui(self, info):
        self.info_label.text = info
        self.ep_list.clear_widgets()
        for pid, pidx, ptitle in self.current_episodes:
            btn_text = f'[{pidx}] {ptitle}'
            if len(btn_text) > 30:
                btn_text = btn_text[:28] + '...'
            ep_btn = Button(
                text=btn_text,
                size_hint_y=None,
                height=dp(42),
                background_color=(0.25, 0.25, 0.25, 1),
                color=(1, 1, 1, 1),
                font_size=dp(12),
                on_press=lambda btn, a=pid, b=pidx: self.download_single_episode(a, b)
            )
            self.ep_list.add_widget(ep_btn)

        self.preview_btn.disabled = False
        self.download_all_btn.disabled = False
        self.search_btn.disabled = False
        self.search_btn.text = '查询'
        self.status_label.text = f'找到 {len(self.current_episodes)} 个章节'

    def _update_ui_error(self, err):
        self.info_label.text = f'查询失败：{err}'
        self.search_btn.disabled = False
        self.search_btn.text = '查询'
        self.status_label.text = '查询失败，检查车号或网络'

    def preview_album(self, instance=None):
        if not self.current_album:
            return
        import webbrowser
        url = f'https://18comic.vip/photo/{self.current_album.id}'
        webbrowser.open(url)
        self.status_label.text = '已打开网页版'

    def download_album(self, instance=None):
        if not self.current_album:
            return
        album_id = self.current_album.id
        title = self.current_album.title
        save_dir = os.path.join(DOWNLOAD_PATH, f'{album_id}_{self._sanitize(title)}')

        try:
            os.makedirs(save_dir, exist_ok=True)
        except:
            pass

        self.show_popup('下载', f'开始下载《{title}》')

        self.download_all_btn.disabled = True
        self.download_all_btn.text = '下载中...'
        self.status_label.text = '正在下载...'

        threading.Thread(target=self._do_download_album, args=(album_id, save_dir), daemon=True).start()

    def _do_download_album(self, album_id, save_dir):
        try:
            opt_dict = {
                'dir_rule': {'rule': 'Bd_Aid_Atitle', 'base_dir': save_dir},
                'download': {'cache': True, 'image': {'decode': True, 'suffix': None}, 'threading': {'image': 30}},
                'client': {'impl': 'api', 'retry_times': 5,
                           'postman': {'type': 'curl_cffi', 'meta_data': {'impersonate': 'chrome', 'proxies': None}}}
            }
            opt = JmOption.construct(opt_dict)
            album, dler = jmcomic.download_album(album_id, opt)
            Clock.schedule_once(lambda dt: self._download_done(), 0)
        except Exception as e:
            Clock.schedule_once(lambda dt: self._download_error(str(e)[:100]), 0)

    def download_single_episode(self, photo_id, index, instance=None):
        if not self.current_album:
            return
        album = self.current_album
        title = f'第{index}章'
        save_dir = os.path.join(DOWNLOAD_PATH, f'{album.id}_{self._sanitize(album.title)}',
                                f'{int(index):03d}_{title}')

        try:
            os.makedirs(save_dir, exist_ok=True)
        except:
            pass

        self.show_popup('下载章节', f'开始下载{title}')
        self.status_label.text = f'正在下载{title}...'

        threading.Thread(target=self._do_download_ep, args=(photo_id, save_dir), daemon=True).start()

    def _do_download_ep(self, photo_id, save_dir):
        try:
            opt_dict = {
                'dir_rule': {'rule': 'Bd_Pname', 'base_dir': save_dir},
                'download': {'cache': True, 'image': {'decode': True, 'suffix': None}, 'threading': {'image': 30}},
                'client': {'impl': 'api', 'retry_times': 5,
                           'postman': {'type': 'curl_cffi', 'meta_data': {'impersonate': 'chrome', 'proxies': None}}}
            }
            opt = JmOption.construct(opt_dict)
            photo_obj, dler = jmcomic.download_photo(photo_id, opt)
            Clock.schedule_once(lambda dt: self._download_done(), 0)
        except Exception as e:
            Clock.schedule_once(lambda dt: self._download_error(str(e)[:100]), 0)

    def _download_done(self):
        self.download_all_btn.disabled = False
        self.download_all_btn.text = '下载全部'
        self.status_label.text = '下载完成！保存在手机 Download/JMComic 文件夹'

    def _download_error(self, err):
        self.download_all_btn.disabled = False
        self.download_all_btn.text = '下载全部'
        self.status_label.text = f'下载失败：{err}'

    def _sanitize(self, name):
        invalid = r'<>:"/\|?*'
        for c in invalid:
            name = name.replace(c, '_')
        return name.strip('. ')[:60]

    def show_popup(self, title, msg):
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        content.add_widget(Label(text=msg, font_size=dp(14)))
        btn = Button(text='确定', size_hint=(1, 0.4), background_color=(1, 0.4, 0.7, 1))
        content.add_widget(btn)
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
        btn.bind(on_press=popup.dismiss)
        popup.open()


class JMComicApp(App):
    def build(self):
        self.title = 'JMComic 禁漫宝'
        return JMComicLayout()


if __name__ == '__main__':
    jmcomic.disable_jm_log()
    JMComicApp().run()
