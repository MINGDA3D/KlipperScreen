# -*- coding: utf-8 -*-
import logging
import os
import pathlib
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GdkPixbuf, Gio, Gtk, Pango


def find_widget(widget, wanted_type):
    # Returns a widget of wanted_type or None
    if isinstance(widget, wanted_type):
        return widget
    if isinstance(widget, (Gtk.Container, Gtk.Bin, Gtk.Button, Gtk.Alignment, Gtk.Box)):
        for _ in widget.get_children():
            result = find_widget(_, wanted_type)
            if result is not None:
                return result


def format_label(widget, lines=2):
    label = find_widget(widget, Gtk.Label)
    if label is not None:
        label.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        label.set_line_wrap(True)
        label.set_ellipsize(Pango.EllipsizeMode.END)
        label.set_lines(lines)

#add by Sampson for self-test at 20230911 begin
def create_labels(label_texts):
    labels = []
    for text in label_texts:
        #label = Gtk.Label()
        #set_label_text_color(label, text, "white")
        label = Gtk.Label()
        label.set_markup(text)
        # label.set_hexpand(True)
        # label.set_halign(Gtk.Align.START)
        # label.set_vexpand(True)
        # label.set_valign(Gtk.Align.START)
        #label.set_line_wrap(True)
        # label.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        labels.append(label)
    return labels

def create_images(n):
    images = []
    for i in range(n):
        image = Gtk.Image()
        images.append(image)
    return images

def center_widgets(widget):
    align = Gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0.0, yscale=0.0)
    align.add(widget)
    return align

