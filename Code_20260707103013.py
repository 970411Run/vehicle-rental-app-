"""
╔══════════════════════════════════════════════════════╗
║     🚗  租车公司车辆管理系统 v2.0 - 手机版 🚗       ║
║     ✨ 车辆管理 · 租车管理 · 保险管理 · 费用结算     ║
║     ✨ 合同生成 · 图片上传 · 数据统计                ║
╚══════════════════════════════════════════════════════╝
"""

import os
import json
import shutil
from datetime import datetime, date
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.spinner import Spinner
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.properties import StringProperty, ListProperty, ObjectProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp

# 设置窗口大小（开发时模拟手机竖屏）
Window.size = (400, 750)

# ==================== 数据管理 ====================
DATA_DIR = "rental_data"
VEHICLES_FILE = os.path.join(DATA_DIR, "vehicles.json")
RENTALS_FILE = os.path.join(DATA_DIR, "rentals.json")
INSURANCES_FILE = os.path.join(DATA_DIR, "insurances.json")
IMAGES_DIR = os.path.join(DATA_DIR, "vehicle_images")
CONTRACTS_DIR = os.path.join(DATA_DIR, "contracts")
CONTRACTS_HTML_DIR = os.path.join(DATA_DIR, "contract_html")

for d in [DATA_DIR, IMAGES_DIR, CONTRACTS_DIR, CONTRACTS_HTML_DIR]:
    os.makedirs(d, exist_ok=True)

def load_json(filepath, default):
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return default

def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def gen_id():
    return datetime.now().strftime("%Y%m%d%H%M%S%f")

# ==================== 颜色主题 ====================
PRIMARY = (0.95, 0.30, 0.15, 1)       # 红色主色
PRIMARY_LIGHT = (1.0, 0.45, 0.30, 1)   # 浅红
BG_COLOR = (0.96, 0.96, 0.98, 1)        # 背景灰
CARD_BG = (1, 1, 1, 1)                  # 卡片白
TEXT_DARK = (0.15, 0.15, 0.2, 1)        # 深色文字
TEXT_GRAY = (0.5, 0.5, 0.55, 1)         # 灰色文字
SUCCESS = (0.20, 0.75, 0.35, 1)         # 绿色
WARNING = (0.95, 0.65, 0.10, 1)         # 橙色
DANGER = (0.90, 0.25, 0.25, 1)          # 红色
WHITE = (1, 1, 1, 1)

# ==================== 通用组件 ====================
def create_input(hint="", text="", password=False, multiline=False):
    """创建统一风格的输入框"""
    inp = TextInput(
        hint_text=hint,
        text=text,
        password=password,
        multiline=multiline,
        size_hint_y=None,
        height=dp(40),
        font_size=dp(14),
        background_normal='',
        background_active='',
        background_color=(0.97, 0.97, 0.99, 1),
        foreground_color=TEXT_DARK,
        hint_text_color=(0.6, 0.6, 0.65, 1),
        cursor_color=TEXT_DARK,
        padding=[dp(12), dp(8), dp(12), dp(8)],
        write_tab=False,
    )
    # 添加底部边框效果
    return inp

def create_button(text, color=PRIMARY, on_press=None, height=dp(44), font_size=dp(15), bold=True):
    """创建统一风格的按钮"""
    btn = Button(
        text=text,
        size_hint_y=None,
        height=height,
        font_size=font_size,
        bold=bold,
        background_normal='',
        background_down='',
        background_color=color,
        color=WHITE,
        on_press=on_press or (lambda x: None),
    )
    return btn

def create_label(text, font_size=dp(14), color=TEXT_DARK, bold=False, halign='left', size_hint_y=None, height=None):
    """创建统一风格的标签"""
    lbl = Label(
        text=text,
        font_size=font_size,
        color=color,
        bold=bold,
        halign=halign,
        valign='middle',
        size_hint_y=size_hint_y or None,
        height=height or dp(30),
        text_size=(None, None),
    )
    if halign != 'left':
        lbl.text_size=(lbl.width, None)
    return lbl

def create_title(text):
    """创建标题"""
    return create_label(text, font_size=dp(18), bold=True, color=PRIMARY, height=dp(40))

def create_subtitle(text):
    """创建副标题"""
    return create_label(text, font_size=dp(13), color=TEXT_GRAY, height=dp(24))

def create_card(content_widget):
    """创建卡片容器"""
    card = BoxLayout(
        orientation='vertical',
        size_hint_y=None,
        padding=[dp(16), dp(12), dp(16), dp(12)],
        spacing=dp(6),
    )
    # 设置背景
    from kivy.graphics import Color, RoundedRectangle
    card.bind(size=lambda *a: setattr(card, '_bg_rect', None) or card.canvas.before.clear() or (
        card.canvas.before.add(Color(1,1,1,1)),
        card.canvas.before.add(RoundedRectangle(size=card.size, pos=card.pos, radius=[dp(12)]))
    ))
    card.add_widget(content_widget)
    return card

def show_popup(title, message, is_error=False):
    """显示弹窗"""
    content = BoxLayout(orientation='vertical', spacing=dp(12), padding=dp(10))
    msg_color = DANGER if is_error else SUCCESS
    content.add_widget(Label(
        text=message,
        font_size=dp(14),
        color=msg_color,
        halign='center',
        valign='middle',
        text_size=(dp(250), None),
        size_hint_y=None,
        height=dp(60),
    ))
    btn = create_button("确定", height=dp(40), font_size=dp(14))
    content.add_widget(btn)
    
    popup = Popup(
        title=title,
        content=content,
        size_hint=(0.8, 0.4),
        auto_dismiss=False,
        title_color=PRIMARY,
        title_size=dp(16),
        separator_color=PRIMARY,
    )
    btn.bind(on_press=popup.dismiss)
    popup.open()

def show_confirm(title, message, on_confirm):
    """显示确认弹窗"""
    content = BoxLayout(orientation='vertical', spacing=dp(12), padding=dp(10))
    content.add_widget(Label(
        text=message,
        font_size=dp(14),
        color=TEXT_DARK,
        halign='center',
        valign='middle',
        text_size=(dp(250), None),
        size_hint_y=None,
        height=dp(50),
    ))
    btn_row = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(40))
    btn_cancel = create_button("取消", color=TEXT_GRAY, height=dp(40), font_size=dp(14))
    btn_ok = create_button("确认", color=DANGER, height=dp(40), font_size=dp(14))
    btn_row.add_widget(btn_cancel)
    btn_row.add_widget(btn_ok)
    content.add_widget(btn_row)
    
    popup = Popup(
        title=title,
        content=content,
        size_hint=(0.8, 0.4),
        auto_dismiss=False,
        title_color=PRIMARY,
        title_size=dp(16),
        separator_color=PRIMARY,
    )
    btn_cancel.bind(on_press=popup.dismiss)
    btn_ok.bind(on_press=lambda x: (popup.dismiss(), on_confirm()))
    popup.open()

