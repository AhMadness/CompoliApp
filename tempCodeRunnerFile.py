            flag_file = f"flags/{country}.png"
            if os.path.isfile(flag_file):
                flag_image = go.layout.Image(
                    source=Image.open(flag_file),
                    xref="x",
                    yref="y",
                    x=x - 0.5,  # Adjust the x position of the flag image
                    y=y - 0.5,  # Adjust the y position of the flag image
                    sizex=1,
                    sizey=1,
                    xanchor="center",
                    yanchor="middle"
                )

                self.fig.add_layout_image(flag_image)