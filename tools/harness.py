"""v0.1 - drives TrainFrame in headless Chrome over the DevTools protocol (stdlib only) and checks the shell.

Usage (from the repo root):  python -I tools/harness.py [--keep] [--shots DIR]

Serves the repo on a local port, starts headless Chrome with a fresh profile, and checks adding files, class and file
tabs, folders, moving files, the class editor, an open file's rail and notes, the calculator window, settings and persistence across a reload.
Exit 0 when every check passes. --shots saves screenshots. The DevTools code is RunDown's (from QuizQrusher's cdp_shot.py).
"""
import base64, functools, http.server, json, os, shutil, socket, struct, subprocess, sys, tempfile, threading, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = next((p for p in [r"C:\Program Files\Google\Chrome\Application\chrome.exe", r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                           "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/usr/bin/google-chrome", "/usr/bin/chromium"] if os.path.exists(p)), None)


def ws_connect(url):
    host_port, path = url[len("ws://"):].split("/", 1)
    host, port = host_port.split(":")
    s = socket.create_connection((host, int(port)))
    key = base64.b64encode(os.urandom(16)).decode()
    s.sendall(("GET /%s HTTP/1.1\r\nHost: %s\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
               "Sec-WebSocket-Key: %s\r\nSec-WebSocket-Version: 13\r\n\r\n" % (path, host_port, key)).encode())
    buf = b""
    while b"\r\n\r\n" not in buf:
        buf += s.recv(4096)
    return s, buf.split(b"\r\n\r\n", 1)[1]


def ws_send(s, text):
    data = text.encode()
    head = bytearray([0x81])
    n = len(data)
    if n < 126:
        head.append(0x80 | n)
    elif n < 65536:
        head.append(0x80 | 126); head += struct.pack(">H", n)
    else:
        head.append(0x80 | 127); head += struct.pack(">Q", n)
    mask = os.urandom(4)
    s.sendall(bytes(head) + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(data)))


def ws_recv(s, pending):
    buf = pending
    def need(k):
        nonlocal buf
        while len(buf) < k:
            chunk = s.recv(1 << 20)
            if not chunk:
                raise EOFError
            buf += chunk
    message = b""
    while True:
        need(2)
        fin, n = buf[0] & 0x80, buf[1] & 0x7F
        off = 2
        if n == 126:
            need(4); n = struct.unpack(">H", buf[2:4])[0]; off = 4
        elif n == 127:
            need(10); n = struct.unpack(">Q", buf[2:10])[0]; off = 10
        need(off + n)
        message += buf[off:off + n]
        buf = buf[off + n:]
        if fin:
            return message.decode(), buf