# ==================== 主屏幕 ====================
class HomeScreen(Screen):
    """主菜单屏幕"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "home"
        
        main = BoxLayout(orientation='vertical', spacing=dp(0))
        
        # 顶部标题区
        header = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(140),
            padding=[dp(20), dp(20), dp(20), dp(10)],
        )
        from kivy.graphics import Color, Rectangle
        header.bind(size=lambda *a: header.canvas.before.clear() or (
            header.canvas.before.add(Color(*PRIMARY)),
            header.canvas.before.add(Rectangle(size=header.size, pos=header.pos))
        ))
        title = Label(
            text="🚗 租车管理系统",
            font_size=dp(24),
            bold=True,
            color=WHITE,
            size_hint_y=None,
            height=dp(40),
        )
        subtitle = Label(
            text="车辆 · 租车 · 保险 · 结算 · 合同",
            font_size=dp(13),
            color=(1, 1, 1, 0.8),
            size_hint_y=None,
            height=dp(24),
        )
        version = Label(
            text="v2.0 手机版",
            font_size=dp(11),
            color=(1, 1, 1, 0.6),
            size_hint_y=None,
            height=dp(18),
        )
        header.add_widget(title)
        header.add_widget(subtitle)
        header.add_widget(version)
        main.add_widget(header)
        
        # 功能按钮区
        scroll = ScrollView()
        btn_area = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=[dp(16), dp(16), dp(16), dp(20)],
            size_hint_y=None,
        )
        btn_area.bind(minimum_height=btn_area.setter('height'))
        
        menus = [
            ("🚗 车辆管理", PRIMARY, "vehicle"),
            ("📋 租车管理", (0.20, 0.55, 0.85, 1), "rental"),
            ("🛡️ 保险管理", (0.85, 0.60, 0.15, 1), "insurance"),
            ("💰 费用结算", (0.15, 0.70, 0.50, 1), "settlement"),
            ("📄 合同管理", (0.55, 0.30, 0.85, 1), "contract"),
            ("🔍 综合搜索", (0.60, 0.60, 0.65, 1), "search"),
            ("📊 数据统计", (0.90, 0.45, 0.10, 1), "stats"),
        ]
        
        for text, color, screen_name in menus:
            btn = create_button(
                text=text,
                color=color,
                height=dp(52),
                font_size=dp(17),
            )
            btn.bind(on_press=lambda x, sn=screen_name: setattr(self.manager, 'current', sn))
            btn_area.add_widget(btn)
        
        scroll.add_widget(btn_area)
        main.add_widget(scroll)
        
        self.add_widget(main)


# ==================== 车辆管理 ====================
class VehicleScreen(Screen):
    """车辆管理屏幕"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "vehicle"
        self.current_vehicle_id = None
        
        main = BoxLayout(orientation='vertical', spacing=0)
        
        # 顶部导航
        top_bar = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            padding=[dp(8), dp(6), dp(8), dp(6)],
        )
        from kivy.graphics import Color, Rectangle
        top_bar.bind(size=lambda *a: top_bar.canvas.before.clear() or (
            top_bar.canvas.before.add(Color(*PRIMARY)),
            top_bar.canvas.before.add(Rectangle(size=top_bar.size, pos=top_bar.pos))
        ))
        back_btn = Button(
            text="← 返回",
            size_hint_x=None,
            width=dp(70),
            font_size=dp(14),
            color=WHITE,
            background_normal='',
            background_down='',
            background_color=(0,0,0,0),
            on_press=lambda x: setattr(self.manager, 'current', 'home')
        )
        self.title_label = Label(
            text="车辆管理",
            font_size=dp(17),
            bold=True,
            color=WHITE,
        )
        add_btn = Button(
            text="+ 添加",
            size_hint_x=None,
            width=dp(70),
            font_size=dp(14),
            color=WHITE,
            background_normal='',
            background_down='',
            background_color=(0,0,0,0),
        )
        add_btn.bind(on_press=lambda x: self.show_add_dialog())
        top_bar.add_widget(back_btn)
        top_bar.add_widget(self.title_label)
        top_bar.add_widget(add_btn)
        main.add_widget(top_bar)
        
        # 选项卡
        tab_bar = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(0),
        )
        self.tab_list = Button(
            text="车辆列表",
            font_size=dp(13),
            color=PRIMARY,
            bold=True,
            background_normal='',
            background_down='',
            background_color=(0.95, 0.95, 0.97, 1),
        )
        self.tab_add = Button(
            text="添加/编辑",
            font_size=dp(13),
            color=TEXT_GRAY,
            background_normal='',
            background_down='',
            background_color=(0.92, 0.92, 0.95, 1),
        )
        self.tab_list.bind(on_press=lambda x: self.switch_tab('list'))
        self.tab_add.bind(on_press=lambda x: self.switch_tab('add'))
        tab_bar.add_widget(self.tab_list)
        tab_bar.add_widget(self.tab_add)
        main.add_widget(tab_bar)
        
        # 内容区
        self.content_area = BoxLayout(orientation='vertical')
        main.add_widget(self.content_area)
        
        self.add_widget(main)
        self.switch_tab('list')
    
    def switch_tab(self, tab):
        self.current_tab = tab
        if tab == 'list':
            self.tab_list.color = PRIMARY
            self.tab_list.bold = True
            self.tab_list.background_color = (0.95, 0.95, 0.97, 1)
            self.tab_add.color = TEXT_GRAY
            self.tab_add.bold = False
            self.tab_add.background_color = (0.92, 0.92, 0.95, 1)
            self.show_list()
        else:
            self.tab_add.color = PRIMARY
            self.tab_add.bold = True
            self.tab_add.background_color = (0.95, 0.95, 0.97, 1)
            self.tab_list.color = TEXT_GRAY
            self.tab_list.bold = False
            self.tab_list.background_color = (0.92, 0.92, 0.95, 1)
            self.show_add_form()
    
    def show_list(self):
        self.content_area.clear_widgets()
        
        vehicles = load_json(VEHICLES_FILE, [])
        
        if not vehicles:
            empty = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(40))
            empty.add_widget(Label(
                text="🚗",
                font_size=dp(50),
                size_hint_y=None,
                height=dp(70),
            ))
            empty.add_widget(Label(
                text="暂无车辆数据",
                font_size=dp(15),
                color=TEXT_GRAY,
                size_hint_y=None,
                height=dp(30),
            ))
            empty.add_widget(Label(
                text="点击上方「+ 添加」添加车辆",
                font_size=dp(12),
                color=(0.65, 0.65, 0.7, 1),
                size_hint_y=None,
                height=dp(24),
            ))
            self.content_area.add_widget(empty)
            return
        
        scroll = ScrollView()
        container = BoxLayout(
            orientation='vertical',
            spacing=dp(8),
            padding=[dp(12), dp(8), dp(12), dp(8)],
            size_hint_y=None,
        )
        container.bind(minimum_height=container.setter('height'))
        
        status_colors = {
            '空闲': SUCCESS,
            '已租': WARNING,
            '维修': DANGER,
            '停用': TEXT_GRAY,
        }
        
        for v in vehicles:
            card = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                padding=[dp(14), dp(10), dp(14), dp(10)],
                spacing=dp(4),
            )
            # 卡片背景
            from kivy.graphics import Color, RoundedRectangle
            card.bind(size=lambda w, *a, c=card: (
                c.canvas.before.clear(),
                c.canvas.before.add(Color(1,1,1,1)),
                c.canvas.before.add(RoundedRectangle(size=c.size, pos=c.pos, radius=[dp(10)]))
            ))
            
            # 第一行：车牌 + 状态
            row1 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(30))
            plate = Label(
                text=f"🚗 {v.get('plate', '')}",
                font_size=dp(16),
                bold=True,
                color=TEXT_DARK,
                halign='left',
                size_hint_x=0.7,
            )
            status = v.get('status', '空闲')
            sc = status_colors.get(status, TEXT_GRAY)
            status_label = Label(
                text=status,
                font_size=dp(12),
                bold=True,
                color=sc,
                halign='right',
                size_hint_x=0.3,
            )
            row1.add_widget(plate)
            row1.add_widget(status_label)
            card.add_widget(row1)
            
            # 第二行：品牌型号
            row2 = Label(
                text=f"{v.get('brand', '')} {v.get('model', '')}  |  {v.get('color', '')}  |  {v.get('year', '')}年",
                font_size=dp(12),
                color=TEXT_GRAY,
                halign='left',
                size_hint_y=None,
                height=dp(22),
            )
            card.add_widget(row2)
            
            # 第三行：操作按钮
            row3 = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(32),
                spacing=dp(6),
            )
            btn_view = Button(
                text="查看",
                font_size=dp(12),
                color=PRIMARY,
                background_normal='',
                background_down='',
                background_color=(0.95, 0.93, 0.93, 1),
                on_press=lambda x, vid=v['id']: self.view_vehicle(vid),
            )
            btn_edit = Button(
                text="编辑",
                font_size=dp(12),
                color=(0.20, 0.55, 0.85, 1),
                background_normal='',
                background_down='',
                background_color=(0.92, 0.95, 0.98, 1),
                on_press=lambda x, vid=v['id']: self.edit_vehicle(vid),
            )
            btn_del = Button(
                text="删除",
                font_size=dp(12),
                color=DANGER,
                background_normal='',
                background_down='',
                background_color=(0.98, 0.93, 0.93, 1),
                on_press=lambda x, vid=v['id'], vp=v.get('plate', ''): self.delete_vehicle(vid, vp),
            )
            row3.add_widget(btn_view)
            row3.add_widget(btn_edit)
            row3.add_widget(btn_del)
            card.add_widget(row3)
            
            container.add_widget(card)
        
        scroll.add_widget(container)
        self.content_area.add_widget(scroll)
    
    def show_add_form(self, vehicle_data=None):
        self.content_area.clear_widgets()
        self.current_vehicle_id = vehicle_data['id'] if vehicle_data else None
        
        scroll = ScrollView()
        form = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=[dp(16), dp(12), dp(16), dp(12)],
            size_hint_y=None,
        )
        form.bind(minimum_height=form.setter('height'))
        
        # 表单字段
        fields = [
            ("车牌号 *", "plate", "如：粤B12345"),
            ("品牌 *", "brand", "如：开瑞"),
            ("型号", "model", "如：江豚EV"),
            ("颜色", "color", "如：白色"),
            ("年份", "year", "如：2024"),
            ("车架号(VIN)", "vin", ""),
            ("发动机号", "engine_no", ""),
            ("购买日期", "purchase_date", "格式：2024-01-01"),
            ("日租金(元)", "daily_rent", "如：200"),
            ("里程(km)", "mileage", "如：5000"),
        ]
        
        self.inputs = {}
        for label_text, key, hint in fields:
            form.add_widget(create_label(label_text, font_size=dp(13), bold=True, height=dp(24)))
            inp = create_input(
                hint=hint,
                text=str(vehicle_data.get(key, '')) if vehicle_data and vehicle_data.get(key) else '',
            )
            self.inputs[key] = inp
            form.add_widget(inp)
        
        # 状态选择
        form.add_widget(create_label("车辆状态", font_size=dp(13), bold=True, height=dp(24)))
        self.status_spinner = Spinner(
            text=vehicle_data.get('status', '空闲') if vehicle_data else '空闲',
            values=('空闲', '已租', '维修', '停用'),
            size_hint_y=None,
            height=dp(40),
            font_size=dp(14),
            background_normal='',
            background_color=(0.97, 0.97, 0.99, 1),
            color=TEXT_DARK,
        )
        form.add_widget(self.status_spinner)
        
        # 备注
        form.add_widget(create_label("备注", font_size=dp(13), bold=True, height=dp(24)))
        self.remark_input = create_input("备注信息", multiline=True)
        self.remark_input.height = dp(60)
        if vehicle_data and vehicle_data.get('remark'):
            self.remark_input.text = vehicle_data['remark']
        form.add_widget(self.remark_input)
        
        # 保存按钮
        save_btn = create_button(
            "💾 保存车辆信息" if vehicle_data else "+ 添加车辆",
            height=dp(48),
            font_size=dp(16),
        )
        save_btn.bind(on_press=lambda x: self.save_vehicle())
        form.add_widget(save_btn)
        
        scroll.add_widget(form)
        self.content_area.add_widget(scroll)
    
    def save_vehicle(self):
        plate = self.inputs['plate'].text.strip()
        brand = self.inputs['brand'].text.strip()
        
        if not plate or not brand:
            show_popup("提示", "车牌号和品牌为必填项！", is_error=True)
            return
        
        vehicles = load_json(VEHICLES_FILE, [])
        
        # 检查车牌重复
        for v in vehicles:
            if v['plate'] == plate and v.get('id') != self.current_vehicle_id:
                show_popup("提示", f"车牌 {plate} 已存在！", is_error=True)
                return
        
        vehicle_data = {
            'id': self.current_vehicle_id or gen_id(),
            'plate': plate,
            'brand': brand,
            'model': self.inputs['model'].text.strip(),
            'color': self.inputs['color'].text.strip(),
            'year': self.inputs['year'].text.strip(),
            'vin': self.inputs['vin'].text.strip(),
            'engine_no': self.inputs['engine_no'].text.strip(),
            'purchase_date': self.inputs['purchase_date'].text.strip(),
            'daily_rent': self.inputs['daily_rent'].text.strip(),
            'mileage': self.inputs['mileage'].text.strip(),
            'status': self.status_spinner.text,
            'remark': self.remark_input.text.strip(),
            'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        if self.current_vehicle_id:
            for i, v in enumerate(vehicles):
                if v.get('id') == self.current_vehicle_id:
                    vehicle_data['created_at'] = v.get('created_at', vehicle_data['updated_at'])
                    vehicles[i] = vehicle_data
                    break
        else:
            vehicle_data['created_at'] = vehicle_data['updated_at']
            vehicles.append(vehicle_data)
        
        save_json(VEHICLES_FILE, vehicles)
        show_popup("成功", "车辆信息已保存！")
        self.switch_tab('list')
    
    def view_vehicle(self, vid):
        vehicles = load_json(VEHICLES_FILE, [])
        v = next((x for x in vehicles if x.get('id') == vid), None)
        if not v:
            show_popup("错误", "车辆不存在！", is_error=True)
            return
        
        content = BoxLayout(orientation='vertical', spacing=dp(8), padding=dp(10))
        scroll = ScrollView()
        info_box = BoxLayout(
            orientation='vertical',
            spacing=dp(6),
            size_hint_y=None,
        )
        info_box.bind(minimum_height=info_box.setter('height'))
        
        info_items = [
            ("车牌号", v.get('plate', '')),
            ("品牌", v.get('brand', '')),
            ("型号", v.get('model', '')),
            ("颜色", v.get('color', '')),
            ("年份", v.get('year', '')),
            ("车架号", v.get('vin', '')),
            ("发动机号", v.get('engine_no', '')),
            ("购买日期", v.get('purchase_date', '')),
            ("日租金", f"{v.get('daily_rent', '')} 元/天"),
            ("里程", f"{v.get('mileage', '')} km"),
            ("状态", v.get('status', '')),
            ("备注", v.get('remark', '')),
            ("创建时间", v.get('created_at', '')),
            ("更新时间", v.get('updated_at', '')),
        ]
        
        for label, value in info_items:
            item = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(28),
            )
            item.add_widget(Label(
                text=f"{label}：",
                font_size=dp(12),
                color=TEXT_GRAY,
                halign='left',
                size_hint_x=0.35,
                text_size=(None, None),
            ))
            item.add_widget(Label(
                text=str(value),
                font_size=dp(12),
                color=TEXT_DARK,
                halign='left',
                size_hint_x=0.65,
                text_size=(None, None),
            ))
            info_box.add_widget(item)
        
        scroll.add_widget(info_box)
        content.add_widget(scroll)
        
        btn_row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(8),
        )
        btn_close = create_button("关闭", color=TEXT_GRAY, height=dp(40), font_size=dp(14))
        btn_edit = create_button("编辑", color=(0.20, 0.55, 0.85, 1), height=dp(40), font_size=dp(14))
        btn_row.add_widget(btn_close)
        btn_row.add_widget(btn_edit)
        content.add_widget(btn_row)
        
        popup = Popup(
            title=f"🚗 {v.get('plate', '')} 详情",
            content=content,
            size_hint=(0.9, 0.75),
            title_color=PRIMARY,
            title_size=dp(16),
            separator_color=PRIMARY,
        )
        btn_close.bind(on_press=popup.dismiss)
        btn_edit.bind(on_press=lambda x: (popup.dismiss(), self.edit_vehicle(vid)))
        popup.open()
    
    def edit_vehicle(self, vid):
        vehicles = load_json(VEHICLES_FILE, [])
        v = next((x for x in vehicles if x.get('id') == vid), None)
        if v:
            self.current_vehicle_id = vid
            self.switch_tab('add')
            # 重新填充表单
            Clock.schedule_once(lambda dt: self.show_add_form(v), 0.1)
    
    def delete_vehicle(self, vid, plate):
        def do_delete():
            vehicles = load_json(VEHICLES_FILE, [])
            vehicles = [v for v in vehicles if v.get('id') != vid]
            save_json(VEHICLES_FILE, vehicles)
            show_popup("成功", f"车辆 {plate} 已删除！")
            self.show_list()
        
        show_confirm("确认删除", f"确定要删除车辆 {plate} 吗？此操作不可恢复！", do_delete)
    
    def show_add_dialog(self):
        self.current_vehicle_id = None
        self.switch_tab('add')


