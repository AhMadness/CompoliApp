import sys, os, json, base64, tempfile
from statistics import mean

from PIL import Image

from data import (
    data, data_usa, data_eu, data_g20, data_nato,
    countries, states, data_search                      # ← your existing modules
)

import plotly.graph_objects as go
import plotly.io as pio

from PyQt6.QtCore import Qt, QUrl, QTimer
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtGui import QIcon, QDesktopServices
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QLineEdit, QLabel, QPushButton,
    QComboBox, QCompleter, QMessageBox, QHBoxLayout, QMenu
)

def resource_path(rel_path: str):
    """
    Return an absolute path whether we’re running from source or from a PyInstaller one-file bundle.
    """
    base = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base, rel_path)

# ──────────────────────────  MAIN DIALOG  ────────────────────────── #

class InputDialog(QDialog):
    def __init__(self, view: QWebEngineView, parent=None):
        super().__init__(parent)
        self.view = view
        self.page_ready = False   # set True when the page finishes first load
        self.mPos = None

        # ── BUILD BASE FIGURE ── #
        self.fig = self._build_base_figure()

        # add EU aggregate once, before any searches
        eu_scores = [(data[c][0], data[c][1]) for c in data if c.title() in data_eu]
        data["European Union"] = (round(mean(x for x, _ in eu_scores), 2),
                                  round(mean(y for _, y in eu_scores), 2))
        data_search.append("European Union")

        # ── PYQT LAYOUT ── #
        self._build_gui()
        self._load_initial_html()   # one-time page load


    # ──────────────────────────  BUILDERS  ────────────────────────── #

    def _build_base_figure(self) -> go.Figure:
        axis_range = [-10, 10]
        fig = go.Figure()
        fig.update_xaxes(range=axis_range, title='', tickmode='linear',
                         showticklabels=False, side='top', showgrid=False)
        fig.update_yaxes(range=axis_range, title='', tickmode='linear',
                         showticklabels=False, side='right', showgrid=False)
        fig.update_layout(plot_bgcolor='white', height=600, width=600,
                          margin=dict(l=20, r=0, t=0, b=20), autosize=False)

        # axis lines
        fig.add_trace(go.Scatter(x=[-11, 11], y=[0, 0], marker=dict(color="black"), showlegend=False))
        fig.add_trace(go.Scatter(x=[0, 0], y=[-11, 11], marker=dict(color="black"), showlegend=False))

        # labels
        fnt = dict(size=18, color='black', family="Montserrat")
        fig.add_annotation(x=-10, y=0, text="Communism",  textangle=-90, xanchor='right', yanchor='middle',
                           showarrow=False, font=fnt)
        fig.add_annotation(x=10,  y=0, text="Capitalism", textangle=90,  xanchor='left',  yanchor='middle',
                           showarrow=False, font=fnt)
        fig.add_annotation(x=0,   y=10, text="Authoritarian", yanchor='bottom',
                           showarrow=False, font=fnt)
        fig.add_annotation(x=0,   y=-10,text="Libertarian",   yanchor='top',
                           showarrow=False, font=fnt)

        # quadrant fills
        fig.add_shape(type="rect", x0=-10, y0=-10, x1=0,  y1=0,  fillcolor="#C8E4BC", line_width=0, layer="below")
        fig.add_shape(type="rect", x0=0,  y0=-10, x1=10, y1=0,  fillcolor="#F5F5A7", line_width=0, layer="below")
        fig.add_shape(type="rect", x0=-10, y0=0,  x1=0,  y1=10, fillcolor="#F9BABA", line_width=0, layer="below")
        fig.add_shape(type="rect", x0=0,  y0=0,  x1=10, y1=10, fillcolor="#92D9F8", line_width=0, layer="below")
        return fig


    def _build_gui(self):
        self.setWindowTitle("Compoli Navigator")
        view.setWindowIcon(QIcon(resource_path("favicon.ico")))
        self.setFixedSize(222, 150)
        vbox = QVBoxLayout(self)

        # search line
        self.lineEdit = QLineEdit(placeholderText="Search...")
        self.lineEdit.setFixedSize(150, 24)
        completer = QCompleter(data_search, self)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.activated.connect(self._on_completer)
        self.lineEdit.setCompleter(completer)
        self.lineEdit.editingFinished.connect(self._on_submit)
        hl = QHBoxLayout(); hl.addWidget(self.lineEdit); vbox.addLayout(hl)

        # country dropdown
        self.dropdown = QComboBox(); self.dropdown.setFixedSize(150, 24)
        self.dropdown.addItem("Country List")
        specials = ["G20","EU","NATO","All"]
        self.dropdown.addItems(specials); self.dropdown.insertSeparator(len(specials)+1)
        self.dropdown.addItems(list(data.keys()))
        self.dropdown.currentIndexChanged.connect(self._on_dropdown)
        hl = QHBoxLayout(); hl.addWidget(self.dropdown); vbox.addLayout(hl)

        # state dropdown
        self.stateDropdown = QComboBox(); self.stateDropdown.setFixedSize(150, 24)
        self.stateDropdown.addItem("U.S State List")
        modes = ["Real","Relative"]
        self.stateDropdown.addItems(modes); self.stateDropdown.insertSeparator(len(modes)+1)
        self.stateDropdown.addItems(list(data_usa["Real"].keys()))
        self.stateDropdown.currentIndexChanged.connect(self._on_state_dropdown)
        hl = QHBoxLayout(); hl.addWidget(self.stateDropdown); vbox.addLayout(hl)

        # buttons
        plotBtn = QPushButton("Plot!")
        plotBtn.setFixedSize(60, 30)
        plotBtn.clicked.connect(self._on_submit)

        resetBtn = QPushButton("Reset")
        resetBtn.setFixedSize(60, 30)
        resetBtn.clicked.connect(self._on_reset)

        refBtn = QPushButton("?")
        refBtn.setFixedSize(20, 20)
        refBtn.clicked.connect(self._on_refs)
        refBtn.setToolTip("References")

        hl = QHBoxLayout(); hl.addStretch(1)
        hl.addWidget(plotBtn); hl.addWidget(resetBtn); hl.addWidget(refBtn); hl.addStretch(1)
        vbox.addLayout(hl)


    # ──────────────────────────  INITIAL PAGE LOAD  ────────────────────────── #

    def _load_initial_html(self):
        """Load the base figure once and inject JS helpers."""
        fig_html = pio.to_html(self.fig, include_plotlyjs='cdn',
                               full_html=False, div_id='chart')
        helpers = """
        <script>
        function addPoint(trace){ Plotly.addTraces('chart', trace); }
        function addFlag(b64,x,y){
            const img={source:'data:image/png;base64,'+b64,
                       xref:'x',yref:'y',x:x,y:y,sizex:1,sizey:1,
                       xanchor:'center',yanchor:'middle'};
            const cur = (document.getElementById('chart').layout.images||[]);
            Plotly.relayout('chart',{images:cur.concat([img])});
        }
        </script>
        """
        html = f"<html><head><meta charset='utf-8'></head><body>{fig_html}{helpers}</body></html>"

        self.view.loadFinished.connect(lambda ok: setattr(self, "page_ready", bool(ok)))
        self.view.setHtml(html, QUrl("about:blank"))


    # ──────────────────────────  EVENT HANDLERS  ────────────────────────── #

    def _on_completer(self, text:str):
        if ' - USA' in text:
            self._plot_state(text.replace(' - USA',''), "Real")
        else:
            self._plot_country(text)
        QTimer.singleShot(250, self.lineEdit.clear)

    def _on_submit(self):
        txt = self.lineEdit.text().title().strip()
        if not txt: return
        if txt in states:
            self._plot_state(txt, "Real")
        else:
            self._plot_country(txt)
        self.lineEdit.clear()

    def _on_dropdown(self, idx:int):
        choice = self.dropdown.itemText(idx)
        if choice == "Country List": return

        mapping = {
            "EU"  : [c.title() for c in data_eu],
            "G20" : [c.title() for c in data_g20],
            "NATO": [c.title() for c in data_nato],
            "All" : list(data.keys())
        }
        for country in mapping.get(choice, [choice]):
            self._plot_country(country)

        self.dropdown.blockSignals(True); self.dropdown.setCurrentIndex(0); self.dropdown.blockSignals(False)

    def _on_state_dropdown(self, idx:int):
        choice = self.stateDropdown.itemText(idx)
        if choice == "U.S State List": return

        if choice in ("Real","Relative"):
            for st in data_usa[choice].keys():
                self._plot_state(st, choice)
        else:
            self._plot_state(choice, "Real")

        self.stateDropdown.blockSignals(True); self.stateDropdown.setCurrentIndex(0); self.stateDropdown.blockSignals(False)


    # ──────────────────────────  PLOTTING HELPERS  ────────────────────────── #

    def _run_js(self, script:str):
        """Queue JS code; wait for initial load if needed."""
        if self.page_ready:
            self.view.page().runJavaScript(script)
        else:
            QTimer.singleShot(100, lambda s=script: self._run_js(s))

    def _js_add_point(self, trace:dict):
        self._run_js(f"addPoint({json.dumps(trace)});")

    def _js_add_flag(self, path:str, x:float, y:float):
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        self._run_js(f"addFlag('{b64}', {x}, {y});")

    # country / state to plot
    def _plot_country(self, country:str):
        if country not in data: return
        x, y = data[country]

        trace = dict(x=[x], y=[y], mode='markers',
                     marker=dict(size=10, symbol='circle', color='black'),
                     showlegend=False,
                     hovertemplate=f"<span>{country}</span><extra></extra>")
        self._js_add_point(trace)

        flag = resource_path(f"flags/{country}.png")
        if os.path.isfile(flag):
            self._js_add_flag(flag, x, y)

    def _plot_state(self, state:str, mode:str):
        if state not in data_usa[mode]: return
        x, y = data_usa[mode][state]

        trace = dict(x=[x], y=[y], mode='markers',
                     marker=dict(size=10, symbol='circle', color='black'),
                     showlegend=False,
                     hovertemplate=f"<span>{state}</span><extra></extra>")
        self._js_add_point(trace)

        flag = resource_path(f"flags_usa/{state}.png")
        if os.path.isfile(flag):
            self._js_add_flag(flag, x, y)


    # ──────────────────────────  RESET  ────────────────────────── #

    def _on_reset(self):
        if QMessageBox.question(self, "Reset confirmation", "Reset the plot?") != QMessageBox.StandardButton.Yes:
            return
        self.fig = self._build_base_figure()
        self.page_ready = False
        self._load_initial_html()


    # ──────────────────────────  MISC  ────────────────────────── #

    def _on_refs(self):
        menu = QMenu(self)
        menu.addAction("Economic Data",
                       lambda: self._open("https://en.wikipedia.org/wiki/Index_of_Economic_Freedom#Rankings_and_scores"))
        menu.addAction("Social Data",
                       lambda: self._open("https://en.wikipedia.org/wiki/Democracy_Index#Components"))
        menu.addAction("USA Data",
                       lambda: self._open("https://www.freedominthe50states.org/"))
        menu.exec(self.sender().mapToGlobal(self.sender().rect().bottomLeft()))

    def _open(self,url:str):
        QDesktopServices.openUrl(QUrl(url))

    # ─── smoother window drag ───
    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = e.globalPosition().toPoint()  # store global cursor pos
            e.accept()

    def mouseMoveEvent(self, e):
        if (e.buttons() & Qt.MouseButton.LeftButton) and hasattr(self, "_drag_pos"):
            new_pos = self.pos() + (e.globalPosition().toPoint() - self._drag_pos)
            self.move(new_pos)
            self._drag_pos = e.globalPosition().toPoint()  # update for the next move
            e.accept()

    def closeEvent(self, e): QApplication.quit()


# ──────────────────────────  APP SETUP  ────────────────────────── #

app  = QApplication(sys.argv)
view = QWebEngineView()
view.setWindowTitle("Compoli"); view.setWindowIcon(QIcon("favicon.ico"))
view.setFixedSize(610,620)

dlg = InputDialog(view)
view.show(); dlg.show(); dlg.raise_()

sys.exit(app.exec())
