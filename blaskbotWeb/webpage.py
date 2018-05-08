from flask import Flask
from flask_socketio import SocketIO

blaskbot_web = Flask(__name__)
socketio = SocketIO(blaskbot_web)

bit_icon_progression = [1, 10, 100, 1000, 5000, 10000, 100000]


def load_page(page_loc, style_loc, number_of_bits, username, message):
    template_lines = []
    with open(page_loc, 'r') as alert_page:
        template_lines = alert_page.readlines()
    stylesheet_lines = []
    with open(style_loc, 'r') as stylesheet:
        stylesheet_lines = stylesheet.readlines()
    for line_index, template_line in enumerate(template_lines):
        n_spaces = len(template_line) - len(template_line.lstrip())
        if "<!-- STYLESHEET -->" in template_line:
            # Get indentation
            template_lines[line_index:line_index + 1] = [
                ''.join([' ' * n_spaces, line]) for line in stylesheet_lines]
        if "<!-- VIDEO LINK -->" in template_line:
            template_lines[line_index] = ' ' * n_spaces\
                    + """<source src="./static/bits.mp4" type="video/mp4">"""
        if "<!-- BIT TEXT -->" in template_line:
            bit_icon = 1
            for bit_threshold in bit_icon_progression:
                if number_of_bits < bit_threshold:
                    break
                bit_icon = bit_threshold
            icon_line = """<image src="./static/{0}.gif" width=70> {1} <image src="./static/{0}.gif" width=70>""".format(bit_icon, number_of_bits)
            template_lines[line_index] = ''.join([' ' * n_spaces, icon_line])
        if "<!-- MESSAGE -->" in template_line:
            template_lines[line_index] = ''.join([' ' * n_spaces, username, ": ", message])
            #template_lines[line_index] = ''.join([' ' * n_spaces, str(number_of_bits), icon_line, ": ", message])
    return '\n'.join(template_lines)


@blaskbot_web.route('/')
def render():
    return load_page('./templates/alert.html',
                     './static/styles.css',
                     1500,
                     'Blaskatronic',
                     'Wobbey Beans')

if __name__ == '__main__':
    blaskbot_web.run(use_reloader=True, debug=True, port=1234)