def set_window_background_color(window, color):
    screen = window.get_screen()
    rgba = Gdk.RGBA()
    rgba.parse(color)
    provider = Gtk.CssProvider()
    css = f"window {{ background-color: {rgba.to_string()} }}"

    try:
        provider.load_from_data(css.encode())
        context = window.get_style_context()
        context.add_provider(provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    except Exception as e:
        print(f"Error loading CSS: {e}")
        
def set_label_text_color(label, text, color):
    label.set_markup(f'<span foreground="{color}">{text}</span>')      
    
def set_text_font_size(label, font_size):
    style_context = label.get_style_context()
    css_data = b'label { font-size: ' + str(font_size).encode() + b'px; }'
    css_provider = Gtk.CssProvider()
    css_provider.load_from_data(css_data)

    style_context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

  
def set_image(image, filename, new_width, new_height):
    pixbuf = GdkPixbuf.Pixbuf.new_from_file(filename)  # Replace with the actual path to your image file
    pixbuf = pixbuf.scale_simple(new_width, new_height, GdkPixbuf.InterpType.BILINEAR)
    image.new_from_pixbuf(pixbuf)
#add end

class KlippyGtk:
    labels = {}

    def __init__(self, screen):
        self.screen = screen
        self.themedir = os.path.join(pathlib.Path(__file__).parent.resolve().parent, "styles", screen.theme, "images")
        self.cursor = screen.show_cursor
        self.font_size_type = screen._config.get_main_config().get("font_size", "medium")
        self.width = screen.width
        self.height = screen.height
        self.font_ratio = [33, 49] if self.screen.vertical_mode else [43, 29]
        self.font_size = min(self.width / self.font_ratio[0], self.height / self.font_ratio[1])
        self.img_scale = self.font_size * 2
        self.button_image_scale = 1.38
        self.bsidescale = .65  # Buttons with image at the side

        #add by Sampson for self-test at 20230911 begin 
        self.themedir = os.path.join(pathlib.Path(__file__).parent.resolve().parent, "styles", screen.theme, "images")
        self.image_pass = os.path.join(self.themedir, "check_pass.svg")
        self.image_fail = os.path.join(self.themedir, "check_fail.svg")
        self.image_loading = os.path.join(self.themedir, "loading.gif")
        self.images = []
        self.test_items = ["Nozzle Heating", "Bed Heating", "Nozzle Cooling Fan", "Hotend Cooling Fan", "Material Detect"]
        # self.btn = Gtk.Button(label=f"Continue")
        #add end
        if self.font_size_type == "max":
            self.font_size = self.font_size * 1.2
            self.bsidescale = .7
        elif self.font_size_type == "extralarge":
            self.font_size = self.font_size * 1.14
            self.img_scale = self.img_scale * 0.7
            self.bsidescale = 1
        elif self.font_size_type == "large":
            self.font_size = self.font_size * 1.09
            self.img_scale = self.img_scale * 0.9
            self.bsidescale = .8
        elif self.font_size_type == "small":
            self.font_size = self.font_size * 0.91
            self.bsidescale = .55
        self.img_width = self.font_size * 3
        self.img_height = self.font_size * 3
        self.titlebar_height = self.font_size * 2
        logging.info(f"Font size: {self.font_size:.1f} ({self.font_size_type})")

        if self.screen.vertical_mode:
            self.action_bar_width = int(self.width)
            self.action_bar_height = int(self.height * .1)
            self.content_width = self.width
            self.content_height = self.height - self.titlebar_height - self.action_bar_height
        else:
            self.action_bar_width = int(self.width * .1)
            self.action_bar_height = int(self.height)
            self.content_width = self.width - self.action_bar_width
            self.content_height = self.height - self.titlebar_height

        self.keyboard_height = self.content_height * 0.5
        if (self.height / self.width) >= 3:  # Ultra-tall
            self.keyboard_height = self.keyboard_height * 0.5

        self.color_list = {}  # This is set by screen.py init_style()
        for key in self.color_list:
            if "base" in self.color_list[key]:
                rgb = [int(self.color_list[key]['base'][i:i + 2], 16) for i in range(0, 6, 2)]
                self.color_list[key]['rgb'] = rgb

    def get_temp_color(self, device):
        # logging.debug("Color list %s" % self.color_list)
        if device not in self.color_list:
            return False, False

        if 'base' in self.color_list[device]:
            rgb = self.color_list[device]['rgb'].copy()
            if self.color_list[device]['state'] > 0:
                rgb[1] = rgb[1] + self.color_list[device]['hsplit'] * self.color_list[device]['state']
            self.color_list[device]['state'] += 1
            rgb = [x / 255 for x in rgb]
            # logging.debug(f"Assigning color: {device} {rgb}")
        else:
            colors = self.color_list[device]['colors']
            if self.color_list[device]['state'] >= len(colors):
                self.color_list[device]['state'] = 0
            color = colors[self.color_list[device]['state'] % len(colors)]
            rgb = [int(color[i:i + 2], 16) / 255 for i in range(0, 6, 2)]
            self.color_list[device]['state'] += 1
            # logging.debug(f"Assigning color: {device} {rgb} {color}")
        return rgb

    def reset_temp_color(self):
        for key in self.color_list:
            self.color_list[key]['state'] = 0

    @staticmethod
    def Label(label, style=None):
        la = Gtk.Label(label)
        if style is not None:
            la.get_style_context().add_class(style)
        return la

    def Image(self, image_name=None, width=None, height=None):
        if image_name is None:
            return Gtk.Image()
        pixbuf = self.PixbufFromIcon(image_name, width, height)
        return Gtk.Image.new_from_pixbuf(pixbuf) if pixbuf is not None else Gtk.Image()

    def PixbufFromIcon(self, filename, width=None, height=None):
        width = width if width is not None else self.img_width
        height = height if height is not None else self.img_height
        filename = os.path.join(self.themedir, filename)
        for ext in ["svg", "png"]:
            pixbuf = self.PixbufFromFile(f"{filename}.{ext}", int(width), int(height))
            if pixbuf is not None:
                return pixbuf
        return None

    @staticmethod
    def PixbufFromFile(filename, width=-1, height=-1):
        try:
            return GdkPixbuf.Pixbuf.new_from_file_at_size(filename, int(width), int(height))
        except Exception as e:
            logging.exception(e)
            logging.error(f"Unable to find image {filename}")
            return None

    def PixbufFromHttp(self, resource, width=-1, height=-1):
        response = self.screen.apiclient.get_thumbnail_stream(resource)
        if response is False:
            return None
        stream = Gio.MemoryInputStream.new_from_data(response, None)
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_stream_at_scale(stream, int(width), int(height), True)
        except Exception as e:
            logging.exception(e)
            return None
        stream.close_async(2)
        return pixbuf

    def Button(self, image_name=None, label=None, style=None, scale=None, position=Gtk.PositionType.TOP, lines=2):
        if self.font_size_type == "max" and label is not None and scale is None:
            image_name = None
        b = Gtk.Button()
        if label is not None:
            b.set_label(label.replace("\n", " "))
        b.set_hexpand(True)
        b.set_vexpand(True)
        b.set_can_focus(False)
        b.set_image_position(position)
        b.set_always_show_image(True)
        if image_name is not None:
            if scale is None:
                scale = self.button_image_scale
            if label is None:
                scale = scale * 1.4
            width = height = self.img_scale * scale
            b.set_image(self.Image(image_name, width, height))
            spinner = Gtk.Spinner.new()
            spinner.set_no_show_all(True)
            spinner.set_size_request(width, height)
            spinner.hide()
            box = find_widget(b, Gtk.Box)
            if box:
                box.add(spinner)

        if label is not None:
            format_label(b, lines)
        if style is not None:
            b.get_style_context().add_class(style)
        b.connect("clicked", self.screen.reset_screensaver_timeout)
        return b

    @staticmethod
    def Button_busy(widget, busy):
        spinner = find_widget(widget, Gtk.Spinner)
        image = find_widget(widget, Gtk.Image)
        if busy:
            widget.set_sensitive(False)
            if image:
                widget.set_always_show_image(False)
                image.hide()
            if spinner:
                spinner.start()
                spinner.show()
        else:
            if image:
                widget.set_always_show_image(True)
                image.show()
            if spinner:
                spinner.stop()
                spinner.hide()
            widget.set_sensitive(True)

    def Dialog(self, title, buttons, content, callback=None, *args):
        dialog = Gtk.Dialog(title=title)
        dialog.set_default_size(self.width, self.height)
        dialog.set_resizable(False)
        dialog.set_transient_for(self.screen)
        dialog.set_modal(True)

        for button in buttons:
            dialog.add_button(button['name'], button['response'])
            button = dialog.get_widget_for_response(button['response'])
            button.set_size_request((self.width - 30) / 3, self.height / 5)
            format_label(button, 3)

        dialog.connect("response", self.screen.reset_screensaver_timeout)
        dialog.connect("response", callback, *args)
        dialog.get_style_context().add_class("dialog")

        content_area = dialog.get_content_area()
        content_area.set_margin_start(15)
        content_area.set_margin_end(15)
        content_area.set_margin_top(15)
        content_area.set_margin_bottom(15)
        content_area.add(content)

        dialog.show_all()
        # Change cursor to blank
        if self.cursor:
            dialog.get_window().set_cursor(
                Gdk.Cursor.new_for_display(Gdk.Display.get_default(), Gdk.CursorType.ARROW))
        else:
            dialog.get_window().set_cursor(
                Gdk.Cursor.new_for_display(Gdk.Display.get_default(), Gdk.CursorType.BLANK_CURSOR))

        self.screen.dialogs.append(dialog)
        logging.info(f"Showing dialog {dialog.get_title()} {dialog.get_size()}")
        return dialog

    #add by Sampson for self-test at 20230911 begin  
    def remove_all_dialog(self):
        self.close_screensaver()
        for dialog in self.screen.dialogs:
            self.remove_dialog(dialog)

    # def enable_button(self):
    #     self.btn.set_sensitive(True)

    def creat_self_test_dialog(self):
        dialog = Gtk.Dialog(title="KlipperScreen")
        dialog.set_default_size(self.width, self.height)
        dialog.set_resizable(False)
        dialog.set_transient_for(self.screen)
        dialog.set_modal(True)

        self_test_label = Gtk.Label()
        set_label_text_color(self_test_label, f"Printer Self-Test", f"white")
        # set_label_text_color(self_test_label, "Do not touch the printer during power-on self-test.", "red")
        set_text_font_size(self_test_label, 26)
    
        labels = create_labels(self.test_items)
        images = create_images(len(labels))
        self.images = images

        warning_label = Gtk.Label()
        set_label_text_color(warning_label, "Do not touch the printer during power-on self-test.", "red")
        # warning_label.set_text("Self-test Ended")
        # set_text_font_size(warning_label, 21)
        
        # images[0].set_from_file(image_pass)
        # images[1].set_from_file(image_fail)
        #images[0].set_from_file(image_loading)

        # btn = Gtk.Button(label=f"Continue")
        # msg.set_hexpand(True)
        # msg.set_vexpand(True)
        # msg.get_child().set_line_wrap(True)
        # msg.get_child().set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        # msg.get_child().set_max_width_chars(40)
        # self.btn.set_sensitive(False)
        # self.btn.connect("clicked", self.remove_all_dialog)

        vbox = Gtk.VBox(spacing=self.height*0.1)
        dialog.get_style_context().add_class("dialog")

        content_area = dialog.get_content_area()
        content_area.set_margin_start(15)
        content_area.set_margin_end(15)
        content_area.set_margin_top(15)
        content_area.set_margin_bottom(15)
        content_area.add(vbox)
        #dialog.add(vbox)
    
        vbox.pack_start(center_widgets(self_test_label), False, False, 0)
        for i in range(len(labels)):
            hbox = Gtk.HBox(spacing=self.width*0.3)
            hbox.pack_start(labels[i], True, False, 0)
            hbox.pack_start(images[i], True, False, 0)
            vbox.pack_start(center_widgets(hbox), True, False, 0)
    	
        vbox.pack_start(center_widgets(warning_label), True, False, 0)
        # vbox.pack_start(center_widgets(self.btn), True, False, 0)

        dialog.show_all()
        # Change cursor to blank
        if self.cursor:
            dialog.get_window().set_cursor(
                Gdk.Cursor.new_for_display(Gdk.Display.get_default(), Gdk.CursorType.ARROW))
        else:
            dialog.get_window().set_cursor(
                Gdk.Cursor.new_for_display(Gdk.Display.get_default(), Gdk.CursorType.BLANK_CURSOR))

        self.screen.dialogs.append(dialog)
        logging.info(f"Showing dialog {dialog.get_title()} {dialog.get_size()}")
        return dialog

    def change_state(self, step, state):
        if step < 0 and step > len(self.images):
            return
        imagePath = self.image_loading
        if state == -1:
            imagePath = self.image_fail
        elif state == 0:
            imagePath = self.image_pass
        self.images[step].set_from_file(imagePath)
#add end

    def remove_dialog(self, dialog, *args):
        if self.screen.updating:
            return
        dialog.destroy()
        if dialog in self.screen.dialogs:
            logging.info("Removing Dialog")
            self.screen.dialogs.remove(dialog)
            return
        logging.debug(f"Cannot remove dialog {dialog}")

    @staticmethod
    def HomogeneousGrid(width=None, height=None):
        g = Gtk.Grid()
        g.set_row_homogeneous(True)
        g.set_column_homogeneous(True)
        if width is not None and height is not None:
            g.set_size_request(width, height)
        return g

    def ToggleButton(self, text):
        b = Gtk.ToggleButton(text)
        b.props.relief = Gtk.ReliefStyle.NONE
        b.set_hexpand(True)
        b.set_vexpand(True)
        b.connect("clicked", self.screen.reset_screensaver_timeout)
        return b

    def ScrolledWindow(self, steppers=True):
        scroll = Gtk.ScrolledWindow()
        scroll.set_property("overlay-scrolling", False)
        scroll.set_vexpand(True)
        scroll.add_events(Gdk.EventMask.BUTTON_PRESS_MASK |
                          Gdk.EventMask.TOUCH_MASK |
                          Gdk.EventMask.BUTTON_RELEASE_MASK)
        scroll.set_kinetic_scrolling(True)
        if self.screen._config.get_main_config().getboolean("show_scroll_steppers", fallback=False) and steppers:
            scroll.get_vscrollbar().get_style_context().add_class("with-steppers")
        return scroll
