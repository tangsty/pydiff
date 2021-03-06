#-------------------------------------------------------------
#                        HTML generation
#-------------------------------------------------------------

from utils import *


#-------------------- types and utilities ----------------------

class Tag:
    def __init__(self, tag, idx, start=-1):
        self.tag = tag
        self.idx = idx
        self.start = start

    def __repr__(self):
        return "tag:" + str(self.tag) + ":" + str(self.idx)


# escape for HTML
def escape(s):
    s = s.replace('"', '&quot;')
    s = s.replace("'", '&#39;')
    s = s.replace("<", '&lt;')
    s = s.replace(">", '&gt;')
    return s


uid_count = -1
uid_hash = {}


def clear_uid():
    global uid_count, uid_hash
    uid_count = -1
    uid_hash = {}


def uid(node):
    if uid_hash.has_key(node):
        return uid_hash[node]

    global uid_count
    uid_count += 1
    uid_hash[node] = str(uid_count)
    return str(uid_count)


def html_header():
    install_path = get_install_path()

    js_filename = install_path + 'nav.js'
    js_file = open(js_filename, 'r')
    js_text = js_file.read()
    js_file.close()

    css_filename = install_path + 'diff.css'
    css_file = open(css_filename, 'r')
    css_text = css_file.read()
    css_file.close()

    out = []
    out.append('<html>\n')
    out.append('<head>\n')
    out.append('<META http-equiv="Content-Type" content="text/html; charset=utf-8">\n')

    out.append('<style>\n')
    out.append(css_text)
    out.append('\n</style>\n')

    out.append('<script type="text/javascript">\n')
    out.append(js_text)
    out.append('\n</script>\n')

    out.append('</head>\n')
    out.append('<body>\n')
    return ''.join(out)


def html_footer():
    out = []
    out.append('</body>\n')
    out.append('</html>\n')
    return ''.join(out)


def write_html(text, side):
    out = []
    out.append('<div id="' + side + '" class="src">')
    out.append('<pre>')
    if side == 'left':
        out.append('<a id="leftstart" tid="rightstart"></a>')
    else:
        out.append('<a id="rightstart" tid="leftstart"></a>')

    out.append(text)
    out.append('</pre>')
    out.append('</div>')
    return ''.join(out)


def htmlize(changes, file1, file2, text1, text2):
    tags1 = change_tags(changes, 'left')
    tags2 = change_tags(changes, 'right')
    tagged_text1 = apply_tags(text1, tags1)
    tagged_text2 = apply_tags(text2, tags2)

    outname = base_name(file1) + '-' + base_name(file2) + '.html'
    outfile = open(outname, 'w')
    outfile.write(html_header())
    outfile.write(write_html(tagged_text1, 'left'))
    outfile.write(write_html(tagged_text2, 'right'))
    outfile.write(html_footer())
    outfile.close()


# put the tags generated by change_tags into the text and create HTML
def apply_tags(s, tags):
    tags = sorted(tags, key=lambda t: (t.idx, -t.start))
    curr = 0
    out = []
    for t in tags:
        while curr < t.idx and curr < len(s):
            out.append(escape(s[curr]))
            curr += 1
        out.append(t.tag)

    while curr < len(s):
        out.append(escape(s[curr]))
        curr += 1
    return ''.join(out)


#--------------------- tag generation functions ----------------------

def change_tags(changes, side):
    tags = []
    for c in changes:
        key = c.orig if side == 'left' else c.cur
        if hasattr(key, 'lineno'):
            start = node_start(key)
            end = node_end(key)

            if c.orig is not None and c.cur is not None:
                # <a ...> for change and move
                tags.append(Tag(link_start(c, side), start))
                tags.append(Tag("</a>", end, start))
            else:
                # <span ...> for deletion and insertion
                tags.append(Tag(span_start(c), start))
                tags.append(Tag('</span>', end, start))

    return tags


def change_class(change):
    if change.cur is not None:
        return 'd'
    elif change.orig is not None:
        return 'i'
    elif change.cost > 0:
        return 'c'
    else:
        return 'u'


def span_start(change):
    return '<span class=' + qs(change_class(change)) + '>'


def link_start(change, side):
    cls = change_class(change)

    if side == 'left':
        me, other = change.orig, change.cur
    else:
        me, other = change.cur, change.orig

    return ('<a id=' + qs(uid(me)) +
            ' tid=' + qs(uid(other)) +
            ' class=' + qs(cls) +
            '>')


def qs(s):
    return "'" + s + "'"
