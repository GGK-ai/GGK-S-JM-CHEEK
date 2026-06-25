# ===== JMComic 禁漫宝 - Kivy安卓轻量版 =====
# 邪王真眼之力加持！✨
# 使用requests代替curl_cffi，打包更轻松
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
import json
import os
import re

# 安卓存储路径
if platform == 'android':
    try:
        from android.permissions import request_permissions, Permission
        request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
        from android.storage import primary_external_storage_path
        DOWNLOAD_PATH = os.path.join(primary_external_storage_path(), 'Download', 'JMComic')
    except:
        DOWNLOAD_PATH = '/storage/emulated/0/Download/JMComic'
else:
    DOWNLOAD_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'JM下载')

import requests


class JMComicLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=dp(5), padding=dp(10), **kwargs)
        self.current_album = None
        self.current_episodes = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36',
            'Referer': 'https://18comic.vip/'
        })

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
            # 获取专辑信息
            url = f'https://18comic.vip/api/album/{album_id}'
            resp = self.session.get(url, timeout=30)

            if resp.status_code != 200:
                Clock.schedule_once(lambda dt: self._update_error(f'HTTP {resp.status_code}'), 0)
                return

            data = resp.json()

            if 'album' not in data:
                # 尝试从其他路径解析
                Clock.schedule_once(lambda dt: self._update_error('无法解析响应数据'), 0)
                return

            album_data = data['album']
            title = album_data.get('title', '未知标题')
            author = album_data.get('author', {}).get('name', '未知') if isinstance(album_data.get('author'), dict) else album_data.get('author', '未知')
            tags_list = album_data.get('tags', [])
            tags_str = ', '.join([t.get('name', '') for t in tags_list[:5] if isinstance(t, dict)]) if tags_list else '无标签'

            # 获取章节列表
            episodes = album_data.get('episodes', [])
            if not episodes:
                episodes = album_data.get('photos', [])

            self.current_episodes = []
            ep_list_display = []

            for ep in episodes:
                if isinstance(ep, dict):
                    ep_id = ep.get('id', '')
                    ep_idx = ep.get('index', ep.get('order', 0))
                    ep_title = ep.get('title', f'第{ep_idx}章')
                elif isinstance(ep, (list, tuple)):
                    ep_id = ep[0]
                    ep_idx = ep[1]
                    ep_title = ep[2] if len(ep) > 2 else f'第{ep_idx}章'
                else:
                    continue

                self.current_episodes.append((ep_id, ep_idx, ep_title))

            if not self.current_episodes:
                # 尝试从photo列表获取
                photos = album_data.get('photos', [])
                for p in photos:
                    if isinstance(p, dict):
                        pid = p.get('id', '')
                        pidx = p.get('index', 0)
                        ptitle = p.get('title', f'第{pidx}章')
                        self.current_episodes.append((pid, pidx, ptitle))

            info = f'[b]标题：[/b]{title}\n'
            info += f'[b]作者：[/b]{author}\n'
            info += f'[b]章节：[/b]{len(self.current_episodes)}'

            Clock.schedule_once(lambda dt: self._update_ui(info, title, album_id), 0)

        except Exception as e:
            err = str(e)[:100]
            Clock.schedule_once(lambda dt: self._update_error(err), 0)

    def _update_ui(self, info, title, album_id):
        self.info_label.text = info
        self.current_title = title
        self.current_id = album_id

        self.ep_list.clear_widgets()
        for ep_id, ep_idx, ep_title in self.current_episodes:
            btn_text = f'[{ep_idx}] {ep_title}'
            if len(btn_text) > 30:
                btn_text = btn_text[:28] + '...'
            ep_btn = Button(
                text=btn_text,
                size_hint_y=None,
                height=dp(42),
                background_color=(0.25, 0.25, 0.25, 1),
                color=(1, 1, 1, 1),
                font_size=dp(12),
                on_press=lambda btn, eid=ep_id, eidx=ep_idx: self.download_single_episode(eid, eidx)
            )
            self.ep_list.add_widget(ep_btn)

        self.preview_btn.disabled = False
        self.download_all_btn.disabled = False
        self.search_btn.disabled = False
        self.search_btn.text = '查询'
        self.status_label.text = f'找到 {len(self.current_episodes)} 个章节'

    def _update_error(self, err):
        self.info_label.text = f'查询失败：{err}'
        self.search_btn.disabled = False
        self.search_btn.text = '查询'
        self.status_label.text = '查询失败，检查车号或网络'

    def preview_album(self, instance=None):
        if not self.current_id:
            return
        import webbrowser
        url = f'https://18comic.vip/photo/{self.current_id}'
        webbrowser.open(url)
        self.status_label.text = '已打开网页版'

    def download_album(self, instance=None):
        if not self.current_id:
            return

        save_dir = os.path.join(DOWNLOAD_PATH, f'{self.current_id}_{self._sanitize(self.current_title)}')

        try:
            os.makedirs(save_dir, exist_ok=True)
        except:
            pass

        self.show_popup('下载', f'开始下载《{self.current_title}》（共{len(self.current_episodes)}章）')
        self.download_all_btn.disabled = True
        self.download_all_btn.text = '下载中...'
        self.status_label.text = '正在下载...'

        threading.Thread(target=self._do_download_all, args=(save_dir,), daemon=True).start()

    def _do_download_all(self, save_dir):
        try:
            for i, (ep_id, ep_idx, ep_title) in enumerate(self.current_episodes):
                Clock.schedule_once(lambda dt, idx=ep_idx: self.status_label.config(text=f'正在下载第{idx}章...'), 0)
                ep_save_dir = os.path.join(save_dir, f'{int(ep_idx):03d}_{self._sanitize(ep_title)}')
                self._download_episode_images(ep_id, ep_save_dir)

            Clock.schedule_once(lambda dt: self._download_done(), 0)
        except Exception as e:
            Clock.schedule_once(lambda dt, err=str(e)[:100]: self._download_error(err), 0)

    def download_single_episode(self, ep_id, ep_idx):
        ep_title = f'第{ep_idx}章'
        save_dir = os.path.join(DOWNLOAD_PATH, f'{self.current_id}_{self._sanitize(self.current_title)}',
                                f'{int(ep_idx):03d}_{ep_title}')

        try:
            os.makedirs(save_dir, exist_ok=True)
        except:
            pass

        self.show_popup('下载章节', f'开始下载{ep_title}')
        self.status_label.text = f'正在下载{ep_title}...'

        threading.Thread(target=self._do_download_single, args=(ep_id, save_dir), daemon=True).start()

    def _do_download_single(self, ep_id, save_dir):
        try:
            self._download_episode_images(ep_id, save_dir)
            Clock.schedule_once(lambda dt: self._download_done(), 0)
        except Exception as e:
            Clock.schedule_once(lambda dt, err=str(e)[:100]: self._download_error(err), 0)

    def _download_episode_images(self, ep_id, save_dir):
        """下载一个章节的所有图片"""
        try:
            os.makedirs(save_dir, exist_ok=True)

            # 获取章节图片列表
            url = f'https://18comic.vip/api/photo/{ep_id}'
            resp = self.session.get(url, timeout=30)

            if resp.status_code != 200:
                return

            data = resp.json()
            photo_data = data.get('photo', data)

            # 获取图片URL列表
            img_urls = []
            if 'images' in photo_data:
                img_urls = photo_data['images']
            elif 'img_list' in photo_data:
                img_urls = photo_data['img_list']

            if not img_urls:
                # 尝试从其他字段获取
                for key in ['imgs', 'pics', 'files', 'urls']:
                    if key in photo_data:
                        img_urls = photo_data[key]
                        break

            if not img_urls and isinstance(photo_data, list):
                img_urls = photo_data

            if not img_urls:
                Clock.schedule_once(lambda dt: self.log_text_append('没有找到图片链接'), 0)
                return

            # 下载每张图片
            for idx, img_url in enumerate(img_urls):
                if isinstance(img_url, dict):
                    img_url = img_url.get('url', img_url.get('src', ''))

                if not img_url or not isinstance(img_url, str):
                    continue

                # 确保URL完整
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                elif img_url.startswith('/'):
                    img_url = 'https://18comic.vip' + img_url

                try:
                    img_resp = self.session.get(img_url, timeout=60)
                    if img_resp.status_code == 200:
                        ext = '.jpg'
                        if 'image/png' in img_resp.headers.get('Content-Type', ''):
                            ext = '.png'
                        elif 'image/webp' in img_resp.headers.get('Content-Type', ''):
                            ext = '.webp'

                        fname = os.path.join(save_dir, f'{idx+1:04d}{ext}')
                        with open(fname, 'wb') as f:
                            f.write(img_resp.content)
                except:
                    continue

        except Exception as e:
            Clock.schedule_once(lambda dt, err=str(e)[:50]: self.log_text_append(f'下载出错：{err}'), 0)

    def log_text_append(self, text):
        self.status_label.text = text

    def _download_done(self):
        self.download_all_btn.disabled = False
        self.download_all_btn.text = '下载全部'
        self.status_label.text = '下载完成！保存在 Download/JMComic 文件夹'

    def _download_error(self, err):
        self.download_all_btn.disabled = False
        self.download_all_btn.text = '下载全部'
        self.status_label.text = f'下载失败：{err}'

    def _sanitize(self, name):
        if not name:
            return 'unnamed'
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
    JMComicApp().run()
