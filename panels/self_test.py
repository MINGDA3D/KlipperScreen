import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, Pango

self.self_test_label_texts = ["Nozzle Heating", "Bed Heating", "Hotend Cooling Fan", "Part Cooling Fan", "Material Detect"]

def create_labels():
    labels = []
    for text in self.self_test_label_texts:
        label = Gtk.Label()
        set_label_text_color(label, text, "white")
        
        labels.append(label)
    return labels

def create_images():
    images = []
    for i in range(len(self.self_test_label_texts)):
        image = Gtk.Image()
        images.append(image)
    return images

def center_widgets(widget):
    align = Gtk.Alignment(xalign=0.5, yalign=0.5, xscale=0.0, yscale=0.0)
    align.add(widget)
    return align
    
def create_window():
    window = Gtk.Window()
    window.connect("delete-event", Gtk.main_quit)
    window.set_default_size(600, 360)

    # Create and add the "Printer Self-Test" label in the first row
    self_test_label = Gtk.Label()
    set_label_text_color(self_test_label, f"Printer Self-Test", f"white")
    set_text_font_size(self_test_label, 26)

    labels = create_labels()
    images = create_images()
    
    warning_label = Gtk.Label()
    set_label_text_color(warning_label, f"Do not touch the printer during power-on self-test.", f"red")
    set_text_font_size(warning_label, 26)
    
    # #set_image(images[0], f"check_pass.svg", 32, 32)
    image_pass = f"check_pass1.svg"
    image_fail = f"check_fail1.svg"
    images[0].set_from_file(image_pass)
    images[1].set_from_file(image_fail)
    images[2].set_from_file("loading2.gif")

    vbox = Gtk.VBox(spacing=30)
    window.add(vbox)

    vbox.pack_start(center_widgets(self_test_label), False, False, 0)
    for i in range(len(labels)):
        hbox = Gtk.HBox(spacing=50)
        hbox.pack_start(labels[i], True, False, 0)
        hbox.pack_start(images[i], True, False, 0)
        vbox.pack_start(center_widgets(hbox), True, False, 0)
	
    vbox.pack_start(center_widgets(warning_label), True, False, 0)   	
    return window
    


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
    # Get the style context of the label
    style_context = label.get_style_context()

    # Use CSS to set the font size (16px in this case)
    css_provider = Gtk.CssProvider()
    css_provider.load_from_data(b'label { font-size: 26px; }')

    # Add the CSS provider to the style context
    style_context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)   

def set_image(image, filename, new_width, new_height):
    pixbuf = GdkPixbuf.Pixbuf.new_from_file(filename)  # Replace with the actual path to your image file
    pixbuf = pixbuf.scale_simple(new_width, new_height, GdkPixbuf.InterpType.BILINEAR)
    image.new_from_pixbuf(pixbuf)    
    
if __name__ == "__main__":
    window = create_window()
    set_window_background_color(window, "black")
    window.show_all()
    Gtk.main()
