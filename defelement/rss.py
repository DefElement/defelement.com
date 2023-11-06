import html


def make_rss(elements, title, desc, date):
    out = ("<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n"
           "<rss version=\"2.0\">\n"
           "<channel>\n"
           f"  <title>DefElement {title}</title>\n"
           "  <link>https://www.defelement.com/</link>\n"
           f"   <description>{desc}</description>\n")

    for e in elements:
        out += "  <item>\n"
        out += f"    <title>{html.unescape(e.html_name)}</title>\n"
        out += f"    <link>https://www.defelement.com/elements/{e.html_filename}</link>\n"
        out += f"    <description>{html.unescape(e.html_name)}</description>\n"
        if getattr(e, date) is not None:
            out += f"    <pubDate>{getattr(e, date).strftime('%a, %d %b %Y')}</pubDate>\n"
        out += "  </item>\n"

    out += ("</channel>\n"
            "</rss>\n")
    return out
