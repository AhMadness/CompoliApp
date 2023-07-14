import sys
import os
import tempfile

import pandas as pd
from PIL import Image

from data import data, data_usa, data_eu, data_g20, data_nato, countries, states, data_search

import plotly.graph_objects as go
import plotly.offline as po

from PyQt6.QtCore import Qt, QUrl, QTimer
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtGui import QIcon, QAction, QDesktopServices

from PyQt6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QLineEdit, QLabel, QPushButton, QComboBox, QCompleter, QMessageBox, QHBoxLayout, QMenu)


class InputDialog(QDialog):
    def __init__(self, view, parent=None):
        super(InputDialog, self).__init__(parent)
        self.mPos = None
        
# --------------------  PLOTLY GRAPH -------------------- #

        axis_range = [-10, 10]

        self.fig = go.Figure()

        self.fig.update_xaxes(range=axis_range, title='', tickmode='linear', showticklabels=False, side='top', gridcolor="rgb(224,224,224)", showgrid=False)
        self.fig.update_yaxes(range=axis_range, title='', tickmode='linear', showticklabels=False, side='right', gridcolor="rgb(224,224,224)", showgrid=False)

        self.fig.update_layout(
            plot_bgcolor='rgb(255,255,255)', 
            height=600, 
            width=600, 
            margin=dict(l=20, r=0, t=0, b=20),
            autosize=False
        )

        # fig.add_vline(x=0, line_width=3)
        # fig.add_hline(y=0, line_width=3)

        # Adding X & Y Axis ~
        self.fig.add_trace(go.Scatter(x=[-11, 11], y=[0, 0], marker=dict(color="black", opacity=1), showlegend=False))
        self.fig.add_trace(go.Scatter(x=[0, 0], y=[-11, 11], marker=dict(color="black", opacity=1), showlegend=False))

        # Add Axis Labels ~
        font = dict(size=18, color='black', family="Montserrat")
        self.fig.add_annotation(x=-10, y=0, text="Communism", xanchor='right', yanchor='middle', textangle=-90, showarrow=False, font=font)
        self.fig.add_annotation(x=10, y=0, text="Capitalism", xanchor='left', yanchor='middle', textangle=90, showarrow=False, font=font)
        self.fig.add_annotation(x=0, y=10, text="Authoritarian", xanchor='center', yanchor='bottom', showarrow=False, font=font)
        self.fig.add_annotation(x=0, y=-10, text="Libertarian", xanchor='center', yanchor='top', showarrow=False, font=font)

        # Adding Color To Quadrants ~
        self.fig.add_shape(type="rect", x0=-10, y0=-10, x1=0, y1=0, fillcolor="#C8E4BC", opacity=1, layer="below", line_width=0,)
        self.fig.add_shape(type="rect", x0=0, y0=-10, x1=10, y1=0, fillcolor="#F5F5A7", opacity=1, layer="below", line_width=0,)
        self.fig.add_shape(type="rect", x0=-10, y0=0, x1=0, y1=10, fillcolor="#F9BABA", opacity=1, layer="below", line_width=0,)
        self.fig.add_shape(type="rect", x0=0, y0=0, x1=10, y1=10, fillcolor="#92D9F8", opacity=1, layer="below", line_width=0,)
        
        self.view = view
        
        
# -------------------- PYQT6 GUI -------------------- #


# -------------------- Adding European Union to Excel file ----------------------- #

        from statistics import mean

        # Adding European Union to the data
        eu_data = [(data[country][0], data[country][1]) for country in data if country.title() in data_eu]
        economy_eu = round(mean([score[0] for score in eu_data]), 2)
        social_eu = round(mean([score[1] for score in eu_data]), 2)

        # Update the data dictionary
        data["European Union"] = (economy_eu, social_eu)
        data_search.append("European Union")
                
# --------------------- INPUT BOX -------------------------- #

        self.setWindowTitle("Compoli Navigator")
        self.setWindowIcon(QIcon("favicon.ico"))
        self.setFixedSize(222, 150)
        layout = QVBoxLayout()

