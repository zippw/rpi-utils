    def generate_gradient(self, colors, step):
        gradient = []
        for i in range(len(colors)):
            gradient.append(colors[i])
            next_color = colors[(i + 1) % len(colors)]
            for j in range(1, step):
                gradient.append(
                    [
                        round(
                            colors[i][k] + ((next_color[k] - colors[i][k]) / step * j)
                        )
                        for k in range(3)
                    ]
                )
        return gradient
    
    def update_lights(self, gradient, index):
        for i in range(len(self.DEFAULT_LIGHT)):
            for j in range(self.LED_COUNT[self.DEFAULT_LIGHT[i]]):
                r, g, b = gradient[(index + j) % len(gradient)]
                self.strips[self.DEFAULT_LIGHT[i]].setPixelColor(j, Color(r, g, b))
            self.strips[self.DEFAULT_LIGHT[i]].show()
        return (index + 1) % len(gradient)
    
    def show_pm2(self, pdg = 0):
        pm2_processes = get_pm2_processes()

        for i, process in enumerate(pm2_processes):
            max_id_len = max(len(str(process["pm_id"])) for process in pm2_processes)
            max_id_len = max_id_len if max_id_len > 2 else 2
            self.draw.text(
                (0, pdg),
                "-" * (2 + max_id_len + 3 + 10 + 2),
                font=self.font,
                fill=255,
            )
            self.draw.text(
                (0, pdg + 8),
                f"| {'id'[:max_id_len]:<{max_id_len}} | {'name'[:10]:<10} |",
                font=self.font,
                fill=255,
            )
            self.draw.text(
                (0, pdg + 8 * 2),
                "-" * (2 + max_id_len + 3 + 10 + 2),
                font=self.font,
                fill=255,
            )
            for i, process in enumerate(pm2_processes):
                self.draw.text(
                    (0, pdg + 8 * 3 + i * 8),
                    f"| {str(process['pm_id'])[:max_id_len]:<{max_id_len}} | {process['name'][:10]:<10} |",
                    font=self.font,
                    fill=255,
                )