class Page:
    def __init__(self, ws_url):
        self.s, self.pending = ws_connect(ws_url)
        self.n = 0
        self.errors = []

    def call(self, method, **params):
        self.n += 1
        my = self.n   # a dialog handled while waiting makes a call of its own, which moves self.n
        ws_send(self.s, json.dumps({"id": my, "method": method, "params": params}))
        while True:
            msg, self.pending = ws_recv(self.s, self.pending)
            m = json.loads(msg)
            if m.get("method") == "Runtime.exceptionThrown":
                self.errors.append(m["params"]["exceptionDetails"].get("exception", {}).get("description") or m["params"]["exceptionDetails"].get("text"))
            if m.get("method") == "Runtime.consoleAPICalled" and m["params"].get("type") == "error":
                self.errors.append(" ".join(str(a.get("value", a.get("description", ""))) for a in m["params"]["args"]))
            if m.get("method") == "Page.javascriptDialogOpening":
                self.call("Page.handleJavaScriptDialog", accept=True)
            if m.get("id") == my:
                if "error" in m:
                    raise RuntimeError("%s: %s" % (method, m["error"]))
                return m.get("result", {})

    def ev(self, js):
        r = self.call("Runtime.evaluate", expression=js, returnByValue=True, awaitPromise=True)
        if r.get("exceptionDetails"):
            raise RuntimeError("JS error in %r: %s" % (js[:80], r["exceptionDetails"].get("exception", {}).get("description")))
        return r["result"].get("value")

    def key(self, key, code=None, vk=0, text=None, mods=0):
        p = {"type": "keyDown" if text else "rawKeyDown", "key": key, "code": code or key, "windowsVirtualKeyCode": vk, "modifiers": mods}
        if text:
            p["text"] = text
            p["unmodifiedText"] = text
        self.call("Input.dispatchKeyEvent", **p)
        self.call("Input.dispatchKeyEvent", type="keyUp", key=key, code=code or key, windowsVirtualKeyCode=vk, modifiers=mods)
        time.sleep(0.02)

    def type(self, s):
        for ch in s:
            if ch == "\n":
                self.key("Enter", "Enter", 13, "\r")
                continue
            self.call("Input.dispatchKeyEvent", type="keyDown", key=ch, text=ch, unmodifiedText=ch)
            self.call("Input.dispatchKeyEvent", type="keyUp", key=ch)
        time.sleep(0.03)

    def click_el(self, selector):
        r = self.ev("(function(){var e=document.querySelector(%s); if(!e) return null; e.scrollIntoView({block:'nearest'}); var b=e.getBoundingClientRect(); return [b.left+b.width/2, b.top+b.height/2];})()" % json.dumps(selector))
        if not r:
            raise RuntimeError("no element " + selector)
        for t in ("mousePressed", "mouseReleased"):
            self.call("Input.dispatchMouseEvent", type=t, x=r[0], y=r[1], button="left", clickCount=1)
        time.sleep(0.12)

    def drag(self, x0, y0, x1, y1):
        self.call("Input.dispatchMouseEvent", type="mousePressed", x=x0, y=y0, button="left", clickCount=1)
        for i in range(1, 6):
            self.call("Input.dispatchMouseEvent", type="mouseMoved", x=x0 + (x1 - x0) * i / 5, y=y0 + (y1 - y0) * i / 5, button="left", buttons=1)
        self.call("Input.dispatchMouseEvent", type="mouseReleased", x=x1, y=y1, button="left", clickCount=1)
        time.sleep(0.1)

    def shot(self, path):
        data = self.call("Page.captureScreenshot", format="png")["data"]
        open(path, "wb").write(base64.b64decode(data))

    def wait_ready(self):
        for _ in range(100):
            if self.ev("!!(window.__tf && document.getElementById('homeGrid').innerHTML)"):
                break
            time.sleep(0.1)
        time.sleep(0.3)


FAILS = []


def check(name, cond, detail=""):
    print(("  ok   " if cond else "  FAIL ") + name + ("" if cond else "  -> " + str(detail)))
    if not cond:
        FAILS.append(name)