# ==================== 租车管理 ====================
class RentalScreen(Screen):
    """租车管理屏幕"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "rental"
        
        main = BoxLayout(orientation='vertical', spacing=0)
        
        # 顶部导航
        top_bar = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            padding=[dp(8), dp(6), dp(8), dp(6)],
        )
        from kivy.graphics import Color, Rectangle
        top_bar.bind(size=lambda *a: top_bar.canvas.before.clear() or (
            top_bar.canvas.before.add(Color(0.20, 0.55, 0.85, 1)),
            top_bar.canvas.before.add(Rectangle(size=top_bar.size, pos=top_bar.pos))
        ))
        back_btn = Button(
            text="← 返回",
            size_hint_x=None,
            width=dp(70),
            font_size=dp(14),
            color=WHITE,
            background_normal='',
            background_down='',
            background_color=(0,0,0,0),
            on_press=lambda x: setattr(self.manager, 'current', 'home')
        )
        title_label = Label(
            text="租车管理",
            font_size=dp(17),
            bold=True,
            color=WHITE,
        )
        add_btn = Button(
            text="+ 新增",
            size_hint_x=None,
            width=dp(70),
            font_size=dp(14),
            color=WHITE,
            background_normal='',
            background_down='',
            background_color=(0,0,0,0),
        )
        add_btn.bind(on_press=lambda x: self.show_add_form())
        top_bar.add_widget(back_btn)
        top_bar.add_widget(title_label)
        top_bar.add_widget(add_btn)
        main.add_widget(top_bar)
        
        # 选项卡
        tab_bar = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(0),
        )
        self.tab_list = Button(
            text="租车记录",
            font_size=dp(13),
            color=(0.20, 0.55, 0.85, 1),
            bold=True,
            background_normal='',
            background_down='',
            background_color=(0.93, 0.96, 0.98, 1),
        )
        self.tab_add = Button(
            text="新增租车",
            font_size=dp(13),
            color=TEXT_GRAY,
            background_normal='',
            background_down='',
            background_color=(0.92, 0.92, 0.95, 1),
        )
        self.tab_list.bind(on_press=lambda x: self.switch_tab('list'))
        self.tab_add.bind(on_press=lambda x: self.switch_tab('add'))
        tab_bar.add_widget(self.tab_list)
        tab_bar.add_widget(self.tab_add)
        main.add_widget(tab_bar)
        
        # 内容区
        self.content_area = BoxLayout(orientation='vertical')
        main.add_widget(self.content_area)
        
        self.add_widget(main)
        self.switch_tab('list')
    
    def switch_tab(self, tab):
        self.current_tab = tab
        if tab == 'list':
            self.tab_list.color = (0.20, 0.55, 0.85, 1)
            self.tab_list.bold = True
            self.tab_list.background_color = (0.93, 0.96, 0.98, 1)
            self.tab_add.color = TEXT_GRAY
            self.tab_add.bold = False
            self.tab_add.background_color = (0.92, 0.92, 0.95, 1)
            self.show_list()
        else:
            self.tab_add.color = (0.20, 0.55, 0.85, 1)
            self.tab_add.bold = True
            self.tab_add.background_color = (0.93, 0.96, 0.98, 1)
            self.tab_list.color = TEXT_GRAY
            self.tab_list.bold = False
            self.tab_list.background_color = (0.92, 0.92, 0.95, 1)
            self.show_add_form()
    
    def show_list(self):
        self.content_area.clear_widgets()
        
        rentals = load_json(RENTALS_FILE, [])
        rentals.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        if not rentals:
            empty = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(40))
            empty.add_widget(Label(text="📋", font_size=dp(50), size_hint_y=None, height=dp(70)))
            empty.add_widget(Label(text="暂无租车记录", font_size=dp(15), color=TEXT_GRAY, size_hint_y=None, height=dp(30)))
            self.content_area.add_widget(empty)
            return
        
        scroll = ScrollView()
        container = BoxLayout(
            orientation='vertical',
            spacing=dp(8),
            padding=[dp(12), dp(8), dp(12), dp(8)],
            size_hint_y=None,
        )
        container.bind(minimum_height=container.setter('height'))
        
        for r in rentals:
            card = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                padding=[dp(14), dp(10), dp(14), dp(10)],
                spacing=dp(4),
            )
            from kivy.graphics import Color, RoundedRectangle
            card.bind(size=lambda w, *a, c=card: (
                c.canvas.before.clear(),
                c.canvas.before.add(Color(1,1,1,1)),
                c.canvas.before.add(RoundedRectangle(size=c.size, pos=c.pos, radius=[dp(10)]))
            ))
            
            # 第一行：车牌 + 租车人
            row1 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(28))
            row1.add_widget(Label(
                text=f"🚗 {r.get('plate', '')}",
                font_size=dp(15),
                bold=True,
                color=TEXT_DARK,
                halign='left',
                size_hint_x=0.5,
            ))
            row1.add_widget(Label(
                text=f"👤 {r.get('renter_name', '')}",
                font_size=dp(14),
                color=TEXT_DARK,
                halign='right',
                size_hint_x=0.5,
            ))
            card.add_widget(row1)
            
            # 第二行：租期
            row2 = Label(
                text=f"📅 {r.get('start_date', '')} 至 {r.get('end_date', '')}",
                font_size=dp(12),
                color=TEXT_GRAY,
                halign='left',
                size_hint_y=None,
                height=dp(22),
            )
            card.add_widget(row2)
            
            # 第三行：费用信息
            row3 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(22))
            row3.add_widget(Label(
                text=f"租金：{r.get('total_rent', '')}元 | 押金：{r.get('deposit', '')}元",
                font_size=dp(11),
                color=TEXT_GRAY,
                halign='left',
                size_hint_x=0.6,
            ))
            status_text = "✅已还车" if r.get('return_date') else "🔄在租中"
            row3.add_widget(Label(
                text=status_text,
                font_size=dp(11),
                color=SUCCESS if r.get('return_date') else WARNING,
                halign='right',
                size_hint_x=0.4,
            ))
            card.add_widget(row3)
            
            container.add_widget(card)
        
        scroll.add_widget(container)
        self.content_area.add_widget(scroll)
    
    def show_add_form(self):
        self.content_area.clear_widgets()
        
        scroll = ScrollView()
        form = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=[dp(16), dp(12), dp(16), dp(12)],
            size_hint_y=None,
        )
        form.bind(minimum_height=form.setter('height'))
        
        # 加载车辆列表供选择
        vehicles = load_json(VEHICLES_FILE, [])
        idle_vehicles = [v for v in vehicles if v.get('status') == '空闲']
        vehicle_plates = [v['plate'] for v in idle_vehicles] if idle_vehicles else ['暂无空闲车辆']
        
        form.add_widget(create_label("选择车辆 *", font_size=dp(13), bold=True, height=dp(24)))
        self.plate_spinner = Spinner(
            text=vehicle_plates[0],
            values=vehicle_plates,
            size_hint_y=None,
            height=dp(40),
            font_size=dp(14),
            background_normal='',
            background_color=(0.97, 0.97, 0.99, 1),
            color=TEXT_DARK,
        )
        form.add_widget(self.plate_spinner)
        
        # 租车人信息
        form.add_widget(create_label("租车人信息", font_size=dp(14), bold=True, color=PRIMARY, height=dp(28)))
        
        renter_fields = [
            ("姓名 *", "renter_name", "租车人姓名"),
            ("身份证号 *", "id_number", ""),
            ("联系电话 *", "phone", ""),
            ("地址", "address", ""),
            ("驾驶证号", "license_no", ""),
        ]
        
        self.renter_inputs = {}
        for label_text, key, hint in renter_fields:
            form.add_widget(create_label(label_text, font_size=dp(13), bold=True, height=dp(24)))
            inp = create_input(hint=hint)
            self.renter_inputs[key] = inp
            form.add_widget(inp)
        
        # 租赁信息
        form.add_widget(create_label("租赁信息", font_size=dp(14), bold=True, color=PRIMARY, height=dp(28)))
        
        lease_fields = [
            ("起租日期 *", "start_date", "格式：2026-07-07"),
            ("到期日期 *", "end_date", "格式：2026-08-07"),
            ("日租金(元)", "daily_rent", "如：200"),
            ("租金总额(元) *", "total_rent", "如：6000"),
            ("押金(元)", "deposit", "如：2000"),
            ("起租里程(km)", "start_mileage", "如：5000"),
        ]
        
        self.lease_inputs = {}
        for label_text, key, hint in lease_fields:
            form.add_widget(create_label(label_text, font_size=dp(13), bold=True, height=dp(24)))
            inp = create_input(hint=hint)
            self.lease_inputs[key] = inp
            form.add_widget(inp)
        
        # 备注
        form.add_widget(create_label("备注", font_size=dp(13), bold=True, height=dp(24)))
        self.remark_input = create_input("备注信息", multiline=True)
        self.remark_input.height = dp(50)
        form.add_widget(self.remark_input)
        
        # 提交按钮
        submit_btn = create_button("📋 确认新增租车", color=(0.20, 0.55, 0.85, 1), height=dp(48), font_size=dp(16))
        submit_btn.bind(on_press=lambda x: self.save_rental())
        form.add_widget(submit_btn)
        
        scroll.add_widget(form)
        self.content_area.add_widget(scroll)
    
    def save_rental(self):
        plate = self.plate_spinner.text
        if plate == '暂无空闲车辆':
            show_popup("提示", "没有空闲车辆可供出租！", is_error=True)
            return
        
        name = self.renter_inputs['renter_name'].text.strip()
        id_number = self.renter_inputs['id_number'].text.strip()
        phone = self.renter_inputs['phone'].text.strip()
        
        if not name or not id_number or not phone:
            show_popup("提示", "租车人姓名、身份证号、联系电话为必填项！", is_error=True)
            return
        
        start_date = self.lease_inputs['start_date'].text.strip()
        end_date = self.lease_inputs['end_date'].text.strip()
        total_rent = self.lease_inputs['total_rent'].text.strip()
        
        if not start_date or not end_date or not total_rent:
            show_popup("提示", "起租日期、到期日期、租金总额为必填项！", is_error=True)
            return
        
        rental_data = {
            'id': gen_id(),
            'plate': plate,
            'renter_name': name,
            'id_number': id_number,
            'phone': phone,
            'address': self.renter_inputs['address'].text.strip(),
            'license_no': self.renter_inputs['license_no'].text.strip(),
            'start_date': start_date,
            'end_date': end_date,
            'daily_rent': self.lease_inputs['daily_rent'].text.strip(),
            'total_rent': total_rent,
            'deposit': self.lease_inputs['deposit'].text.strip(),
            'start_mileage': self.lease_inputs['start_mileage'].text.strip(),
            'return_date': '',
            'return_mileage': '',
            'damage_notes': '',
            'remark': self.remark_input.text.strip(),
            'settled': False,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'updated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        # 保存租车记录
        rentals = load_json(RENTALS_FILE, [])
        rentals.append(rental_data)
        save_json(RENTALS_FILE, rentals)
        
        # 更新车辆状态为空闲 -> 已租
        vehicles = load_json(VEHICLES_FILE, [])
        for v in vehicles:
            if v['plate'] == plate:
                v['status'] = '已租'
                break
        save_json(VEHICLES_FILE, vehicles)
        
        show_popup("成功", f"租车记录已创建！\n车辆 {plate} 已出租给 {name}")
        self.switch_tab('list')


# ==================== 保险管理 ====================
class InsuranceScreen(Screen):
    """保险管理屏幕"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "insurance"
        
        main = BoxLayout(orientation='vertical', spacing=0)
        
        # 顶部导航
        top_bar = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            padding=[dp(8), dp(6), dp(8), dp(6)],
        )
        from kivy.graphics import Color, Rectangle
        top_bar.bind(size=lambda *a: top_bar.canvas.before.clear() or (
            top_bar.canvas.before.add(Color(0.85, 0.60, 0.15, 1)),
            top_bar.canvas.before.add(Rectangle(size=top_bar.size, pos=top_bar.pos))
        ))
        back_btn = Button(
            text="← 返回",
            size_hint_x=None,
            width=dp(70),
            font_size=dp(14),
            color=WHITE,
            background_normal='',
            background_down='',
            background_color=(0,0,0,0),
            on_press=lambda x: setattr(self.manager, 'current', 'home')
        )
        title_label = Label(
            text="保险管理",
            font_size=dp(17),
            bold=True,
            color=WHITE,
        )
        add_btn = Button(
            text="+ 添加",
            size_hint_x=None,
            width=dp(70),
            font_size=dp(14),
            color=WHITE,
            background_normal='',
            background_down='',
            background_color=(0,0,0,0),
        )
        add_btn.bind(on_press=lambda x: self.show_add_form())
        top_bar.add_widget(back_btn)
        top_bar.add_widget(title_label)
        top_bar.add_widget(add_btn)
        main.add_widget(top_bar)
        
        # 选项卡
        tab_bar = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(0),
        )
        self.tab_list = Button(
            text="保险列表",
            font_size=dp(13),
            color=(0.85, 0.60, 0.15, 1),
            bold=True,
            background_normal='',
            background_down='',
            background_color=(0.98, 0.96, 0.93, 1),
        )
        self.tab_remind = Button(
            text="到期提醒",
            font_size=dp(13),
            color=TEXT_GRAY,
            background_normal='',
            background_down='',
            background_color=(0.92, 0.92, 0.95, 1),
        )
        self.tab_list.bind(on_press=lambda x: self.switch_tab('list'))
        self.tab_remind.bind(on_press=lambda x: self.switch_tab('remind'))
        tab_bar.add_widget(self.tab_list)
        tab_bar.add_widget(self.tab_remind)
        main.add_widget(tab_bar)
        
        # 内容区
        self.content_area = BoxLayout(orientation='vertical')
        main.add_widget(self.content_area)
        
        self.add_widget(main)
        self.switch_tab('list')
    
    def switch_tab(self, tab):
        self.current_tab = tab
        if tab == 'list':
            self.tab_list.color = (0.85, 0.60, 0.15, 1)
            self.tab_list.bold = True
            self.tab_list.background_color = (0.98, 0.96, 0.93, 1)
            self.tab_remind.color = TEXT_GRAY
            self.tab_remind.bold = False
            self.tab_remind.background_color = (0.92, 0.92, 0.95, 1)
            self.show_list()
        else:
            self.tab_remind.color = (0.85, 0.60, 0.15, 1)
            self.tab_remind.bold = True
            self.tab_remind.background_color = (0.98, 0.96, 0.93, 1)
            self.tab_list.color = TEXT_GRAY
            self.tab_list.bold = False
            self.tab_list.background_color = (0.92, 0.92, 0.95, 1)
            self.show_remind()
    
    def show_list(self):
        self.content_area.clear_widgets()
        
        insurances = load_json(INSURANCES_FILE, [])
        insurances.sort(key=lambda x: x.get('end_date', ''))
        
        if not insurances:
            empty = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(40))
            empty.add_widget(Label(text="🛡️", font_size=dp(50), size_hint_y=None, height=dp(70)))
            empty.add_widget(Label(text="暂无保险记录", font_size=dp(15), color=TEXT_GRAY, size_hint_y=None, height=dp(30)))
            self.content_area.add_widget(empty)
            return
        
        scroll = ScrollView()
        container = BoxLayout(
            orientation='vertical',
            spacing=dp(8),
            padding=[dp(12), dp(8), dp(12), dp(8)],
            size_hint_y=None,
        )
        container.bind(minimum_height=container.setter('height'))
        
        today = date.today()
        
        for ins in insurances:
            card = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                padding=[dp(14), dp(10), dp(14), dp(10)],
                spacing=dp(4),
            )
            from kivy.graphics import Color, RoundedRectangle
            card.bind(size=lambda w, *a, c=card: (
                c.canvas.before.clear(),
                c.canvas.before.add(Color(1,1,1,1)),
                c.canvas.before.add(RoundedRectangle(size=c.size, pos=c.pos, radius=[dp(10)]))
            ))
            
            # 第一行：车牌 + 保险类型
            row1 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(28))
            row1.add_widget(Label(
                text=f"🚗 {ins.get('plate', '')}",
                font_size=dp(15),
                bold=True,
                color=TEXT_DARK,
                halign='left',
                size_hint_x=0.5,
            ))
            row1.add_widget(Label(
                text=f"🛡️ {ins.get('type', '')}",
                font_size=dp(13),
                color=(0.85, 0.60, 0.15, 1),
                halign='right',
                size_hint_x=0.5,
            ))
            card.add_widget(row1)
            
            # 第二行：保险公司 + 保单号
            row2 = Label(
                text=f"{ins.get('company', '')} | {ins.get('policy_no', '')}",
                font_size=dp(12),
                color=TEXT_GRAY,
                halign='left',
                size_hint_y=None,
                height=dp(22),
            )
            card.add_widget(row2)
            
            # 第三行：保险期间 + 状态
            row3 = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(22))
            row3.add_widget(Label(
                text=f"{ins.get('start_date', '')} 至 {ins.get('end_date', '')}",
                font_size=dp(11),
                color=TEXT_GRAY,
                halign='left',
                size_hint_x=0.6,
            ))
            # 计算状态
            try:
                end = datetime.strptime(ins.get('end_date', '2099-01-01'), '%Y-%m-%d').date()
                days_left = (end - today).days
                if days_left < 0:
                    status_text = "❌已过期"
                    sc = DANGER
                elif days_left <= 30:
                    status_text = f"⚠️{days_left}天后到期"
                    sc = WARNING
                else:
                    status_text = "✅有效"
                    sc = SUCCESS
            except:
                status_text = "✅有效"
                sc = SUCCESS
            row3.add_widget(Label(
                text=status_text,
                font_size=dp(11),
                color=sc,
                halign='right',
                size_hint_x=0.4,
            ))
            card.add_widget(row3)
            
            container.add_widget(card)
        
        scroll.add_widget(container)
        self.content_area.add_widget(scroll)
    
    def show_remind(self):
        self.content_area.clear_widgets()
        
        insurances = load_json(INSURANCES_FILE, [])
        today = date.today()
        
        expiring = []
        expired = []
        for ins in insurances:
            try:
                end = datetime.strptime(ins.get('end_date', '2099-01-01'), '%Y-%m-%d').date()
                days_left = (end - today).days
                if days_left < 0:
                    expired.append((ins, days_left))
                elif days_left <= 30:
                    expiring.append((ins, days_left))
            except:
                pass
        
        scroll = ScrollView()
        container = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=[dp(16), dp(12), dp(16), dp(12)],
            size_hint_y=None,
        )
        container.bind(minimum_height=container.setter('height'))
        
        # 即将到期
        if expiring:
            container.add_widget(create_label("⚠️ 即将到期（30天内）", font_size=dp(14), bold=True, color=WARNING, height=dp(28)))
            for ins, days in sorted(expiring, key=lambda x: x[1]):
                item = BoxLayout(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=dp(30),
                    padding=[dp(8), dp(4), dp(8), dp(4)],
                )
                from kivy.graphics import Color, RoundedRectangle
                item.bind(size=lambda w, *a, c=item: (
                    c.canvas.before.clear(),
                    c.canvas.before.add(Color(1, 0.97, 0.92, 1)),
                    c.canvas.before.add(RoundedRectangle(size=c.size, pos=c.pos, radius=[dp(6)]))
                ))
                item.add_widget(Label(
                    text=f"{ins.get('plate', '')} - {ins.get('type', '')}",
                    font_size=dp(12),
                    color=TEXT_DARK,
                    halign='left',
                    size_hint_x=0.7,
                ))
                item.add_widget(Label(
                    text=f"{days}天后到期",
                    font_size=dp(12),
                    color=WARNING,
                    bold=True,
                    halign='right',
                    size_hint_x=0.3,
                ))
                container.add_widget(item)
        else:
            container.add_widget(create_label("✅ 无即将到期保险", font_size=dp(13), color=SUCCESS, height=dp(28)))
        
        # 已过期
        if expired:
            container.add_widget(create_label("❌ 已过期", font_size=dp(14), bold=True, color=DANGER, height=dp(28)))
            for ins, days in sorted(expired, key=lambda x: x[1]):
                item = BoxLayout(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=dp(30),
                    padding=[dp(8), dp(4), dp(8), dp(4)],
                )
                from kivy.graphics import Color, RoundedRectangle
                item.bind(size=lambda w, *a, c=item: (
                    c.canvas.before.clear(),
                    c.canvas.before.add(Color(1, 0.93, 0.93, 1)),
                    c.canvas.before.add(RoundedRectangle(size=c.size, pos=c.pos, radius=[dp(6)]))
                ))
                item.add_widget(Label(
                    text=f"{ins.get('plate', '')} - {ins.get('type', '')}",
                    font_size=dp(12),
                    color=TEXT_DARK,
                    halign='left',
                    size_hint_x=0.7,
                ))
                item.add_widget(Label(
                    text=f"已过期{-days}天",
                    font_size=dp(12),
                    color=DANGER,
                    bold=True,
                    halign='right',
                    size_hint_x=0.3,
                ))
                container.add_widget(item)
        
        if not expiring and not expired:
            container.add_widget(Label(
                text="🎉 所有保险均在有效期内！",
                font_size=dp(14),
                color=SUCCESS,
                halign='center',
                size_hint_y=None,
                height=dp(40),
            ))
        
        scroll.add_widget(container)
        self.content_area.add_widget(scroll)
    
    def show_add_form(self):
        self.content_area.clear_widgets()
        
        scroll = ScrollView()
        form = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=[dp(16), dp(12), dp(16), dp(12)],
            size_hint_y=None,
        )
        form.bind(minimum_height=form.setter('height'))
        
        # 加载车辆列表
        vehicles = load_json(VEHICLES_FILE, [])
        plates = [v['plate'] for v in vehicles] if vehicles else ['暂无车辆']
        
        form.add_widget(create_label("选择车辆 *", font_size=dp(13), bold=True, height=dp(24)))
        self.plate_spinner = Spinner(
            text=plates[0],
            values=plates,
            size_hint_y=None,
            height=dp(40),
            font_size=dp(14),
            background_normal='',
            background_color=(0.97, 0.97, 0.99, 1),
            color=TEXT_DARK,
        )
        form.add_widget(self.plate_spinner)
        
        ins_fields = [
            ("保险公司 *", "company", "如：中国人保"),
            ("保单号 *", "policy_no", ""),
            ("保险类型", "type", "如：交强险/商业险/三者险"),
            ("起始日期 *", "start_date", "格式：2026-01-01"),
            ("截止日期 *", "end_date", "格式：2027-01-01"),
            ("保费(元)", "premium", "如：3500"),
            ("保额(元)", "coverage", "如：1000000"),
        ]
        
        self.ins_inputs = {}
        for label_text, key, hint in ins_fields:
            form.add_widget(create_label(label_text, font_size=dp(13), bold=True, height=dp(24)))
            inp = create_input(hint=hint)
            self.ins_inputs[key] = inp
            form.add_widget(inp)
        
        # 备注
        form.add_widget(create_label("备注", font_size=dp(13), bold=True, height=dp(24)))
        self.remark_input = create_input("备注信息", multiline=True)
        self.remark_input.height = dp(50)
        form.add_widget(self.remark_input)
        
        # 提交按钮
        submit_btn = create_button("🛡️ 确认添加保险", color=(0.85, 0.60, 0.15, 1), height=dp(48), font_size=dp(16))
        submit_btn.bind(on_press=lambda x: self.save_insurance())
        form.add_widget(submit_btn)
        
        scroll.add_widget(form)
        self.content_area.add_widget(scroll)
    
    def save_insurance(self):
        plate = self.plate_spinner.text
        if plate == '暂无车辆':
            show_popup("提示", "请先添加车辆！", is_error=True)
            return
        
        company = self.ins_inputs['company'].text.strip()
        policy_no = self.ins_inputs['policy_no'].text.strip()
        start_date = self.ins_inputs['start_date'].text.strip()
        end_date = self.ins_inputs['end_date'].text.strip()
        
        if not company or not policy_no or not start_date or not end_date:
            show_popup("提示", "保险公司、保单号、起止日期为必填项！", is_error=True)
            return
        
        ins_data = {
            'id': gen_id(),
            'plate': plate,
            'company': company,
            'policy_no': policy_no,
            'type': self.ins_inputs['type'].text.strip(),
            'start_date': start_date,
            'end_date': end_date,
            'premium': self.ins_inputs['premium'].text.strip(),
            'coverage': self.ins_inputs['coverage'].text.strip(),
            'remark': self.remark_input.text.strip(),
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        insurances = load_json(INSURANCES_FILE, [])
        insurances.append(ins_data)
        save_json(INSURANCES_FILE, insurances)
        
        show_popup("成功", f"保险记录已添加！\n{plate} - {ins_data['type']}")
        self.switch_tab('list')


# ==================== 费用结算 ====================
class SettlementScreen(Screen):
    """费用结算屏幕"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "settlement"
        
        main = BoxLayout(orientation='vertical', spacing=0)
        
        # 顶部导航
        top_bar = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            padding=[dp(8), dp(6), dp(8), dp(6)],
        )
        from kivy.graphics import Color, Rectangle
        top_bar.bind(size=lambda *a: top_bar.canvas.before.clear() or (
            top_bar.canvas.before.add(Color(0.15, 0.70, 0.50, 1)),
            top_bar.canvas.before.add(Rectangle(size=top_bar.size, pos=top_bar.pos))
        ))
        back_btn = Button(
            text="← 返回",
            size_hint_x=None,
            width=dp(70),
            font_size=dp(14),
            color=WHITE,
            background_normal='',
            background_down='',
            background_color=(0,0,0,0),
            on_press=lambda x: setattr(self.manager, 'current', 'home')
        )
        title_label = Label(
            text="💰 费用结算",
            font_size=dp(17),
            bold=True,
            color=WHITE,
        )
        top_bar.add_widget(back_btn)
        top_bar.add_widget(title_label)
        top_bar.add_widget(BoxLayout(size_hint_x=None, width=dp(70)))  # 占位
        main.add_widget(top_bar)
        
        # 内容区
        scroll = ScrollView()
        self.form = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=[dp(16), dp(12), dp(16), dp(12)],
            size_hint_y=None,
        )
        self.form.bind(minimum_height=self.form.setter('height'))
        
        # 加载未还车的租车记录
        rentals = load_json(RENTALS_FILE, [])
        active_rentals = [r for r in rentals if not r.get('return_date')]
        rental_labels = []
        self.rental_map = {}
        if active_rentals:
            for r in active_rentals:
                label = f"{r['plate']} - {r['renter_name']} (到期:{r['end_date']})"
                rental_labels.append(label)
                self.rental_map[label] = r
        else:
            rental_labels = ['暂无在租记录']
        
        self.form.add_widget(create_label("选择租车记录 *", font_size=dp(13), bold=True, height=dp(24)))
        self.rental_spinner = Spinner(
            text=rental_labels[0],
            values=rental_labels,
            size_hint_y=None,
            height=dp(40),
            font_size=dp(14),
            background_normal='',
            background_color=(0.97, 0.97, 0.99, 1),
            color=TEXT_DARK,
        )
        self.form.add_widget(self.rental_spinner)
        
        # 还车信息
        self.form.add_widget(create_label("还车信息", font_size=dp(14), bold=True, color=(0.15, 0.70, 0.50, 1), height=dp(28)))
        
        return_fields = [
            ("实际还车日期 *", "return_date", "格式：2026-08-15"),
            ("还车里程(km)", "return_mileage", "如：8000"),
            ("损坏/违章备注", "damage_notes", "如：右后保险杠刮蹭"),
        ]
        
        self.return_inputs = {}
        for label_text, key, hint in return_fields:
            self.form.add_widget(create_label(label_text, font_size=dp(13), bold=True, height=dp(24)))
            inp = create_input(hint=hint)
            self.return_inputs[key] = inp
            self.form.add_widget(inp)
        
        # 费用信息
        self.form.add_widget(create_label("费用信息", font_size=dp(14), bold=True, color=(0.15, 0.70, 0.50, 1), height=dp(28)))
        
        fee_fields = [
            ("逾期费(元)", "overdue_fee", "自动计算或手动填写"),
            ("损坏/违章费(元)", "damage_fee", "如：500"),
        ]
        
        self.fee_inputs = {}
        for label_text, key, hint in fee_fields:
            self.form.add_widget(create_label(label_text, font_size=dp(13), bold=True, height=dp(24)))
            inp = create_input(hint=hint)
            self.fee_inputs[key] = inp
            self.form.add_widget(inp)
        
        # 计算按钮
        calc_btn = create_button("💰 计算费用", color=(0.15, 0.70, 0.50, 1), height=dp(44), font_size=dp(15))
        calc_btn.bind(on_press=lambda x: self.calculate_fees())
        self.form.add_widget(calc_btn)
        
        # 结果显示区
        self.result_area = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(4))
        self.form.add_widget(self.result_area)
        
        scroll.add_widget(self.form)
        main.add_widget(scroll)
        
        self.add_widget(main)
    
    def calculate_fees(self):
        self.result_area.clear_widgets()
        
        label = self.rental_spinner.text
        if label == '暂无在租记录':
            show_popup("提示", "没有在租的记录可供结算！", is_error=True)
            return
        
        rental = self.rental_map.get(label)
        if not rental:
            show_popup("提示", "租车记录不存在！", is_error=True)
            return
        
        return_date_str = self.return_inputs['return_date'].text.strip()
        if not return_date_str:
            show_popup("提示", "请填写实际还车日期！", is_error=True)
            return
        
        try:
            start = datetime.strptime(rental['start_date'], '%Y-%m-%d').date()
            end = datetime.strptime(rental['end_date'], '%Y-%m-%d').date()
            return_date = datetime.strptime(return_date_str, '%Y-%m-%d').date()
        except:
            show_popup("提示", "日期格式错误，请使用 YYYY-MM-DD 格式！", is_error=True)
            return
        
        # 计算实际天数
        actual_days = (return_date - start).days
        if actual_days < 0:
            actual_days = 0
        
        # 计算逾期
        overdue_days = (return_date - end).days
        if overdue_days < 0:
            overdue_days = 0
        
        try:
            daily_rent = float(rental.get('daily_rent', 0) or 0)
        except:
            daily_rent = 0
        
        actual_rent = actual_days * daily_rent
        overdue_fee = overdue_days * daily_rent * 1.5  # 1.5倍逾期费
        
        # 手动填写的逾期费
        try:
            manual_overdue = float(self.fee_inputs['overdue_fee'].text.strip() or 0)
        except:
            manual_overdue = 0
        if manual_overdue > 0:
            overdue_fee = manual_overdue
        
        try:
            damage_fee = float(self.fee_inputs['damage_fee'].text.strip() or 0)
        except:
            damage_fee = 0
        
        total_payable = actual_rent + overdue_fee + damage_fee
        
        try:
            deposit = float(rental.get('deposit', 0) or 0)
        except:
            deposit = 0
        
        balance = deposit - total_payable
        
        # 显示结果
        self.result_area.add_widget(create_label("📊 费用明细", font_size=dp(15), bold=True, color=(0.15, 0.70, 0.50, 1), height=dp(30)))
        
        result_items = [
            ("约定租金", f"{float(rental.get('total_rent', 0) or 0):.0f} 元"),
            ("实际租车天数", f"{actual_days} 天"),
            ("实际租金", f"{actual_rent:.0f} 元"),
            ("逾期天数", f"{overdue_days} 天"),
            ("逾期费", f"{overdue_fee:.0f} 元"),
            ("损坏/违章费", f"{damage_fee:.0f} 元"),
            ("应付总额", f"{total_payable:.0f} 元"),
            ("押金", f"{deposit:.0f} 元"),
        ]
        
        for label, value in result_items:
            item_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(26))
            item_row.add_widget(Label(
                text=label,
                font_size=dp(12),
                color=TEXT_GRAY,
                halign='left',
                size_hint_x=0.5,
            ))
            item_row.add_widget(Label(
                text=value,
                font_size=dp(13),
                color=TEXT_DARK,
                bold=True,
                halign='right',
                size_hint_x=0.5,
            ))
            self.result_area.add_widget(item_row)
        
        # 余额
        balance_color = SUCCESS if balance >= 0 else DANGER
        balance_text = f"{'应退' if balance >= 0 else '需补'}：{abs(balance):.0f} 元"
        self.result_area.add_widget(BoxLayout(size_hint_y=None, height=dp(8)))
        balance_row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(36),
            padding=[dp(8), dp(4), dp(8), dp(4)],
        )
        from kivy.graphics import Color, RoundedRectangle
        balance_row.bind(size=lambda w, *a, c=balance_row, col=balance_color: (
            c.canvas.before.clear(),
            c.canvas.before.add(Color(*((0.92, 0.98, 0.94, 1) if balance >= 0 else (0.98, 0.93, 0.93, 1)))),
            c.canvas.before.add(RoundedRectangle(size=c.size, pos=c.pos, radius=[dp(6)]))
        ))
        balance_row.add_widget(Label(
            text="结算结果",
            font_size=dp(13),
            color=TEXT_DARK,
            bold=True,
            halign='left',
            size_hint_x=0.4,
        ))
        balance_row.add_widget(Label(
            text=balance_text,
            font_size=dp(15),
            color=balance_color,
            bold=True,
            halign='right',
            size_hint_x=0.6,
        ))
        self.result_area.add_widget(balance_row)
        
        # 确认结算按钮
        confirm_btn = create_button("✅ 确认结算并还车", color=(0.15, 0.70, 0.50, 1), height=dp(48), font_size=dp(16))
        confirm_btn.bind(on_press=lambda x: self.confirm_settlement(rental, return_date_str, balance))
        self.result_area.add_widget(confirm_btn)
    
    def confirm_settlement(self, rental, return_date_str, balance):
        def do_settle():
            # 更新租车记录
            rentals = load_json(RENTALS_FILE, [])
            for r in rentals:
                if r.get('id') == rental['id']:
                    r['return_date'] = return_date_str
                    r['return_mileage'] = self.return_inputs['return_mileage'].text.strip()
                    r['damage_notes'] = self.return_inputs['damage_notes'].text.strip()
                    r['overdue_fee'] = float(self.fee_inputs['overdue_fee'].text.strip() or 0)
                    r['damage_fee'] = float(self.fee_inputs['damage_fee'].text.strip() or 0)
                    r['balance'] = balance
                    r['settled'] = True
                    r['updated_at'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    break
            save_json(RENTALS_FILE, rentals)
            
            # 更新车辆状态为空闲
            vehicles = load_json(VEHICLES_FILE, [])
            for v in vehicles:
                if v['plate'] == rental['plate']:
                    v['status'] = '空闲'
                    break
            save_json(VEHICLES_FILE, vehicles)
            
            show_popup("结算完成", f"还车成功！\n结算结果：{'应退' if balance >= 0 else '需补'}{abs(balance):.0f}元")
            
            # 刷新界面
            self.refresh_form()
        
        show_confirm("确认结算", f"确认完成结算并还车吗？\n{'退还' if balance >= 0 else '补缴'}金额：{abs(balance):.0f}元", do_settle)
    
    def refresh_form(self):
        """刷新表单"""
        self.form.clear_widgets()
        # 重新初始化
        rentals = load_json(RENTALS_FILE, [])
        active_rentals = [r for r in rentals if not r.get('return_date')]
        rental_labels = []
        self.rental_map = {}
        if active_rentals:
            for r in active_rentals:
                label = f"{r['plate']} - {r['renter_name']} (到期:{r['end_date']})"
                rental_labels.append(label)
                self.rental_map[label] = r
        else:
            rental_labels = ['暂无在租记录']
        
        self.form.add_widget(create_label("选择租车记录 *", font_size=dp(13), bold=True, height=dp(24)))
        self.rental_spinner = Spinner(
            text=rental_labels[0],
            values=rental_labels,
            size_hint_y=None,
            height=dp(40),
            font_size=dp(14),
            background_normal='',
            background_color=(0.97, 0.97, 0.99, 1),
            color=TEXT_DARK,
        )
        self.form.add_widget(self.rental_spinner)
        
        self.form.add_widget(create_label("还车信息", font_size=dp(14), bold=True, color=(0.15, 0.70, 0.50, 1), height=dp(28)))
        
        return_fields = [
            ("实际还车日期 *", "return_date", "格式：2026-08-15"),
            ("还车里程(km)", "return_mileage", "如：8000"),
            ("损坏/违章备注", "damage_notes", "如：右后保险杠刮蹭"),
        ]
        
        self.return_inputs = {}
        for label_text, key, hint in return_fields:
            self.form.add_widget(create_label(label_text, font_size=dp(13), bold=True, height=dp(24)))
            inp = create_input(hint=hint)
            self.return_inputs[key] = inp
            self.form.add_widget(inp)
        
        self.form.add_widget(create_label("费用信息", font_size=dp(14), bold=True, color=(0.15, 0.70, 0.50, 1), height=dp(28)))
        
        fee_fields = [
            ("逾期费(元)", "overdue_fee", "自动计算或手动填写"),
            ("损坏/违章费(元)", "damage_fee", "如：500"),
        ]
        
        self.fee_inputs = {}
        for label_text, key, hint in fee_fields:
            self.form.add_widget(create_label(label_text, font_size=dp(13), bold=True, height=dp(24)))
            inp = create_input(hint=hint)
            self.fee_inputs[key] = inp
            self.form.add_widget(inp)
        
        calc_btn = create_button("💰 计算费用", color=(0.15, 0.70, 0.50, 1), height=dp(44), font_size=dp(15))
        calc_btn.bind(on_press=lambda x: self.calculate_fees())
        self.form.add_widget(calc_btn)
        
        self.result_area = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(4))
        self.form.add_widget(self.result_area)


# ==================== 合同管理 ====================
class ContractScreen(Screen):
    """合同管理屏幕"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "contract"
        
        main = BoxLayout(orientation='vertical', spacing=0)
        
        # 顶部导航
        top_bar = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            padding=[dp(8), dp(6), dp(8), dp(6)],
        )
        from kivy.graphics import Color, Rectangle
        top_bar.bind(size=lambda *a: top_bar.canvas.before.clear() or (
            top_bar.canvas.before.add(Color(0.55, 0.30, 0.85, 1)),
            top_bar.canvas.before.add(Rectangle(size=top_bar.size, pos=top_bar.pos))
        ))
        back_btn = Button(
            text="← 返回",
            size_hint_x=None,
            width=dp(70),
            font_size=dp(14),
            color=WHITE,
            background_normal='',
            background_down='',
            background_color=(0,0,0,0),
            on_press=lambda x: setattr(self.manager, 'current', 'home')
        )
        title_label = Label(
            text="📄 合同管理",
            font_size=dp(17),
            bold=True,
            color=WHITE,
        )
        new_btn = Button(
            text="+ 生成",
            size_hint_x=None,
            width=dp(70),
            font_size=dp(14),
            color=WHITE,
            background_normal='',
            background_down='',
            background_color=(0,0,0,0),
        )
        new_btn.bind(on_press=lambda x: self.generate_contract())
        top_bar.add_widget(back_btn)
        top_bar.add_widget(title_label)
        top_bar.add_widget(new_btn)
        main.add_widget(top_bar)
        
        # 内容区
        scroll = ScrollView()
        self.content = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=[dp(16), dp(12), dp(16), dp(12)],
            size_hint_y=None,
        )
        self.content.bind(minimum_height=self.content.setter('height'))
        
        # 选择租车记录
        rentals = load_json(RENTALS_FILE, [])
        settled_rentals = [r for r in rentals if r.get('settled')]
        rental_labels = []
        self.rental_map = {}
        if settled_rentals:
            for r in settled_rentals:
                label = f"{r['plate']} - {r['renter_name']}"
                rental_labels.append(label)
                self.rental_map[label] = r
            rental_labels.append("全部已结算记录")
        else:
            rental_labels = ['暂无已结算记录']
        
        self.content.add_widget(create_label("选择租车记录", font_size=dp(13), bold=True, height=dp(24)))
        self.rental_spinner = Spinner(
            text=rental_labels[0],
            values=rental_labels,
            size_hint_y=None,
            height=dp(40),
            font_size=dp(14),
            background_normal='',
            background_color=(0.97, 0.97, 0.99, 1),
            color=TEXT_DARK,
        )
        self.content.add_widget(self.rental_spinner)
        
        # 甲方信息
        self.content.add_widget(create_label("甲方（出租方）信息", font_size=dp(14), bold=True, color=(0.55, 0.30, 0.85, 1), height=dp(28)))
        
        party_a_fields = [
            ("公司名称 *", "company_name", "如：XX租车有限公司"),
            ("联系电话 *", "company_phone", ""),
            ("地址", "company_address", ""),
        ]
        
        self.party_a_inputs = {}
        for label_text, key, hint in party_a_fields:
            self.content.add_widget(create_label(label_text, font_size=dp(13), bold=True, height=dp(24)))
            inp = create_input(hint=hint)
            self.party_a_inputs[key] = inp
            self.content.add_widget(inp)
        
        # 生成按钮
        gen_btn = create_button("📄 生成合同", color=(0.55, 0.30, 0.85, 1), height=dp(48), font_size=dp(16))
        gen_btn.bind(on_press=lambda x: self.do_generate())
        self.content.add_widget(gen_btn)
        
        # 合同预览区
        self.preview_area = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(4))
        self.content.add_widget(self.preview_area)
        
        scroll.add_widget(self.content)
        main.add_widget(scroll)
        
        self.add_widget(main)
    
    def generate_contract(self):
        """生成合同"""
        label = self.rental_spinner.text
        if label == '暂无已结算记录' or label == '全部已结算记录':
            if label == '全部已结算记录':
                # 显示所有合同列表
                self.show_all_contracts()
            return
        
        rental = self.rental_map.get(label)
        if not rental:
            show_popup("提示", "请选择租车记录！", is_error=True)
            return
        
        company_name = self.party_a_inputs['company_name'].text.strip()
        company_phone = self.party_a_inputs['company_phone'].text.strip()
        
        if not company_name or not company_phone:
            show_popup("提示", "公司名称和联系电话为必填项！", is_error=True)
            return
        
        # 加载车辆信息
        vehicles = load_json(VEHICLES_FILE, [])
        vehicle = next((v for v in vehicles if v['plate'] == rental['plate']), {})
        
        # 生成合同内容
        contract_id = f"HT-{rental['id']}"
        now = datetime.now()
        
        contract_text = f"""
╔══════════════════════════════════════════════════════╗
║          车 辆 租 赁 合 同                           ║
╠══════════════════════════════════════════════════════╣
║  合同编号：{contract_id}                            ║
║  签订日期：{now.strftime("%Y年%m月%d日")}                        ║
╚══════════════════════════════════════════════════════╝

甲方（出租方）：{company_name}
联系电话：{company_phone}
地    址：{self.party_a_inputs['company_address'].text.strip()}

乙方（承租方）：{rental['renter_name']}
身份证号：{rental['id_number']}
联系电话：{rental['phone']}
地    址：{rental.get('address', '')}
驾驶证号：{rental.get('license_no', '')}

──────────────────────────────────────────────────────
                    租赁车辆信息
──────────────────────────────────────────────────────
车牌号码：{rental['plate']}
车辆品牌：{vehicle.get('brand', '')}
车辆型号：{vehicle.get('model', '')}
车辆颜色：{vehicle.get('color', '')}
车架号码：{vehicle.get('vin', '')}

──────────────────────────────────────────────────────
                    租赁条款
──────────────────────────────────────────────────────
起租日期：{rental['start_date']}
到期日期：{rental['end_date']}
还车日期：{rental.get('return_date', '')}
日租金：{rental.get('daily_rent', '')} 元/天
租金总额：{rental.get('total_rent', '')} 元
押金金额：{rental.get('deposit', '')} 元

──────────────────────────────────────────────────────
                    费用结算
──────────────────────────────────────────────────────
"""
        
        if rental.get('settled'):
            contract_text += f"""
逾期费：{rental.get('overdue_fee', 0):.0f} 元
损坏/违章费：{rental.get('damage_fee', 0):.0f} 元
应付总额：{float(rental.get('overdue_fee', 0) or 0) + float(rental.get('damage_fee', 0) or 0) + float(rental.get('total_rent', 0) or 0):.0f} 元
押金：{rental.get('deposit', 0):.0f} 元
结算余额：{rental.get('balance', 0):.0f} 元
"""
        
        contract_text += f"""
──────────────────────────────────────────────────────
                    合同条款
──────────────────────────────────────────────────────
1. 甲方保证所出租车辆技术状况良好，备胎、随车工具等齐全。
2. 乙方应按时归还车辆，逾期按日租金1.5倍收取逾期费。
3. 租赁期间发生违章、事故等，由乙方承担全部责任及费用。
4. 乙方应妥善保管车辆，不得擅自改装、转租或抵押。
5. 还车时车辆应保持交付时状态，如有损坏照价赔偿。
6. 保险由甲方负责购买，事故理赔按保险条款执行。
7. 本合同一式两份，甲乙双方各执一份，自签字之日起生效。

──────────────────────────────────────────────────────
                    签字盖章
──────────────────────────────────────────────────────
甲方（盖章）：________________    日期：________________

乙方（签字）：________________    日期：________________

──────────────────────────────────────────────────────
"""
        
        # 保存合同
        contract_file = os.path.join(CONTRACTS_DIR, f"{contract_id}.txt")
        with open(contract_file, 'w', encoding='utf-8') as f:
            f.write(contract_text)
        
        # 生成HTML版本
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>车辆租赁合同 - {contract_id}</title>
<style>
body {{ font-family: "Microsoft YaHei", sans-serif; max-width: 800px; margin: 0 auto; padding: 30px; color: #333; }}
h1 {{ text-align: center; color: #8B0000; border-bottom: 2px solid #8B0000; padding-bottom: 10px; }}
h2 {{ color: #8B0000; border-left: 4px solid #8B0000; padding-left: 10px; margin-top: 25px; }}
.info-row {{ display: flex; margin: 8px 0; }}
.info-label {{ width: 120px; font-weight: bold; color: #555; }}
.info-value {{ flex: 1; }}
table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
th {{ background-color: #8B0000; color: white; }}
.sign-area {{ display: flex; justify-content: space-between; margin-top: 40px; }}
.sign-box {{ text-align: center; }}
.sign-line {{ border-bottom: 1px solid #333; width: 200px; display: inline-block; margin-bottom: 5px; }}
</style>
</head>
<body>
<h1>🚗 车辆租赁合同</h1>
<p style="text-align:center; color:#666;">合同编号：{contract_id} | 签订日期：{now.strftime("%Y年%m月%d日")}</p>

<h2>甲方（出租方）信息</h2>
<div class="info-row"><span class="info-label">公司名称：</span><span class="info-value">{company_name}</span></div>
<div class="info-row"><span class="info-label">联系电话：</span><span class="info-value">{company_phone}</span></div>
<div class="info-row"><span class="info-label">地    址：</span><span class="info-value">{self.party_a_inputs['company_address'].text.strip()}</span></div>

<h2>乙方（承租方）信息</h2>
<div class="info-row"><span class="info-label">姓    名：</span><span class="info-value">{rental['renter_name']}</span></div>
<div class="info-row"><span class="info-label">身份证号：</span><span class="info-value">{rental['id_number']}</span></div>
<div class="info-row"><span class="info-label">联系电话：</span><span class="info-value">{rental['phone']}</span></div>
<div class="info-row"><span class="info-label">地    址：</span><span class="info-value">{rental.get('address', '')}</span></div>
<div class="info-row"><span class="info-label">驾驶证号：</span><span class="info-value">{rental.get('license_no', '')}</span></div>

<h2>租赁车辆信息</h2>
<div class="info-row"><span class="info-label">车牌号码：</span><span class="info-value">{rental['plate']}</span></div>
<div class="info-row"><span class="info-label">车辆品牌：</span><span class="info-value">{vehicle.get('brand', '')}</span></div>
<div class="info-row"><span class="info-label">车辆型号：</span><span class="info-value">{vehicle.get('model', '')}</span></div>
<div class="info-row"><span class="info-label">车辆颜色：</span><span class="info-value">{vehicle.get('color', '')}</span></div>
<div class="info-row"><span class="info-label">车架号码：</span><span class="info-value">{vehicle.get('vin', '')}</span></div>

<h2>租赁条款</h2>
<table>
<tr><th>项目</th><th>内容</th></tr>
<tr><td>起租日期</td><td>{rental['start_date']}</td></tr>
<tr><td>到期日期</td><td>{rental['end_date']}</td></tr>
<tr><td>还车日期</td><td>{rental.get('return_date', '')}</td></tr>
<tr><td>日租金</td><td>{rental.get('daily_rent', '')} 元/天</td></tr>
<tr><td>租金总额</td><td>{rental.get('total_rent', '')} 元</td></tr>
<tr><td>押金金额</td><td>{rental.get('deposit', '')} 元</td></tr>
</table>

<h2>合同条款</h2>
<ol>
<li>甲方保证所出租车辆技术状况良好，备胎、随车工具等齐全。</li>
<li>乙方应按时归还车辆，逾期按日租金1.5倍收取逾期费。</li>
<li>租赁期间发生违章、事故等，由乙方承担全部责任及费用。</li>
<li>乙方应妥善保管车辆，不得擅自改装、转租或抵押。</li>
<li>还车时车辆应保持交付时状态，如有损坏照价赔偿。</li>
<li>保险由甲方负责购买，事故理赔按保险条款执行。</li>
<li>本合同一式两份，甲乙双方各执一份，自签字之日起生效。</li>
</ol>

<h2>签字盖章</h2>
<div class="sign-area">
<div class="sign-box"><div class="sign-line"></div><p>甲方（盖章）</p><p>日期：____________</p></div>
<div class="sign-box"><div class="sign-line"></div><p>乙方（签字）</p><p>日期：____________</p></div>
</div>
</body>
</html>
"""
        html_file = os.path.join(CONTRACTS_HTML_DIR, f"{contract_id}.html")
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # 显示预览
        self.preview_area.clear_widgets()
        self.preview_area.add_widget(create_label("📄 合同已生成", font_size=dp(15), bold=True, color=(0.55, 0.30, 0.85, 1), height=dp(30)))
        
        preview_text = contract_text.strip()
        if len(preview_text) > 500:
            preview_text = preview_text[:500] + "\n\n...（完整内容请查看文件）"
        
        preview_label = Label(
            text=preview_text,
            font_size=dp(10),
            color=TEXT_DARK,
            halign='left',
            valign='top',
            size_hint_y=None,
            text_size=(None, None),
        )
        preview_label.bind(texture_size=lambda w, *a: setattr(w, 'height', max(w.texture_size[1], dp(100))))
        self.preview_area.add_widget(preview_label)
        
        show_popup("成功", f"合同已生成！\n文本版：{contract_file}\nHTML版：{html_file}\n\n可用浏览器打开HTML文件，Ctrl+P打印为PDF")
    
    def show_all_contracts(self):
        """显示所有已生成的合同"""
        self.preview_area.clear_widgets()
        
        contracts = []
        if os.path.exists(CONTRACTS_DIR):
            for f in sorted(os.listdir(CONTRACTS_DIR)):
                if f.endswith('.txt'):
                    contracts.append(f)
        
        if not contracts:
            self.preview_area.add_widget(Label(
                text="暂无已生成的合同",
                font_size=dp(13),
                color=TEXT_GRAY,
                size_hint_y=None,
                height=dp(30),
            ))
            return
        
        self.preview_area.add_widget(create_label("📄 已生成的合同", font_size=dp(14), bold=True, color=(0.55, 0.30, 0.85, 1), height=dp(28)))
        
        for c in contracts:
            item = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(32),
                padding=[dp(8), dp(4), dp(8), dp(4)],
            )
            from kivy.graphics import Color, RoundedRectangle
            item.bind(size=lambda w, *a, c=item: (
                c.canvas.before.clear(),
                c.canvas.before.add(Color(0.97, 0.95, 0.99, 1)),
                c.canvas.before.add(RoundedRectangle(size=c.size, pos=c.pos, radius=[dp(6)]))
            ))
            item.add_widget(Label(
                text=c,
                font_size=dp(12),
                color=TEXT_DARK,
                halign='left',
                size_hint_x=0.7,
            ))
            item.add_widget(Label(
                text="查看",
                font_size=dp(11),
                color=(0.55, 0.30, 0.85, 1),
                halign='right',
                size_hint_x=0.3,
            ))
            self.preview_area.add_widget(item)


# ==================== 搜索 ====================
class SearchScreen(Screen):
    """综合搜索屏幕"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "search"
        
        main = BoxLayout(orientation='vertical', spacing=0)
        
        # 顶部导航
        top_bar = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            padding=[dp(8), dp(6), dp(8), dp(6)],
        )
        from kivy.graphics import Color, Rectangle
        top_bar.bind(size=lambda *a: top_bar.canvas.before.clear() or (
            top_bar.canvas.before.add(Color(0.60, 0.60, 0.65, 1)),
            top_bar.canvas.before.add(Rectangle(size=top_bar.size, pos=top_bar.pos))
        ))
        back_btn = Button(
            text="← 返回",
            size_hint_x=None,
            width=dp(70),
            font_size=dp(14),
            color=WHITE,
            background_normal='',
            background_down='',
            background_color=(0,0,0,0),
            on_press=lambda x: setattr(self.manager, 'current', 'home')
        )
        title_label = Label(
            text="🔍 综合搜索",
            font_size=dp(17),
            bold=True,
            color=WHITE,
        )
        top_bar.add_widget(back_btn)
        top_bar.add_widget(title_label)
        top_bar.add_widget(BoxLayout(size_hint_x=None, width=dp(70)))
        main.add_widget(top_bar)
        
        # 搜索区
        search_area = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            padding=[dp(16), dp(12), dp(16), dp(8)],
        )
        
        search_area.add_widget(create_label("输入关键词搜索", font_size=dp(13), bold=True, height=dp(24)))
        self.search_input = create_input("车牌号 / 品牌 / 租车人 / 电话")
        search_area.add_widget(self.search_input)
        
        search_btn = create_button("🔍 搜索", color=(0.60, 0.60, 0.65, 1), height=dp(44), font_size=dp(15))
        search_btn.bind(on_press=lambda x: self.do_search())
        search_area.add_widget(search_btn)
        
        main.add_widget(search_area)
        
        # 结果区
        self.result_area = BoxLayout(orientation='vertical')
        main.add_widget(self.result_area)
        
        self.add_widget(main)
    
    def do_search(self):
        self.result_area.clear_widgets()
        
        keyword = self.search_input.text.strip().lower()
        if not keyword:
            show_popup("提示", "请输入搜索关键词！", is_error=True)
            return
        
        # 搜索车辆
        vehicles = load_json(VEHICLES_FILE, [])
        matched_vehicles = [
            v for v in vehicles
            if keyword in v.get('plate', '').lower()
            or keyword in v.get('brand', '').lower()
            or keyword in v.get('model', '').lower()
            or keyword in v.get('color', '').lower()
        ]
        
        # 搜索租车记录
        rentals = load_json(RENTALS_FILE, [])
        matched_rentals = [
            r for r in rentals
            if keyword in r.get('renter_name', '').lower()
            or keyword in r.get('phone', '').lower()
            or keyword in r.get('plate', '').lower()
        ]
        
        if not matched_vehicles and not matched_rentals:
            self.result_area.add_widget(Label(
                text="🔍 未找到匹配结果",
                font_size=dp(14),
                color=TEXT_GRAY,
                size_hint_y=None,
                height=dp(40),
            ))
            return
        
        scroll = ScrollView()
        container = BoxLayout(
            orientation='vertical',
            spacing=dp(8),
            padding=[dp(12), dp(4), dp(12), dp(8)],
            size_hint_y=None,
        )
        container.bind(minimum_height=container.setter('height'))
        
        if matched_vehicles:
            container.add_widget(create_label(f"🚗 找到 {len(matched_vehicles)} 辆车辆", font_size=dp(14), bold=True, color=PRIMARY, height=dp(28)))
            for v in matched_vehicles:
                item = BoxLayout(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=dp(30),
                    padding=[dp(8), dp(4), dp(8), dp(4)],
                )
                from kivy.graphics import Color, RoundedRectangle
                item.bind(size=lambda w, *a, c=item: (
                    c.canvas.before.clear(),
                    c.canvas.before.add(Color(1,0.97,0.97,1)),
                    c.canvas.before.add(RoundedRectangle(size=c.size, pos=c.pos, radius=[dp(6)]))
                ))
                item.add_widget(Label(
                    text=f"{v['plate']} - {v.get('brand', '')} {v.get('model', '')}",
                    font_size=dp(12),
                    color=TEXT_DARK,
                    halign='left',
                    size_hint_x=0.6,
                ))
                item.add_widget(Label(
                    text=v.get('status', ''),
                    font_size=dp(11),
                    color=SUCCESS if v.get('status') == '空闲' else WARNING,
                    halign='right',
                    size_hint_x=0.4,
                ))
                container.add_widget(item)
        
        if matched_rentals:
            container.add_widget(create_label(f"📋 找到 {len(matched_rentals)} 条租车记录", font_size=dp(14), bold=True, color=(0.20, 0.55, 0.85, 1), height=dp(28)))
            for r in matched_rentals:
                item = BoxLayout(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=dp(30),
                    padding=[dp(8), dp(4), dp(8), dp(4)],
                )
                from kivy.graphics import Color, RoundedRectangle
                item.bind(size=lambda w, *a, c=item: (
                    c.canvas.before.clear(),
                    c.canvas.before.add(Color(0.93, 0.96, 0.98, 1)),
                    c.canvas.before.add(RoundedRectangle(size=c.size, pos=c.pos, radius=[dp(6)]))
                ))
                item.add_widget(Label(
                    text=f"{r['plate']} - {r['renter_name']}",
                    font_size=dp(12),
                    color=TEXT_DARK,
                    halign='left',
                    size_hint_x=0.6,
                ))
                item.add_widget(Label(
                    text=f"{r['start_date']}至{r['end_date']}",
                    font_size=dp(11),
                    color=TEXT_GRAY,
                    halign='right',
                    size_hint_x=0.4,
                ))
                container.add_widget(item)
        
        scroll.add_widget(container)
        self.result_area.add_widget(scroll)


# ==================== 统计 ====================
class StatsScreen(Screen):
    """数据统计屏幕"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "stats"
        
        main = BoxLayout(orientation='vertical', spacing=0)
        
        # 顶部导航
        top_bar = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            padding=[dp(8), dp(6), dp(8), dp(6)],
        )
        from kivy.graphics import Color, Rectangle
        top_bar.bind(size=lambda *a: top_bar.canvas.before.clear() or (
            top_bar.canvas.before.add(Color(0.90, 0.45, 0.10, 1)),
            top_bar.canvas.before.add(Rectangle(size=top_bar.size, pos=top_bar.pos))
        ))
        back_btn = Button(
            text="← 返回",
            size_hint_x=None,
            width=dp(70),
            font_size=dp(14),
            color=WHITE,
            background_normal='',
            background_down='',
            background_color=(0,0,0,0),
            on_press=lambda x: setattr(self.manager, 'current', 'home')
        )
        title_label = Label(
            text="📊 数据统计",
            font_size=dp(17),
            bold=True,
            color=WHITE,
        )
        top_bar.add_widget(back_btn)
        top_bar.add_widget(title_label)
        top_bar.add_widget(BoxLayout(size_hint_x=None, width=dp(70)))
        main.add_widget(top_bar)
        
        # 统计内容
        scroll = ScrollView()
        self.stats_area = BoxLayout(
            orientation='vertical',
            spacing=dp(12),
            padding=[dp(16), dp(12), dp(16), dp(12)],
            size_hint_y=None,
        )
        self.stats_area.bind(minimum_height=self.stats_area.setter('height'))
        scroll.add_widget(self.stats_area)
        main.add_widget(scroll)
        
        self.add_widget(main)
        self.refresh_stats()
    
    def refresh_stats(self):
        self.stats_area.clear_widgets()
        
        vehicles = load_json(VEHICLES_FILE, [])
        rentals = load_json(RENTALS_FILE, [])
        insurances = load_json(INSURANCES_FILE, [])
        
        total_vehicles = len(vehicles)
        total_rentals = len(rentals)
        active_rentals = len([r for r in rentals if not r.get('return_date')])
        settled_rentals = len([r for r in rentals if r.get('settled')])
        total_insurances = len(insurances)
        
        # 状态分布
        status_count = {}
        for v in vehicles:
            s = v.get('status', '空闲')
            status_count[s] = status_count.get(s, 0) + 1
        
        # 品牌分布
        brand_count = {}
        for v in vehicles:
            b = v.get('brand', '未知')
            brand_count[b] = brand_count.get(b, 0) + 1
        
        # 保险到期情况
        today = date.today()
        expiring_soon = 0
        expired = 0
        for ins in insurances:
            try:
                end = datetime.strptime(ins.get('end_date', '2099-01-01'), '%Y-%m-%d').date()
                days = (end - today).days
                if days < 0:
                    expired += 1
                elif days <= 30:
                    expiring_soon += 1
            except:
                pass
        
        # 总计费
        total_rent_amount = sum(float(r.get('total_rent', 0) or 0) for r in rentals)
        total_deposit = sum(float(r.get('deposit', 0) or 0) for r in rentals)
        
        # 概览卡片
        self.stats_area.add_widget(create_label("📊 数据概览", font_size=dp(16), bold=True, color=(0.90, 0.45, 0.10, 1), height=dp(32)))
        
        overview_items = [
            ("车辆总数", str(total_vehicles), PRIMARY),
            ("租车记录", str(total_rentals), (0.20, 0.55, 0.85, 1)),
            ("在租中", str(active_rentals), WARNING),
            ("已结算", str(settled_rentals), SUCCESS),
            ("保险记录", str(total_insurances), (0.85, 0.60, 0.15, 1)),
            ("保险即将到期", str(expiring_soon), WARNING),
            ("保险已过期", str(expired), DANGER),
        ]
        
        for label, value, color in overview_items:
            card = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(40),
                padding=[dp(14), dp(6), dp(14), dp(6)],
            )
            from kivy.graphics import Color, RoundedRectangle
            card.bind(size=lambda w, *a, c=card, col=color: (
                c.canvas.before.clear(),
                c.canvas.before.add(Color(*col)),
                c.canvas.before.add(RoundedRectangle(size=c.size, pos=c.pos, radius=[dp(8)]))
            ))
            card.add_widget(Label(
                text=label,
                font_size=dp(13),
                color=WHITE,
                halign='left',
                size_hint_x=0.6,
            ))
            card.add_widget(Label(
                text=value,
                font_size=dp(18),
                bold=True,
                color=WHITE,
                halign='right',
                size_hint_x=0.4,
            ))
            self.stats_area.add_widget(card)
        
        # 状态分布
        if status_count:
            self.stats_area.add_widget(BoxLayout(size_hint_y=None, height=dp(8)))
            self.stats_area.add_widget(create_label("🚗 车辆状态分布", font_size=dp(14), bold=True, color=PRIMARY, height=dp(28)))
            for status, count in sorted(status_count.items()):
                item = BoxLayout(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=dp(28),
                )
                item.add_widget(Label(
                    text=status,
                    font_size=dp(12),
                    color=TEXT_DARK,
                    halign='left',
                    size_hint_x=0.6,
                ))
                item.add_widget(Label(
                    text=f"{count} 辆 ({count/total_vehicles*100:.0f}%)",
                    font_size=dp(12),
                    color=TEXT_GRAY,
                    halign='right',
                    size_hint_x=0.4,
                ))
                self.stats_area.add_widget(item)
        
        # 品牌分布
        if brand_count:
            self.stats_area.add_widget(BoxLayout(size_hint_y=None, height=dp(8)))
            self.stats_area.add_widget(create_label("🏷️ 品牌分布", font_size=dp(14), bold=True, color=PRIMARY, height=dp(28)))
            for brand, count in sorted(brand_count.items(), key=lambda x: -x[1]):
                item = BoxLayout(
                    orientation='horizontal',
                    size_hint_y=None,
                    height=dp(28),
                )
                item.add_widget(Label(
                    text=brand,
                    font_size=dp(12),
                    color=TEXT_DARK,
                    halign='left',
                    size_hint_x=0.6,
                ))
                item.add_widget(Label(
                    text=f"{count} 辆",
                    font_size=dp(12),
                    color=TEXT_GRAY,
                    halign='right',
                    size_hint_x=0.4,
                ))
                self.stats_area.add_widget(item)
        
        # 财务概览
        self.stats_area.add_widget(BoxLayout(size_hint_y=None, height=dp(8)))
        self.stats_area.add_widget(create_label("💰 财务概览", font_size=dp(14), bold=True, color=(0.15, 0.70, 0.50, 1), height=dp(28)))
        
        finance_items = [
            ("租金总额", f"{total_rent_amount:.0f} 元"),
            ("押金总额", f"{total_deposit:.0f} 元"),
        ]
        for label, value in finance_items:
            item = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(28),
            )
            item.add_widget(Label(
                text=label,
                font_size=dp(12),
                color=TEXT_DARK,
                halign='left',
                size_hint_x=0.5,
            ))
            item.add_widget(Label(
                text=value,
                font_size=dp(13),
                color=(0.15, 0.70, 0.50, 1),
                bold=True,
                halign='right',
                size_hint_x=0.5,
            ))
            self.stats_area.add_widget(item)


# ==================== 主应用 ====================
class VehicleRentalApp(App):
    """主应用类"""
    def build(self):
        self.title = "租车管理系统 v2.0"
        
        # 创建屏幕管理器
        sm = ScreenManager()
        
        # 添加所有屏幕
        sm.add_widget(HomeScreen())
        sm.add_widget(VehicleScreen())
        sm.add_widget(RentalScreen())
        sm.add_widget(InsuranceScreen())
        sm.add_widget(SettlementScreen())
        sm.add_widget(ContractScreen())
        sm.add_widget(SearchScreen())
        sm.add_widget(StatsScreen())
        
        return sm
    
    def on_start(self):
        print("=" * 50)
        print("🚗 租车公司车辆管理系统 v2.0 - 手机版")
        print("=" * 50)
        print(f"📂 数据目录：{os.path.abspath(DATA_DIR)}")
        print(f"🚗 车辆数据：{VEHICLES_FILE}")
        print(f"📋 租车数据：{RENTALS_FILE}")
        print(f"🛡️ 保险数据：{INSURANCES_FILE}")
        print("=" * 50)


if __name__ == '__main__':
    VehicleRentalApp().run()