# -------------------- SEARCH -------------------- #

        self.completer = QCompleter(data_search, self)  # Create a QCompleter with your list of countries
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)  # Make the completer case-insensitive
        self.completer.activated.connect(self.on_completer_activated)  # Connect the activated signal to the on_completer_activated method

        # QLineEdit layout
        search_layout = QHBoxLayout()
        self.lineEdit = QLineEdit()
        self.lineEdit.setFixedHeight(24)
        self.lineEdit.setFixedWidth(150)
        self.lineEdit.setCompleter(self.completer)  
        self.lineEdit.editingFinished.connect(self.on_submit)  
        self.lineEdit.setPlaceholderText("Search...")
        search_layout.addWidget(self.lineEdit)
        layout.addLayout(search_layout)
        

# -------------------- DROPDOWN -------------------- #
        
        # QComboBox layout for countries
        dropdown_layout = QHBoxLayout()
        self.dropdown = QComboBox()  
        self.dropdown.setFixedHeight(24)
        self.dropdown.setFixedWidth(150)
        self.dropdown.addItem("Country List") 
        special_categories = ["G20", "EU", "NATO", "All"]  # Your special categories
        self.dropdown.addItems(special_categories)  # Add the special categories to the dropdown
        self.dropdown.insertSeparator(len(special_categories) + 1)  # Insert a separator after the special categories
        self.dropdown.addItems(list(data.keys()))  # Add the list of countries to the dropdown
        self.dropdown.currentIndexChanged.connect(self.on_dropdown_changed)  # Connect to its signal
        dropdown_layout.addWidget(self.dropdown)
        layout.addLayout(dropdown_layout)
        
        # QComboBox layout for states
        dropdown_state_layout = QHBoxLayout()
        self.stateDropdown = QComboBox()  
        self.stateDropdown.setFixedHeight(24)
        self.stateDropdown.setFixedWidth(150)
        self.stateDropdown.addItem("U.S State List") 
        realative = ["Real", "Relative"]
        self.stateDropdown.addItems(realative)  # add 'Real' and 'Relative' to stateDropdown
        self.stateDropdown.insertSeparator(len(realative) + 1)
        self.stateDropdown.addItems(list(data_usa["Real"].keys()))  # Add the list of states to the dropdown
        self.stateDropdown.currentIndexChanged.connect(self.on_stateDropdown_changed)  # Connect to its signal
        dropdown_state_layout.addWidget(self.stateDropdown)
        layout.addLayout(dropdown_state_layout)


# -------------------- BUTTONS -------------------- #

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)  # Pushes the buttons to the center

        # Plot Button
        self.button = QPushButton("Plot!")
        self.button.setFixedSize(60, 30)
        self.button.clicked.connect(self.on_submit)
        button_layout.addWidget(self.button)

        # Reset Button
        self.reset_button = QPushButton("Reset")
        self.reset_button.setFixedSize(60, 30)
        self.reset_button.clicked.connect(self.on_reset)
        button_layout.addWidget(self.reset_button)

        # "?" Button
        self.dropdown_button = QPushButton("?", self)
        self.dropdown_button.setFixedSize(20, 20)
        self.dropdown_button.clicked.connect(self.on_dropdown_clicked)
        self.dropdown_button.setToolTip("References")

        button_layout.addWidget(self.dropdown_button) 

        button_layout.addStretch(1)  # Pushes the "?" button to the right
        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.view_page()
        
