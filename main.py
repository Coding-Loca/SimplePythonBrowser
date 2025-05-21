import socket
import ssl
import tkinter

WIDTH, HEIGHT = 800, 600
SCROLL_STEP = 100
HSTEP, VSTEP = 13, 18

#URL parsing
class URL:
    def __init__(self, url):
        # Data scheme has a different format, so it's
        # checked differently data:content/type;base64,
        if url.split(":")[0] == "data":
            self.scheme = "data"
            self.host = ""
            self.content_type, self.path = url.split(",",1)
            return
        
        # Separating the scheme from rest of the URL
        self.scheme, url = url.split("://", 1)
        assert self.scheme in ["http", "https", "file", "data"]
        print(url)
        if self.scheme == "http":
            self.port = 80
        elif self.scheme == "https":
            self.port = 443
        elif self.scheme == "file":
            self.host = ""
            self.path = url
            return
        
        # Separating the host from the path
        if "/" not in url:
            url = url + "/"
        self.host, url = url.split("/", 1)
        self.path = "/" + url

        # Parsing custom ports
        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)
        
    def request(self):

        # Seperate checks for these schemes
        if self.scheme == "data":
            content = self.path
            return content
        if self.scheme == "file":
            with open(self.path) as f:
                content = f.read()
            return content

        # Socket connection
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        )
        s.connect((self.host, self.port))
        
        # SSL wrapper
        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)

        # Making a request, note the blank line to mark EoR
        request = "GET {} HTTP/1.1\r\n".format(self.path) 
        request += "Host: {}\r\n".format(self.host)
        request += "Connection: close\r\n"
        request += "User-Agent: Mozilla/5.0\r\n"
        request += "\r\n"
        s.send(request.encode("utf-8"))

        # Getting a response

        response = s.makefile("r", encoding="utf8", newline="\r\n")
        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)

        response_headers = {}
        while True:
            line = response.readline()
            if line == "\r\n": break
            header, value = line.split(":", 1)
            response_headers[header.casefold()] = value.strip()
        
        # Avoiding these because they compress webpages before sending them
        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers
        
        content = response.read()
        s.close
        return content # This is the body of the webpage

# Turning the html body into human-readable text
def lex(body):
    text = ""
    entity = ""
    entity_check = False
    in_tag = False
    for c in body:
        # Replacing &lt and &gt entities with correct chars
        if c.isspace():
            entity_check = False
            if entity == "lt":
                text += "<"
            if entity == "gt":
                text += ">"
        if entity_check == True:
            entity = entity + c
            continue
        if c =="&":
            entity_check = True
            continue
        
        # Actual text rendering
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            text += c
    return text

def layout(text):
    display_list = []
    cursor_x, cursor_y = HSTEP, VSTEP
    for c in text:
        display_list.append((cursor_x, cursor_y, c))
        # Text wrapping
        cursor_x += HSTEP
        if cursor_x >= WIDTH - HSTEP:
            cursor_y += VSTEP
            cursor_x = HSTEP
    return display_list

class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window,
            width=WIDTH,
            height=HEIGHT
        )
        self.canvas.pack()
        self.scroll = 0
        self.window.bind("<Down>", self.scrolldown)
    # Drawing canvas
    def draw(self):
        self.canvas.delete("all") # Clears the previos canvas
        for x, y, c in self.display_list:
            # Skips rendering offscreen text
            if y > self.scroll + HEIGHT: continue
            if y + VSTEP < self.scroll: continue
            self.canvas.create_text(x, y - self.scroll, text=c)
    def load(self, url):
        body = url.request()
        text = lex(body)
        self.display_list = layout(text)
        self.draw()
    def scrolldown(self, e):
        self.scroll += SCROLL_STEP
        self.draw()
if __name__ == "__main__":
    import sys
    Browser().load(URL(sys.argv[1]))
    tkinter.mainloop()

    # NOTE: 
    # because of the way argv works (?), the standard \ slash in windows path
    # causes issues, so the only way to make file:// scheme to work is writing
    # a path with / forward slashes, `main.py file://c:/Users/examples.htm` 
    # TODO:
    # Data scheme is jank, and the enetity code could be cleaner I think
        