def main():
    keep = "--keep" in sys.argv
    shots = sys.argv[sys.argv.index("--shots") + 1] if "--shots" in sys.argv else None
    if shots:
        os.makedirs(shots, exist_ok=True)
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    handler = functools.partial(Quiet, directory=ROOT)
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    httpd.handle_error = lambda *a: None   # Chrome drops keep-alive connections
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    prof = tempfile.mkdtemp(prefix="tfh")
    dport = 9300 + os.getpid() % 500
    chrome = subprocess.Popen([CHROME, "--headless=new", "--remote-debugging-port=%d" % dport, "--user-data-dir=" + prof, "--no-first-run",
                               "--window-size=1280,900", "--disable-gpu", "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(100):
            try:
                tabs = json.loads(urllib.request.urlopen("http://127.0.0.1:%d/json" % dport).read())
                tab = next(t for t in tabs if t["type"] == "page")
                break
            except Exception:
                time.sleep(0.1)
        p = Page(tab["webSocketDebuggerUrl"])
        p.call("Runtime.enable")
        p.call("Page.enable")
        p.call("Page.navigate", url="http://127.0.0.1:%d/index.html" % port)
        p.wait_ready()
        run(p, shots)
        check("no script errors", not p.errors, p.errors)
    finally:
        chrome.kill()
        httpd.shutdown()
        if not keep:
            shutil.rmtree(prof, ignore_errors=True)
    print("\n%d failed" % len(FAILS) if FAILS else "\nall checks passed")
    sys.exit(1 if FAILS else 0)


def run(p, shots):
    J = lambda js: p.ev(js)
    TABS = "Array.from(document.querySelectorAll('#clsTabs .xtab-name')).map(function(b){ return b.textContent; })"
    FTABS = "Array.from(document.querySelectorAll('#fileTabs .xtab-name')).map(function(b){ return b.textContent; })"
    CARDS = "Array.from(document.querySelectorAll('#homeGrid > .grid .folder b')).map(function(b){ return b.textContent; })"
    S = lambda: J("[__tf.screen, __tf.tabs().cur]")
    PATH = lambda: J("(function(){ var t = __tf.tabs(); return t.by[t.cur] ? t.by[t.cur].path : null; })()")

    print("Empty library")
    check("starts on the Library home with the empty state", J("__tf.screen") == "home" and J("!!document.querySelector('#homeGrid .empty')"))
    check("no class tabs yet", J(TABS) == [])
    check("app switcher shows when hosted, with TrainFrame current",
          J("!document.getElementById('appSwitch').classList.contains('hidden') && document.querySelector('.appsw-item.tf').getAttribute('aria-current')") == "page")

    print("Adding files")
    p.click_el("[data-act=demo]")
    for _ in range(30):
        if J("!!__tf.files.demo"):
            break
        time.sleep(0.1)
    check("the demo file is added (its header IDs are in braces)", J("!!__tf.files.demo") and J("__tf.info.demo.problems.map(function(x){ return x.id; })") == ["P1", "P2"])
    check("it stays on the Library, which now lists Demo", J("__tf.screen") == "home" and J(CARDS) == ["Demo"], (S(), J(CARDS)))
    J("""(async function(){
      var t = await fetch('examples/demo.frame').then(function(r){ return r.text(); });
      var a = await __tf.importTexts([{ name: 'x.frame', text: t }, { name: 'bad.frame', text: 'title: no header' },
        { name: 'noid.frame', text: '@frame\\ntitle: T' },
        { name: 'other.frame', text: '@frame {second}\\ntitle: Second file\\nclass: ECEN 305\\nfolder: Exams/Midterm 1\\n\\n@problem {P1} A\\npoints: 5\\n' }]);
      window.__rep = a; __tf.afterImport(a);
    })()""")
    rep = J("__rep.map(function(r){ return r.kind; })")
    check("report: same file unchanged, two bad, one added", rep == ["same", "bad", "bad", "ok"], rep)
    check("the report shows on the Library", J("document.querySelectorAll('#homeAdd #addReport li').length") == 4)
    check("class cards are sorted", J(CARDS) == ["Demo", "ECEN 305"], J(CARDS))

    print("Class tabs")
    p.click_el("#homeGrid [data-copen='Demo']")
    check("clicking a class opens its tab next to Library", J(TABS) == ["Demo"] and S() == ["class", "Demo"], (J(TABS), S()))
    check("it opens on Assignments with its folder", J("Array.from(document.querySelectorAll('#sec_assignments .folder b')).map(function(b){ return b.textContent; })") == ["Examples"])
    J("__tf.openClass('ECEN 305')")
    p.click_el("#sec_assignments .folder[data-go='Exams']")
    p.click_el("#sec_assignments .folder[data-go='Exams/Midterm 1']")
    check("a second class tab goes after the current one", J(TABS) == ["Demo", "ECEN 305"], J(TABS))
    check("folders open inside the class", PATH() == "Exams/Midterm 1", PATH())
    p.click_el("#clsTabs [data-cpick='Demo']")
    check("clicking a class tab switches to it", S() == ["class", "Demo"])
    p.click_el("#clsTabs [data-cpick='ECEN 305']")
    check("each class tab remembers its folder", PATH() == "Exams/Midterm 1", PATH())

    print("File tabs")
    p.click_el("#sec_assignments .fcard .open")
    check("opening a file adds a tab above the class's sections", J(FTABS) == ["Second file"] and J("__tf.cur") == "second", (J(FTABS), J("__tf.cur")))
    check("no section is selected while a file shows", J("document.querySelectorAll('#secTabs [aria-selected=true]').length") == 0)
    p.click_el("#clsTabs [data-cpick='Demo']")
    p.click_el("#sec_assignments .folder[data-go='Examples']")
    p.click_el("#sec_assignments .fcard .open")
    check("each class keeps its own open files", J(FTABS) == ["A Tour of TrainFrame"], J(FTABS))
    check("the rail has Formulas, then P1 and P2", J("Array.from(document.querySelectorAll('#rail a .rn')).map(function(e){ return e.textContent; })") == ["Fx", "P1", "P2"])
    check("the path line names the class and folder", J("document.querySelector('.fpath .crumbs').textContent") == "Demo›Examples", J("document.querySelector('.fpath .crumbs').textContent"))
    p.click_el("#rail a[data-p=P2]")
    for _ in range(30):   # let the smooth scroll settle
        y0 = J("Math.round(window.scrollY)")
        time.sleep(0.15)
        if J("Math.round(window.scrollY)") == y0:
            break
    check("clicking P2 in the rail scrolls there and highlights it", J("__tf.curProblem") == "P2" and y0 > 300, (J("__tf.curProblem"), y0))
    p.click_el("#clsTabs [data-cpick='ECEN 305']")
    check("the other class shows its own file", J("__tf.cur") == "second")
    p.click_el("#clsTabs [data-cpick='Demo']")
    check("switching back returns to the same scroll spot", abs(J("Math.round(window.scrollY)") - y0) <= 2 and J("__tf.curProblem") == "P2", (J("Math.round(window.scrollY)"), y0))
    p.click_el("#secTabs [data-sec=assignments]")
    check("a section tab shows the section and keeps the file tab", J("__tf.cur") is None and J(FTABS) == ["A Tour of TrainFrame"])
    p.click_el("#fileTabs [data-fpick=demo]")
    check("the file tab brings the file back where it was", abs(J("Math.round(window.scrollY)") - y0) <= 2, (J("Math.round(window.scrollY)"), y0))
    if shots:
        p.shot(os.path.join(shots, "tabs.png"))

    print("Notes")
    check("the notes tab shows on an open file", J("!document.getElementById('noteDock').classList.contains('hidden')"))
    p.click_el("#noteToggle")
    check("the notes box opens", J("!document.getElementById('notePanel').classList.contains('hidden')"))
    p.click_el("#noteHeading")
    p.type("Tau is RC.")
    time.sleep(0.7)
    check("Insert heading adds the problem you're on", J("document.getElementById('noteText').value") == "## P2 · RC charging\nTau is RC.", repr(J("document.getElementById('noteText').value")))
    check("notes are saved", J("__tf.notes.demo && __tf.notes.demo.text") == "## P2 · RC charging\nTau is RC.")
    p.click_el("#clsTabs [data-cpick='ECEN 305']")
    check("another file has its own (empty) notes", J("document.getElementById('noteText').value") == "")
    p.click_el("#clsTabs [data-cpick='Demo']")
    if shots:
        p.shot(os.path.join(shots, "notes.png"))

    print("Persistence")
    J("__tf.flush()")
    time.sleep(0.3)
    p.call("Page.reload")
    p.wait_ready()
    time.sleep(0.3)
    check("the class tabs come back", J(TABS) == ["Demo", "ECEN 305"] and S() == ["class", "Demo"], (J(TABS), S()))
    check("the open file comes back at its scroll spot", J("__tf.cur") == "demo" and abs(J("Math.round(window.scrollY)") - y0) <= 2, (J("__tf.cur"), J("Math.round(window.scrollY)"), y0))
    check("notes survive a reload", J("__tf.notes.demo && __tf.notes.demo.text") == "## P2 · RC charging\nTau is RC.")

    print("Closing tabs")
    p.click_el("#fileTabs [data-fclose=demo]")
    check("closing the only file tab shows the class's section", J(FTABS) == [] and J("__tf.cur") is None and J("document.getElementById('fstrip').classList.contains('hidden')"))
    p.click_el("#clsTabs [data-cclose='Demo']")
    check("closing a class tab moves to its neighbor", J(TABS) == ["ECEN 305"] and S() == ["class", "ECEN 305"], (J(TABS), S()))
    p.click_el("#clsTabs [data-cclose='ECEN 305']")
    check("closing the last class tab shows the Library", J(TABS) == [] and J("__tf.screen") == "home")
    check("the classes stay in the Library", J(CARDS) == ["Demo", "ECEN 305"])

    print("Folders and moving")
    p.click_el("#homeGrid [data-copen='ECEN 305']")
    check("a reopened class keeps its file tabs", J(FTABS) == ["Second file"] and J("__tf.cur") == "second", (J(FTABS), J("__tf.cur")))
    p.click_el("#secTabs [data-sec=assignments]")
    J("__tf.goFolder('ECEN 305', '')")
    p.click_el("[data-act=newfolder]")
    p.type("Homework")
    p.key("Enter", "Enter", 13, "\r")
    time.sleep(0.2)
    check("New folder makes and opens an empty folder", PATH() == "Homework" and J("!!__tf.places['ECEN 305\\u0001Homework']"), PATH())
    check("an empty folder made in the app can be removed", J("!!document.querySelector('[data-act=rmplace]')"))
    J("__tf.goFolder('Demo', 'Examples')")
    p.click_el("[data-act=move][data-id=demo]")
    J("document.getElementById('moveCls').value = 'ECEN 305'; document.getElementById('moveFolder').value = 'Homework'; document.getElementById('moveDialog').close('ok')")
    time.sleep(0.2)
    check("Move files the demo under ECEN 305 > Homework", J("[__tf.files.demo.cls, __tf.files.demo.folder]") == ["ECEN 305", "Homework"] and S() == ["class", "ECEN 305"] and PATH() == "Homework",
          (J("[__tf.files.demo.cls, __tf.files.demo.folder]"), S(), PATH()))
    check("the Demo class and its tab are gone once it's empty", J(TABS) == ["ECEN 305"], J(TABS))
    p.click_el("[data-act=move][data-id=demo]")
    J("document.getElementById('moveDialog').close('reset')")
    time.sleep(0.2)
    check("Use the file's own puts it back", J("[__tf.files.demo.cls, __tf.files.demo.folder]") == [None, None] and J(TABS) == ["ECEN 305", "Demo"], J(TABS))

    print("Formula sheet and search")
    J("__tf.openClass('Demo'); __tf.showSection('formulas')")
    check("the formula sheet lists the demo's 4 formulas", J("document.querySelectorAll('#sec_formulas .flist li').length") == 4)
    J("__tf.showSection('search'); var s = document.getElementById('searchBox'); s.value = 'memoryless'; s.dispatchEvent(new Event('input'))")
    check("search finds a line", J("document.querySelectorAll('#searchHits li button').length") >= 1)
    p.click_el("#searchHits li button")
    check("a search hit opens the file in a tab", J("__tf.cur") == "demo" and J(FTABS) == ["A Tour of TrainFrame"])

    print("Class editor")
    J("__tf.openClass('ECEN 305'); __tf.showSection('assignments')")
    p.click_el("[data-act=editclass]")
    check("Edit class opens with the name filled in", J("document.getElementById('classDialog').open && document.getElementById('className').value") == "ECEN 305")
    J("document.getElementById('className').value = 'Probability'; document.getElementById('classDialog').close('ok')")
    time.sleep(0.2)
    check("renaming renames the tab and moves the files and folders", J(TABS) == ["Probability", "Demo"] and J("__tf.clsOf(__tf.files.second)") == "Probability" and J("!!__tf.places['Probability\\u0001Homework']"),
          (J(TABS), J("__tf.clsOf(__tf.files.second)")))
    J("""(async function(){ var a = await __tf.importTexts([{ name: 'third.frame', text: '@frame {third}\\ntitle: Third\\nclass: ECEN 305\\n' }]); __tf.afterImport(a); })()""")
    check("a new file with the old class name lands in the renamed class", J("__tf.clsOf(__tf.files.third)") == "Probability")
    p.click_el("[data-act=editclass]")
    J("document.getElementById('classDialog').close('archive')")
    time.sleep(0.2)
    check("archiving closes the tab and lists it under Archived", J(TABS) == ["Demo"] and J("__tf.classes.Probability.archived") is True, J(TABS))
    J("__tf.showScreen('home')")
    check("the Library shows it under Archived only", J(CARDS) == ["Demo"] and J("document.querySelectorAll('#archList .folder').length") == 1, J(CARDS))
    J("document.getElementById('archList').open = true")
    p.click_el("#archList [data-copen='Probability']")
    check("an archived class still opens, with a note", S() == ["class", "Probability"] and J("!document.getElementById('archBar').classList.contains('hidden')"))
    p.click_el("#archBar [data-act=unarchive]")
    check("Unarchive brings it back", J("__tf.classes.Probability.archived") is False and J("document.getElementById('archBar').classList.contains('hidden')"))
    p.click_el("[data-act=editclass]")
    J("document.getElementById('classDialog').close('delete')")
    time.sleep(0.4)
    J("1")
    check("deleting a class deletes its files and closes its tab", J("Object.keys(__tf.files).sort()") == ["demo"] and J(TABS) == ["Demo"] and J("__tf.screen") == "home",
          (J("Object.keys(__tf.files).sort()"), J(TABS), J("__tf.screen")))

    print("Calculator")
    p.click_el("#calcBtn")
    check("the calculator window opens", J("!document.getElementById('calcWin').classList.contains('hidden')"))
    r0 = J("(function(){ var b = document.getElementById('calcHead').getBoundingClientRect(); return [b.left + 40, b.top + 12]; })()")
    p.drag(r0[0], r0[1], r0[0] - 300, r0[1] + 200)
    pos = J("JSON.parse(localStorage.getItem('trainFrame:calcPos'))")
    check("dragging the title bar moves it and remembers the spot", pos and abs(pos["y"] - (r0[1] - 12 + 200)) < 4, (pos, r0))
    check("it stays open on other screens", J("__tf.showScreen('settings'), !document.getElementById('calcWin').classList.contains('hidden')"))

    print("Settings")
    check("settings render with the Teal accent selected", J("document.querySelector('#set_accent [aria-pressed=true]').title") == "Teal")
    p.click_el("#set_theme [data-val=dark]")
    check("the theme switch sets data-theme", J("document.documentElement.getAttribute('data-theme')") == "dark")
    STORAGE = "Array.from(document.querySelectorAll('#settingsBody .set-row')).filter(function(r){ return r.querySelector('.set-label').textContent === 'Storage'; })[0].querySelector('.set-desc').textContent"
    check("the storage row counts files and notes", J(STORAGE).startswith("1 file and 1 notes box"), J(STORAGE))

    print("Phone width")
    p.call("Emulation.setDeviceMetricsOverride", width=390, height=844, deviceScaleFactor=2, mobile=True)
    J("__tf.openFile('demo')")
    time.sleep(0.3)
    check("the rail becomes a sideways strip", J("getComputedStyle(document.getElementById('rail')).flexDirection") == "row")
    UNDER = "(document.querySelector('.appbar').offsetHeight + document.getElementById('chead').offsetHeight) + 'px'"
    check("the rail strip sits right under the sticky bars", J("getComputedStyle(document.getElementById('rail')).top") == J(UNDER),
          (J("getComputedStyle(document.getElementById('rail')).top"), J(UNDER)))
    check("the page doesn't scroll sideways", J("document.documentElement.scrollWidth <= window.innerWidth"), J("[document.documentElement.scrollWidth, window.innerWidth]"))
    check("the calculator spans the width", J("(function(){ var b = document.getElementById('calcWin').getBoundingClientRect(); return b.left <= 9 && b.right >= window.innerWidth - 9; })()"))
    if shots:
        p.shot(os.path.join(shots, "phone.png"))
    J("__tf.showScreen('home')")
    check("the Library fits a phone too", J("document.documentElement.scrollWidth <= window.innerWidth"), J("[document.documentElement.scrollWidth, window.innerWidth]"))
    p.call("Emulation.clearDeviceMetricsOverride")


if __name__ == "__main__":
    main()