# -------------------- FUCNTIONS -------------------- #

    def view_page(self):
        # Create a temporary file
        temp_file_name = tempfile.mktemp(".html")

        config = {"displayModeBar": False, "showTips": False}

        # Save the Plotly figure to the temporary file
        po.plot(self.fig, filename=temp_file_name, auto_open=False, config=config)

        # Load the temporary file in the QWebEngineView
        self.view.load(QUrl.fromLocalFile(temp_file_name))
        
    def on_dropdown_changed(self, index):
        selected_category = self.dropdown.itemText(index)

        if selected_category != "Country List":
            if selected_category == "EU":
                countries_to_plot = [country.title() for country in data_eu]
            elif selected_category == "G20":
                countries_to_plot = [country.title() for country in data_g20]
            elif selected_category == "NATO":
                countries_to_plot = [country.title() for country in data_nato]
            elif selected_category == "All":
                countries_to_plot = list(data.keys())
            else:
                countries_to_plot = [selected_category]

            for country in countries_to_plot:
                self.process_country(country)

            # Reset the selected index
            self.dropdown.blockSignals(True)
            self.dropdown.setCurrentIndex(0)
            self.dropdown.blockSignals(False)
            
    def on_stateDropdown_changed(self, index):
        selected_state_category = self.stateDropdown.itemText(index)

        if selected_state_category != "State List":
            if selected_state_category in ["Real", "Relative"]:
                states_to_plot = list(data_usa[selected_state_category].keys())
                type = selected_state_category
            else:
                states_to_plot = [selected_state_category]
                # If a specific state is selected, default to "Real"
                type = "Real"  

            for state in states_to_plot:
                self.process_state(state, type)

            # Reset the selected index
            self.stateDropdown.blockSignals(True)
            self.stateDropdown.setCurrentIndex(0)
            self.stateDropdown.blockSignals(False)
            
            
    def on_completer_activated(self, text):
        if ' - USA' in text:  # if text is a state
            state = text.replace(' - USA', '')  # remove ' - USA' from the text
            self.process_state(state, "Real")  # by default, we'll use "Real" for states
        else:  # if text is a country
            self.process_country(text)
        QTimer.singleShot(250, self.lineEdit.clear)

    # def on_submit(self):
    #     country = self.lineEdit.text().title() or "Default Country"  # Default country name
    #     self.process_country(country)
    #     self.lineEdit.clear()
    
    def on_submit(self):
        text = self.lineEdit.text().title().strip()  # added .strip() to remove leading/trailing spaces
        if text:  # check if string is not empty
            if text in states:  # if text is a state
                self.process_state(text, "Real")  # by default, we'll use "Real" for states
            else:  # if text is a country
                self.process_country(text)
        self.lineEdit.clear()
            
    def on_reset(self):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Icon.Question)
        msgBox.setText("Are you sure you want to reset the plot?")
        msgBox.setWindowTitle("Reset Confirmation")
        msgBox.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        returnValue = msgBox.exec()
        if returnValue == QMessageBox.StandardButton.Yes:
            # Resetting the plot
            self.fig = go.Figure()
            
            axis_range = [-10, 10]

            self.fig.update_xaxes(range=axis_range, title='', tickmode='linear', showticklabels=False, side='top', gridcolor="rgb(224,224,224)", showgrid=False)
            self.fig.update_yaxes(range=axis_range, title='', tickmode='linear', showticklabels=False, side='right', gridcolor="rgb(224,224,224)", showgrid=False)

            self.fig.update_layout(
                plot_bgcolor='rgb(255,255,255)', 
                height=600, 
                width=600, 
                margin=dict(l=20, r=0, t=0, b=20),
                autosize=False
            )

            # Adding X & Y Axis
            self.fig.add_trace(go.Scatter(x=[-11, 11], y=[0, 0], marker=dict(color="black", opacity=1), showlegend=False))
            self.fig.add_trace(go.Scatter(x=[0, 0], y=[-11, 11], marker=dict(color="black", opacity=1), showlegend=False))

            # Add Axis Labels
            font = dict(size=18, color='black', family="Montserrat")
            self.fig.add_annotation(x=-10, y=0, text="Communism", xanchor='right', yanchor='middle', textangle=-90, showarrow=False, font=font)
            self.fig.add_annotation(x=10, y=0, text="Capitalism", xanchor='left', yanchor='middle', textangle=90, showarrow=False, font=font)
            self.fig.add_annotation(x=0, y=10, text="Authoritarian", xanchor='center', yanchor='bottom', showarrow=False, font=font)
            self.fig.add_annotation(x=0, y=-10, text="Libertarian", xanchor='center', yanchor='top', showarrow=False, font=font)

            # Adding Color To Quadrants
            self.fig.add_shape(type="rect", x0=-10, y0=-10, x1=0, y1=0, fillcolor="#C8E4BC", opacity=1, layer="below", line_width=0,)
            self.fig.add_shape(type="rect", x0=0, y0=-10, x1=10, y1=0, fillcolor="#F5F5A7", opacity=1, layer="below", line_width=0,)
            self.fig.add_shape(type="rect", x0=-10, y0=0, x1=0, y1=10, fillcolor="#F9BABA", opacity=1, layer="below", line_width=0,)
            self.fig.add_shape(type="rect", x0=0, y0=0, x1=10, y1=10, fillcolor="#92D9F8", opacity=1, layer="below", line_width=0,)

            self.view_page()


    def process_country(self, country):
        if country in data:  # Check if country is in the data dictionary
            x, y = data[country]  # Get economic and social scores directly from the data dictionary

            flag_file = f"flags/{country}.png"
            if os.path.isfile(flag_file):
                flag_image = go.layout.Image(
                    source=Image.open(flag_file),
                    xref="x",
                    yref="y",
                    x=x,  # Adjust the x position of the flag image
                    y=y,  # Adjust the y position of the flag image
                    sizex=1,
                    sizey=1,
                    xanchor="center",
                    yanchor="middle"
                )

                scatter_point = go.Scatter(
                    x=[x],
                    y=[y],
                    mode="markers",
                    marker=dict(size=10, symbol='circle', color="black"),
                    showlegend=False,
                    hovertemplate=f"<span>{country}</span><extra></extra>",
                    hoverlabel=dict(bgcolor='white', font=dict(color='black'))
                )
                self.fig.add_layout_image(flag_image)
                self.fig.add_trace(scatter_point)
                self.view_page()  # Update the graph with the new flag image

            else:
                # print(f"No flag file found for {country}")
                pass
        else:
            # print(f"No data found for {country}")
            pass
            
    def process_state(self, state, type):
        # Check if the state is in the data_usa[type] dictionary
        if state in data_usa[type]:  
            x, y = data_usa[type][state]

            flag_file = f"flags_usa/{state}.png"
            if os.path.isfile(flag_file):
                flag_image = go.layout.Image(
                    source=Image.open(flag_file),
                    xref="x",
                    yref="y",
                    x=x,  # Adjust the x position of the flag image
                    y=y,  # Adjust the y position of the flag image
                    sizex=1,
                    sizey=1,
                    xanchor="center",
                    yanchor="middle"
                )

                scatter_point = go.Scatter(
                    x=[x],
                    y=[y],
                    mode="markers",
                    marker=dict(size=10, symbol='circle', color="black"),
                    showlegend=False,
                    hovertemplate=f"<span>{state}</span><extra></extra>",
                    hoverlabel=dict(bgcolor='white', font=dict(color='black'))
                )
                self.fig.add_layout_image(flag_image)
                self.fig.add_trace(scatter_point)
                self.view_page()  # Update the graph with the new flag image

            else:
                # print(f"No flag file found for {state}")
                pass
        else:
            # print(f"No data found for {state}")
            pass

            
    def create_menu(self):
        menu = QMenu(self)

        economic_data_action = menu.addAction("Economic Data")
        economic_data_action.triggered.connect(lambda: self.open_url("https://en.wikipedia.org/wiki/Index_of_Economic_Freedom#Rankings_and_scores"))

        social_data_action = menu.addAction("Social Data")
        social_data_action.triggered.connect(lambda: self.open_url("https://en.wikipedia.org/wiki/Democracy_Index#Components"))
        
        usa_data_action = menu.addAction("USA Data")
        usa_data_action.triggered.connect(lambda: self.open_url("https://www.freedominthe50states.org/"))
        
        return menu
    
    # Defocus the reference button
    def showEvent(self, event):
        super().showEvent(event)
        self.lineEdit.setFocus()

    def open_url(self, url):
        QDesktopServices.openUrl(QUrl(url))

    def mousePressEvent(self, event):
        self.mPos = event.pos()
        event.accept()

    def on_dropdown_clicked(self):
        menu = self.create_menu()
        menu.exec(self.dropdown_button.mapToGlobal(self.dropdown_button.rect().bottomLeft()))

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            if self.mPos is not None:
                # move window to the current mouse position subtract mPos to keep the offset
                self.move(self.mapToGlobal(event.pos() - self.mPos))
            event.accept()
                
    def closeEvent(self, event):
        QApplication.quit()

# -------------------- MAIN APP -------------------- #

# Create a QApplication
app = QApplication(sys.argv)

# Create a QWebEngineView
view = QWebEngineView()

# Set the window title
view.setWindowTitle("Compoli")

# Set the window icon
view.setWindowIcon(QIcon("favicon.ico"))

# Resize the window
view.setFixedSize(610, 620)

# Create an input dialog
dialog = InputDialog(view)

# Show the QWebEngineView
view.show()

# Show the input dialog and bring it to the front
dialog.show()
dialog.raise_()

# Start the QApplication
sys.exit(app.exec())
